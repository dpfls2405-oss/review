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
html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}

/* ── 전체 배경 ── */
.stApp { background-color: #F0F2F8; }

/* ══════════════════════════════
   사이드바
══════════════════════════════ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
    border-right: 1px solid #334155;
}
/* 사이드바 모든 텍스트 기본 색상 */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] label {
    color: #E2E8F0 !important;
}
/* 사이드바 selectbox / multiselect 컨테이너 */
section[data-testid="stSidebar"] .stSelectbox > div > div,
section[data-testid="stSidebar"] .stMultiSelect > div > div {
    background: #1E293B !important;
    border: 1.5px solid #475569 !important;
    border-radius: 8px !important;
    color: #F1F5F9 !important;
}
/* 선택된 태그(chip) */
section[data-testid="stSidebar"] .stMultiSelect span[data-baseweb="tag"] {
    background: #3B82F6 !important;
    color: white !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
    padding: 2px 10px !important;
}
section[data-testid="stSidebar"] .stMultiSelect span[data-baseweb="tag"] span {
    color: white !important;
}
/* 구분선 */
section[data-testid="stSidebar"] hr {
    border-color: #334155 !important;
    margin: 14px 0 !important;
}
/* ── 사이드바 필터 섹션 제목 ── */
.sb-section-label {
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #94A3B8 !important;
    margin-bottom: 6px !important;
    margin-top: 4px !important;
}
.sb-filter-group {
    background: rgba(255,255,255,0.05);
    border-radius: 10px;
    padding: 14px 14px 10px 14px;
    margin-bottom: 10px;
    border: 1px solid #334155;
}
/* selectbox 라벨 크기 */
section[data-testid="stSidebar"] .stSelectbox label {
    font-size: 14px !important;
    font-weight: 600 !important;
    color: #CBD5E1 !important;
    margin-bottom: 4px !important;
}
section[data-testid="stSidebar"] .stMultiSelect label {
    font-size: 14px !important;
    font-weight: 600 !important;
    color: #CBD5E1 !important;
    margin-bottom: 4px !important;
}
/* selectbox 선택된 값 텍스트 */
section[data-testid="stSidebar"] .stSelectbox div[data-testid="stMarkdownContainer"] p {
    font-size: 15px !important;
    font-weight: 600 !important;
    color: #F8FAFC !important;
}
/* 사이드바 caption */
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] small {
    font-size: 12px !important;
    color: #64748B !important;
}

/* ══════════════════════════════
   KPI 카드
══════════════════════════════ */
.kpi-wrap {
    background: white;
    border-radius: 16px;
    padding: 24px 22px 20px 22px;
    border-left: 5px solid;
    box-shadow: 0 4px 16px rgba(0,0,0,0.07);
    height: 100%;
    transition: transform 0.15s;
}
.kpi-wrap:hover { transform: translateY(-2px); }
.kpi-label {
    font-size: 13px;
    color: #64748B;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.kpi-value {
    font-size: 36px;
    font-weight: 900;
    color: #0F172A;
    line-height: 1;
    letter-spacing: -0.02em;
}
.kpi-sub {
    font-size: 13px;
    color: #94A3B8;
    margin-top: 8px;
}

/* ══════════════════════════════
   섹션 카드
══════════════════════════════ */
.section-card {
    background: white;
    border-radius: 16px;
    padding: 24px 26px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    margin-bottom: 16px;
}
.section-title {
    font-size: 17px;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 18px;
    padding-bottom: 12px;
    border-bottom: 2px solid #F1F5F9;
    letter-spacing: -0.01em;
}

/* ══════════════════════════════
   탭
══════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: transparent;
    padding-bottom: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: white;
    border-radius: 10px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: 600;
    color: #475569;
    border: 1.5px solid #E2E8F0;
    transition: all 0.15s;
}
.stTabs [aria-selected="true"] {
    background: #1D4ED8 !important;
    color: white !important;
    border-color: #1D4ED8 !important;
    box-shadow: 0 4px 12px rgba(29,78,216,0.35);
}

/* ══════════════════════════════
   월별 추이 탭 인라인 필터
   → 깔끔한 필터 바로 교체
══════════════════════════════ */
.filter-bar {
    background: white;
    border-radius: 12px;
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 24px;
    border: 1.5px solid #E2E8F0;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

/* ══════════════════════════════
   분석 리포트
══════════════════════════════ */
.report-box {
    background: linear-gradient(135deg, #EFF6FF 0%, #F0FDF4 100%);
    border-radius: 12px;
    padding: 22px 24px;
    border: 1px solid #BFDBFE;
    line-height: 2.0;
    color: #1E3A5F;
    font-size: 14px;
}
.report-box strong { color: #1D4ED8; }
.report-tag-warn {
    background:#FEF9C3; color:#92400E;
    padding:3px 10px; border-radius:99px;
    font-size:12px; font-weight:700;
    display:inline-block; margin-right:4px;
}
.report-tag-ok {
    background:#D1FAE5; color:#065F46;
    padding:3px 10px; border-radius:99px;
    font-size:12px; font-weight:700;
    display:inline-block; margin-right:4px;
}
.report-tag-bad {
    background:#FEE2E2; color:#991B1B;
    padding:3px 10px; border-radius:99px;
    font-size:12px; font-weight:700;
    display:inline-block; margin-right:4px;
}

/* ══════════════════════════════
   테이블 글씨 크기
══════════════════════════════ */
.dataframe { font-size: 14px !important; }
.dataframe thead th {
    font-size: 13px !important;
    font-weight: 700 !important;
    background: #F8FAFC !important;
}
.dataframe tbody td { font-size: 14px !important; }

/* 전반적 본문 글씨 */
.stMarkdown p { font-size: 14px; }
p, li { font-size: 14px !important; }
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

    # 정제
    for col in ['ym','series','brand','combo','supply','name']:
        if col not in f.columns:
            f[col] = np.nan
    for col in ['ym','combo','actual']:
        if col not in a.columns:
            a[col] = np.nan

    for df in [f, a]:
        for col in df.select_dtypes(include=['object', 'string']).columns:
            df[col] = df[col].astype(str).str.strip()
        if 'supply' in df.columns:
            df['supply'] = df['supply'].replace({'': '<NA>', 'nan': '<NA>'})

    f = f.dropna(subset=['series','brand','combo'])
    f = f[~f['series'].astype(str).str.isnumeric()]
    f = f[f['series'].astype(str).str.len() >= 2]
    return f, a

f_df, a_df = load_data()

# 전체 병합
mg_all = pd.merge(f_df, a_df[["ym","combo","actual"]], on=["ym","combo"], how="left")
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
    st.markdown('<div class="sb-section-label">📅 기준 년월</div>', unsafe_allow_html=True)
    ym_options = sorted(mg_all["ym"].unique(), reverse=True)
    sel_ym = st.selectbox(" ", ym_options, label_visibility="collapsed")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── 필터 ② 브랜드
    st.markdown('<div class="sb-section-label">🏷️ 브랜드</div>', unsafe_allow_html=True)
    all_brands = sorted(mg_all["brand"].unique())
    sel_brands = st.multiselect(" ", all_brands, default=all_brands, label_visibility="collapsed")
    if not sel_brands:
        sel_brands = all_brands

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── 필터 ③ 공급단
    st.markdown('<div class="sb-section-label">🏭 공급단</div>', unsafe_allow_html=True)
    supply_vals = sorted([
        v for v in mg_all["supply"].unique()
        if v not in ("<NA>", "nan", "", "None")
    ])
    sel_supply = st.selectbox(" ", ["전체"] + supply_vals, label_visibility="collapsed")

    st.markdown("---")

    # 데이터 현황
    st.markdown(f"""
    <div style="font-size:13px; color:#94A3B8; line-height:2;">
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
        # ★ 인라인 필터: 흰 카드 안에 라디오 + 멀티셀렉트만
        st.markdown('<div class="section-card" style="padding:18px 22px 14px 22px">', unsafe_allow_html=True)
        fc1, fc2 = st.columns([1, 4])
        with fc1:
            st.markdown("**집계 기준**")
            ts_mode = st.radio(
                "집계 기준", ["브랜드별", "시리즈별"],
                horizontal=False, label_visibility="collapsed"
            )
        with fc2:
            group_col = "brand" if ts_mode == "브랜드별" else "series"
            choices   = sorted(df_ts[group_col].unique())
            default_c = choices[:4] if len(choices) > 4 else choices
            st.markdown(f"**표시할 {ts_mode[:-1]} 선택**")
            ts_sel = st.multiselect(
                f"표시할 {ts_mode[:-1]}",
                choices, default=default_c,
                label_visibility="collapsed"
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
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab3:
    df_sr = apply_filters(mg_all, ym=sel_ym, brands=sel_brands, supply=sel_supply)

    if df_sr.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    else:
        # 인라인 필터 (Top N 슬라이더만)
        st.markdown('<div class="section-card" style="padding:16px 22px 12px 22px">', unsafe_allow_html=True)
        sf1, sf2 = st.columns([1, 3])
        with sf1:
            st.markdown("**표시할 시리즈 수**")
            top_n = st.slider(" ", 5, 30, 15, label_visibility="collapsed")
        with sf2:
            st.markdown(
                f"<div style='padding-top:12px; font-size:14px; color:#64748B'>"
                f"예측 수요 기준 상위 <b style='color:#1D4ED8; font-size:18px'>{top_n}</b>개 시리즈 표시</div>",
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

        sr_agg = df_sr.groupby("series").agg(
            forecast=("forecast","sum"), actual=("actual","sum")
        ).reset_index()
        sr_agg["달성률(%)"] = np.where(
            sr_agg["forecast"] > 0,
            (sr_agg["actual"] / sr_agg["forecast"] * 100).round(1), 0
        )
        sr_agg["오차량"] = (sr_agg["actual"] - sr_agg["forecast"]).abs()
        sr_top = sr_agg.sort_values("forecast", ascending=False).head(top_n)

        col_l, col_r = st.columns([3, 2])

        with col_l:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">시리즈별 예측 vs 실수주</div>', unsafe_allow_html=True)
            sr_plot = sr_top.sort_values("forecast")
            fig_sr = go.Figure()
            fig_sr.add_trace(go.Bar(
                y=sr_plot["series"], x=sr_plot["forecast"], name="예측 수요",
                orientation="h", marker_color="#93C5FD",
                text=sr_plot["forecast"].apply(fmt_int),
                textposition="outside", textfont=dict(size=12)
            ))
            fig_sr.add_trace(go.Bar(
                y=sr_plot["series"], x=sr_plot["actual"], name="실 수주",
                orientation="h", marker_color="#34D399",
                text=sr_plot["actual"].apply(fmt_int),
                textposition="outside", textfont=dict(size=12)
            ))
            fig_sr.update_layout(
                barmode="group", template="plotly_white",
                height=max(340, top_n * 30),
                margin=dict(l=0, r=70, t=10, b=0),
                font=dict(size=14),
                xaxis=dict(showgrid=True, gridcolor="#F3F4F6", tickfont=dict(size=13)),
                yaxis=dict(tickfont=dict(size=13)),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=13))
            )
            st.plotly_chart(fig_sr, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_r:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">달성률 구간 분포</div>', unsafe_allow_html=True)
            bins   = [0, 70, 90, 110, 130, 9999]
            labels = ["70% 미만","70~90%","90~110%","110~130%","130% 초과"]
            sr_agg["구간"] = pd.cut(sr_agg["달성률(%)"], bins=bins, labels=labels, right=False)
            bin_cnt = (
                sr_agg["구간"].value_counts()
                .reindex(labels, fill_value=0)
                .reset_index()
            )
            bin_cnt.columns = ["구간","건수"]
            bc = ["#EF4444","#F87171","#22C55E","#FBBF24","#F59E0B"]
            fig_bin = go.Figure(go.Bar(
                x=bin_cnt["구간"], y=bin_cnt["건수"],
                marker_color=bc,
                text=bin_cnt["건수"], textposition="outside",
                textfont=dict(size=14)
            ))
            fig_bin.update_layout(
                template="plotly_white", height=230,
                margin=dict(l=0, r=0, t=10, b=0),
                font=dict(size=13),
                yaxis=dict(showgrid=True, gridcolor="#F3F4F6", tickfont=dict(size=13)),
                xaxis=dict(tickfont=dict(size=12))
            )
            st.plotly_chart(fig_bin, use_container_width=True)

            st.markdown('<div class="section-title" style="margin-top:8px">오차량 vs 달성률</div>',
                        unsafe_allow_html=True)
            fig_sc = go.Figure(go.Scatter(
                x=sr_top["오차량"], y=sr_top["달성률(%)"],
                mode="markers+text",
                text=sr_top["series"], textposition="top center",
                textfont=dict(size=12),
                marker=dict(
                    size=13, color=sr_top["달성률(%)"],
                    colorscale="RdYlGn", cmin=70, cmax=130,
                    showscale=True,
                    colorbar=dict(thickness=10, len=0.7, tickfont=dict(size=12))
                )
            ))
            fig_sc.add_hline(y=100, line_dash="dot", line_color="#94A3B8")
            fig_sc.update_layout(
                template="plotly_white", height=240,
                margin=dict(l=0, r=0, t=10, b=0),
                font=dict(size=13),
                xaxis=dict(title="오차량", tickfont=dict(size=12),
                           showgrid=True, gridcolor="#F3F4F6"),
                yaxis=dict(title="달성률 (%)", tickfont=dict(size=12),
                           showgrid=True, gridcolor="#F3F4F6")
            )
            st.plotly_chart(fig_sc, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # 하단 테이블
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">시리즈별 상세 수치</div>', unsafe_allow_html=True)
        disp = sr_top.rename(columns={
            "series":"시리즈", "forecast":"예측 수요", "actual":"실 수주",
            "달성률(%)":"달성률(%)", "오차량":"오차량"
        }).sort_values("예측 수요", ascending=False)

        def color_rate(v):
            if isinstance(v, (int, float)):
                if v >= 100: return "background:#D1FAE5; color:#065F46; font-weight:700"
                if v >= 90:  return "background:#FEF9C3; color:#92400E; font-weight:700"
                return "background:#FEE2E2; color:#991B1B; font-weight:700"
            return ""

        styled = (
            disp.style
            .format({"예측 수요":"{:,.0f}","실 수주":"{:,.0f}",
                     "오차량":"{:,.0f}","달성률(%)":"{:.1f}%"})
            .applymap(color_rate, subset=["달성률(%)"])
        )
        st.dataframe(styled, use_container_width=True, height=320)
        st.markdown('</div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  탭4: 상세 데이터
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab4:
    df_det = apply_filters(mg_all, ym=sel_ym, brands=sel_brands, supply=sel_supply)

    if df_det.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    else:
        # 인라인 필터 바
        st.markdown('<div class="section-card" style="padding:16px 22px 12px 22px">', unsafe_allow_html=True)
        dc1, dc2, dc3 = st.columns([2, 2, 1])
        with dc1:
            st.markdown("**🔍 검색**")
            search = st.text_input(" ", placeholder="콤보코드 / 시리즈명 / 품목명...",
                                   label_visibility="collapsed")
        with dc2:
            st.markdown("**정렬 기준**")
            sort_by = st.selectbox(" ", [
                "오차량 큰 순","예측수요 큰 순","실수주 큰 순",
                "달성률 높은 순","달성률 낮은 순"
            ], label_visibility="collapsed")
        with dc3:
            st.markdown("**표시 행 수**")
            show_n = st.slider(" ", 10, 300, 50, label_visibility="collapsed")
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
