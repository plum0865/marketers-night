import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

# ═══════════════════════════════════════════════════════════════
# 1. 페이지 설정
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="마케터의 밤 · 지출 대시보드",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded",
)

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQwyqr83a7VFrYiqtKpnJenXkPV3S3zx_u-7jZ2wWltFDLUAyQGMDJdquCnSh54h_j4cwvzyX7n_Skk/pub?gid=0&single=true&output=csv"

# ═══════════════════════════════════════════════════════════════
# 2. 프리미엄 디자인 시스템
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ═══════ 웹폰트 (Pretendard + Inter) ═══════ */
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.min.css');
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ═══════ 글로벌 ═══════ */
:root {
    /* 색상 */
    --bg-primary:   #f8f9fc;
    --bg-card:      #ffffff;
    --text-primary: #1a1a2e;        /* 진한 네이비: 흰 배경 대비 WCAG AAA */
    --text-secondary: #475569;      /* 슬레이트 600: 중간 톤 ↑ 대비 강화 */
    --text-muted:   #64748b;        /* 슬레이트 500: 보조 텍스트도 읽기 쉽게 */
    --border-light: rgba(0,0,0,0.04);
    --accent-1:     #667eea;
    --accent-2:     #764ba2;
    /* 그림자 */
    --shadow-sm:    0 1px 3px rgba(0,0,0,0.04);
    --shadow-md:    0 4px 16px rgba(0,0,0,0.06);
    --shadow-lg:    0 12px 40px rgba(0,0,0,0.10);
    --shadow-glow:  0 8px 32px rgba(102,126,234,0.18);
    /* 라운딩 */
    --radius-sm:    10px;
    --radius-md:    16px;
    --radius-lg:    20px;
    /* ★ 타이포그래피 시스템 */
    --font-sans: 'Pretendard', 'Inter', -apple-system, 'Segoe UI', sans-serif;
    --font-num:  'Inter', 'Pretendard', 'Segoe UI', sans-serif;
}
html, body, [class*="css"] {
    font-family: var(--font-sans);
    -webkit-font-smoothing: antialiased;   /* 맥OS 글꼴 부드럽게 */
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;    /* 글꼴 렌더링 최적화 */
    font-size: 15px;                       /* 기본 크기 살짝 키움 (14→15) */
    line-height: 1.65;                     /* 한국어 행간 넉넉하게 */
    color: var(--text-primary);
    letter-spacing: -0.01em;               /* 한국어 자간 미세 조정 */
}
.stApp { background: var(--bg-primary); }
.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 1rem !important;
    max-width: 100% !important;          /* ① 전체 폭 사용 */
    padding-left: 2.5rem !important;     /* 좌우 여백 최소화 */
    padding-right: 2.5rem !important;
}

/* ═══════ 사이드바 ═══════ */
[data-testid="stSidebar"] {
    background: linear-gradient(175deg, #0c0c1d 0%, #1a1a3e 40%, #2d1b69 100%);
    border-right: 1px solid rgba(255,255,255,0.04);
}
[data-testid="stSidebar"] * { color: #d0d4e0 !important; font-family: var(--font-sans); }
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] h5 { color: #ffffff !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.06) !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label {
    color: #a0a8c0 !important; font-weight: 600 !important;
    font-size: 0.82rem !important; letter-spacing: 0.8px; text-transform: uppercase;
    line-height: 1.4;
}

/* ── 사이드바 로고 ── */
.sidebar-logo {
    text-align: center; padding: 2rem 0 1rem 0;
}
.sidebar-logo .moon {
    font-size: 2.6rem;
    filter: drop-shadow(0 0 18px rgba(251,191,36,0.4));
    animation: float 4s ease-in-out infinite;
}
@keyframes float {
    0%,100% { transform: translateY(0); }
    50%     { transform: translateY(-6px); }
}
.sidebar-logo .title {
    font-size: 1.15rem; font-weight: 800; color: #fff !important;
    letter-spacing: 3px; margin-top: 6px;
    font-family: var(--font-sans);
}
.sidebar-logo .sub {
    font-size: 0.68rem; color: #8b92b0 !important;
    letter-spacing: 2px; margin-top: 4px;
    font-family: var(--font-num);
}

/* ── 사이드바 스탯 카드 ── */
.sb-stat {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px; padding: 12px 14px; margin-bottom: 8px;
    display: flex; align-items: center; gap: 12px;
    transition: background 0.2s;
}
.sb-stat:hover { background: rgba(255,255,255,0.08); }
.sb-stat .icon {
    width: 36px; height: 36px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
}
.sb-stat .icon.i1 { background: rgba(99,102,241,0.15); }
.sb-stat .icon.i2 { background: rgba(59,130,246,0.15); }
.sb-stat .icon.i3 { background: rgba(168,85,247,0.15); }
.sb-stat .info .lbl { font-size: 0.72rem; color: #8b92b0 !important; letter-spacing: 0.3px; line-height: 1.3; }
.sb-stat .info .val { font-size: 0.88rem; font-weight: 700; color: #eceef4 !important; font-family: var(--font-num); letter-spacing: 0.02em; }

/* ═══════ 히어로 배너 ═══════ */
.hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    border-radius: var(--radius-lg);
    padding: 36px 40px 32px 40px;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 40px rgba(102,126,234,0.22);
}
.hero::before {
    content: '';
    position: absolute; top: -50%; right: -20%;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero::after {
    content: '🌙';
    position: absolute; top: 20px; right: 36px;
    font-size: 4.5rem; opacity: 0.12;
    filter: blur(1px);
}
.hero .hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 30px;
    padding: 6px 18px;
    font-size: 0.76rem; font-weight: 700;
    color: rgba(255,255,255,0.95);
    letter-spacing: 1.2px;
    margin-bottom: 16px;
    font-family: var(--font-num);
}
.hero h1 {
    color: #fff !important; font-size: 2.1rem !important; font-weight: 900 !important;
    margin: 0 0 8px 0 !important; letter-spacing: -0.3px;
    -webkit-text-fill-color: #fff !important;
    background: none !important;
    line-height: 1.3;
    font-family: var(--font-sans);
    text-shadow: 0 2px 12px rgba(0,0,0,0.10);
}
.hero .desc {
    color: rgba(255,255,255,0.82); font-size: 1rem; font-weight: 400;
    line-height: 1.6; letter-spacing: 0.01em;
}

/* ═══════ 필터 스트립 ═══════ */
.filter-strip {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    padding: 14px 26px;
    margin-bottom: 1.6rem;
    display: flex; justify-content: space-between; align-items: center;
    box-shadow: var(--shadow-sm);
}
.filter-strip .left {
    display: flex; align-items: center; gap: 10px;
    font-size: 0.92rem; font-weight: 700; color: var(--text-primary);
    letter-spacing: -0.01em;
}
.filter-strip .dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #22c55e; box-shadow: 0 0 8px rgba(34,197,94,0.4);
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%,100% { opacity: 1; }
    50%     { opacity: 0.4; }
}
.filter-strip .right {
    font-size: 0.84rem; color: var(--text-secondary); font-weight: 500;
    font-family: var(--font-num);
}
.filter-strip .right b { color: var(--accent-1); }

/* ═══════ st.metric 숨김 ═══════ */
[data-testid="stMetric"] { display: none !important; }

/* ═══════ KPI 카드 ═══════ */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 16px;
    margin-bottom: 2rem;
}
@media (max-width: 1100px) { .kpi-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 700px)  { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }

.kpi {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    padding: 22px 22px 18px 22px;
    position: relative; overflow: hidden;
    transition: all 0.3s cubic-bezier(.25,.8,.25,1);
    box-shadow: var(--shadow-sm);
}
.kpi:hover {
    transform: translateY(-6px) scale(1.015);
    box-shadow: var(--shadow-lg);
    border-color: rgba(102,126,234,0.15);
}
/* 상단 그라데이션 바 */
.kpi::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 4px;
    border-radius: var(--radius-md) var(--radius-md) 0 0;
}
.kpi.c-red::before    { background: linear-gradient(90deg,#ef4444,#f87171); }
.kpi.c-amber::before  { background: linear-gradient(90deg,#f59e0b,#fbbf24); }
.kpi.c-green::before  { background: linear-gradient(90deg,#22c55e,#4ade80); }
.kpi.c-blue::before   { background: linear-gradient(90deg,#3b82f6,#60a5fa); }
.kpi.c-purple::before { background: linear-gradient(90deg,#8b5cf6,#a78bfa); }
/* 호버 글로우 */
.kpi.c-red:hover    { box-shadow: 0 12px 36px rgba(239,68,68,0.12); }
.kpi.c-amber:hover  { box-shadow: 0 12px 36px rgba(245,158,11,0.12); }
.kpi.c-green:hover  { box-shadow: 0 12px 36px rgba(34,197,94,0.12); }
.kpi.c-blue:hover   { box-shadow: 0 12px 36px rgba(59,130,246,0.12); }
.kpi.c-purple:hover { box-shadow: 0 12px 36px rgba(139,92,246,0.12); }

.kpi .icon-box {
    width: 44px; height: 44px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem; margin-bottom: 14px;
}
.kpi .icon-box.ib-red    { background: #fef2f2; }
.kpi .icon-box.ib-amber  { background: #fffbeb; }
.kpi .icon-box.ib-green  { background: #f0fdf4; }
.kpi .icon-box.ib-blue   { background: #eff6ff; }
.kpi .icon-box.ib-purple { background: #f5f3ff; }

.kpi .kpi-lbl {
    font-size: 0.78rem; font-weight: 600; color: var(--text-secondary);
    letter-spacing: 0.3px; margin-bottom: 8px;
    line-height: 1.3;
}
.kpi .kpi-val {
    font-size: 1.6rem; font-weight: 800; color: var(--text-primary);
    font-family: var(--font-num); line-height: 1.25; margin-bottom: 10px;
    letter-spacing: -0.02em;
    font-variant-numeric: tabular-nums;  /* 숫자 폭 균일 정렬 */
}
.kpi .kpi-badge {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.76rem; font-weight: 600; padding: 4px 12px;
    border-radius: 20px;
    font-family: var(--font-num);
    letter-spacing: 0.01em;
}
.kpi .kpi-badge.b-up   { background: #f0fdf4; color: #16a34a; }
.kpi .kpi-badge.b-down { background: #fef2f2; color: #dc2626; }
.kpi .kpi-badge.b-info { background: #f0f4ff; color: #4f6adb; }

/* ═══════ 섹션 구분선 ═══════ */
.section-divider {
    display: flex; align-items: center; gap: 14px;
    margin: 2rem 0 1.2rem 0;
}
.section-divider .line {
    flex: 1; height: 1px;
    background: linear-gradient(to right, var(--border-light), #e2e8f0, var(--border-light));
}
.section-divider .label {
    font-size: 0.76rem; font-weight: 700; color: var(--text-secondary);
    letter-spacing: 2.5px; text-transform: uppercase; white-space: nowrap;
    font-family: var(--font-num);
}

/* ═══════ 탭 ═══════ */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card); border-radius: 14px;
    padding: 6px; box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-light); gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px; padding: 11px 26px;
    font-weight: 700; font-size: 0.9rem; color: var(--text-secondary);
    transition: all 0.25s ease;
    letter-spacing: -0.01em;
}
.stTabs [data-baseweb="tab"]:hover {
    background: #f1f5f9; color: var(--text-primary);
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, var(--accent-1), var(--accent-2)) !important;
    color: #fff !important;
    box-shadow: var(--shadow-glow);
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.2rem; }

/* ═══════ 차트 카드 ═══════ */
.chart-wrap {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    padding: 24px 26px 16px 26px;
    box-shadow: var(--shadow-sm);
    margin-bottom: 0.8rem;
    transition: box-shadow 0.3s ease;
}
.chart-wrap:hover { box-shadow: var(--shadow-md); }
.chart-wrap .cw-head {
    display: flex; align-items: center; gap: 10px; margin-bottom: 4px;
}
.chart-wrap .cw-icon {
    width: 32px; height: 32px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.95rem;
}
.chart-wrap .cw-icon.ci-bar    { background: #eff6ff; }
.chart-wrap .cw-icon.ci-line   { background: #fef3c7; }
.chart-wrap .cw-icon.ci-pie    { background: #f5f3ff; }
.chart-wrap .cw-icon.ci-rank   { background: #fef2f2; }
.chart-wrap .cw-icon.ci-trend  { background: #ecfdf5; }
.chart-wrap .cw-icon.ci-cum    { background: #fdf4ff; }
.chart-wrap .cw-title  { font-size: 1.02rem; font-weight: 700; color: var(--text-primary); letter-spacing: -0.01em; }
.chart-wrap .cw-sub    { font-size: 0.84rem; color: var(--text-secondary); margin-bottom: 14px; margin-left: 42px; line-height: 1.5; }

/* ═══════ Expander ═══════ */
details[data-testid="stExpander"] {
    background: var(--bg-card); border-radius: 14px !important;
    border: 1px solid var(--border-light) !important;
    box-shadow: var(--shadow-sm);
}
details[data-testid="stExpander"] summary { font-weight: 700; color: var(--text-primary); font-size: 0.95rem; letter-spacing: -0.01em; }

/* ═══════ 데이터 테이블 ═══════ */
.stDataFrame { border-radius: 12px; overflow: hidden; }

/* ═══════ 구분선 ═══════ */
hr { border: none; height: 1px; background: linear-gradient(to right, transparent, #e2e8f0, transparent); margin: 1.5rem 0; }

/* ═══════ 푸터 ═══════ */
.app-ft { text-align: center; color: var(--text-muted); font-size: 0.78rem; padding: 1.5rem 0 0.5rem 0; letter-spacing: 0.4px; font-family: var(--font-num); }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# 3. 데이터 로드
# ═══════════════════════════════════════════════════════════════
@st.cache_data(ttl=60)
def load_data(src):
    try:
        raw = pd.read_csv(src, header=None, skiprows=4)
        # ② H열(7)=참석율, K열(10)=참석인원 추가
        df = raw.iloc[:, [1,2,7,10,11,20,21]].copy()
        df.columns = ['날짜_원본','후원사명','참석율','참석인원','케이터링','후원입금','소계_지출']
        cvt = lambda v: (lambda s: 0.0 if s in ('','-') else float(s))(
            str(v).replace(',','').replace('₩','').replace(' ','').replace('%','').strip()) if pd.notna(v) else 0.0
        def to_date(v):
            if pd.isna(v): return pd.NaT
            m = re.search(r'(\d{4})[\.\s](\d{1,2})[\.\s](\d{1,2})', str(v))
            return pd.to_datetime(f"{m.group(1)}-{m.group(2)}-{m.group(3)}") if m else pd.NaT
        df['날짜']     = df['날짜_원본'].apply(to_date)
        for c in ['케이터링','후원입금','소계_지출','참석인원']: df[c] = df[c].apply(cvt)
        # 참석율: 퍼센트(%) 값 파싱
        df['참석율'] = df['참석율'].apply(cvt)
        df = df[df['날짜'].notna() & ~df['후원사명'].str.contains('합계|소계|전체', na=False)]
        df['Year']  = df['날짜'].dt.year.astype('Int64')
        df['Month'] = df['날짜'].dt.month.astype('Int64')
        return df.sort_values('날짜')
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
        return pd.DataFrame()

main_df = load_data(SHEET_URL)


# ═══════════════════════════════════════════════════════════════
# 4. 사이드바
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
        <div class='sidebar-logo'>
            <div class='moon'>🌙</div>
            <div class='title'>마케터의 밤</div>
            <div class='sub'>EXPENSE DASHBOARD v4.0</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("---")

    if not main_df.empty:
        st.markdown("##### 🗓️ 기간 필터")
        years = sorted(main_df['Year'].unique(), reverse=True)
        sel_year = st.selectbox("연도", years, help="분석할 연도를 선택하세요")
        y_df = main_df[main_df['Year'] == sel_year]
        months = sorted(y_df['Month'].unique())

        ba, bb = st.columns(2)
        with ba:
            if st.button("📌 전체 선택", use_container_width=True):
                st.session_state['sel_months'] = months
        with bb:
            if st.button("🔄 초기화", use_container_width=True):
                st.session_state['sel_months'] = []
        dm = st.session_state.get('sel_months', [])
        sel_months = st.multiselect("월 선택", months,
            default=[m for m in dm if m in months],
            format_func=lambda x: f"{x:02d}월")

        st.markdown("---")
        st.markdown("##### 📋 데이터 요약")
        d_min = main_df['날짜'].min().strftime('%Y.%m.%d')
        d_max = main_df['날짜'].max().strftime('%Y.%m.%d')
        stats = [("📅","i1","전체 기간",f"{d_min} ~ {d_max}"),
                 ("📊","i2","전체 데이터",f"{len(main_df):,}건"),
                 ("🏢","i3","후원사 수",f"{main_df['후원사명'].nunique()}개")]
        for emo, ic, lbl, val in stats:
            st.markdown(f"""<div class='sb-stat'>
                <div class='icon {ic}'>{emo}</div>
                <div class='info'><div class='lbl'>{lbl}</div><div class='val'>{val}</div></div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div style='text-align:center;padding:.5rem 0;color:#4b5076;font-size:.7rem;'>Built with ❤️ Streamlit & Plotly</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# 5. 히어로 배너
# ═══════════════════════════════════════════════════════════════
st.markdown("""
    <div class='hero'>
        <div class='hero-badge'>✨ REAL-TIME ANALYTICS</div>
        <h1>마케터의 밤 &nbsp;지출 리포트</h1>
        <div class='desc'>후원사 지출 현황을 한눈에 파악하고, 데이터 기반 인사이트를 확인하세요</div>
    </div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# 6. 메인 대시보드
# ═══════════════════════════════════════════════════════════════
if not main_df.empty:
    f_df = y_df[y_df['Month'].isin(sel_months)].copy() if sel_months else y_df.copy()

    # ── 집계 ──
    s_spent  = f_df['소계_지출'].sum()
    s_cater  = f_df['케이터링'].sum()
    s_income = f_df['후원입금'].sum()
    n_count  = len(f_df)
    c_ratio  = (s_cater / s_spent * 100) if s_spent else 0
    # ② 참석인원 / 참석율 집계
    s_attend   = f_df['참석인원'].sum()
    avg_attend_rate = f_df.loc[f_df['참석율'] > 0, '참석율'].mean() if (f_df['참석율'] > 0).any() else 0

    prev = main_df[main_df['Year'] == sel_year - 1]
    if sel_months: prev = prev[prev['Month'].isin(sel_months)]
    p_total = prev['소계_지출'].sum() if not prev.empty else 0
    delta   = ((s_spent - p_total) / p_total * 100) if p_total else None

    # ── 필터 스트립 ──
    fl = f"📅 {sel_year}년"
    fl += f" · {', '.join(f'{m}월' for m in sel_months)}" if sel_months else " · 전체"
    st.markdown(f"""
        <div class='filter-strip'>
            <div class='left'><div class='dot'></div> {fl}</div>
            <div class='right'>조회 결과 <b>{n_count:,}</b> 건</div>
        </div>""", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════
    # 6-1. KPI 카드
    # ═══════════════════════════════════════════════════════
    def badge(val, suffix="", inverse=False):
        if val is None: return "<span class='kpi-badge b-info'>데이터 없음</span>"
        cls = "b-info"
        if val > 0: cls = "b-down" if inverse else "b-up"
        elif val < 0: cls = "b-up" if inverse else "b-down"
        sign = "▲ " if val > 0 else ("▼ " if val < 0 else "")
        return f"<span class='kpi-badge {cls}'>{sign}{abs(val):.1f}%{suffix}</span>"


    kpis = [
        ("c-red",   "ib-red",   "💰", "총 지출액",      f"₩{s_spent:,.0f}",  badge(delta," 전년비",True)),
        ("c-amber", "ib-amber", "🍔", "케이터링",       f"₩{s_cater:,.0f}",  f"<span class='kpi-badge b-info'>지출의 {c_ratio:.1f}%</span>"),
        ("c-green", "ib-green", "📈", "후원 입금",       f"₩{s_income:,.0f}", f"<span class='kpi-badge {'b-up' if s_income>=s_spent else 'b-down'}'>{'흑자' if s_income>=s_spent else '적자'} 구간</span>"),
        ("c-blue",  "ib-blue",  "👥", "총 참석인원",     f"{s_attend:,.0f}명", f"<span class='kpi-badge b-info'>총 {n_count:,}회</span>"),
        ("c-purple","ib-purple","📊", "참석율 현황",     f"{avg_attend_rate:.1f}%", f"<span class='kpi-badge {'b-up' if avg_attend_rate>=70 else 'b-down'}'>{'양호' if avg_attend_rate>=70 else '개선 필요'}</span>"),
    ]
    html = "<div class='kpi-grid'>"
    for cc,ic,em,lbl,val,bdg in kpis:
        html += f"""<div class='kpi {cc}'>
            <div class='icon-box {ic}'>{em}</div>
            <div class='kpi-lbl'>{lbl}</div>
            <div class='kpi-val'>{val}</div>
            {bdg}
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    # ── 섹션 구분선 ──
    st.markdown("""<div class='section-divider'>
        <div class='line'></div><div class='label'>상세 분석</div><div class='line'></div>
    </div>""", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════
    # 6-2. 차트
    # ═══════════════════════════════════════════════════════
    CT = dict(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Pretendard, Inter, -apple-system, sans-serif", color="#1a1a2e", size=13),
        margin=dict(t=20, b=20, l=20, r=20),
        hoverlabel=dict(bgcolor="white", font_size=14, font_family="Pretendard, Inter, sans-serif",
                        bordercolor="#e2e8f0"),
    )

    tab1, tab2, tab3 = st.tabs(["📊  월별 분석", "🏢  후원사 분석", "📈  트렌드"])

    # ── TAB 1 ──
    with tab1:
        L, R = st.columns([1.3, 1])
        with L:
            st.markdown("""<div class='chart-wrap'>
                <div class='cw-head'><div class='cw-icon ci-bar'>📊</div><div class='cw-title'>월별 지출 현황</div></div>
                <div class='cw-sub'>월별 총 지출액 추이를 바 차트로 확인합니다</div>
            </div>""", unsafe_allow_html=True)
            mp = f_df.resample('ME', on='날짜')['소계_지출'].sum().reset_index()
            mp['l'] = mp['날짜'].dt.strftime('%y년 %m월')
            n = max(len(mp)-1,1)
            cols = [f'rgba(102,126,234,{.4+.6*i/n})' for i in range(len(mp))]
            f1 = go.Figure(go.Bar(x=mp['l'],y=mp['소계_지출'],
                marker=dict(color=cols,cornerradius=8,line=dict(color='rgba(102,126,234,.6)',width=.5)),
                text=[f"₩{v:,.0f}" for v in mp['소계_지출']], textposition='outside',
                textfont=dict(size=12,color='#1a1a2e',family='Inter, Pretendard, sans-serif'),
                hovertemplate="<b>%{x}</b><br>₩%{y:,.0f}<extra></extra>"))
            f1.update_layout(**CT,height=420,showlegend=False,
                xaxis=dict(tickfont=dict(size=12,color='#475569',family='Pretendard'),showgrid=False),
                yaxis=dict(tickformat=',.0f',tickprefix='₩',gridcolor='rgba(0,0,0,.04)',
                           tickfont=dict(size=11,color='#64748b',family='Inter')))
            st.plotly_chart(f1, use_container_width=True)

        with R:
            st.markdown("""<div class='chart-wrap'>
                <div class='cw-head'><div class='cw-icon ci-line'>🔀</div><div class='cw-title'>항목별 비교</div></div>
                <div class='cw-sub'>지출 · 케이터링 · 후원 입금의 월간 흐름을 비교합니다</div>
            </div>""", unsafe_allow_html=True)
            md = f_df.resample('ME',on='날짜').agg({'소계_지출':'sum','케이터링':'sum','후원입금':'sum'}).reset_index()
            md['l'] = md['날짜'].dt.strftime('%y.%m')
            f2 = go.Figure()
            for c,nm,co,d in [('소계_지출','총 지출','#ef4444','solid'),('케이터링','케이터링','#f59e0b','dash'),('후원입금','후원 입금','#22c55e','dot')]:
                f2.add_trace(go.Scatter(x=md['l'],y=md[c],name=nm,mode='lines+markers',
                    line=dict(width=2.5,color=co,dash=d),marker=dict(size=7),
                    hovertemplate=f"<b>{nm}</b><br>₩%{{y:,.0f}}<extra></extra>"))
            f2.update_layout(**CT,height=420,
                legend=dict(orientation='h',y=1.1,xanchor='center',x=.5,font=dict(size=12,family='Pretendard')),
                xaxis=dict(showgrid=False,tickfont=dict(size=11,color='#475569',family='Pretendard')),
                yaxis=dict(tickformat=',.0f',tickprefix='₩',gridcolor='rgba(0,0,0,.04)',
                           tickfont=dict(size=11,color='#64748b',family='Inter')))
            st.plotly_chart(f2, use_container_width=True)

    # ── TAB 2 ──
    with tab2:
        L2, R2 = st.columns([1, 1.2])
        ss = f_df.groupby('후원사명')['소계_지출'].sum().sort_values(ascending=False).reset_index()

        with L2:
            st.markdown("""<div class='chart-wrap'>
                <div class='cw-head'><div class='cw-icon ci-pie'>🍕</div><div class='cw-title'>후원사별 지출 비중</div></div>
                <div class='cw-sub'>상위 후원사의 지출 점유율을 확인합니다</div>
            </div>""", unsafe_allow_html=True)
            tn=8
            if len(ss)>tn:
                td=ss.head(tn).copy()
                od=pd.DataFrame([{'후원사명':'기타','소계_지출':ss.iloc[tn:]['소계_지출'].sum()}])
                pdf=pd.concat([td,od],ignore_index=True)
            else: pdf=ss
            pal=['#667eea','#764ba2','#f093fb','#f5576c','#4facfe','#00f2fe','#43e97b','#fa709a','#cbd5e1']
            f3=go.Figure(go.Pie(labels=pdf['후원사명'],values=pdf['소계_지출'],hole=.58,
                marker=dict(colors=pal[:len(pdf)],line=dict(color='white',width=3)),
                textinfo='percent',textposition='auto',textfont=dict(size=13,color='white',family='Inter, Pretendard'),
                hovertemplate="<b>%{label}</b><br>₩%{value:,.0f}<br>%{percent}<extra></extra>",sort=False))
            f3.add_annotation(text=f"<b style='font-size:17px;color:#1a1a2e;font-family:Inter'>₩{s_spent:,.0f}</b><br><span style='font-size:12px;color:#64748b'>총 지출</span>",showarrow=False)
            f3.update_layout(**CT,height=460,showlegend=True,
                legend=dict(orientation='h',y=-.08,xanchor='center',x=.5,font=dict(size=11,family='Pretendard'),itemwidth=30))
            st.plotly_chart(f3, use_container_width=True)

        with R2:
            st.markdown("""<div class='chart-wrap'>
                <div class='cw-head'><div class='cw-icon ci-rank'>🏆</div><div class='cw-title'>후원사 지출 TOP 10</div></div>
                <div class='cw-sub'>지출 금액 기준 상위 후원사 순위입니다</div>
            </div>""", unsafe_allow_html=True)
            t10=ss.head(10).sort_values('소계_지출',ascending=True)
            mx=t10['소계_지출'].max()
            bc=['#f5576c' if v==mx else '#667eea' for v in t10['소계_지출']]
            f4=go.Figure(go.Bar(y=t10['후원사명'],x=t10['소계_지출'],orientation='h',
                marker=dict(color=bc,cornerradius=8),
                text=[f"₩{v:,.0f}" for v in t10['소계_지출']],textposition='auto',
                textfont=dict(size=12,color='white',family='Inter, Pretendard'),
                hovertemplate="<b>%{y}</b><br>₩%{x:,.0f}<extra></extra>"))
            f4.update_layout(**CT,height=460,showlegend=False,
                xaxis=dict(tickformat=',.0f',tickprefix='₩',gridcolor='rgba(0,0,0,.04)',tickfont=dict(size=11,color='#64748b',family='Inter')),
                yaxis=dict(tickfont=dict(size=12,color='#1a1a2e',family='Pretendard'),automargin=True))
            st.plotly_chart(f4, use_container_width=True)

    # ── TAB 3 ──
    with tab3:
        L3, R3 = st.columns(2)
        with L3:
            st.markdown("""<div class='chart-wrap'>
                <div class='cw-head'><div class='cw-icon ci-trend'>📈</div><div class='cw-title'>일별 지출 트렌드</div></div>
                <div class='cw-sub'>일자별 지출과 7일 이동평균선을 확인합니다</div>
            </div>""", unsafe_allow_html=True)
            dy=f_df.groupby('날짜')['소계_지출'].sum().reset_index().sort_values('날짜')
            dy['MA7']=dy['소계_지출'].rolling(7,min_periods=1).mean()
            f5=go.Figure()
            f5.add_trace(go.Scatter(x=dy['날짜'],y=dy['소계_지출'],name='일별',mode='markers',
                marker=dict(size=5,color='rgba(102,126,234,.45)'),
                hovertemplate="<b>%{x|%Y.%m.%d}</b><br>₩%{y:,.0f}<extra></extra>"))
            f5.add_trace(go.Scatter(x=dy['날짜'],y=dy['MA7'],name='7일 평균',mode='lines',
                line=dict(width=3,color='#ef4444'),
                hovertemplate="<b>7일 평균</b><br>₩%{y:,.0f}<extra></extra>"))
            f5.update_layout(**CT,height=420,
                legend=dict(orientation='h',y=1.1,xanchor='center',x=.5,font=dict(size=12,family='Pretendard')),
                xaxis=dict(showgrid=False,tickfont=dict(size=11,color='#475569',family='Pretendard')),
                yaxis=dict(tickformat=',.0f',tickprefix='₩',gridcolor='rgba(0,0,0,.04)',tickfont=dict(size=11,color='#64748b',family='Inter')))
            st.plotly_chart(f5, use_container_width=True)

        with R3:
            st.markdown("""<div class='chart-wrap'>
                <div class='cw-head'><div class='cw-icon ci-cum'>💹</div><div class='cw-title'>누적 지출 vs 누적 수입</div></div>
                <div class='cw-sub'>시간에 따른 누적 금액 흐름을 비교합니다</div>
            </div>""", unsafe_allow_html=True)
            dc2=f_df.groupby('날짜').agg({'소계_지출':'sum','후원입금':'sum'}).reset_index().sort_values('날짜')
            dc2['c_s']=dc2['소계_지출'].cumsum(); dc2['c_i']=dc2['후원입금'].cumsum()
            f6=go.Figure()
            f6.add_trace(go.Scatter(x=dc2['날짜'],y=dc2['c_s'],name='누적 지출',fill='tozeroy',
                fillcolor='rgba(239,68,68,.08)',line=dict(width=2.5,color='#ef4444'),
                hovertemplate="<b>누적 지출</b><br>₩%{y:,.0f}<extra></extra>"))
            f6.add_trace(go.Scatter(x=dc2['날짜'],y=dc2['c_i'],name='누적 수입',fill='tozeroy',
                fillcolor='rgba(34,197,94,.08)',line=dict(width=2.5,color='#22c55e'),
                hovertemplate="<b>누적 수입</b><br>₩%{y:,.0f}<extra></extra>"))
            f6.update_layout(**CT,height=420,
                legend=dict(orientation='h',y=1.1,xanchor='center',x=.5,font=dict(size=12,family='Pretendard')),
                xaxis=dict(showgrid=False,tickfont=dict(size=11,color='#475569',family='Pretendard')),
                yaxis=dict(tickformat=',.0f',tickprefix='₩',gridcolor='rgba(0,0,0,.04)',tickfont=dict(size=11,color='#64748b',family='Inter')))
            st.plotly_chart(f6, use_container_width=True)

    # ═══════════════════════════════════════════════════════
    # 6-3. 테이블
    # ═══════════════════════════════════════════════════════
    st.markdown("""<div class='section-divider'>
        <div class='line'></div><div class='label'>원본 데이터</div><div class='line'></div>
    </div>""", unsafe_allow_html=True)

    with st.expander("🔍 데이터 정합성 확인 테이블"):
        vd = f_df[['날짜','후원사명','케이터링','후원입금','소계_지출']].copy()
        vd['날짜'] = vd['날짜'].dt.strftime('%Y-%m-%d')
        st.dataframe(vd,
            column_config={
                "날짜":     st.column_config.TextColumn("📅 날짜",width="small"),
                "후원사명": st.column_config.TextColumn("🏢 후원사명",width="medium"),
                "케이터링": st.column_config.NumberColumn("🍔 케이터링",format="₩%,.0f"),
                "후원입금": st.column_config.NumberColumn("📈 후원입금",format="₩%,.0f"),
                "소계_지출": st.column_config.ProgressColumn("💰 소계 지출",format="₩%,.0f",
                    min_value=0, max_value=float(vd['소계_지출'].max()) if not vd.empty else 1),
            }, use_container_width=True, height=400, hide_index=True)
        st.download_button("📥 CSV 다운로드",
            vd.to_csv(index=False).encode('utf-8-sig'),
            file_name=f"마케터의밤_지출_{sel_year}.csv",
            mime="text/csv", use_container_width=True)

else:
    st.markdown("""<div style='text-align:center;padding:5rem 2rem;color:#94a3b8;'>
        <div style='font-size:4rem;margin-bottom:1rem;'>📊</div>
        <h2 style='color:#64748b;'>데이터를 불러오는 중입니다...</h2>
        <p>Google Sheets URL이 올바른지 확인해주세요.</p>
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 7. 푸터
# ═══════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("<div class='app-ft'>🌙 마케터의 밤 지출 리포트 <b>v4.0</b> · Streamlit & Plotly</div>", unsafe_allow_html=True)
