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
    font-size: 15px;
}
.stApp { background-color: #EAECF4; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A1628 0%, #172035 100%);
    border-right: 1px solid #2A3A52;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] label { color: #DDE3EE !important; }
section[data-testid="stSidebar"] .stSelectbox > div > div,
section[data-testid="stSidebar"] .stMultiSelect > div > div {
    background: #1C2B3F !important;
    border: 2px solid #3D5A80 !important;
    border-radius: 8px !important;
    color: #EEF2FF !important;
}
section[data-testid="stSidebar"] .stMultiSelect span[data-baseweb="tag"] {
    background: #2563EB !important; color: white !important;
    font-size: 13px !important; font-weight: 700 !important;
    border-radius: 6px !important; padding: 3px 10px !important;
}
section[data-testid="stSidebar"] .stMultiSelect span[data-baseweb="tag"] span { color: white !important; }
section[data-testid="stSidebar"] hr { border-color: #2A3A52 !important; margin: 16px 0 !important; }
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label {
    font-size: 14px !important; font-weight: 700 !important;
    color: #93B4D8 !important; margin-bottom: 6px !important;
}
.stSelectbox label, .stMultiSelect label, .stSlider label,
.stTextInput label, .stRadio label {
    font-size: 15px !important; font-weight: 700 !important;
    color: #1E3A5F !important; margin-bottom: 6px !important;
}
.stSelectbox > div > div {
    background: #F0F5FF !important; border: 2px solid #93C5FD !important;
    border-radius: 8px !important; font-size: 15px !important;
    font-weight: 600 !important; color: #1E3A5F !important; min-height: 44px !important;
}
.stSelectbox > div > div:hover { border-color: #2563EB !important; background: #EBF2FF !important; }
.stMultiSelect > div > div {
    background: #F0F5FF !important; border: 2px solid #93C5FD !important;
    border-radius: 8px !important; font-size: 15px !important;
    color: #1E3A5F !important; min-height: 44px !important;
}
.stMultiSelect > div > div:hover { border-color: #2563EB !important; }
.stMultiSelect span[data-baseweb="tag"] {
    background: #DBEAFE !important; color: #1D4ED8 !important;
    font-size: 13px !important; font-weight: 700 !important;
    border-radius: 6px !important; border: 1px solid #93C5FD !important;
}
.stTextInput > div > div > input {
    background: #F8FAFF !important; border: 2px solid #CBD5E1 !important;
    border-radius: 8px !important; font-size: 15px !important;
    color: #1E3A5F !important; padding: 10px 14px !important; min-height: 44px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #2563EB !important; box-shadow: 0 0 0 3px rgba(37,99,235,0.15) !important;
}
.stTextInput > div > div > input::placeholder { color: #94A3B8 !important; font-size: 14px !important; }
.stRadio > div { gap: 8px !important; }
.stRadio > div > label {
    background: #F1F5F9 !important; border: 2px solid #CBD5E1 !important;
    border-radius: 8px !important; padding: 8px 16px !important;
    font-size: 14px !important; font-weight: 600 !important; color: #475569 !important; cursor: pointer !important;
}
.stRadio > div > label:has(input:checked) {
    background: #EFF6FF !important; border-color: #2563EB !important; color: #1D4ED8 !important;
}
.kpi-wrap {
    background: white; border-radius: 16px; padding: 24px 22px 20px 22px;
    border-left: 5px solid; box-shadow: 0 4px 16px rgba(0,0,0,0.07); height: 100%;
}
.kpi-label { font-size: 13px; color: #64748B; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 10px; }
.kpi-value { font-size: 36px; font-weight: 900; line-height: 1; letter-spacing: -0.02em; }
.kpi-sub { font-size: 13px; color: #94A3B8; margin-top: 8px; }
.filter-card {
    background: #F0F5FF; border-radius: 12px; padding: 18px 22px 14px 22px;
    border: 1.5px solid #BFDBFE; margin-bottom: 16px;
}
.section-card {
    background: white; border-radius: 16px; padding: 24px 26px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 16px;
}
.section-title {
    font-size: 17px; font-weight: 700; color: #0F172A; margin-bottom: 18px;
    padding-bottom: 12px; border-bottom: 2px solid #EFF6FF; letter-spacing: -0.01em;
}
/* 기본 Streamlit 탭 숨김 → 커스텀 탭으로 대체 */
.stTabs [data-baseweb="tab-list"] { display: none !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 0 !important; }

/* ── 커스텀 드래그 탭 바 ── */
.custom-tab-bar {
    display: flex; gap: 8px; padding: 0 0 16px 0;
    flex-wrap: nowrap; align-items: center; user-select: none;
}
.custom-tab {
    display: flex; align-items: center; gap: 7px;
    padding: 10px 22px; border-radius: 10px;
    font-size: 15px; font-weight: 600; color: #475569;
    background: white; border: 1.5px solid #CBD5E1;
    cursor: grab; transition: all 0.15s; white-space: nowrap;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.custom-tab:hover { border-color: #93C5FD; color: #1D4ED8; box-shadow: 0 3px 10px rgba(29,78,216,0.12); }
.custom-tab.active { background: #1D4ED8 !important; color: white !important; border-color: #1D4ED8 !important; box-shadow: 0 4px 14px rgba(29,78,216,0.35); }
.custom-tab.dragging { opacity: 0.4; cursor: grabbing; }
.custom-tab.drag-over { border-color: #60A5FA !important; background: #EFF6FF !important; color: #1D4ED8 !important; transform: scale(1.05); }
.report-box {
    background: linear-gradient(135deg, #EFF6FF 0%, #F0FDF4 100%);
    border-radius: 12px; padding: 22px 24px; border: 1px solid #BFDBFE;
    line-height: 2.0; color: #1E3A5F; font-size: 15px;
}
.report-box strong { color: #1D4ED8; }
.report-tag-warn { background:#FEF9C3; color:#92400E; padding:3px 10px; border-radius:99px; font-size:12px; font-weight:700; display:inline-block; margin-right:4px; }
.report-tag-ok   { background:#D1FAE5; color:#065F46; padding:3px 10px; border-radius:99px; font-size:12px; font-weight:700; display:inline-block; margin-right:4px; }
.report-tag-bad  { background:#FEE2E2; color:#991B1B; padding:3px 10px; border-radius:99px; font-size:12px; font-weight:700; display:inline-block; margin-right:4px; }

/* ── 분석 카드 (탭4 전용) ── */
.analysis-card {
    background: linear-gradient(135deg, #EFF6FF 0%, #F8FAFF 100%);
    border-radius: 16px; padding: 26px 28px;
    border: 1.5px solid #BFDBFE;
    box-shadow: 0 2px 12px rgba(29,78,216,0.08);
    margin-top: 4px;
}
.analysis-title {
    font-size: 16px; font-weight: 800; color: #1E3A5F;
    margin-bottom: 16px; padding-bottom: 10px;
    border-bottom: 2px solid #DBEAFE;
    letter-spacing: -0.01em;
}
.an-section { margin-bottom: 14px; }
.an-section-title { font-size: 13px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px; }
.an-row {
    display: flex; align-items: flex-start; gap: 10px;
    padding: 8px 12px; border-radius: 8px;
    background: white; margin-bottom: 6px;
    border: 1px solid #E2E8F0; font-size: 14px; line-height: 1.7;
}
.an-badge {
    flex-shrink: 0; padding: 2px 10px; border-radius: 99px;
    font-size: 12px; font-weight: 700; white-space: nowrap; margin-top: 2px;
}
.badge-danger { background:#FEE2E2; color:#991B1B; }
.badge-warn   { background:#FEF9C3; color:#92400E; }
.badge-ok     { background:#D1FAE5; color:#065F46; }
.badge-over   { background:#EDE9FE; color:#5B21B6; }
.an-summary {
    background: white; border-radius: 10px; padding: 14px 18px;
    border: 1px solid #DBEAFE; font-size: 14px; line-height: 2.0;
    color: #1E3A5F;
}
.highlight-blue { color: #1D4ED8; font-weight: 700; }
.highlight-red  { color: #DC2626; font-weight: 700; }
.highlight-green{ color: #059669; font-weight: 700; }
.highlight-warn { color: #D97706; font-weight: 700; }

.stDownloadButton > button {
    background: #1D4ED8 !important; color: white !important;
    border: none !important; border-radius: 8px !important;
    font-size: 15px !important; font-weight: 600 !important; padding: 10px 24px !important;
}
.stDownloadButton > button:hover { background: #1E40AF !important; }
.stAlert { font-size: 15px !important; }
p { font-size: 15px !important; }
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
        dates  = ["2025-06","2025-07","2025-08","2025-10",
                  "2025-11","2025-12","2026-01","2026-02"]
        brands = ["데스커","일룸","퍼시스","시디즈"]
        series_list = ["ACCESSORY","IBLE","SPOON","SODA",
                       "T60","RINGO","T20","GX","AROUND","PLT"]
        supply_pool = ['시디즈제품','의자양지상품','베트남제품']
        rows, a_rows = [], []
        for ym in dates:
            for b in brands:
                for s in series_list:
                    sup = np.random.choice(supply_pool + [np.nan], p=[0.28,0.28,0.28,0.16])
                    rows.append({'ym':ym,'brand':b,'series':s,
                                 'combo':f"{s[:6]}-{b[:2]}",'name':f"{b} {s}",
                                 'forecast':int(np.random.randint(200,4000)),'supply':sup})
                    a_rows.append({'ym':ym,'combo':f"{s[:6]}-{b[:2]}",
                                   'actual':max(0,int(np.random.normal(1800,900)))})
        f = pd.DataFrame(rows)
        a = pd.DataFrame(a_rows)

    for col in ['ym','series','brand','combo','supply','name']:
        if col not in f.columns: f[col] = np.nan
    for col in ['ym','combo','actual']:
        if col not in a.columns: a[col] = np.nan

    for df in [f, a]:
        for col in df.select_dtypes(include=['object','string']).columns:
            df[col] = df[col].astype(str).str.strip()
        if 'supply' in df.columns:
            df['supply'] = df['supply'].replace({'':'<NA>','nan':'<NA>'})

    f = f.dropna(subset=['series','brand','combo'])
    f = f[~f['series'].astype(str).str.isnumeric()]
    f = f[f['series'].astype(str).str.len() >= 2]

    brand_values = set(f['brand'].dropna().astype(str).str.strip().unique())
    f = f[~f['series'].astype(str).isin(brand_values)]

    return f, a

f_df, a_df = load_data()

mg_all = pd.merge(f_df, a_df[["ym","combo","actual"]], on=["ym","combo"], how="left")
mg_all["actual"]    = pd.to_numeric(mg_all["actual"],   errors='coerce').fillna(0).astype(int)
mg_all["forecast"]  = pd.to_numeric(mg_all["forecast"], errors='coerce').fillna(0).astype(int)
mg_all["차이"]       = mg_all["actual"] - mg_all["forecast"]
mg_all["오차량"]     = mg_all["차이"].abs()
mg_all["달성률(%)"]  = np.where(mg_all["forecast"]>0,
                                (mg_all["actual"]/mg_all["forecast"]*100).round(1), 0)
try:    mg_all["ym_dt"] = pd.to_datetime(mg_all["ym"]+"-01")
except: mg_all["ym_dt"] = mg_all["ym"]


# ══════════════════════════════════════════════
#  유틸
# ══════════════════════════════════════════════
def apply_filters(df, ym=None, brands=None, supply=None):
    d = df.copy()
    if ym:      d = d[d["ym"]==ym]
    if brands:  d = d[d["brand"].isin(brands)]
    if supply and supply != "전체":
        d = d[d["supply"]==supply]
    return d

def fmt_int(v): return f"{int(v):,}"
def fmt_pct(v): return f"{v:.1f}%"


# ══════════════════════════════════════════════
#  사이드바
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 4px 4px 4px">
        <div style="font-size:22px;font-weight:900;color:#F8FAFC;letter-spacing:-0.02em;">📦 수요예측</div>
        <div style="font-size:12px;color:#64748B;margin-top:4px;">Demand Forecast Dashboard</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")

    ym_options = sorted(mg_all["ym"].unique(), reverse=True)
    sel_ym = st.selectbox("📅 기준 년월", ym_options)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    all_brands = sorted(mg_all["brand"].unique())
    sel_brands = st.multiselect("🏷️ 브랜드", all_brands, default=all_brands)
    if not sel_brands: sel_brands = all_brands

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    supply_vals = sorted([v for v in mg_all["supply"].unique()
                          if v not in ("<NA>","nan","","None")])
    sel_supply = st.selectbox("🏭 공급단", ["전체"]+supply_vals)

    st.markdown("---")
    st.markdown(f"""
    <div style="font-size:14px;color:#94A3B8;line-height:2.2;">
        📆 기간: <b style="color:#CBD5E1">{mg_all['ym'].min()} ~ {mg_all['ym'].max()}</b><br>
        🔢 총 콤보 수: <b style="color:#CBD5E1">{mg_all['combo'].nunique():,}개</b>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  드래그앤드롭 탭 구현
# ══════════════════════════════════════════════
import streamlit.components.v1 as components

# Streamlit 기본 탭을 숨기고 커스텀 드래그 가능한 탭 바를 주입
components.html("""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:transparent;">
<script>
(function () {
    var RETRY = 0;

    function applyActive(btn) {
        btn._isActive = true;
        btn.style.background   = '#1D4ED8';
        btn.style.color        = 'white';
        btn.style.borderColor  = '#1D4ED8';
        btn.style.boxShadow    = '0 4px 14px rgba(29,78,216,0.35)';
        btn.style.cursor       = 'grab';
    }
    function applyInactive(btn) {
        btn._isActive = false;
        btn.style.background   = 'white';
        btn.style.color        = '#475569';
        btn.style.borderColor  = '#CBD5E1';
        btn.style.boxShadow    = '0 1px 4px rgba(0,0,0,0.06)';
        btn.style.cursor       = 'grab';
    }

    function init() {
        var doc = window.parent.document;

        // 이미 삽입됐으면 스킵
        if (doc.getElementById('__drag_tab_bar__')) return;

        var tabList = doc.querySelector('[data-baseweb="tab-list"]');
        if (!tabList) {
            if (RETRY++ < 20) setTimeout(init, 300);
            return;
        }

        var stTabs = Array.from(tabList.querySelectorAll('[role="tab"]'));
        if (stTabs.length === 0) {
            if (RETRY++ < 20) setTimeout(init, 300);
            return;
        }

        // 원래 탭 목록 숨기기
        tabList.style.display = 'none';

        // ── 커스텀 탭 바 DOM 생성 ──
        var bar = doc.createElement('div');
        bar.id = '__drag_tab_bar__';
        bar.style.cssText = 'display:flex;gap:8px;padding:0 0 14px 0;' +
                            'align-items:center;user-select:none;flex-wrap:nowrap;';

        var dragSrc = null;

        stTabs.forEach(function (stTab, idx) {
            var btn      = doc.createElement('div');
            btn._tabIdx  = idx;         // 원래 Streamlit 탭 인덱스 고정
            btn.draggable = true;
            btn.textContent = stTab.textContent.trim();
            btn.style.cssText =
                'padding:10px 22px;border-radius:10px;font-size:15px;font-weight:600;' +
                'border:1.5px solid #CBD5E1;transition:all 0.15s;white-space:nowrap;' +
                "font-family:'Noto Sans KR',sans-serif;" +
                'box-shadow:0 1px 4px rgba(0,0,0,0.06);';

            if (stTab.getAttribute('aria-selected') === 'true') applyActive(btn);
            else applyInactive(btn);

            // ── 클릭: 원래 탭 트리거 ──
            btn.addEventListener('click', function () {
                Array.from(bar.children).forEach(applyInactive);
                applyActive(btn);
                stTabs[btn._tabIdx].click();
            });

            // ── 드래그 이벤트 ──
            btn.addEventListener('dragstart', function (e) {
                dragSrc = btn;
                e.dataTransfer.effectAllowed = 'move';
                setTimeout(function () { btn.style.opacity = '0.35'; }, 0);
            });

            btn.addEventListener('dragend', function () {
                btn.style.opacity   = '1';
                btn.style.transform = '';
                Array.from(bar.children).forEach(function (b) {
                    b.style.transform   = '';
                    b.style.borderColor = b._isActive ? '#1D4ED8' : '#CBD5E1';
                    b.style.background  = b._isActive ? '#1D4ED8' : 'white';
                    b.style.color       = b._isActive ? 'white'   : '#475569';
                });
            });

            btn.addEventListener('dragover', function (e) {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                if (btn !== dragSrc) {
                    btn.style.transform   = 'scale(1.06)';
                    btn.style.borderColor = '#60A5FA';
                    btn.style.background  = btn._isActive ? '#1553b0' : '#EFF6FF';
                    btn.style.color       = btn._isActive ? 'white'   : '#1D4ED8';
                }
            });

            btn.addEventListener('dragleave', function () {
                btn.style.transform = '';
                if (btn._isActive) applyActive(btn);
                else               applyInactive(btn);
            });

            btn.addEventListener('drop', function (e) {
                e.preventDefault();
                if (!dragSrc || dragSrc === btn) return;

                // DOM 순서만 바꿈 (각 버튼의 _tabIdx는 그대로 유지)
                var all  = Array.from(bar.children);
                var from = all.indexOf(dragSrc);
                var to   = all.indexOf(btn);
                if (from < to) bar.insertBefore(dragSrc, btn.nextSibling);
                else           bar.insertBefore(dragSrc, btn);

                btn.style.transform = '';
                if (btn._isActive) applyActive(btn);
                else               applyInactive(btn);
            });

            bar.appendChild(btn);
        });

        // Streamlit 탭 컨테이너 바로 앞에 삽입
        tabList.parentNode.insertBefore(bar, tabList.nextSibling);
    }

    // Streamlit 재렌더링 후 탭 바가 사라지면 재삽입
    var mo = new MutationObserver(function () {
        var doc = window.parent.document;
        if (!doc.getElementById('__drag_tab_bar__')) {
            RETRY = 0;
            init();
        }
    });
    mo.observe(window.parent.document.body, { childList: true, subtree: true });

    init();
})();
</script>
</body>
</html>
""", height=0, scrolling=False)

tab1, tab2, tab3, tab4 = st.tabs([
    "  📊 개요  ","  📈 월별 추이  ","  🔎 시리즈 분석  ","  📋 상세 데이터  "
])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  탭1: 개요
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab1:
    df_ov = apply_filters(mg_all, ym=sel_ym, brands=sel_brands, supply=sel_supply)
    if df_ov.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
        st.stop()

    t_f = int(df_ov["forecast"].sum()); t_a = int(df_ov["actual"].sum())
    t_d = t_a - t_f; t_r = round(t_a/t_f*100,1) if t_f>0 else 0.0
    month_label = sel_ym.replace("-","년 ")+"월"

    c1,c2,c3,c4 = st.columns(4)
    kpi_list = [
        (c1,"#3B82F6","예측 수요",   fmt_int(t_f), f"{month_label} 예측 합계"),
        (c2,"#10B981","실 수주",     fmt_int(t_a), f"{month_label} 실수주 합계"),
        (c3,"#F59E0B" if t_d>=0 else "#EF4444","예측 오차",
             ("▲ +" if t_d>=0 else "▼ ")+fmt_int(abs(t_d)), "실수주 − 예측"),
        (c4,"#8B5CF6","달성률",      fmt_pct(t_r), "실수주 ÷ 예측 × 100"),
    ]
    for col,color,label,value,sub in kpi_list:
        with col:
            st.markdown(f"""<div class="kpi-wrap" style="border-left-color:{color}">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value" style="color:{color}">{value}</div>
                <div class="kpi-sub">{sub}</div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    brand_agg = df_ov.groupby("brand").agg(
        forecast=("forecast","sum"), actual=("actual","sum")).reset_index()
    brand_agg["달성률"] = np.where(brand_agg["forecast"]>0,
        (brand_agg["actual"]/brand_agg["forecast"]*100).round(1), 0)

    col_l, col_r = st.columns([3,2])
    with col_l:
        st.markdown('<div class="section-card"><div class="section-title">브랜드별 예측 vs 실수주</div>', unsafe_allow_html=True)
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(name="예측 수요", x=brand_agg["brand"], y=brand_agg["forecast"],
            marker_color="#93C5FD", text=brand_agg["forecast"].apply(fmt_int), textposition="outside"))
        fig_bar.add_trace(go.Bar(name="실 수주", x=brand_agg["brand"], y=brand_agg["actual"],
            marker_color="#34D399", text=brand_agg["actual"].apply(fmt_int), textposition="outside"))
        fig_bar.update_layout(barmode="group", template="plotly_white", height=320,
            margin=dict(l=0,r=0,t=10,b=0), font=dict(size=14),
            legend=dict(orientation="h",yanchor="bottom",y=1.02,font=dict(size=13)),
            yaxis=dict(showgrid=True,gridcolor="#F3F4F6"), xaxis=dict(tickfont=dict(size=14)))
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="section-card"><div class="section-title">브랜드별 달성률</div>', unsafe_allow_html=True)
        bar_colors = ["#22C55E" if v>=95 else "#F59E0B" if v>=80 else "#EF4444" for v in brand_agg["달성률"]]
        fig_rate = go.Figure(go.Bar(x=brand_agg["달성률"], y=brand_agg["brand"], orientation="h",
            marker_color=bar_colors, text=[f"{v:.1f}%" for v in brand_agg["달성률"]],
            textposition="outside"))
        fig_rate.add_vline(x=100, line_dash="dot", line_color="#94A3B8",
                           annotation_text="100%", annotation_font_size=13)
        fig_rate.update_layout(template="plotly_white", height=320,
            margin=dict(l=0,r=50,t=10,b=0), font=dict(size=14),
            xaxis=dict(range=[0,max(135,brand_agg["달성률"].max()+20)]),
            yaxis=dict(tickfont=dict(size=15,color="#0F172A")))
        st.plotly_chart(fig_rate, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    col_pie, col_rep = st.columns([1,2])
    with col_pie:
        st.markdown('<div class="section-card"><div class="section-title">공급단별 예측 비중</div>', unsafe_allow_html=True)
        sup_agg = (df_ov[~df_ov["supply"].isin(["<NA>","nan","","None"])]
                   .groupby("supply")["forecast"].sum().reset_index())
        if not sup_agg.empty:
            fig_pie = go.Figure(go.Pie(labels=sup_agg["supply"], values=sup_agg["forecast"],
                hole=0.5, textinfo="label+percent", textfont=dict(size=14),
                marker=dict(colors=["#60A5FA","#34D399","#FBBF24","#A78BFA"])))
            fig_pie.update_layout(height=290, margin=dict(l=0,r=0,t=10,b=0),
                showlegend=True, legend=dict(font=dict(size=13)))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("공급단 데이터 없음")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_rep:
        st.markdown('<div class="section-card"><div class="section-title">자동 분석 요약</div>', unsafe_allow_html=True)
        sr_agg2 = df_ov.groupby("series").agg(f=("forecast","sum"),a=("actual","sum")).reset_index()
        sr_agg2["달성률"] = np.where(sr_agg2["f"]>0,(sr_agg2["a"]/sr_agg2["f"]*100).round(1),0)
        sr_agg2["오차량"] = (sr_agg2["a"]-sr_agg2["f"]).abs()
        top_err  = sr_agg2.sort_values("오차량",ascending=False).head(3)
        under_s  = sr_agg2[sr_agg2["달성률"]<90].sort_values("달성률").head(3)
        over_s   = sr_agg2[sr_agg2["달성률"]>110].sort_values("달성률",ascending=False).head(3)
        color_r  = "#10B981" if t_r>=100 else "#EF4444"
        trend_w  = "초과달성" if t_r>=100 else "미달"
        html_r = f"""<div class="report-box">
            <b>{month_label}</b> 전체 달성률 <b style="color:{color_r};font-size:16px">{fmt_pct(t_r)}</b>
            — 예측 대비 <b style="color:{color_r}">{trend_w}</b> 상태입니다.<br><br>"""
        if not top_err.empty:
            html_r += "<b>📍 오차 상위 시리즈</b><br>"
            for _, row in top_err.iterrows():
                if row["달성률"]<90:    tag = '<span class="report-tag-bad">과소예측</span>'
                elif row["달성률"]>110: tag = '<span class="report-tag-warn">과대예측</span>'
                else:                  tag = '<span class="report-tag-ok">양호</span>'
                html_r += f"&nbsp;&nbsp;{tag} <b>{row['series']}</b> 달성률 {row['달성률']:.1f}% (오차 {fmt_int(row['오차량'])}건)<br>"
        if not under_s.empty:
            html_r += f"<br><b>⚠️ 과소예측 (&lt;90%)</b>: {', '.join(under_s['series'].tolist())}<br>"
        if not over_s.empty:
            html_r += f"<b>🔺 과대예측 (&gt;110%)</b>: {', '.join(over_s['series'].tolist())}<br>"
        html_r += """<br><b>💡 권장 조치</b><br>
            &nbsp;&nbsp;① 오차 상위 품목의 재고·채널 현황 즉시 점검<br>
            &nbsp;&nbsp;② 과소예측 품목은 반품·납기 원인 확인<br>
            &nbsp;&nbsp;③ 다음 예측 주기에 최근 3개월 추세 가중치 반영</div>"""
        st.markdown(html_r, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  탭2: 월별 추이
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab2:
    df_ts = apply_filters(mg_all, brands=sel_brands, supply=sel_supply)
    if df_ts.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    else:
        st.markdown('<div class="filter-card">', unsafe_allow_html=True)
        fc1, fc2 = st.columns([1,4])
        with fc1:
            ts_mode = st.radio("📐 집계 기준", ["브랜드별","시리즈별"], horizontal=False)
        with fc2:
            group_col = "brand" if ts_mode=="브랜드별" else "series"
            choices   = sorted(df_ts[group_col].unique())
            default_c = choices[:4] if len(choices)>4 else choices
            ts_sel    = st.multiselect(f"📌 표시할 {ts_mode[:-1]} 선택", choices, default=default_c)
        st.markdown('</div>', unsafe_allow_html=True)

        if not ts_sel:
            st.info(f"위에서 {ts_mode[:-1]}을 하나 이상 선택하세요.")
        else:
            agg_ts = (df_ts[df_ts[group_col].isin(ts_sel)]
                      .groupby(["ym_dt",group_col])
                      .agg(forecast=("forecast","sum"), actual=("actual","sum"))
                      .reset_index().sort_values("ym_dt"))

            PAL_F = ["#93C5FD","#86EFAC","#FDE68A","#DDD6FE","#FBCFE8"]
            PAL_A = ["#1D4ED8","#15803D","#B45309","#6D28D9","#BE185D"]

            st.markdown('<div class="section-card"><div class="section-title">월별 예측 vs 실수주 추이</div>', unsafe_allow_html=True)
            fig_ts = go.Figure()
            for i, item in enumerate(ts_sel):
                d = agg_ts[agg_ts[group_col]==item].sort_values("ym_dt")
                fig_ts.add_trace(go.Scatter(x=d["ym_dt"], y=d["forecast"], name=f"{item} 예측",
                    mode="lines+markers", line=dict(dash="dot",color=PAL_F[i%len(PAL_F)],width=2), marker=dict(size=7)))
                fig_ts.add_trace(go.Scatter(x=d["ym_dt"], y=d["actual"], name=f"{item} 실적",
                    mode="lines+markers", line=dict(color=PAL_A[i%len(PAL_A)],width=2.5), marker=dict(size=8)))
            fig_ts.update_layout(template="plotly_white", height=380, margin=dict(l=0,r=0,t=10,b=0),
                font=dict(size=14), xaxis=dict(title="기준월",showgrid=False),
                yaxis=dict(title="수량",showgrid=True,gridcolor="#F3F4F6"),
                legend=dict(orientation="h",yanchor="bottom",y=1.02,font=dict(size=13)),
                hovermode="x unified")
            st.plotly_chart(fig_ts, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-card"><div class="section-title">월별 달성률 추이</div>', unsafe_allow_html=True)
            rate_ts = agg_ts.copy()
            rate_ts["달성률"] = np.where(rate_ts["forecast"]>0,
                (rate_ts["actual"]/rate_ts["forecast"]*100).round(1), 0)
            fig_rt = go.Figure()
            for i, item in enumerate(ts_sel):
                d = rate_ts[rate_ts[group_col]==item].sort_values("ym_dt")
                fig_rt.add_trace(go.Scatter(x=d["ym_dt"], y=d["달성률"], name=item,
                    mode="lines+markers", line=dict(color=PAL_A[i%len(PAL_A)],width=2.5), marker=dict(size=8)))
            fig_rt.add_hline(y=100, line_dash="dot", line_color="#94A3B8",
                             annotation_text="100% 기준", annotation_font_size=13)
            fig_rt.update_layout(template="plotly_white", height=280, margin=dict(l=0,r=0,t=10,b=0),
                font=dict(size=14), xaxis=dict(title="기준월",showgrid=False),
                yaxis=dict(title="달성률 (%)",showgrid=True,gridcolor="#F3F4F6"),
                legend=dict(orientation="h",yanchor="bottom",y=1.02,font=dict(size=13)),
                hovermode="x unified")
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
        st.markdown('<div class="filter-card">', unsafe_allow_html=True)
        sf1, sf2, sf3 = st.columns([1,1,2])
        with sf1: top_n = st.slider("📊 Top N", 5, 30, 20, key="sr_topn")
        with sf2:
            sr_sort = st.selectbox("🔃 정렬 기준", [
                "차이량(실-예측) 큰 순","예측수요 큰 순","실수주 큰 순","달성률 높은 순","달성률 낮은 순"], key="sr_sort")
        with sf3:
            st.markdown(f"<div style='padding-top:36px;font-size:15px;color:#1D4ED8;font-weight:600'>"
                        f"상위 <b style='font-size:20px'>{top_n}</b>개 시리즈 · 정렬: <b>{sr_sort}</b></div>",
                        unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        sr_agg = df_sr.groupby("series").agg(forecast=("forecast","sum"),actual=("actual","sum")).reset_index()
        sr_agg["차이량"]    = sr_agg["actual"] - sr_agg["forecast"]
        sr_agg["오차량"]    = sr_agg["차이량"].abs()
        sr_agg["달성률(%)"] = np.where(sr_agg["forecast"]>0,(sr_agg["actual"]/sr_agg["forecast"]*100).round(1),0)

        sr_sort_map = {
            "차이량(실-예측) 큰 순":("오차량",False), "예측수요 큰 순":("forecast",False),
            "실수주 큰 순":("actual",False), "달성률 높은 순":("달성률(%)",False), "달성률 낮은 순":("달성률(%)",True)
        }
        ss_col, ss_asc = sr_sort_map[sr_sort]
        sr_top  = sr_agg.sort_values(ss_col, ascending=ss_asc).head(top_n)
        sr_plot = sr_top.sort_values("forecast", ascending=True)
        chart_h = max(420, top_n*32)

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown(f'<div class="section-card"><div class="section-title">예측수요 / 실수주 / 차이량 (Top {top_n})</div>', unsafe_allow_html=True)
            fig_3bar = go.Figure()
            fig_3bar.add_trace(go.Bar(y=sr_plot["series"], x=sr_plot["forecast"], name="예측수요",
                orientation="h", marker_color="#5B8DEF",
                text=sr_plot["forecast"].apply(fmt_int), textposition="outside", textfont=dict(size=11)))
            fig_3bar.add_trace(go.Bar(y=sr_plot["series"], x=sr_plot["actual"], name="실수주",
                orientation="h", marker_color="#34D399",
                text=sr_plot["actual"].apply(fmt_int), textposition="outside", textfont=dict(size=11)))
            diff_colors = ["#60A5FA" if v>=0 else "#F87171" for v in sr_plot["차이량"]]
            fig_3bar.add_trace(go.Bar(y=sr_plot["series"], x=sr_plot["차이량"], name="차이량(실-예측)",
                orientation="h", marker_color=diff_colors,
                text=[f"+{fmt_int(v)}" if v>=0 else fmt_int(v) for v in sr_plot["차이량"]],
                textposition="outside", textfont=dict(size=11)))
            fig_3bar.update_layout(barmode="group", template="plotly_white", height=chart_h,
                margin=dict(l=0,r=80,t=10,b=0), font=dict(size=13),
                xaxis=dict(showgrid=True,gridcolor="#F3F4F6",zeroline=True,zerolinecolor="#CBD5E1"),
                yaxis=dict(tickfont=dict(size=13,color="#1F2937")),
                legend=dict(orientation="h",yanchor="bottom",y=1.01,font=dict(size=12)))
            st.plotly_chart(fig_3bar, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_r:
            st.markdown(f'<div class="section-card"><div class="section-title">달성률 (Top {top_n})</div>', unsafe_allow_html=True)
            rate_colors = ["#34D399" if v>=100 else "#FBBF24" if v>=90 else "#F87171" for v in sr_plot["달성률(%)"]]
            fig_rate = go.Figure(go.Bar(y=sr_plot["series"], x=sr_plot["달성률(%)"],
                orientation="h", marker_color=rate_colors,
                text=[f"{v:.1f}%" for v in sr_plot["달성률(%)"]],
                textposition="outside", textfont=dict(size=12)))
            fig_rate.add_vline(x=100, line_dash="dash", line_color="#94A3B8",
                               annotation_text="100%", annotation_position="top")
            x_max = max(150, float(sr_plot["달성률(%)"].max())+30)
            fig_rate.update_layout(template="plotly_white", height=chart_h,
                margin=dict(l=0,r=70,t=10,b=0), font=dict(size=13),
                xaxis=dict(range=[0,x_max],showgrid=True,gridcolor="#F3F4F6",ticksuffix="%"),
                yaxis=dict(tickfont=dict(size=13,color="#1F2937")))
            st.plotly_chart(fig_rate, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        sum_col, tbl_col = st.columns([1,3])
        with sum_col:
            st.markdown('<div class="section-card"><div class="section-title">달성률 구간 분포</div>', unsafe_allow_html=True)
            bins    = [0,70,90,100,110,9999]
            blabels = ["70% 미만","70~90%","90~100%","100~110%","110% 초과"]
            sr_agg["구간"] = pd.cut(sr_agg["달성률(%)"], bins=bins, labels=blabels, right=False)
            bin_cnt = sr_agg["구간"].value_counts().reindex(blabels,fill_value=0).reset_index()
            bin_cnt.columns = ["구간","건수"]
            fig_bin = go.Figure(go.Bar(x=bin_cnt["구간"], y=bin_cnt["건수"],
                marker_color=["#EF4444","#F87171","#FBBF24","#34D399","#059669"],
                text=bin_cnt["건수"], textposition="outside", textfont=dict(size=14)))
            fig_bin.update_layout(template="plotly_white", height=260, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig_bin, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tbl_col:
            st.markdown('<div class="section-card"><div class="section-title">시리즈별 상세 수치</div>', unsafe_allow_html=True)
            disp = sr_top.rename(columns={"series":"시리즈","forecast":"예측수요","actual":"실수주",
                "차이량":"차이량(실-예측)","오차량":"오차량(절대)","달성률(%)":"달성률(%)"})[
                ["시리즈","예측수요","실수주","차이량(실-예측)","달성률(%)"]].copy()
            def color_rate(v):
                if isinstance(v,(int,float)):
                    if v>=100: return "background:#D1FAE5;color:#065F46;font-weight:700"
                    if v>=90:  return "background:#FEF9C3;color:#92400E;font-weight:700"
                    return "background:#FEE2E2;color:#991B1B;font-weight:700"
                return ""
            def color_diff(v):
                if isinstance(v,(int,float)):
                    if v>0: return "color:#059669;font-weight:600"
                    if v<0: return "color:#DC2626;font-weight:600"
                return ""
            styled = (disp.style
                .format({"예측수요":"{:,.0f}","실수주":"{:,.0f}",
                         "차이량(실-예측)":"{:+,.0f}","달성률(%)":"{:.1f}%"})
                .applymap(color_rate, subset=["달성률(%)"])
                .applymap(color_diff, subset=["차이량(실-예측)"]))
            st.dataframe(styled, use_container_width=True, height=280)
            st.markdown('</div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  탭4: 상세 데이터  ★ 하단 동적 분석 추가
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab4:
    df_det = apply_filters(mg_all, ym=sel_ym, brands=sel_brands, supply=sel_supply)

    if df_det.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    else:
        # ── 인라인 필터
        st.markdown('<div class="filter-card">', unsafe_allow_html=True)
        dc1, dc2, dc3 = st.columns([2,2,1])
        with dc1:
            search = st.text_input("🔍 검색", placeholder="콤보코드 / 시리즈명 / 품목명...")
        with dc2:
            sort_by = st.selectbox("🔃 정렬 기준", [
                "오차량 큰 순","예측수요 큰 순","실수주 큰 순","달성률 높은 순","달성률 낮은 순"])
        with dc3:
            show_n = st.slider("📋 표시 행 수", 10, 300, 50)
        st.markdown('</div>', unsafe_allow_html=True)

        sort_map = {
            "오차량 큰 순":("오차량",False), "예측수요 큰 순":("forecast",False),
            "실수주 큰 순":("actual",False), "달성률 높은 순":("달성률(%)",False), "달성률 낮은 순":("달성률(%)",True)
        }
        sc, sa = sort_map[sort_by]
        df_det2 = df_det.sort_values(sc, ascending=sa)

        if search:
            mask = (df_det2["combo"].str.contains(search, case=False, na=False) |
                    df_det2["series"].str.contains(search, case=False, na=False) |
                    df_det2["name"].str.contains(search, case=False, na=False))
            df_det2 = df_det2[mask]

        total_rows = len(df_det2)
        st.markdown(f"<div style='font-size:14px;color:#64748B;margin-bottom:8px'>"
                    f"조건에 맞는 데이터 <b style='color:#1D4ED8'>{total_rows:,}건</b> 중 "
                    f"상위 <b style='color:#1D4ED8'>{min(show_n,total_rows)}건</b> 표시</div>",
                    unsafe_allow_html=True)

        cols_show = ["ym","brand","series","combo","name","supply","forecast","actual","차이","달성률(%)"]
        display_det = df_det2[cols_show].head(show_n).copy()
        display_det["supply"] = display_det["supply"].replace({"<NA>":"—"})

        styled_det = (display_det.style
            .format({"forecast":"{:,.0f}","actual":"{:,.0f}","차이":"{:,.0f}","달성률(%)":"{:.1f}%"})
            .applymap(lambda v: "background:#FEE2E2;color:#991B1B"
                      if isinstance(v,(int,float)) and v<0 else "", subset=["차이"]))
        st.dataframe(styled_det, use_container_width=True, height=400)

        csv_data = df_det2[cols_show].to_csv(index=False, encoding="utf-8-sig")
        st.download_button("⬇️  CSV 다운로드", data=csv_data,
                           file_name=f"forecast_detail_{sel_ym}.csv", mime="text/csv")

        # ══════════════════════════════════════════
        #  ★ 동적 분석 카드 (필터/검색 결과 기반)
        # ══════════════════════════════════════════
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

        if df_det2.empty:
            st.info("검색·필터 조건에 맞는 데이터가 없어 분석을 생성할 수 없습니다.")
        else:
            # ── 분석용 집계
            t_fc   = int(df_det2["forecast"].sum())
            t_ac   = int(df_det2["actual"].sum())
            t_diff = t_ac - t_fc
            t_rate = round(t_ac / t_fc * 100, 1) if t_fc > 0 else 0.0
            n_rows = len(df_det2)

            # 달성률 구간 분류
            over110  = df_det2[df_det2["달성률(%)"] >  110]
            ok90_110 = df_det2[(df_det2["달성률(%)"] >= 90) & (df_det2["달성률(%)"] <= 110)]
            under90  = df_det2[df_det2["달성률(%)"] <  90]
            zero_fc  = df_det2[df_det2["forecast"]  == 0]

            # 오차 상위 5개
            top5_err  = df_det2.nlargest(5, "오차량")[["series","combo","name","forecast","actual","차이","달성률(%)"]]
            # 예측 초과 상위 3 (실 > 예측)
            top3_over = (df_det2[df_det2["차이"] > 0]
                         .nlargest(3, "차이")[["series","combo","name","forecast","actual","차이"]])
            # 예측 미달 상위 3 (실 < 예측)
            top3_under= (df_det2[df_det2["차이"] < 0]
                         .nsmallest(3, "차이")[["series","combo","name","forecast","actual","차이"]])

            # 브랜드별 요약
            brand_sum = (df_det2.groupby("brand")
                         .agg(forecast=("forecast","sum"), actual=("actual","sum"))
                         .reset_index())
            brand_sum["rate"] = np.where(brand_sum["forecast"]>0,
                                         (brand_sum["actual"]/brand_sum["forecast"]*100).round(1), 0)
            best_brand  = brand_sum.loc[brand_sum["rate"].idxmax()]  if not brand_sum.empty else None
            worst_brand = brand_sum.loc[brand_sum["rate"].idxmin()]  if not brand_sum.empty else None

            # 시리즈별 요약
            sr_sum = (df_det2.groupby("series")
                      .agg(forecast=("forecast","sum"), actual=("actual","sum"))
                      .reset_index())
            sr_sum["rate"] = np.where(sr_sum["forecast"]>0,
                                      (sr_sum["actual"]/sr_sum["forecast"]*100).round(1), 0)

            month_label2 = sel_ym.replace("-","년 ")+"월"
            filter_desc  = f"{month_label2}"
            if sel_supply != "전체": filter_desc += f" · {sel_supply}"
            if search: filter_desc += f" · 검색: '{search}'"
            sort_desc = sort_by

            # ── 전체 요약 한 줄
            if t_rate >= 100:
                rate_color = "highlight-green"; rate_word = "초과달성"
            elif t_rate >= 90:
                rate_color = "highlight-warn";  rate_word = "근접"
            else:
                rate_color = "highlight-red";   rate_word = "미달"

            diff_sign = "+" if t_diff >= 0 else ""
            diff_color = "highlight-green" if t_diff >= 0 else "highlight-red"

            summary_html = f"""
            <div class="an-summary">
                <b>{filter_desc}</b> 기준 <b>{n_rows:,}건</b> 품목 분석 결과,
                예측 수요 <b class="highlight-blue">{fmt_int(t_fc)}</b>개 대비
                실 수주 <b class="highlight-blue">{fmt_int(t_ac)}</b>개 —
                달성률 <b class="{rate_color}">{t_rate:.1f}% ({rate_word})</b>,
                오차 <b class="{diff_color}">{diff_sign}{fmt_int(t_diff)}</b>개.
                &nbsp;·&nbsp; 달성률 구간: 
                <span style="color:#EF4444;font-weight:700">미달(&lt;90%) {len(under90)}건</span> /
                <span style="color:#D97706;font-weight:700">근접(90~110%) {len(ok90_110)}건</span> /
                <span style="color:#059669;font-weight:700">초과(&gt;110%) {len(over110)}건</span>
            </div>"""

            # ── 분석 카드 출력
            st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="analysis-title">🔬 현재 조건 상세 분석 · <span style="font-size:13px;color:#64748B;font-weight:500">정렬: {sort_desc}</span></div>',
                        unsafe_allow_html=True)

            # 요약 한 줄
            st.markdown(summary_html, unsafe_allow_html=True)
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

            # ── 2열: 오차 상위 + 브랜드 요약
            col_a, col_b = st.columns([3, 2])

            with col_a:
                st.markdown('<div class="an-section"><div class="an-section-title">📌 오차 상위 5개 품목</div>', unsafe_allow_html=True)
                for _, row in top5_err.iterrows():
                    if row["달성률(%)"] > 110:
                        badge_cls, badge_txt = "badge-over",   "초과"
                    elif row["달성률(%)"] >= 90:
                        badge_cls, badge_txt = "badge-ok",     "근접"
                    else:
                        badge_cls, badge_txt = "badge-danger", "미달"
                    sign = "+" if row["차이"] >= 0 else ""
                    diff_c = "#059669" if row["차이"]>=0 else "#DC2626"
                    st.markdown(
                        f"<div class='an-row'>"
                        f"<span class='an-badge {badge_cls}'>{badge_txt} {row['달성률(%)']:.0f}%</span>"
                        f"<div><b style='color:#0F172A'>{row['series']}</b>"
                        f"<span style='color:#94A3B8;font-size:12px;margin-left:8px'>{str(row['combo'])[:24]}</span><br>"
                        f"<span style='color:#475569'>예측 {fmt_int(row['forecast'])} → 실적 {fmt_int(row['actual'])} </span>"
                        f"<b style='color:{diff_c}'>({sign}{fmt_int(row['차이'])})</b></div>"
                        f"</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_b:
                st.markdown('<div class="an-section"><div class="an-section-title">🏷️ 브랜드별 달성률</div>', unsafe_allow_html=True)
                for _, row in brand_sum.sort_values("rate", ascending=False).iterrows():
                    if row["rate"] >= 100:   bc, bw = "#D1FAE5", "#065F46"
                    elif row["rate"] >= 90:  bc, bw = "#FEF9C3", "#92400E"
                    else:                   bc, bw = "#FEE2E2", "#991B1B"
                    bar_pct = min(int(row["rate"]), 200)
                    st.markdown(
                        f"<div class='an-row' style='display:block;padding:10px 14px'>"
                        f"<div style='display:flex;justify-content:space-between;margin-bottom:6px'>"
                        f"<b style='color:#0F172A'>{row['brand']}</b>"
                        f"<b style='background:{bc};color:{bw};padding:2px 10px;border-radius:99px;font-size:13px'>"
                        f"{row['rate']:.1f}%</b></div>"
                        f"<div style='background:#F1F5F9;border-radius:4px;height:8px;overflow:hidden'>"
                        f"<div style='width:{bar_pct/2}%;height:8px;background:"
                        f"{'#34D399' if row['rate']>=100 else '#FBBF24' if row['rate']>=90 else '#F87171'}"
                        f";border-radius:4px'></div></div>"
                        f"<div style='font-size:12px;color:#94A3B8;margin-top:4px'>"
                        f"예측 {fmt_int(row['forecast'])} / 실적 {fmt_int(row['actual'])}</div>"
                        f"</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

            # ── 2열: 예측 초과 / 예측 미달 상위 3
            col_c, col_d = st.columns(2)

            with col_c:
                st.markdown('<div class="an-section"><div class="an-section-title">🔺 예측 초과 상위 3개 (실수주 &gt; 예측)</div>', unsafe_allow_html=True)
                if top3_over.empty:
                    st.markdown("<div style='color:#94A3B8;font-size:14px;padding:8px'>초과 품목 없음</div>", unsafe_allow_html=True)
                else:
                    for _, row in top3_over.iterrows():
                        st.markdown(
                            f"<div class='an-row'>"
                            f"<span class='an-badge badge-over'>+{fmt_int(row['차이'])}</span>"
                            f"<div><b style='color:#0F172A'>{row['series']}</b>"
                            f"<span style='color:#94A3B8;font-size:12px;margin-left:8px'>{str(row['combo'])[:20]}</span><br>"
                            f"<span style='color:#475569'>예측 {fmt_int(row['forecast'])} → 실적 {fmt_int(row['actual'])}</span></div>"
                            f"</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_d:
                st.markdown('<div class="an-section"><div class="an-section-title">🔻 예측 미달 상위 3개 (실수주 &lt; 예측)</div>', unsafe_allow_html=True)
                if top3_under.empty:
                    st.markdown("<div style='color:#94A3B8;font-size:14px;padding:8px'>미달 품목 없음</div>", unsafe_allow_html=True)
                else:
                    for _, row in top3_under.iterrows():
                        st.markdown(
                            f"<div class='an-row'>"
                            f"<span class='an-badge badge-danger'>{fmt_int(row['차이'])}</span>"
                            f"<div><b style='color:#0F172A'>{row['series']}</b>"
                            f"<span style='color:#94A3B8;font-size:12px;margin-left:8px'>{str(row['combo'])[:20]}</span><br>"
                            f"<span style='color:#475569'>예측 {fmt_int(row['forecast'])} → 실적 {fmt_int(row['actual'])}</span></div>"
                            f"</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # ── 시리즈 분포 (달성률 하위 & 상위 각 3개)
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            col_e, col_f = st.columns(2)

            with col_e:
                st.markdown('<div class="an-section"><div class="an-section-title">⚠️ 달성률 하위 시리즈</div>', unsafe_allow_html=True)
                bot3_sr = sr_sum[sr_sum["forecast"]>0].nsmallest(5,"rate")
                for _, row in bot3_sr.iterrows():
                    pct = min(int(row["rate"]), 200)
                    st.markdown(
                        f"<div class='an-row' style='display:block;padding:10px 14px'>"
                        f"<div style='display:flex;justify-content:space-between;margin-bottom:5px'>"
                        f"<b style='color:#0F172A'>{row['series']}</b>"
                        f"<b style='color:#DC2626'>{row['rate']:.1f}%</b></div>"
                        f"<div style='background:#F1F5F9;border-radius:4px;height:7px'>"
                        f"<div style='width:{pct/2}%;height:7px;background:#F87171;border-radius:4px'></div></div>"
                        f"<div style='font-size:12px;color:#94A3B8;margin-top:4px'>예측 {fmt_int(row['forecast'])} / 실적 {fmt_int(row['actual'])}</div>"
                        f"</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_f:
                st.markdown('<div class="an-section"><div class="an-section-title">✅ 달성률 상위 시리즈</div>', unsafe_allow_html=True)
                top3_sr = sr_sum[sr_sum["forecast"]>0].nlargest(5,"rate")
                for _, row in top3_sr.iterrows():
                    pct = min(int(row["rate"]), 200)
                    st.markdown(
                        f"<div class='an-row' style='display:block;padding:10px 14px'>"
                        f"<div style='display:flex;justify-content:space-between;margin-bottom:5px'>"
                        f"<b style='color:#0F172A'>{row['series']}</b>"
                        f"<b style='color:#059669'>{row['rate']:.1f}%</b></div>"
                        f"<div style='background:#F1F5F9;border-radius:4px;height:7px'>"
                        f"<div style='width:{pct/2}%;height:7px;background:#34D399;border-radius:4px'></div></div>"
                        f"<div style='font-size:12px;color:#94A3B8;margin-top:4px'>예측 {fmt_int(row['forecast'])} / 실적 {fmt_int(row['actual'])}</div>"
                        f"</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)  # analysis-card 닫기
