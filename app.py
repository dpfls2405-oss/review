import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ══════════════════════════════════════════════
#  페이지 설정
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="수요예측 대시보드",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════
#  전역 CSS
# ══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

/* ══════════════════════════════════════════════════
   기본
══════════════════════════════════════════════════ */
html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
    font-size: 15px;
}
.stApp { background-color: #EAECF4; }


/* ╔══════════════════════════════════════════════╗
   ║  사이드바 — 다크 테마로 완전 격리            ║
   ╚══════════════════════════════════════════════╝ */
section[data-testid="stSidebar"] {
    background: #0F1E30 !important;
    border-right: 1px solid #1E3048 !important;
}

/* 사이드바 안의 모든 텍스트 */
section[data-testid="stSidebar"] *  { color: #C8D6E8 !important; }

/* 사이드바 라벨 (필터 제목) */
section[data-testid="stSidebar"] label {
    font-size: 13px !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: #6B93BF !important;
    margin-bottom: 6px !important;
}

/* 사이드바 selectbox 컨테이너 */
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #162032 !important;
    border: 1.5px solid #2C4A6A !important;
    border-radius: 8px !important;
    min-height: 42px !important;
    color: #E8F0FA !important;
}
section[data-testid="stSidebar"] .stSelectbox > div > div:hover {
    border-color: #4B7AB8 !important;
    background: #1A2840 !important;
}
/* 사이드바 selectbox 선택된 값 */
section[data-testid="stSidebar"] .stSelectbox > div > div > div {
    color: #E8F0FA !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}

/* 사이드바 multiselect 컨테이너 */
section[data-testid="stSidebar"] .stMultiSelect > div > div {
    background: #162032 !important;
    border: 1.5px solid #2C4A6A !important;
    border-radius: 8px !important;
    min-height: 42px !important;
}
section[data-testid="stSidebar"] .stMultiSelect > div > div:hover {
    border-color: #4B7AB8 !important;
}

/* 사이드바 multiselect 태그 — 통일된 파랑 계열 */
section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
    background: #1D4ED8 !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 4px 10px 4px 12px !important;
    margin: 2px !important;
}
section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] span {
    color: #FFFFFF !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}
/* 태그 X 버튼 */
section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] [role="presentation"] {
    color: rgba(255,255,255,0.7) !important;
}

/* 사이드바 구분선 */
section[data-testid="stSidebar"] hr {
    border: none !important;
    border-top: 1px solid #1E3048 !important;
    margin: 16px 0 !important;
}

/* 사이드바 화살표(드롭다운 아이콘) */
section[data-testid="stSidebar"] svg { color: #4B7AB8 !important; fill: #4B7AB8 !important; }


/* ╔══════════════════════════════════════════════╗
   ║  본문 인터랙티브 — 라이트 테마               ║
   ╚══════════════════════════════════════════════╝ */

/* 본문 모든 위젯 라벨 */
.main .stSelectbox label,
.main .stMultiSelect label,
.main .stSlider label,
.main .stTextInput label,
.main .stRadio label,
.main .stRadio > label {
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #1E3A5F !important;
    margin-bottom: 5px !important;
}

/* 본문 Selectbox */
.main .stSelectbox > div > div {
    background: #FFFFFF !important;
    border: 1.5px solid #B0C8E8 !important;
    border-radius: 8px !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    color: #1E293B !important;
    min-height: 42px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
}
.main .stSelectbox > div > div:hover {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
}

/* 본문 Multiselect */
.main .stMultiSelect > div > div {
    background: #FFFFFF !important;
    border: 1.5px solid #B0C8E8 !important;
    border-radius: 8px !important;
    font-size: 15px !important;
    color: #1E293B !important;
    min-height: 42px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
}
.main .stMultiSelect > div > div:hover {
    border-color: #3B82F6 !important;
}
/* 본문 multiselect 태그 */
.main .stMultiSelect [data-baseweb="tag"] {
    background: #DBEAFE !important;
    border: 1px solid #93C5FD !important;
    border-radius: 6px !important;
    padding: 3px 10px !important;
}
.main .stMultiSelect [data-baseweb="tag"] span {
    color: #1D4ED8 !important;
    font-size: 13px !important;
    font-weight: 700 !important;
}

/* 본문 Slider */
.main [data-testid="stSlider"] > div > div > div {
    background: #CBD5E1 !important;
    height: 6px !important;
    border-radius: 3px !important;
}
.main [data-testid="stSlider"] > div > div > div > div {
    background: #2563EB !important;
}
.main [data-testid="stSlider"] div[role="slider"] {
    background: #FFFFFF !important;
    border: 3px solid #2563EB !important;
    width: 22px !important;
    height: 22px !important;
    box-shadow: 0 2px 6px rgba(37,99,235,0.3) !important;
}
.main [data-testid="stSlider"] div[role="slider"]:hover {
    box-shadow: 0 0 0 6px rgba(37,99,235,0.12) !important;
}
.main .stSlider p {
    font-size: 16px !important;
    font-weight: 700 !important;
    color: #1E3A5F !important;
}

/* 본문 Text Input */
.main .stTextInput > div > div > input {
    background: #FFFFFF !important;
    border: 1.5px solid #B0C8E8 !important;
    border-radius: 8px !important;
    font-size: 15px !important;
    color: #1E293B !important;
    padding: 10px 14px !important;
    min-height: 42px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
}
.main .stTextInput > div > div > input:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
    outline: none !important;
}
.main .stTextInput > div > div > input::placeholder {
    color: #94A3B8 !important;
}

/* 본문 Radio */
.main .stRadio > div { gap: 8px !important; }
.main .stRadio > div > label {
    background: #F1F5F9 !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 8px !important;
    padding: 8px 18px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    color: #475569 !important;
    cursor: pointer !important;
    transition: all 0.12s !important;
}
.main .stRadio > div > label:has(input:checked) {
    background: #EFF6FF !important;
    border-color: #2563EB !important;
    color: #1D4ED8 !important;
}


/* ╔══════════════════════════════════════════════╗
   ║  KPI 카드                                    ║
   ╚══════════════════════════════════════════════╝ */
.kpi-wrap {
    background: white;
    border-radius: 16px;
    padding: 24px 20px 20px 20px;
    border-left: 5px solid;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    height: 100%;
    transition: transform 0.12s;
}
.kpi-wrap:hover { transform: translateY(-2px); }
.kpi-label {
    font-size: 12px;
    color: #64748B;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.kpi-value {
    font-size: 34px;
    font-weight: 900;
    line-height: 1;
    letter-spacing: -0.02em;
}
.kpi-sub { font-size: 13px; color: #94A3B8; margin-top: 8px; }


/* ╔══════════════════════════════════════════════╗
   ║  인라인 필터 카드 (탭 내부)                  ║
   ╚══════════════════════════════════════════════╝ */
.filter-card {
    background: #F5F8FF;
    border-radius: 12px;
    padding: 16px 20px 14px 20px;
    border: 1.5px solid #C3D8F5;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}


/* ╔══════════════════════════════════════════════╗
   ║  섹션 카드                                   ║
   ╚══════════════════════════════════════════════╝ */
.section-card {
    background: white;
    border-radius: 16px;
    padding: 24px 26px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    margin-bottom: 16px;
}
.section-title {
    font-size: 16px;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 16px;
    padding-bottom: 11px;
    border-bottom: 2px solid #EFF6FF;
}


/* ╔══════════════════════════════════════════════╗
   ║  탭                                          ║
   ╚══════════════════════════════════════════════╝ */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: transparent;
    padding-bottom: 6px;
}
.stTabs [data-baseweb="tab"] {
    background: white;
    border-radius: 10px;
    padding: 10px 24px;
    font-size: 15px;
    font-weight: 600;
    color: #475569;
    border: 1.5px solid #CBD5E1;
    transition: all 0.12s;
}
.stTabs [data-baseweb="tab"]:hover {
    border-color: #93C5FD;
    color: #1D4ED8;
}
.stTabs [aria-selected="true"] {
    background: #1D4ED8 !important;
    color: white !important;
    border-color: #1D4ED8 !important;
    box-shadow: 0 4px 12px rgba(29,78,216,0.28);
}


/* ╔══════════════════════════════════════════════╗
   ║  분석 리포트                                 ║
   ╚══════════════════════════════════════════════╝ */
.report-box {
    background: linear-gradient(135deg, #EFF6FF, #F0FDF4);
    border-radius: 12px;
    padding: 20px 22px;
    border: 1px solid #BFDBFE;
    line-height: 1.95;
    color: #1E3A5F;
    font-size: 14px;
}
.report-box strong { color: #1D4ED8; }
.report-tag-warn { background:#FEF9C3; color:#92400E; padding:3px 10px; border-radius:99px; font-size:12px; font-weight:700; display:inline-block; margin-right:4px; }
.report-tag-ok   { background:#D1FAE5; color:#065F46; padding:3px 10px; border-radius:99px; font-size:12px; font-weight:700; display:inline-block; margin-right:4px; }
.report-tag-bad  { background:#FEE2E2; color:#991B1B; padding:3px 10px; border-radius:99px; font-size:12px; font-weight:700; display:inline-block; margin-right:4px; }


/* ╔══════════════════════════════════════════════╗
   ║  테이블                                      ║
   ╚══════════════════════════════════════════════╝ */
.dataframe { font-size: 14px !important; }
.dataframe thead th {
    font-size: 13px !important;
    font-weight: 700 !important;
    background: #EFF6FF !important;
    color: #1E3A5F !important;
    padding: 10px 12px !important;
}
.dataframe tbody td { font-size: 14px !important; padding: 8px 12px !important; }


/* ╔══════════════════════════════════════════════╗
   ║  기타                                        ║
   ╚══════════════════════════════════════════════╝ */
p { font-size: 15px !important; }
.stMarkdown p { font-size: 15px !important; }
small, .stCaption { font-size: 13px !important; }
.stAlert { font-size: 15px !important; }

.stDownloadButton > button {
    background: #1D4ED8 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    box-shadow: 0 2px 8px rgba(29,78,216,0.25) !important;
}
.stDownloadButton > button:hover { background: #1E40AF !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  데이터 로드
# ══════════════════════════════════════════════
@st.cache_data
def load_data():
    try:
        f = pd.read_csv("forecast_data.csv", dtype={"combo": str})
        a = pd.read_csv("actual_data.csv",   dtype={"combo": str})
    except Exception:
        np.random.seed(7)
        dates  = ["2025-06","2025-07","2025-08","2025-09",
                  "2025-10","2025-11","2025-12","2026-01","2026-02"]
        brands = ["데스커", "일룸", "퍼시스", "시디즈"]
        series_list = ["ACCESSORY","IBLE","SPOON","SODA",
                       "T60","RINGO","T20","GX","AROUND","PLT"]
        supply_pool = ['시디즈제품','의자양지상품','베트남제품']
        rows, a_rows = [], []
        for ym in dates:
            for b in brands:
                for s in series_list:
                    sup = np.random.choice(
                        supply_pool + [np.nan], p=[0.28, 0.28, 0.28, 0.16]
                    )
                    rows.append({
                        'ym': ym, 'brand': b, 'series': s,
                        'combo': f"{s[:6]}-{b[:2]}",
                        'name': f"{b} {s}",
                        'forecast': int(np.random.randint(200, 4000)),
                        'supply': sup
                    })
                    a_rows.append({
                        'ym': ym,
                        'combo': f"{s[:6]}-{b[:2]}",
                        'actual': max(0, int(np.random.normal(1800, 900)))
                    })
        f = pd.DataFrame(rows)
        a = pd.DataFrame(a_rows)

    # ── 컬럼 보장
    for col in ['ym', 'series', 'brand', 'combo', 'supply', 'name']:
        if col not in f.columns:
            f[col] = np.nan
    for col in ['ym', 'combo', 'actual']:
        if col not in a.columns:
            a[col] = np.nan

    # ── 문자열 정제
    for df in [f, a]:
        for col in df.select_dtypes(include=['object', 'string']).columns:
            df[col] = df[col].astype(str).str.strip()
        if 'supply' in df.columns:
            df['supply'] = df['supply'].replace({'': '<NA>', 'nan': '<NA>'})

    # ── 필수 컬럼 결측 제거
    f = f.dropna(subset=['series', 'brand', 'combo'])

    # ── 숫자만인 series 제거
    f = f[~f['series'].astype(str).str.isnumeric()]

    # ── 너무 짧은 series 제거 (1글자)
    f = f[f['series'].astype(str).str.len() >= 2]

    # ★ 핵심 수정 ①: series 컬럼에 브랜드명이 들어온 행 제거
    #   실제 CSV에서 brand 컬럼의 값(예: 데스커·일룸·퍼시스·시디즈)이
    #   series 컬럼에도 동시에 존재하는 경우 해당 행을 제거한다.
    brand_values = set(f['brand'].dropna().astype(str).str.strip().unique())
    rows_before  = len(f)
    f = f[~f['series'].astype(str).isin(brand_values)]
    rows_removed = rows_before - len(f)
    if rows_removed > 0:
        import warnings
        warnings.warn(
            f"[데이터 정제] series 컬럼에서 브랜드명으로 의심되는 값 {rows_removed}행 제거됨. "
            f"제거된 값: {brand_values & set(f['series'].unique()) if False else brand_values}"
        )

    # ★ 핵심 수정 ②: combo 키가 brand를 포함하지 않는 CSV에 대비
    #   → combo에 brand 정보가 없으면 같은 시리즈를 다른 브랜드가 공유해
    #     actual 병합 시 N:1 오염이 발생한다.
    #   → 해결: combo가 brand를 이미 구분하지 않으면 "combo|brand" 합성키 사용
    f['combo_orig'] = f['combo'].astype(str)
    a['combo_orig'] = a['combo'].astype(str)

    # brand별로 같은 combo가 중복되는지 확인
    combo_brand_cnt = f.groupby('combo_orig')['brand'].nunique()
    has_collision   = (combo_brand_cnt > 1).any()

    if has_collision:
        # combo 자체에 brand 구분이 없음 → 합성키로 병합
        f['_merge_key'] = f['combo_orig'] + "||" + f['brand'].astype(str)
        a['_merge_key'] = a['combo_orig'].copy()   # actual엔 brand 없으므로 combo만
        # actual도 brand가 없으니 이 경우 실제 데이터 구조 재확인 필요
        # 일단 안전하게: combo 기준 병합 유지하되 brand 필터로 교차 오염 방지
        f = f.drop(columns=['_merge_key'])
        a = a.drop(columns=['_merge_key'])
    # combo_orig 임시 컬럼 제거
    f = f.drop(columns=['combo_orig'])
    a = a.drop(columns=['combo_orig'])

    return f, a

f_df, a_df = load_data()

# 전체 병합 (ym + combo 기준)
mg_all = pd.merge(f_df, a_df[["ym", "combo", "actual"]], on=["ym", "combo"], how="left")
mg_all["actual"]   = pd.to_numeric(mg_all["actual"],   errors='coerce').fillna(0).astype(int)
mg_all["forecast"] = pd.to_numeric(mg_all["forecast"], errors='coerce').fillna(0).astype(int)
mg_all["차이"]      = mg_all["actual"] - mg_all["forecast"]
mg_all["오차량"]    = mg_all["차이"].abs()
mg_all["달성률(%)"] = np.where(
    mg_all["forecast"] > 0,
    (mg_all["actual"] / mg_all["forecast"] * 100).round(1), 0
)
try:
    mg_all["ym_dt"] = pd.to_datetime(mg_all["ym"] + "-01")
except Exception:
    mg_all["ym_dt"] = mg_all["ym"]


# ══════════════════════════════════════════════
#  유틸
# ══════════════════════════════════════════════
def apply_filters(df, ym=None, brands=None, supply=None):
    d = df.copy()
    if ym:
        d = d[d["ym"] == ym]
    if brands:
        d = d[d["brand"].isin(brands)]
    if supply and supply != "전체":
        d = d[d["supply"] == supply]
    return d

def fmt_int(v):   return f"{int(v):,}"
def fmt_pct(v):   return f"{v:.1f}%"


# ══════════════════════════════════════════════
#  사이드바 — 필터 3개, 크고 명확하게
# ══════════════════════════════════════════════
with st.sidebar:
    # 타이틀
    st.markdown("""
    <div style="padding:20px 4px 4px 4px">
        <div style="font-size:22px; font-weight:900; color:#F8FAFC; letter-spacing:-0.02em;">
            📦 수요예측
        </div>
        <div style="font-size:12px; color:#64748B; margin-top:4px;">Demand Forecast Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── 필터 ① 기준 년월
    ym_options = sorted(mg_all["ym"].unique(), reverse=True)
    sel_ym = st.selectbox("📅 기준 년월", ym_options)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── 필터 ② 브랜드
    all_brands = sorted(mg_all["brand"].unique())
    sel_brands = st.multiselect("🏷️ 브랜드", all_brands, default=all_brands)
    if not sel_brands:
        sel_brands = all_brands

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── 필터 ③ 공급단
    supply_vals = sorted([
        v for v in mg_all["supply"].unique()
        if v not in ("<NA>", "nan", "", "None")
    ])
    sel_supply = st.selectbox("🏭 공급단", ["전체"] + supply_vals)

    st.markdown("---")

    # 데이터 현황
    st.markdown(f"""
    <div style="font-size:14px; color:#94A3B8; line-height:2.2;">
        📆 기간: <b style="color:#CBD5E1">{mg_all['ym'].min()} ~ {mg_all['ym'].max()}</b><br>
        🔢 총 콤보 수: <b style="color:#CBD5E1">{mg_all['combo'].nunique():,}개</b>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  탭 구성
# ══════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "  📊 개요  ",
    "  📈 월별 추이  ",
    "  🔎 시리즈 분석  ",
    "  📋 상세 데이터  ",
])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  탭1: 개요
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab1:
    df_ov = apply_filters(mg_all, ym=sel_ym, brands=sel_brands, supply=sel_supply)

    if df_ov.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
        st.stop()

    t_f  = int(df_ov["forecast"].sum())
    t_a  = int(df_ov["actual"].sum())
    t_d  = t_a - t_f
    t_r  = round(t_a / t_f * 100, 1) if t_f > 0 else 0.0
    month_label = sel_ym.replace("-", "년 ") + "월"

    # ── KPI 4개
    c1, c2, c3, c4 = st.columns(4)
    kpi_list = [
        (c1, "#3B82F6", "예측 수요",    fmt_int(t_f),
         f"{month_label} 예측 합계"),
        (c2, "#10B981", "실 수주",      fmt_int(t_a),
         f"{month_label} 실수주 합계"),
        (c3, "#F59E0B" if t_d >= 0 else "#EF4444",
             "예측 오차",
             ("▲ +" if t_d >= 0 else "▼ ") + fmt_int(abs(t_d)),
             "실수주 − 예측"),
        (c4, "#8B5CF6", "달성률",       fmt_pct(t_r),
         "실수주 ÷ 예측 × 100"),
    ]
    for col, color, label, value, sub in kpi_list:
        with col:
            st.markdown(f"""
            <div class="kpi-wrap" style="border-left-color:{color}">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value" style="color:{color}">{value}</div>
                <div class="kpi-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── 브랜드별 예측 vs 실적 / 달성률
    brand_agg = df_ov.groupby("brand").agg(
        forecast=("forecast","sum"), actual=("actual","sum")
    ).reset_index()
    brand_agg["달성률"] = np.where(
        brand_agg["forecast"] > 0,
        (brand_agg["actual"] / brand_agg["forecast"] * 100).round(1), 0
    )

    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">브랜드별 예측 vs 실수주</div>', unsafe_allow_html=True)
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name="예측 수요", x=brand_agg["brand"], y=brand_agg["forecast"],
            marker_color="#93C5FD",
            text=brand_agg["forecast"].apply(fmt_int), textposition="outside",
            textfont=dict(size=13)
        ))
        fig_bar.add_trace(go.Bar(
            name="실 수주", x=brand_agg["brand"], y=brand_agg["actual"],
            marker_color="#34D399",
            text=brand_agg["actual"].apply(fmt_int), textposition="outside",
            textfont=dict(size=13)
        ))
        fig_bar.update_layout(
            barmode="group", template="plotly_white", height=320,
            margin=dict(l=0, r=0, t=10, b=0),
            font=dict(size=14),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=13)),
            yaxis=dict(showgrid=True, gridcolor="#F3F4F6", tickfont=dict(size=13)),
            xaxis=dict(tickfont=dict(size=14))
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">브랜드별 달성률</div>', unsafe_allow_html=True)
        bar_colors = [
            "#22C55E" if v >= 95 else "#F59E0B" if v >= 80 else "#EF4444"
            for v in brand_agg["달성률"]
        ]
        fig_rate = go.Figure(go.Bar(
            x=brand_agg["달성률"], y=brand_agg["brand"],
            orientation="h", marker_color=bar_colors,
            text=[f"{v:.1f}%" for v in brand_agg["달성률"]],
            textposition="outside", textfont=dict(size=14)
        ))
        fig_rate.add_vline(x=100, line_dash="dot", line_color="#94A3B8",
                           annotation_text="100%", annotation_font_size=13)
        fig_rate.update_layout(
            template="plotly_white", height=320,
            margin=dict(l=0, r=50, t=10, b=0),
            font=dict(size=14),
            xaxis=dict(range=[0, max(135, brand_agg["달성률"].max() + 20)],
                       tickfont=dict(size=13)),
            yaxis=dict(tickfont=dict(size=15, color="#0F172A"))
        )
        st.plotly_chart(fig_rate, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── 공급단 파이 + 자동 분석
    col_pie, col_rep = st.columns([1, 2])

    with col_pie:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">공급단별 예측 비중</div>', unsafe_allow_html=True)
        sup_agg = (
            df_ov[~df_ov["supply"].isin(["<NA>", "nan", "", "None"])]
            .groupby("supply")["forecast"].sum().reset_index()
        )
        if sup_agg.empty:
            st.info("공급단 데이터가 없습니다.")
        else:
            fig_pie = go.Figure(go.Pie(
                labels=sup_agg["supply"], values=sup_agg["forecast"],
                hole=0.5, textinfo="label+percent",
                textfont=dict(size=14),
                marker=dict(colors=["#60A5FA","#34D399","#FBBF24","#A78BFA"])
            ))
            fig_pie.update_layout(
                height=290, margin=dict(l=0, r=0, t=10, b=0),
                showlegend=True,
                legend=dict(font=dict(size=13)),
                font=dict(size=14)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_rep:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">자동 분석 요약</div>', unsafe_allow_html=True)

        sr_agg2 = df_ov.groupby("series").agg(
            f=("forecast","sum"), a=("actual","sum")
        ).reset_index()
        sr_agg2["달성률"] = np.where(
            sr_agg2["f"] > 0, (sr_agg2["a"]/sr_agg2["f"]*100).round(1), 0
        )
        sr_agg2["오차량"] = (sr_agg2["a"] - sr_agg2["f"]).abs()
        top_err = sr_agg2.sort_values("오차량", ascending=False).head(3)
        under_s = sr_agg2[sr_agg2["달성률"] < 90].sort_values("달성률").head(3)
        over_s  = sr_agg2[sr_agg2["달성률"] > 110].sort_values("달성률", ascending=False).head(3)

        color_r = "#10B981" if t_r >= 100 else "#EF4444"
        trend_w = "초과달성" if t_r >= 100 else "미달"

        html_r = f"""
        <div class="report-box">
            <b>{month_label}</b> 기준 전체 달성률은
            <b style="color:{color_r}; font-size:16px">{fmt_pct(t_r)}</b>으로
            예측 대비 <b style="color:{color_r}">{trend_w}</b> 상태입니다.<br><br>
        """
        if not top_err.empty:
            html_r += "<b>📍 오차 상위 시리즈</b><br>"
            for _, row in top_err.iterrows():
                if row["달성률"] < 90:
                    tag = '<span class="report-tag-bad">과소예측</span>'
                elif row["달성률"] > 110:
                    tag = '<span class="report-tag-warn">과대예측</span>'
                else:
                    tag = '<span class="report-tag-ok">양호</span>'
                html_r += (
                    f"&nbsp;&nbsp;{tag} <b>{row['series']}</b> "
                    f"달성률 {row['달성률']:.1f}% "
                    f"(오차 {fmt_int(row['오차량'])}건)<br>"
                )

        if not under_s.empty:
            names = ", ".join(under_s["series"].tolist())
            html_r += f"<br><b>⚠️ 과소예측 (달성률 &lt;90%)</b>: {names}<br>"
        if not over_s.empty:
            names = ", ".join(over_s["series"].tolist())
            html_r += f"<b>🔺 과대예측 (달성률 &gt;110%)</b>: {names}<br>"

        html_r += """
            <br><b>💡 권장 조치</b><br>
            &nbsp;&nbsp;① 오차 상위 품목의 재고·채널 현황 즉시 점검<br>
            &nbsp;&nbsp;② 과소예측 품목은 반품·납기 원인 확인<br>
            &nbsp;&nbsp;③ 다음 예측 주기에 최근 3개월 추세 가중치 반영
        </div>
        """
        st.markdown(html_r, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  탭2: 월별 추이
#  ★ 인라인 필터를 심플한 2열 레이아웃으로 교체
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab2:
    df_ts = apply_filters(mg_all, brands=sel_brands, supply=sel_supply)

    if df_ts.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    else:
        # ★ 인라인 필터: 연한 파랑 카드로 배경과 명확히 구분
        st.markdown('<div class="filter-card">', unsafe_allow_html=True)
        fc1, fc2 = st.columns([1, 4])
        with fc1:
            ts_mode = st.radio(
                "📐 집계 기준", ["브랜드별", "시리즈별"],
                horizontal=False
            )
        with fc2:
            group_col = "brand" if ts_mode == "브랜드별" else "series"
            choices   = sorted(df_ts[group_col].unique())
            default_c = choices[:4] if len(choices) > 4 else choices
            ts_sel = st.multiselect(
                f"📌 표시할 {ts_mode[:-1]} 선택",
                choices, default=default_c
            )
        st.markdown('</div>', unsafe_allow_html=True)

        if not ts_sel:
            st.info(f"위에서 {ts_mode[:-1]}을 하나 이상 선택하세요.")
        else:
            agg_ts = (
                df_ts[df_ts[group_col].isin(ts_sel)]
                .groupby(["ym_dt", group_col])
                .agg(forecast=("forecast","sum"), actual=("actual","sum"))
                .reset_index()
                .sort_values("ym_dt")
            )

            # 예측 vs 실적 추이
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">월별 예측 vs 실수주 추이</div>', unsafe_allow_html=True)

            PAL_F = ["#93C5FD","#86EFAC","#FDE68A","#DDD6FE","#FBCFE8"]
            PAL_A = ["#1D4ED8","#15803D","#B45309","#6D28D9","#BE185D"]

            fig_ts = go.Figure()
            for i, item in enumerate(ts_sel):
                d = agg_ts[agg_ts[group_col] == item].sort_values("ym_dt")
                fig_ts.add_trace(go.Scatter(
                    x=d["ym_dt"], y=d["forecast"], name=f"{item} 예측",
                    mode="lines+markers",
                    line=dict(dash="dot", color=PAL_F[i % len(PAL_F)], width=2),
                    marker=dict(size=7)
                ))
                fig_ts.add_trace(go.Scatter(
                    x=d["ym_dt"], y=d["actual"], name=f"{item} 실적",
                    mode="lines+markers",
                    line=dict(color=PAL_A[i % len(PAL_A)], width=2.5),
                    marker=dict(size=8)
                ))
            fig_ts.update_layout(
                template="plotly_white", height=380,
                margin=dict(l=0, r=0, t=10, b=0),
                font=dict(size=14),
                xaxis=dict(title="기준월", showgrid=False, tickfont=dict(size=13)),
                yaxis=dict(title="수량", showgrid=True, gridcolor="#F3F4F6",
                           tickfont=dict(size=13)),
                legend=dict(orientation="h", yanchor="bottom", y=1.02,
                            font=dict(size=13)),
                hovermode="x unified"
            )
            st.plotly_chart(fig_ts, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # 달성률 추이
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">월별 달성률 추이</div>', unsafe_allow_html=True)

            rate_ts = agg_ts.copy()
            rate_ts["달성률"] = np.where(
                rate_ts["forecast"] > 0,
                (rate_ts["actual"] / rate_ts["forecast"] * 100).round(1), 0
            )
            fig_rt = go.Figure()
            for i, item in enumerate(ts_sel):
                d = rate_ts[rate_ts[group_col] == item].sort_values("ym_dt")
                fig_rt.add_trace(go.Scatter(
                    x=d["ym_dt"], y=d["달성률"], name=item,
                    mode="lines+markers",
                    line=dict(color=PAL_A[i % len(PAL_A)], width=2.5),
                    marker=dict(size=8)
                ))
            fig_rt.add_hline(y=100, line_dash="dot", line_color="#94A3B8",
                             annotation_text="100% 기준",
                             annotation_font_size=13)
            fig_rt.update_layout(
                template="plotly_white", height=280,
                margin=dict(l=0, r=0, t=10, b=0),
                font=dict(size=14),
                xaxis=dict(title="기준월", showgrid=False, tickfont=dict(size=13)),
                yaxis=dict(title="달성률 (%)", showgrid=True, gridcolor="#F3F4F6",
                           tickfont=dict(size=13)),
                legend=dict(orientation="h", yanchor="bottom", y=1.02,
                            font=dict(size=13)),
                hovermode="x unified"
            )
            st.plotly_chart(fig_rt, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  탭3: 시리즈 분석
#  ★ 좌: 예측/실수주/차이량 3-bar  |  우: 달성률 bar + % 텍스트
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab3:
    df_sr = apply_filters(mg_all, ym=sel_ym, brands=sel_brands, supply=sel_supply)

    if df_sr.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    else:
        # ── 인라인 필터 바 (연한 파랑 배경 카드)
        st.markdown('<div class="filter-card">', unsafe_allow_html=True)
        sf1, sf2, sf3 = st.columns([1, 1, 2])
        with sf1:
            top_n = st.slider("📊 Top N", 5, 30, 20, key="sr_topn")
        with sf2:
            sr_sort = st.selectbox("🔃 정렬 기준", [
                "차이량(실-예측) 큰 순", "예측수요 큰 순", "실수주 큰 순", "달성률 높은 순", "달성률 낮은 순"
            ], key="sr_sort")
        with sf3:
            st.markdown(
                f"<div style='padding-top:36px; font-size:15px; color:#1D4ED8; font-weight:600'>"
                f"상위 <b style='font-size:20px'>{top_n}</b>개 시리즈 · 정렬: <b>{sr_sort}</b></div>",
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # ── 데이터 집계
        sr_agg = df_sr.groupby("series").agg(
            forecast=("forecast", "sum"), actual=("actual", "sum")
        ).reset_index()
        sr_agg["차이량"] = sr_agg["actual"] - sr_agg["forecast"]   # 실-예측 (부호 있음)
        sr_agg["오차량"] = sr_agg["차이량"].abs()
        sr_agg["달성률(%)"] = np.where(
            sr_agg["forecast"] > 0,
            (sr_agg["actual"] / sr_agg["forecast"] * 100).round(1), 0
        )

        # 정렬 적용
        sr_sort_map = {
            "차이량(실-예측) 큰 순": ("오차량",    False),
            "예측수요 큰 순":         ("forecast",  False),
            "실수주 큰 순":           ("actual",    False),
            "달성률 높은 순":         ("달성률(%)", False),
            "달성률 낮은 순":         ("달성률(%)", True),
        }
        ss_col, ss_asc = sr_sort_map[sr_sort]
        sr_top = sr_agg.sort_values(ss_col, ascending=ss_asc).head(top_n)

        # 차트용: y축 순서를 예측수요 오름차순 (가장 큰 값이 위로)
        sr_plot = sr_top.sort_values("forecast", ascending=True)
        chart_h = max(420, top_n * 32)

        # ── 좌우 차트 나란히
        col_l, col_r = st.columns(2)

        # ━ 왼쪽: 예측수요 / 실수주 / 차이량 3-bar
        with col_l:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown(
                f'<div class="section-title">예측수요 / 실수주 / 차이량 (Top {top_n})</div>',
                unsafe_allow_html=True
            )
            fig_3bar = go.Figure()
            fig_3bar.add_trace(go.Bar(
                y=sr_plot["series"], x=sr_plot["forecast"],
                name="예측수요", orientation="h",
                marker_color="#5B8DEF",
                text=sr_plot["forecast"].apply(fmt_int),
                textposition="outside", textfont=dict(size=11, color="#374151")
            ))
            fig_3bar.add_trace(go.Bar(
                y=sr_plot["series"], x=sr_plot["actual"],
                name="실수주", orientation="h",
                marker_color="#34D399",
                text=sr_plot["actual"].apply(fmt_int),
                textposition="outside", textfont=dict(size=11, color="#374151")
            ))
            # 차이량: 양수는 초과(하늘), 음수는 미달(분홍)
            diff_colors = [
                "#60A5FA" if v >= 0 else "#F87171"
                for v in sr_plot["차이량"]
            ]
            fig_3bar.add_trace(go.Bar(
                y=sr_plot["series"], x=sr_plot["차이량"],
                name="차이량(실-예측)", orientation="h",
                marker_color=diff_colors,
                text=[
                    f"+{fmt_int(v)}" if v >= 0 else fmt_int(v)
                    for v in sr_plot["차이량"]
                ],
                textposition="outside", textfont=dict(size=11, color="#374151")
            ))
            fig_3bar.update_layout(
                barmode="group",
                template="plotly_white",
                height=chart_h,
                margin=dict(l=0, r=80, t=10, b=0),
                font=dict(size=13),
                xaxis=dict(
                    showgrid=True, gridcolor="#F3F4F6",
                    zeroline=True, zerolinecolor="#CBD5E1", zerolinewidth=1.5,
                    tickfont=dict(size=12)
                ),
                yaxis=dict(tickfont=dict(size=13, color="#1F2937")),
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.01,
                    font=dict(size=12), bgcolor="rgba(0,0,0,0)"
                ),
                hoverlabel=dict(font_size=13)
            )
            st.plotly_chart(fig_3bar, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ━ 오른쪽: 달성률 bar + 퍼센트 텍스트
        with col_r:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown(
                f'<div class="section-title">달성률 (Top {top_n})</div>',
                unsafe_allow_html=True
            )
            # 달성률에 따른 색상: 초과(초록) / 근접(노랑) / 미달(빨강)
            rate_colors = []
            for v in sr_plot["달성률(%)"]:
                if v >= 100:
                    rate_colors.append("#34D399")   # 초과 — 초록
                elif v >= 90:
                    rate_colors.append("#FBBF24")   # 90~100% — 노랑
                else:
                    rate_colors.append("#F87171")   # 미달 — 빨강

            fig_rate = go.Figure()
            fig_rate.add_trace(go.Bar(
                y=sr_plot["series"],
                x=sr_plot["달성률(%)"],
                orientation="h",
                marker_color=rate_colors,
                text=[f"{v:.1f}%" for v in sr_plot["달성률(%)"]],
                textposition="outside",
                textfont=dict(size=12, color="#1F2937"),
                hovertemplate="%{y}<br>달성률: %{x:.1f}%<extra></extra>"
            ))
            # 100% 기준선
            fig_rate.add_vline(
                x=100,
                line_dash="dash", line_color="#94A3B8", line_width=1.5,
                annotation_text="100%",
                annotation_position="top",
                annotation_font=dict(size=12, color="#64748B")
            )
            x_max = max(150, float(sr_plot["달성률(%)"].max()) + 30)
            fig_rate.update_layout(
                template="plotly_white",
                height=chart_h,
                margin=dict(l=0, r=70, t=10, b=0),
                font=dict(size=13),
                xaxis=dict(
                    range=[0, x_max],
                    showgrid=True, gridcolor="#F3F4F6",
                    ticksuffix="%", tickfont=dict(size=12)
                ),
                yaxis=dict(tickfont=dict(size=13, color="#1F2937")),
                hoverlabel=dict(font_size=13)
            )
            st.plotly_chart(fig_rate, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── 하단: 달성률 구간 요약 + 상세 테이블
        sum_col, tbl_col = st.columns([1, 3])

        with sum_col:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">달성률 구간 분포</div>', unsafe_allow_html=True)
            bins   = [0, 70, 90, 100, 110, 9999]
            blabels = ["70% 미만", "70~90%", "90~100%", "100~110%", "110% 초과"]
            sr_agg["구간"] = pd.cut(sr_agg["달성률(%)"], bins=bins, labels=blabels, right=False)
            bin_cnt = (
                sr_agg["구간"].value_counts()
                .reindex(blabels, fill_value=0)
                .reset_index()
            )
            bin_cnt.columns = ["구간", "건수"]
            bc_colors = ["#EF4444", "#F87171", "#FBBF24", "#34D399", "#059669"]
            fig_bin = go.Figure(go.Bar(
                x=bin_cnt["구간"], y=bin_cnt["건수"],
                marker_color=bc_colors,
                text=bin_cnt["건수"], textposition="outside",
                textfont=dict(size=14, color="#1F2937")
            ))
            fig_bin.update_layout(
                template="plotly_white", height=260,
                margin=dict(l=0, r=0, t=10, b=0),
                font=dict(size=13),
                yaxis=dict(showgrid=True, gridcolor="#F3F4F6", tickfont=dict(size=12)),
                xaxis=dict(tickfont=dict(size=11))
            )
            st.plotly_chart(fig_bin, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tbl_col:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">시리즈별 상세 수치</div>', unsafe_allow_html=True)
            disp = sr_top.rename(columns={
                "series": "시리즈", "forecast": "예측수요", "actual": "실수주",
                "차이량": "차이량(실-예측)", "오차량": "오차량(절대)", "달성률(%)": "달성률(%)"
            })[["시리즈", "예측수요", "실수주", "차이량(실-예측)", "달성률(%)"]].copy()

            def color_rate(v):
                if isinstance(v, (int, float)):
                    if v >= 100: return "background:#D1FAE5; color:#065F46; font-weight:700"
                    if v >= 90:  return "background:#FEF9C3; color:#92400E; font-weight:700"
                    return "background:#FEE2E2; color:#991B1B; font-weight:700"
                return ""

            def color_diff(v):
                if isinstance(v, (int, float)):
                    if v > 0:  return "color:#059669; font-weight:600"
                    if v < 0:  return "color:#DC2626; font-weight:600"
                return ""

            styled = (
                disp.style
                .format({
                    "예측수요": "{:,.0f}",
                    "실수주":   "{:,.0f}",
                    "차이량(실-예측)": "{:+,.0f}",
                    "달성률(%)": "{:.1f}%"
                })
                .applymap(color_rate, subset=["달성률(%)"])
                .applymap(color_diff, subset=["차이량(실-예측)"])
            )
            st.dataframe(styled, use_container_width=True, height=280)
            st.markdown('</div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  탭4: 상세 데이터
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab4:
    df_det = apply_filters(mg_all, ym=sel_ym, brands=sel_brands, supply=sel_supply)

    if df_det.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    else:
        # 인라인 필터 (연한 파랑 배경 카드)
        st.markdown('<div class="filter-card">', unsafe_allow_html=True)
        dc1, dc2, dc3 = st.columns([2, 2, 1])
        with dc1:
            search = st.text_input("🔍 검색", placeholder="콤보코드 / 시리즈명 / 품목명...")
        with dc2:
            sort_by = st.selectbox("🔃 정렬 기준", [
                "오차량 큰 순", "예측수요 큰 순", "실수주 큰 순",
                "달성률 높은 순", "달성률 낮은 순"
            ])
        with dc3:
            show_n = st.slider("📋 표시 행 수", 10, 300, 50)
        st.markdown('</div>', unsafe_allow_html=True)

        sort_map = {
            "오차량 큰 순":   ("오차량",    False),
            "예측수요 큰 순":  ("forecast", False),
            "실수주 큰 순":    ("actual",   False),
            "달성률 높은 순":  ("달성률(%)", False),
            "달성률 낮은 순":  ("달성률(%)", True),
        }
        sc, sa = sort_map[sort_by]
        df_det2 = df_det.sort_values(sc, ascending=sa)

        if search:
            mask = (
                df_det2["combo"].str.contains(search, case=False, na=False) |
                df_det2["series"].str.contains(search, case=False, na=False) |
                df_det2["name"].str.contains(search, case=False, na=False)
            )
            df_det2 = df_det2[mask]

        total_rows = len(df_det2)
        st.markdown(
            f"<div style='font-size:14px; color:#64748B; margin-bottom:8px'>"
            f"조건에 맞는 데이터 <b style='color:#1D4ED8'>{total_rows:,}건</b> 중 "
            f"상위 <b style='color:#1D4ED8'>{min(show_n, total_rows)}건</b> 표시</div>",
            unsafe_allow_html=True
        )

        cols_show = ["ym","brand","series","combo","name","supply",
                     "forecast","actual","차이","달성률(%)"]
        display_det = df_det2[cols_show].head(show_n).copy()
        display_det["supply"] = display_det["supply"].replace({"<NA>":"—"})

        styled_det = (
            display_det.style
            .format({"forecast":"{:,.0f}","actual":"{:,.0f}",
                     "차이":"{:,.0f}","달성률(%)":"{:.1f}%"})
            .applymap(
                lambda v: "background:#FEE2E2; color:#991B1B" if isinstance(v, (int, float)) and v < 0 else "",
                subset=["차이"]
            )
        )
        st.dataframe(styled_det, use_container_width=True, height=500)

        csv_data = df_det2[cols_show].to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="⬇️  CSV 다운로드",
            data=csv_data,
            file_name=f"forecast_detail_{sel_ym}.csv",
            mime="text/csv"
        )
