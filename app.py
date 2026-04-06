import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# 1. 페이지 설정
st.set_page_config(page_title="마케터의 밤 지출 분석", layout="wide")

# KPI 및 스타일 설정
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.8rem; color: #333333; }
    [data-testid="stMetric"] { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #00d1ff; }
    </style>
    """, unsafe_allow_html=True)

# 💡 여기에 실제 행사 날짜를 정의하세요!
EVENT_MAP = {
    "2025 마케터의 밤": ("2025-01-01", "2025-12-31"),
    "2026 마케터의 밤": ("2026-01-01", "2026-03-31"),
    }

def process_uploaded_file(uploaded_file):
    try:
        raw_data = pd.read_csv(uploaded_file, header=None, skiprows=4)
        clean_df = raw_data.iloc[:, [1, 2, 11, 21]].copy()
        clean_df.columns = ['날짜_원본', '후원사명', '케이터링비용', '총지출액']
        
        def to_num(v):
            if pd.isna(v) or v == '-': return 0.0
            if isinstance(v, str):
                v = v.replace(',', '').replace(' ', '')
                try: return abs(float(v))
                except: return 0.0
            return abs(float(v))

        def to_date(v):
            if pd.isna(v): return pd.NaT
            m = re.search(r'(\d{4})[\.\s](\d{1,2})[\.\s](\d{1,2})', str(v))
            if m: return pd.to_datetime(f"{m.group(1)}-{m.group(2)}-{m.group(3)}")
            return pd.NaT

        clean_df['날짜'] = clean_df['날짜_원본'].apply(to_date)
        clean_df['케이터링비용'] = clean_df['케이터링비용'].apply(to_num)
        clean_df['총지출액'] = clean_df['총지출액'].apply(to_num)
        return clean_df.dropna(subset=['날짜', '후원사명']).sort_values('날짜')
    except Exception as e:
        st.error(f"파일 분석 중 오류: {e}")
        return pd.DataFrame()

# --- 사이드바 ---
with st.sidebar:
    st.header("📂 데이터 업로드")
    uploaded_file = st.file_uploader("CSV 파일을 선택하세요", type=['csv'])
    st.divider()

if uploaded_file is not None:
    main_df = process_uploaded_file(uploaded_file)
    
    if not main_df.empty:
        with st.sidebar:
            st.subheader("🎟️ 행사별 카테고리")
            
            # 행사 선택 (기본적으로 첫 번째 행사 선택)
            selected_events = st.multiselect(
                "분석할 행사를 선택하세요",
                options=list(EVENT_MAP.keys()),
                default=[list(EVENT_MAP.keys())[0]]
            )

            # 선택된 행사들에 따른 날짜 범위 추출
            if selected_events:
                all_dates = []
                for event in selected_events:
                    start, end = EVENT_MAP[event]
                    all_dates.append(pd.to_datetime(start))
                    all_dates.append(pd.to_datetime(end))
                
                s_date = min(all_dates).date()
                e_date = max(all_dates).date()
                
                st.success(f"📌 **선택된 행사 기간**\n{s_date} ~ {e_date}")
            else:
                # 아무것도 선택 안했을 때 전체 기간 표시
                s_date = main_df['날짜'].min().date()
                e_date = main_df['날짜'].max().date()
                st.info("💡 행사를 선택하지 않으면 전체 기간을 보여줍니다.")

        # 데이터 필터링
        mask = (main_df['날짜'].dt.date >= s_date) & (main_df['날짜'].dt.date <= e_date)
        f_df = main_df.loc[mask].copy()

        # KPI 및 차트 로직 (기존과 동일)
        total_spent = float(f_df['총지출액'].sum())
        catering_spent = float(f_df['케이터링비용'].sum())
        
        k1, k2, k3 = st.columns(3)
        k1.metric("💰 총 지출액", f"₩{total_spent:,.0f}")
        k2.metric("🍔 케이터링 지출", f"₩{catering_spent:,.0f}")
        k3.metric("📊 케이터링 비중", f"{(catering_spent/total_spent*100):.1f}%" if total_spent > 0 else "0%")

        st.write("")
        cl, cr = st.columns([1.5, 1])

        # 차트 렌더링 (기존 코드 유지)
        with cl:
            with st.container(border=True):
                st.subheader("📊 월별 지출 현황")
                m_df = f_df.resample('ME', on='날짜')['총지출액'].sum().reset_index()
                m_df['날짜_표시'] = m_df['날짜'].dt.strftime('%y.%m')
                fig_bar = px.bar(m_df, x='날짜_표시', y='총지출액', color='총지출액', color_continuous_scale='Blues', text_auto=',.0f', template="plotly_white")
                fig_bar.update_layout(coloraxis_showscale=False, height=450, margin=dict(l=60, r=10, t=10, b=10), xaxis_title="", yaxis_title="",
                                      xaxis=dict(tickfont=dict(color='#333333', size=12, weight="bold")),
                                      yaxis=dict(tickformat=',.0f', tickprefix='₩', tickfont=dict(color='#333333', size=12, weight="bold")))
                st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

        with cr:
            with st.container(border=True):
                st.subheader("🍕 후원사별 비중 (Top 8)")
                sponsor_group = f_df.groupby('후원사명')['총지출액'].sum().sort_values(ascending=False).reset_index()
                top_n = 8
                top_sponsors = sponsor_group.head(top_n).copy()
                others_sum = sponsor_group.iloc[top_n:]['총지출액'].sum()
                if others_sum > 0:
                    others_df = pd.DataFrame([{'후원사명': '기타 (Others)', '총지출액': others_sum}])
                    plot_df = pd.concat([top_sponsors, others_df], ignore_index=True)
                else: plot_df = top_sponsors

                fig_pie = go.Figure(data=[go.Pie(labels=plot_df['후원사명'], values=plot_df['총지출액'], hole=0.5,
                                               marker=dict(colors=px.colors.sequential.Blues_r, line=dict(color='white', width=2)),
                                               textinfo='percent+label', textposition='outside')])
                fig_pie.add_annotation(text="Total Spent", x=0.5, y=0.55, showarrow=False, font_size=14)
                fig_pie.add_annotation(text=f"₩{total_spent/10000:,.0f}만", x=0.5, y=0.45, showarrow=False, font_size=18, font_family="Arial Black")
                fig_pie.update_layout(showlegend=False, height=450, margin=dict(l=50, r=50, t=30, b=30), font=dict(color='#333333', size=12, weight="bold"))
                st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

        with st.expander("🔍 상세 지출 내역 보기"):
            display_df = f_df[['날짜', '후원사명', '케이터링비용', '총지출액']].copy()
            display_df['날짜'] = display_df['날짜'].dt.strftime('%Y-%m-%d')
            st.dataframe(display_df, use_container_width=True)
