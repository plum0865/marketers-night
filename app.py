import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# 1. 페이지 설정
st.set_page_config(page_title="마케터의 밤 지출 분석", layout="wide")

# 🔍 구글 시트 URL을 본인 것으로 교체하세요
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQwyqr83a7VFrYiqtKpnJenXkPV3S3zx_u-7jZ2wWltFDLUAyQGMDJdquCnSh54h_j4cwvzyX7n_Skk/pub?gid=0&single=true&output=csv"

# --- 🎨 디자인 개선: 간격 및 스타일 CSS ---
st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 20px !important;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-top: 5px solid #f0f2f6;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    [data-testid="stMetricLabel"] { font-size: 1.05rem !important; font-weight: 600 !important; color: #444 !important; }
    [data-testid="stMetricValue"] { font-size: 1.85rem !important; font-weight: 800 !important; }
    [data-testid="column"] { padding: 0 8px !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=1)
def load_data(source):
    try:
        raw_data = pd.read_csv(source, header=None, skiprows=4)
        df = raw_data.iloc[:, [1, 2, 11, 20, 21]].copy()
        df.columns = ['날짜_원본', '후원사명', '케이터링', '후원입금', '소계_지출']
        
        def to_num(v):
            if pd.isna(v): return 0.0
            v_str = str(v).replace(',', '').replace('₩', '').replace(' ', '').strip()
            if v_str == '' or v_str == '-': return 0.0
            try: return float(v_str)
            except: return 0.0

        def to_date(v):
            if pd.isna(v): return pd.NaT
            m = re.search(r'(\d{4})[\.\s](\d{1,2})[\.\s](\d{1,2})', str(v))
            if m: return pd.to_datetime(f"{m.group(1)}-{m.group(2)}-{m.group(3)}")
            return pd.NaT

        df['날짜'] = df['날짜_원본'].apply(to_date)
        df['케이터링'] = df['케이터링'].apply(to_num)
        df['후원입금'] = df['후원입금'].apply(to_num)
        df['소계_지출'] = df['소계_지출'].apply(to_num)
        df = df[df['날짜'].notna()]
        df = df[~df['후원사명'].str.contains('합계|소계|전체', na=False)]
        df['Year'] = df['날짜'].dt.year.astype('Int64')
        df['Month'] = df['날짜'].dt.month.astype('Int64')
        return df.sort_values('날짜')
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
        return pd.DataFrame()

main_df = load_data(SHEET_URL)

st.title("🌙 마케터의 밤 지출 리포트")

if not main_df.empty:
    with st.sidebar:
        st.subheader("🗓️ 기간 선택")
        years = sorted(main_df['Year'].unique(), reverse=True)
        sel_year = st.selectbox("연도", years)
        y_df = main_df[main_df['Year'] == sel_year]
        months = sorted(y_df['Month'].unique())
        sel_months = st.multiselect("월 선택", months, format_func=lambda x: f"{x:02d}월")

    f_df = y_df[y_df['Month'].isin(sel_months)].copy() if sel_months else y_df.copy()

    # 집계 데이터
    sum_total_spent = f_df['소계_지출'].sum()
    sum_catering = f_df['케이터링'].sum()
    sum_income = f_df['후원입금'].sum()
    total_count = len(f_df)

    # --- KPI 레이아웃 ---
    c1, c2, c3, c4 = st.columns(4)
    def set_color(idx, val):
        color = "#e74c3c" if val < 0 else "#1f77b4"
        st.markdown(f"<style>div[data-testid='column']:nth-of-type({idx}) div[data-testid='stMetricValue'] {{ color: {color} !important; }}</style>", unsafe_allow_html=True)

    with c1:
        set_color(1, sum_total_spent)
        st.metric("💰 총 지출액", f"{'-' if sum_total_spent < 0 else ''}₩{abs(sum_total_spent):,.0f}")
    with c2:
        set_color(2, -sum_catering)
        st.metric("🍔 케이터링 지출액", f"-₩{abs(sum_catering):,.0f}")
    with c3:
        set_color(3, sum_income)
        st.metric("📈 후원비용 입금액", f"{'-' if sum_income < 0 else ''}₩{abs(sum_income):,.0f}")
    with c4:
        set_color(4, 1)
        st.metric("📝 지출 건수", f"{total_count}건")

    st.write("---")
    
    # --- 📈 시각화 다듬기 영역 ---
    l_col, r_col = st.columns([1.5, 1])

    with l_col:
        st.subheader("📊 월별 지출 현황")
        m_plot = f_df.resample('ME', on='날짜')['소계_지출'].sum().reset_index()
        m_plot['label'] = m_plot['날짜'].dt.strftime('%y.%m')
        
        # 1. 바 차트 시각화 (색상 통일 및 글자 가독성 확보)
        fig_bar = px.bar(m_plot, x='label', y='소계_지출', 
                         color_discrete_sequence=['#1f77b4'], # 파란색 단일톤으로 깔끔하게 통일
                         text_auto=',.0f', template='plotly_white')
        
        fig_bar.update_layout(height=450, margin=dict(t=20, b=20, l=10, r=10),
                              xaxis_title="", yaxis_title="",
                              xaxis=dict(tickfont=dict(color='black', size=12, family="Arial Bold")),
                              yaxis=dict(tickformat=',.0f', tickprefix='₩', tickfont=dict(color='black', size=12)))
        
        # 핵심: 막대 내부 숫자를 흰색으로 변경하여 가시성 확보
        fig_bar.update_traces(textposition='inside', textfont=dict(color='white', size=14, family="Arial Bold"))
        st.plotly_chart(fig_bar, use_container_width=True)

    with r_col:
        st.subheader("🍕 후원사별 지출 비중")
        sponsor_sums = f_df.groupby('후원사명')['소계_지출'].sum().sort_values(ascending=False).reset_index()
        
        # 상위 8개만 표시하고 나머지는 기타로 묶어 가시성 확보
        top_n = 8
        if len(sponsor_sums) > top_n:
            top_df = sponsor_sums.head(top_n).copy()
            others_val = sponsor_sums.iloc[top_n:]['소계_지출'].sum()
            others_df = pd.DataFrame([{'후원사명': '기타 (Others)', '소계_지출': others_val}])
            plot_df = pd.concat([top_df, others_df], ignore_index=True)
        else:
            plot_df = sponsor_sums

        # 2. 도넛 차트 설정 (중앙 텍스트 완전 삭제 및 블루톤 그라데이션)
        fig_pie = go.Figure(data=[go.Pie(labels=plot_df['후원사명'], values=plot_df['소계_지출'],
                                       hole=0.6, 
                                       marker=dict(colors=px.colors.sequential.Blues_r, line=dict(color='white', width=2)),
                                       textinfo='percent+label', textposition='outside')])
        
        fig_pie.update_traces(textfont=dict(color='black', size=13, family="Arial Bold"))
        fig_pie.update_layout(showlegend=False, height=450, margin=dict(t=50, b=50, l=50, r=50))
        st.plotly_chart(fig_pie, use_container_width=True)

    with st.expander("🔍 데이터 정합성 확인 테이블"):
        v_df = f_df[['날짜', '후원사명', '케이터링', '후원입금', '소계_지출']].copy()
        v_df.columns = ['날짜', '후원사명', '케이터링(L)', '후원입금(U)', '소계_지출(V)']
        st.dataframe(v_df, use_container_width=True)

else:
    st.info("데이터를 불러오는 중입니다...")
