import streamlit as st
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import google.generativeai as genai

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
    font-size: 12px !important; font-weight: 700 !important;
    color: #93B4D8 !important; margin-bottom: 4px !important;
}
section[data-testid="stSidebar"] .stTextInput > div > div > input {
    background: #1C2B3F !important;
    border: 2px solid #3D5A80 !important;
    border-radius: 8px !important;
    color: #EEF2FF !important;
    font-size: 13px !important;
}
section[data-testid="stSidebar"] .stTextInput > div > div > input::placeholder {
    color: #4A6080 !important;
}
section[data-testid="stSidebar"] .stTextInput label {
    font-size: 13px !important; font-weight: 700 !important;
    color: #93B4D8 !important;
}
/* 사이드바 챗봇 채팅 버블 */
section[data-testid="stSidebar"] .stChatMessage {
    background: transparent !important;
}
/* 사이드바 chat_input */
section[data-testid="stSidebar"] .stChatInputContainer > div {
    background: #1C2B3F !important;
    border: 1.5px solid #3D5A80 !important;
    border-radius: 10px !important;
}
section[data-testid="stSidebar"] .stChatInputContainer textarea {
    color: #EEF2FF !important;
    font-size: 13px !important;
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
.stTabs [data-baseweb="tab-list"],
.stTabs [data-baseweb="tab-list"] * { display: none !important; height: 0 !important; overflow: hidden !important; margin: 0 !important; padding: 0 !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 0 !important; }
.custom-tab-bar { display:flex;gap:8px;padding:0 0 16px 0;flex-wrap:nowrap;align-items:center;user-select:none; }
.custom-tab {
    display:flex;align-items:center;gap:7px;padding:10px 22px;border-radius:10px;
    font-size:15px;font-weight:600;color:#475569;background:white;border:1.5px solid #CBD5E1;
    cursor:grab;transition:all 0.15s;white-space:nowrap;box-shadow:0 1px 4px rgba(0,0,0,0.06);
}
.custom-tab:hover { border-color:#93C5FD;color:#1D4ED8;box-shadow:0 3px 10px rgba(29,78,216,0.12); }
.custom-tab.active { background:#1D4ED8 !important;color:white !important;border-color:#1D4ED8 !important;box-shadow:0 4px 14px rgba(29,78,216,0.35); }
.report-box {
    background:linear-gradient(135deg,#EFF6FF 0%,#F0FDF4 100%);border-radius:12px;
    padding:22px 24px;border:1px solid #BFDBFE;line-height:2.0;color:#1E3A5F;font-size:15px;
}
.report-box strong { color:#1D4ED8; }
.report-tag-warn{background:#FEF9C3;color:#92400E;padding:3px 10px;border-radius:99px;font-size:12px;font-weight:700;display:inline-block;margin-right:4px;}
.report-tag-ok  {background:#D1FAE5;color:#065F46;padding:3px 10px;border-radius:99px;font-size:12px;font-weight:700;display:inline-block;margin-right:4px;}
.report-tag-bad {background:#FEE2E2;color:#991B1B;padding:3px 10px;border-radius:99px;font-size:12px;font-weight:700;display:inline-block;margin-right:4px;}
.analysis-card {
    background:linear-gradient(135deg,#EFF6FF 0%,#F8FAFF 100%);border-radius:16px;
    padding:26px 28px;border:1.5px solid #BFDBFE;box-shadow:0 2px 12px rgba(29,78,216,0.08);margin-top:4px;
}
.analysis-title { font-size:16px;font-weight:800;color:#1E3A5F;margin-bottom:16px;padding-bottom:10px;border-bottom:2px solid #DBEAFE;letter-spacing:-0.01em; }
.an-section { margin-bottom:14px; }
.an-section-title { font-size:13px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:8px; }
.an-row { display:flex;align-items:flex-start;gap:10px;padding:8px 12px;border-radius:8px;background:white;margin-bottom:6px;border:1px solid #E2E8F0;font-size:14px;line-height:1.7; }
.an-badge { flex-shrink:0;padding:2px 10px;border-radius:99px;font-size:12px;font-weight:700;white-space:nowrap;margin-top:2px; }
.badge-danger{background:#FEE2E2;color:#991B1B;} .badge-warn{background:#FEF9C3;color:#92400E;}
.badge-ok{background:#D1FAE5;color:#065F46;} .badge-over{background:#EDE9FE;color:#5B21B6;}
.an-summary { background:white;border-radius:10px;padding:14px 18px;border:1px solid #DBEAFE;font-size:14px;line-height:2.0;color:#1E3A5F; }
.highlight-blue{color:#1D4ED8;font-weight:700;} .highlight-red{color:#DC2626;font-weight:700;}
.highlight-green{color:#059669;font-weight:700;} .highlight-warn{color:#D97706;font-weight:700;}
.stDownloadButton > button {
    background:#1D4ED8 !important;color:white !important;border:none !important;
    border-radius:8px !important;font-size:15px !important;font-weight:600 !important;padding:10px 24px !important;
}
.stDownloadButton > button:hover { background:#1E40AF !important; }
.stAlert { font-size:15px !important; }
p { font-size:15px !important; }

/* ── 사이드바 챗봇 패널 ── */
.sb-chat-header {
    background: linear-gradient(135deg, #1D4ED8, #1E40AF);
    border-radius: 10px; padding: 12px 16px; margin-bottom: 10px;
}
.sb-chat-header-title { font-size: 14px; font-weight: 900; color: white; }
.sb-chat-header-sub   { font-size: 11px; color: rgba(255,255,255,0.7); margin-top: 2px; }
.sb-quick-grid { display:grid; grid-template-columns:1fr 1fr; gap:5px; margin-bottom:10px; }
.sb-quick-btn {
    background: #1C2B3F; border: 1px solid #3D5A80;
    border-radius: 7px; padding: 6px 8px;
    font-size: 11px; font-weight: 600; color: #93C5FD !important;
    cursor: pointer; text-align: center; transition: all 0.15s;
}
.sb-quick-btn:hover { background: #2563EB; border-color: #2563EB; color: white !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  데이터 로드
# ══════════════════════════════════════════════
def _csv_mtime():
    """파일 수정시각 기반 캐시 키 — csv 변경 시 자동 갱신"""
    _candidates = [
        os.path.dirname(os.path.abspath(__file__)),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs"),
        "/mnt/user-data/outputs",
    ]
    def _find(fname):
        for d in _candidates:
            p = os.path.join(d, fname)
            if os.path.exists(p):
                return p
        return None
    t = 0
    for fname in ["forecast_data.csv", "actual_data.csv"]:
        p = _find(fname)
        if p:
            t += int(os.path.getmtime(p))
    return t

@st.cache_data(show_spinner=False)
def load_data(_mtime=0):
    try:
        _dir = os.path.dirname(os.path.abspath(__file__))
        _candidates = [
            _dir,
            os.path.join(_dir, "outputs"),
            "/mnt/user-data/outputs",
        ]
        def _find(fname):
            for d in _candidates:
                p = os.path.join(d, fname)
                if os.path.exists(p):
                    return p
            raise FileNotFoundError(fname)
        f = pd.read_csv(_find("forecast_data.csv"), dtype={"combo": str})
        a = pd.read_csv(_find("actual_data.csv"),   dtype={"combo": str})
    except Exception:
        np.random.seed(7)
        dates  = ["2025-06","2025-07","2025-08","2025-10",
                  "2025-11","2025-12","2026-01","2026-02"]
        brands = ["데스커","일룸","퍼시스","시디즈"]
        series_list = ["ACCESSORY","IBLE","SPOON","SODA",
                       "T60","RINGO","T20","GX","AROUND","PLT"]
        supply_pool = ['시디즈(평택)', '베트남', '외주/상품']
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
        if 'brand' in df.columns:
            df['brand'] = df['brand'].replace({'알로소': '시디즈'})
        if 'supply' in df.columns:
            SUPPLY_NORM = {
                '시디즈':      '시디즈(평택)', '의자내작':    '시디즈(평택)',
                '시디즈제품':  '시디즈(평택)', '시디즈평택':  '시디즈(평택)',
                '의자평택상품':'시디즈(평택)', '의자양지상품':'시디즈(평택)',
                '제품':        '시디즈(평택)', '평택의자':    '시디즈(평택)',
                'VN의자':      '베트남',       '베트남의자':  '베트남',
                '시디즈VN':    '베트남',       '시디즈vn':    '베트남',
                'FVN2':        '베트남',       '베트남상품':  '베트남',
                '베트남제품':  '베트남',
                '의자외작':    '외주/상품',    '수입상품':    '베트남',
                '외주상품':    '외주/상품',    '상품':        '외주/상품',
                '진영':        '외주/상품',    '웰시트':      '외주/상품',
                '이화하이':    '외주/상품',    '웰켐':        '외주/상품',
                '한국스틸웨어':'외주/상품',    '다진':        '외주/상품',
                '에브라임':    '외주/상품',    '의자안성상품':'외주/상품',
                '의자상품':    '외주/상품',
                '': '<NA>', 'nan': '<NA>', 'NaN': '<NA>', 'None': '<NA>',
            }
            df['supply'] = df['supply'].astype(str).str.strip().replace(SUPPLY_NORM)
            _valid = {'시디즈(평택)', '베트남', '외주/상품', '<NA>'}
            df['supply'] = df['supply'].apply(lambda v: v if v in _valid else '<NA>')

    # ── combo 기반 supply 보정 (원본 실적 파일 기준 매핑) ──
    # actual의 combo→supply 매핑을 forecast에도 적용
    if 'actual' not in f.columns and 'combo' in a.columns and 'supply' in a.columns:
        combo_sup_ref = a.drop_duplicates('combo').set_index('combo')['supply'].to_dict()
        f['supply'] = f.apply(
            lambda r: combo_sup_ref.get(r['combo'], r['supply']), axis=1
        )

    f = f.dropna(subset=['series','brand','combo'])
    f = f[~f['series'].astype(str).str.strip().isin(['nan','NaN','None',''])]
    f = f[~f['series'].astype(str).str.isnumeric()]
    f = f[f['series'].astype(str).str.len() >= 2]
    brand_values = set(f['brand'].dropna().astype(str).str.strip().unique())
    f = f[~f['series'].astype(str).isin(brand_values)]
    return f, a

f_df, a_df = load_data(_mtime=_csv_mtime())
# forecast에만 있는 경우: actual=0, actual에만 있는 경우: forecast=0
_a_cols = ["ym","combo","brand","series","name","supply","actual"]
_a_for_merge = a_df[[c for c in _a_cols if c in a_df.columns]].copy()
_a_for_merge = _a_for_merge.rename(columns={"brand":"brand_a","series":"series_a","name":"name_a","supply":"supply_a"})

mg_all = pd.merge(f_df, _a_for_merge[["ym","combo","actual"]], on=["ym","combo"], how="outer")

# outer join으로 생긴 누락 컬럼 채우기 (actual에만 있는 행)
for _col in ["brand","series","name","supply","forecast"]:
    if _col not in mg_all.columns:
        mg_all[_col] = pd.NA
# actual에만 있는 행의 brand/series/name/supply를 actual_data에서 채움
_a_meta = a_df[["ym","combo","brand","series","name","supply"]].drop_duplicates(["ym","combo"])
mg_all = mg_all.merge(_a_meta, on=["ym","combo"], how="left", suffixes=("","_from_a"))
for _col in ["brand","series","name","supply"]:
    _col_a = _col + "_from_a"
    if _col_a in mg_all.columns:
        mg_all[_col] = mg_all[_col].fillna(mg_all[_col_a])
        mg_all.drop(columns=[_col_a], inplace=True)
mg_all["actual"]   = pd.to_numeric(mg_all["actual"],  errors='coerce').fillna(0).astype(int)
mg_all["forecast"] = pd.to_numeric(mg_all["forecast"],errors='coerce').fillna(0).astype(int)
mg_all["차이"]      = mg_all["actual"] - mg_all["forecast"]
mg_all["오차량"]    = mg_all["차이"].abs()
mg_all["달성률(%)"] = np.where(mg_all["forecast"]>0,(mg_all["actual"]/mg_all["forecast"]*100).round(1),0)
try:    mg_all["ym_dt"] = pd.to_datetime(mg_all["ym"]+"-01")
except: mg_all["ym_dt"] = mg_all["ym"]


# ══════════════════════════════════════════════
#  유틸
# ══════════════════════════════════════════════
def apply_filters(df, ym=None, ym_range=None, brands=None, supply=None):
    """
    ym       : 단일 월 문자열 (단일 조회 모드)
    ym_range : (시작월, 종료월) 튜플 (누적 범위 모드)
    """
    d = df.copy()
    if ym_range:
        start, end = ym_range
        d = d[(d["ym"] >= start) & (d["ym"] <= end)]
    elif ym:
        d = d[d["ym"] == ym]
    if brands: d = d[d["brand"].isin(brands)]
    if supply and supply != "전체": d = d[d["supply"] == supply]
    return d

def fmt_int(v): return f"{int(v):,}"
def fmt_pct(v): return f"{v:.1f}%"

# ══════════════════════════════════════════════
#  규칙 기반 챗봇 엔진 (API 키 없을 때 fallback)
# ══════════════════════════════════════════════
def rule_based_reply(question: str, df: pd.DataFrame, sel_ym, sel_brands, sel_supply) -> str:
    """키워드 매칭 → 데이터 집계 기반 자동 답변"""
    if df.empty:
        return "현재 선택된 데이터가 없습니다. 사이드바 필터를 확인해주세요."

    q = question.lower()

    # ── 공통 집계 ──
    t_f  = int(df["forecast"].sum())
    t_a  = int(df["actual"].sum())
    t_r  = round(t_a / t_f * 100, 1) if t_f > 0 else 0.0
    t_d  = t_a - t_f
    month = sel_ym.replace("-", "년 ") + "월"

    brand_agg = df.groupby("brand").agg(f=("forecast","sum"), a=("actual","sum")).reset_index()
    brand_agg["r"] = np.where(brand_agg["f"]>0, (brand_agg["a"]/brand_agg["f"]*100).round(1), 0)

    sr_agg = df.groupby("series").agg(f=("forecast","sum"), a=("actual","sum")).reset_index()
    sr_agg["r"]   = np.where(sr_agg["f"]>0, (sr_agg["a"]/sr_agg["f"]*100).round(1), 0)
    sr_agg["err"] = (sr_agg["a"] - sr_agg["f"]).abs()

    # ── 달성률 / 전체 현황 ──
    if any(k in q for k in ["달성률","달성","현황","전체","요약","분석","overview"]):
        status = "✅ 초과달성" if t_r >= 100 else "⚠️ 근접" if t_r >= 90 else "❌ 미달"
        best  = brand_agg.loc[brand_agg["r"].idxmax()]
        worst = brand_agg.loc[brand_agg["r"].idxmin()]
        sign  = "+" if t_d >= 0 else ""
        return (
            f"**{month} 전체 달성률 분석** {status}\n\n"
            f"- 예측: **{t_f:,}** / 실수주: **{t_a:,}**\n"
            f"- 달성률: **{t_r:.1f}%** (오차 {sign}{t_d:,})\n\n"
            f"**브랜드별 달성률**\n"
            + "\n".join([f"- {r['brand']}: {r['r']:.1f}%" for _, r in brand_agg.sort_values('r', ascending=False).iterrows()])
            + f"\n\n🏆 최고: **{best['brand']}** ({best['r']:.1f}%) · 최저: **{worst['brand']}** ({worst['r']:.1f}%)"
        )

    # ── 오차 분석 ──
    if any(k in q for k in ["오차","차이","오류","error","틀린","차이량"]):
        top5 = sr_agg.nlargest(5, "err")
        lines = "\n".join([f"- **{r['series']}**: 오차 {r['err']:,} (달성률 {r['r']:.1f}%)" for _, r in top5.iterrows()])
        return f"**{month} 오차 상위 5개 시리즈**\n\n{lines}\n\n💡 오차가 큰 품목은 수요 변동성이 높거나 예측 모델 보정이 필요합니다."

    # ── 과소예측 ──
    if any(k in q for k in ["과소","미달","부족","under","낮은","낮다"]):
        under = sr_agg[sr_agg["r"] < 90].sort_values("r")
        if under.empty:
            return f"**{month}** 과소예측(달성률 90% 미만) 시리즈가 없습니다. 예측 정확도가 양호합니다! ✅"
        lines = "\n".join([f"- **{r['series']}**: {r['r']:.1f}% (실수주 {r['a']:,} / 예측 {r['f']:,})" for _, r in under.iterrows()])
        return (
            f"**과소예측 시리즈 ({len(under)}개)**\n\n{lines}\n\n"
            "💡 **개선 방안**\n"
            "- 최근 3개월 실적 트렌드를 예측 모델에 반영\n"
            "- 해당 시리즈 영업팀과 수요 급증 원인 파악\n"
            "- 다음 주기 예측 시 상향 보정 검토"
        )

    # ── 과대예측 ──
    if any(k in q for k in ["과대","초과","over","높은","높다","재고"]):
        over = sr_agg[sr_agg["r"] > 110].sort_values("r", ascending=False)
        if over.empty:
            return f"**{month}** 과대예측(달성률 110% 초과) 시리즈가 없습니다. ✅"
        lines = "\n".join([f"- **{r['series']}**: {r['r']:.1f}% (실수주 {r['a']:,} / 예측 {r['f']:,})" for _, r in over.iterrows()])
        return (
            f"**과대예측 시리즈 ({len(over)}개)**\n\n{lines}\n\n"
            "💡 **권장 조치**\n"
            "- 잉여 재고 현황 점검 및 할인 프로모션 검토\n"
            "- 예측 모델의 계절성·이벤트 반영 여부 확인\n"
            "- 다음 주기 예측 시 하향 보정 검토"
        )

    # ── 브랜드 비교 ──
    if any(k in q for k in ["브랜드","brand","비교","compare"]):
        rows_str = "\n".join([
            f"- **{r['brand']}**: 예측 {r['f']:,} / 실수주 {r['a']:,} / 달성률 {r['r']:.1f}%"
            for _, r in brand_agg.sort_values("r", ascending=False).iterrows()
        ])
        best  = brand_agg.loc[brand_agg["r"].idxmax()]
        worst = brand_agg.loc[brand_agg["r"].idxmin()]
        return (
            f"**{month} 브랜드별 성과 비교**\n\n{rows_str}\n\n"
            f"🏆 최고 성과: **{best['brand']}** ({best['r']:.1f}%)\n"
            f"⚠️ 개선 필요: **{worst['brand']}** ({worst['r']:.1f}%)"
        )

    # ── 다음달 / 전략 ──
    if any(k in q for k in ["다음","전략","개선","strategy","next","제안","추천"]):
        top3_err  = sr_agg.nlargest(3, "err")["series"].tolist()
        under_cnt = len(sr_agg[sr_agg["r"] < 90])
        over_cnt  = len(sr_agg[sr_agg["r"] > 110])
        return (
            f"**{month} 분석 기반 다음 주기 전략 제안**\n\n"
            f"📊 현황 요약: 달성률 **{t_r:.1f}%**, 과소예측 {under_cnt}건, 과대예측 {over_cnt}건\n\n"
            f"**🎯 우선 조치 항목**\n"
            f"1. 오차 상위 시리즈 집중 관리: {', '.join(top3_err)}\n"
            f"2. 과소예측 {under_cnt}개 시리즈 → 예측 상향 보정\n"
            f"3. 과대예측 {over_cnt}개 시리즈 → 재고 소진 계획 수립\n"
            f"4. 브랜드별 달성률 편차 원인 분석 후 채널 전략 수정"
        )

    # ── 재고 우선순위 ──
    if any(k in q for k in ["재고","우선순위","priority","stock","긴급","점검"]):
        urgent = sr_agg[sr_agg["r"] < 80].sort_values("r").head(5)
        if urgent.empty:
            return f"**{month}** 달성률 80% 미만 긴급 점검 시리즈가 없습니다. ✅"
        lines = "\n".join([f"- **{r['series']}** (달성률 {r['r']:.1f}%, 오차 {r['err']:,})" for _, r in urgent.iterrows()])
        return f"**긴급 재고 점검 우선순위 (달성률 80% 미만)**\n\n{lines}\n\n💡 위 품목 납기·반품 현황을 즉시 확인하세요."

    # ── fallback ──
    return (
        f"**{month} 기준 현황**\n\n"
        f"- 달성률: **{t_r:.1f}%** | 예측 {t_f:,} → 실수주 {t_a:,}\n\n"
        "다음 키워드로 질문해보세요:\n"
        "📊 달성률 · ⚠️ 오차 · 🔻 과소예측 · 🔺 과대예측 · 🏷️ 브랜드 · 📈 전략 · 💡 재고"
    )


def build_context(df, period_label, sel_brands, sel_supply):
    if df.empty: return "현재 선택된 데이터가 없습니다."
    t_f = int(df["forecast"].sum()); t_a = int(df["actual"].sum())
    t_r = round(t_a/t_f*100,1) if t_f>0 else 0.0; t_d = t_a-t_f
    brand_agg = df.groupby("brand").agg(f=("forecast","sum"),a=("actual","sum")).reset_index()
    brand_agg["r"] = np.where(brand_agg["f"]>0,(brand_agg["a"]/brand_agg["f"]*100).round(1),0)
    brand_lines = "\n".join([f"  - {r['brand']}: 예측 {r['f']:,} / 실수주 {r['a']:,} / 달성률 {r['r']:.1f}%" for _,r in brand_agg.iterrows()])
    sr_agg = df.groupby("series").agg(f=("forecast","sum"),a=("actual","sum")).reset_index()
    sr_agg["r"] = np.where(sr_agg["f"]>0,(sr_agg["a"]/sr_agg["f"]*100).round(1),0)
    sr_agg["err"] = (sr_agg["a"]-sr_agg["f"]).abs()
    top5 = sr_agg.nlargest(5,"err")
    err_lines = "\n".join([f"  - {r['series']}: 달성률 {r['r']:.1f}% / 오차 {r['err']:,}" for _,r in top5.iterrows()])
    under = sr_agg[sr_agg["r"]<90]["series"].tolist()
    over  = sr_agg[sr_agg["r"]>110]["series"].tolist()
    return f"""=== 수요예측 대시보드 현재 데이터 ===
조회 기간: {period_label} | 브랜드: {', '.join(sel_brands)} | 공급단: {sel_supply}
총 품목: {len(df):,}건

[전체] 예측 {t_f:,} / 실수주 {t_a:,} / 달성률 {t_r:.1f}% / 오차 {t_d:+,}

[브랜드별]
{brand_lines}

[오차 상위 5개 시리즈]
{err_lines}

과소예측(<90%): {', '.join(under) if under else '없음'}
과대예측(>110%): {', '.join(over) if over else '없음'}""".strip()


# ══════════════════════════════════════════════
#  사이드바
# ══════════════════════════════════════════════
with st.sidebar:
    # ── 헤더 ──
    st.markdown("""
    <div style="padding:20px 4px 4px 4px">
        <div style="font-size:17px;font-weight:900;color:#F8FAFC;letter-spacing:-0.02em;">📦 수요예측 모니터링</div>
        <div style="font-size:12px;color:#64748B;margin-top:4px;">Demand Forecast Dashboard</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")

    # ── 조회 모드 ──
    # actual 실적이 하나라도 있는 월만 선택 가능하도록 필터링


    # 라디오 버튼 커스텀 스타일 (사이드바 전용 - 가로 컴팩트)
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] .stRadio > label {
        font-size: 12px !important;
        font-weight: 700 !important;
        color: #93B4D8 !important;
        margin-bottom: 4px !important;
    }
    section[data-testid="stSidebar"] .stRadio > div {
        gap: 6px !important;
        flex-direction: row !important;
    }
    section[data-testid="stSidebar"] .stRadio > div > label {
        background: #1C2B3F !important;
        border: 1.5px solid #3D5A80 !important;
        border-radius: 7px !important;
        padding: 4px 8px !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        color: #93C5FD !important;
        cursor: pointer !important;
        min-height: unset !important;
        flex: 1 !important;
        text-align: center !important;
        white-space: nowrap !important;
    }
    section[data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {
        background: #2563EB !important;
        border-color: #60A5FA !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(37,99,235,0.35) !important;
    }
    section[data-testid="stSidebar"] .stRadio > div > label > div {
        display: flex !important;
        gap: 4px !important;
        align-items: center !important;
        justify-content: center !important;
    }
    section[data-testid="stSidebar"] .stRadio > div > label > div > p {
        font-size: 11px !important;
        font-weight: 600 !important;
        color: inherit !important;
        margin: 0 !important;
        line-height: 1 !important;
        white-space: nowrap !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size:12px;font-weight:700;color:#93B4D8;margin-bottom:5px;">📅 조회 방식</div>', unsafe_allow_html=True)
    view_mode = st.radio("조회 방식", ["단일 월", "기간 범위"],
                         horizontal=True, label_visibility="collapsed")
    st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

# forecast 또는 actual 데이터가 있는 모든 월 표시 (미래 예측월 포함)
_yms_with_actual = set(mg_all["ym"].unique())
ym_options      = sorted(_yms_with_actual)
    ym_options_desc = list(reversed(ym_options))

    sel_ym       = None
    sel_ym_range = None

    if view_mode == "단일 월":
        sel_ym = st.selectbox("기준 월 선택", ym_options_desc, label_visibility="collapsed")
        sel_ym_range = None
        period_label = sel_ym.replace("-","년 ") + "월"
        n_months = 1

    else:  # 기간 범위
        col_s, col_e = st.columns(2)
        with col_s:
            start_ym = st.selectbox("시작 월", ym_options, index=0,
                                    label_visibility="visible")
        with col_e:
            # 종료 기본값: 마지막 월
            end_default = len(ym_options) - 1
            end_ym = st.selectbox("종료 월", ym_options,
                                  index=end_default, label_visibility="visible")
        if start_ym > end_ym:
            st.warning("⚠️ 시작 월이 종료 월보다 늦습니다.")
            start_ym, end_ym = end_ym, start_ym

        sel_ym_range = (start_ym, end_ym)
        sel_ym = end_ym        # 단일 월 참조가 필요한 곳(탭2 등)에서 종료월 사용
        period_label = f"{start_ym} ~ {end_ym}"
        n_months = ym_options.index(end_ym) - ym_options.index(start_ym) + 1


    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    all_brands = sorted(mg_all["brand"].unique())
    sel_brand_single = st.selectbox("🏷️ 브랜드", ["전체"] + all_brands)
    sel_brands = all_brands if sel_brand_single == "전체" else [sel_brand_single]
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    _known_supply = ['시디즈(평택)', '베트남', '외주/상품']
    supply_vals = [v for v in _known_supply if v in mg_all["supply"].values]
    sel_supply = st.selectbox("🏭 공급단", ["전체"] + supply_vals)

    st.markdown("---")
    st.markdown(f"""<div style="font-size:13px;color:#94A3B8;line-height:2.2;">
        📆 전체 기간: <b style="color:#CBD5E1">{mg_all['ym'].min()} ~ {mg_all['ym'].max()}</b><br>
        🔢 총 콤보 수: <b style="color:#CBD5E1">{mg_all['combo'].nunique():,}개</b>
    </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════
    #  사이드바 챗봇 ★ NEW
    # ════════════════════════════════════════
    st.markdown("---")

    # API 키 입력
    st.markdown('<div style="font-size:12px;font-weight:700;color:#93B4D8;margin-bottom:4px;">🔑 Gemini API Key</div>', unsafe_allow_html=True)
    api_key = st.text_input("API Key", type="password", placeholder="AIza...",
                            label_visibility="collapsed", key="gemini_api_key")
    if api_key:
        st.markdown('<div style="font-size:11px;color:#34D399;margin-bottom:8px;">✅ API 키 등록됨</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:11px;color:#F87171;margin-bottom:8px;">⚠️ API 키를 입력하면 챗봇이 활성화됩니다</div>', unsafe_allow_html=True)

    # 챗봇 헤더
    st.markdown("""
    <div class="sb-chat-header">
        <div class="sb-chat-header-title" style="font-size:13px;">🤖 AI 분석 어시스턴트</div>
        <div class="sb-chat-header-sub">현재 대시보드 데이터 기반 질의응답 · Gemini 2.0 Flash</div>
    </div>
    """, unsafe_allow_html=True)

    # session_state 초기화
    if "sb_messages" not in st.session_state:
        st.session_state.sb_messages = []
    if "sb_quick" not in st.session_state:
        st.session_state.sb_quick = ""

    # 현재 필터 데이터
    df_chat = apply_filters(mg_all, ym=sel_ym if not sel_ym_range else None, ym_range=sel_ym_range, brands=sel_brands, supply=sel_supply)
    t_f_sb  = int(df_chat["forecast"].sum()) if not df_chat.empty else 0
    t_a_sb  = int(df_chat["actual"].sum())   if not df_chat.empty else 0
    t_r_sb  = round(t_a_sb/t_f_sb*100,1)    if t_f_sb>0 else 0.0
    rate_color_sb = "#34D399" if t_r_sb>=100 else "#F87171"



    # 빠른 질문 버튼 (2열 그리드)
    quick_qs = [
        ("📊", "전체 달성률 분석"),
        ("⚠️", "오차 큰 시리즈"),
        ("🔻", "과소예측 원인"),
        ("📈", "다음달 전략"),
        ("🏷️", "브랜드 비교"),
        ("💡", "재고 우선순위"),
    ]

    # 버튼 CSS 개선
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #1E3A5F 0%, #1C2B3F 100%) !important;
        border: 1.5px solid #4A7FA5 !important;
        border-radius: 10px !important;
        color: #E8F4FF !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        padding: 10px 6px !important;
        line-height: 1.4 !important;
        min-height: 52px !important;
        width: 100% !important;
        text-align: center !important;
        transition: all 0.2s !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3) !important;
        white-space: pre-wrap !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        border-color: #60A5FA !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(37,99,235,0.4) !important;
        transform: translateY(-1px) !important;
    }
    section[data-testid="stSidebar"] .stButton > button:active {
        transform: translateY(0px) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    cols_q = st.columns(2)
    for i, (icon, label) in enumerate(quick_qs):
        with cols_q[i % 2]:
            if st.button(f"{icon}\n{label}", key=f"sb_q_{i}", use_container_width=True):
                st.session_state.sb_quick = f"{icon} {label}에 대해 현재 데이터를 기반으로 분석해줘"

    # 대화 이력 표시 (최근 6개만)
    recent_msgs = st.session_state.sb_messages[-6:] if len(st.session_state.sb_messages) > 6 else st.session_state.sb_messages
    for msg in recent_msgs:
        with st.chat_message(msg["role"]):
            st.markdown(f'<div style="font-size:12px;line-height:1.7">{msg["content"]}</div>',
                        unsafe_allow_html=True)

    # 채팅 입력
    sb_input = st.chat_input("질문 입력...", key="sb_chat_input")

    # 빠른 질문 or 직접 입력 처리
    prompt_sb = None
    if st.session_state.sb_quick:
        prompt_sb = st.session_state.sb_quick
        st.session_state.sb_quick = ""
    elif sb_input:
        prompt_sb = sb_input

    if prompt_sb:
        if not api_key:
            st.warning("⚠️ Gemini API 키를 먼저 입력하세요.")
        else:
            st.session_state.sb_messages.append({"role": "user", "content": prompt_sb})
            context_text = build_context(df_chat, period_label, sel_brands, sel_supply)
            system_instruction = f"""당신은 수요예측 대시보드 전문 분석 어시스턴트입니다.
아래 데이터를 기반으로 간결하고 실용적인 인사이트를 한국어로 제공하세요.
사이드바에 표시되므로 답변은 반드시 300자 이내로 핵심만 작성하세요.
수치는 구체적으로 인용하고, 실행 가능한 조치를 1~3개 제시하세요.

{context_text}"""

            import time

            def call_gemini_with_retry(api_key, system_instruction, history, prompt, max_retries=3):
                """지수 백오프(Exponential Backoff) 재시도 로직"""
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name="gemini-2.0-flash",
                    system_instruction=system_instruction,
                )
                chat = model.start_chat(history=history)
                for attempt in range(max_retries):
                    try:
                        response = chat.send_message(
                            prompt,
                            generation_config=genai.types.GenerationConfig(
                                max_output_tokens=400,
                                temperature=0.7,
                            ),
                        )
                        return response.text, None
                    except Exception as e:
                        err = str(e)
                        is_rate_limit = "quota" in err.lower() or "429" in err or "RESOURCE_EXHAUSTED" in err
                        if is_rate_limit and attempt < max_retries - 1:
                            wait_sec = 2 ** attempt  # 1초 → 2초 → 4초
                            time.sleep(wait_sec)
                            continue
                        return None, err
                return None, "최대 재시도 횟수 초과"

            # 멀티턴 히스토리 변환
            history = []
            for m in st.session_state.sb_messages[:-1]:
                role = "user" if m["role"] == "user" else "model"
                history.append({"role": role, "parts": [m["content"]]})

            # 로딩 스피너 표시 후 호출
            with st.spinner("🤖 분석 중..."):
                reply, err = call_gemini_with_retry(
                    api_key, system_instruction, history, prompt_sb
                )

            if reply:
                st.session_state.sb_messages.append({"role": "assistant", "content": reply})
                st.rerun()
            else:
                if "API_KEY_INVALID" in err or "api key" in err.lower():
                    st.error("❌ API 키가 올바르지 않습니다. Google AI Studio에서 확인하세요.")
                elif "quota" in err.lower() or "429" in err or "RESOURCE_EXHAUSTED" in err:
                    st.warning("⚠️ API 사용량 한도 초과입니다. 잠시 후 자동 재시도했지만 실패했습니다.\n\n💡 1분 정도 기다린 후 다시 질문해 주세요.")
                else:
                    st.error(f"❌ 오류: {err}")

    # 대화 초기화
    if st.session_state.sb_messages:
        if st.button("🗑️ 대화 초기화", key="sb_clear", use_container_width=True):
            st.session_state.sb_messages = []
            st.rerun()


# ══════════════════════════════════════════════
#  드래그앤드롭 탭
# ══════════════════════════════════════════════
import streamlit.components.v1 as components

components.html("""
<!DOCTYPE html><html><body style="margin:0;padding:0;background:transparent;">
<script>
(function(){
  var RETRY=0;
  function applyActive(b){b._isActive=true;b.style.background='#1D4ED8';b.style.color='white';b.style.borderColor='#1D4ED8';b.style.boxShadow='0 4px 14px rgba(29,78,216,0.35)';}
  function applyInactive(b){b._isActive=false;b.style.background='white';b.style.color='#475569';b.style.borderColor='#CBD5E1';b.style.boxShadow='0 1px 4px rgba(0,0,0,0.06)';}
  function init(){
    var doc=window.parent.document;
    if(doc.getElementById('__dtab__'))return;
    var tl=doc.querySelector('[data-baseweb="tab-list"]');
    if(!tl){if(RETRY++<20)setTimeout(init,300);return;}
    var sts=Array.from(tl.querySelectorAll('[role="tab"]'));
    if(!sts.length){if(RETRY++<20)setTimeout(init,300);return;}
    tl.style.display='none';
    var bar=doc.createElement('div');bar.id='__dtab__';
    bar.style.cssText='display:flex;gap:8px;padding:0 0 14px 0;align-items:center;user-select:none;';
    var drag=null;
    sts.forEach(function(st,idx){
      var b=doc.createElement('div');b._tabIdx=idx;b.draggable=true;
      b.textContent=st.textContent.trim();
      b.style.cssText='padding:10px 22px;border-radius:10px;font-size:15px;font-weight:600;border:1.5px solid #CBD5E1;transition:all 0.15s;white-space:nowrap;font-family:"Noto Sans KR",sans-serif;box-shadow:0 1px 4px rgba(0,0,0,0.06);cursor:grab;';
      st.getAttribute('aria-selected')==='true'?applyActive(b):applyInactive(b);
      b.addEventListener('click',function(){Array.from(bar.children).forEach(applyInactive);applyActive(b);sts[b._tabIdx].click();});
      b.addEventListener('dragstart',function(e){drag=b;e.dataTransfer.effectAllowed='move';setTimeout(function(){b.style.opacity='0.35';},0);});
      b.addEventListener('dragend',function(){b.style.opacity='1';b.style.transform='';Array.from(bar.children).forEach(function(x){x.style.transform='';x._isActive?applyActive(x):applyInactive(x);});});
      b.addEventListener('dragover',function(e){e.preventDefault();if(b!==drag){b.style.transform='scale(1.06)';b.style.borderColor='#60A5FA';}});
      b.addEventListener('dragleave',function(){b.style.transform='';b._isActive?applyActive(b):applyInactive(b);});
      b.addEventListener('drop',function(e){e.preventDefault();if(!drag||drag===b)return;var all=Array.from(bar.children);var fi=all.indexOf(drag),ti=all.indexOf(b);fi<ti?bar.insertBefore(drag,b.nextSibling):bar.insertBefore(drag,b);b.style.transform='';b._isActive?applyActive(b):applyInactive(b);});
      bar.appendChild(b);
    });
    tl.parentNode.insertBefore(bar,tl.nextSibling);
  }
  new MutationObserver(function(){var d=window.parent.document;if(!d.getElementById('__dtab__')){RETRY=0;init();}}).observe(window.parent.document.body,{childList:true,subtree:true});
  init();
})();
</script></body></html>
""", height=0, scrolling=False)

tab1, tab2, tab3, tab4, tab_help = st.tabs([
    "  📊 개요  ","  📈 월별 추이  ","  🔎 시리즈 분석  ","  📋 상세 데이터  ","  ❓ 사용법  "
])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  탭1: 개요
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab1:
    df_ov = apply_filters(mg_all, ym=sel_ym if not sel_ym_range else None, ym_range=sel_ym_range, brands=sel_brands, supply=sel_supply)
    if df_ov.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다."); st.stop()

    month_label = period_label  # 단일 월 또는 기간 범위 레이블

    # ── 부품류 키워드 ──
    _PARTS_KW = ['ACCESSORY','악세사리','이지리페어','EASY REPAIR','EASY-REPAIR',
                 '부품','PARTS','PART','리페어','REPAIR','패브릭','FABRIC','가스','실린더']
    def _is_parts(s):
        s_up = str(s).upper()
        return any(kw.upper() in s_up for kw in _PARTS_KW)

    _parts_mask = df_ov["series"].apply(_is_parts)
    df_ov_product = df_ov[~_parts_mask]   # 제품만
    df_ov_parts   = df_ov[_parts_mask]    # 부품류만

    # ── KPI 분류 드롭다운 ──
    kpi_cat = st.selectbox(
        "📦 예측 수요 분류",
        ["전체", "제품 (부품류 제외)", "부품류"],
        key="kpi_cat",
        label_visibility="collapsed",
    )
    if kpi_cat == "제품 (부품류 제외)":
        df_kpi = df_ov_product
        kpi_label = "제품만"
    elif kpi_cat == "부품류":
        df_kpi = df_ov_parts
        kpi_label = "부품류만"
    else:
        df_kpi = df_ov
        kpi_label = "전체"

    t_f=int(df_kpi["forecast"].sum()); t_a=int(df_kpi["actual"].sum())
    t_d=t_a-t_f; t_r=round(t_a/t_f*100,1) if t_f>0 else 0.0

    c1,c2,c3,c4=st.columns(4)
    for col,color,label,value,sub in [
        (c1,"#3B82F6","예측 수요",fmt_int(t_f),f"{month_label} · {kpi_label}"),
        (c2,"#10B981","실 수주",fmt_int(t_a),f"{month_label} 실수주 합계"),
        (c3,"#F59E0B" if t_d>=0 else "#EF4444","예측 오차",("▲ +" if t_d>=0 else "▼ ")+fmt_int(abs(t_d)),"실수주 − 예측"),
        (c4,"#8B5CF6","달성률",fmt_pct(t_r),"실수주 ÷ 예측 × 100"),
    ]:
        with col:
            st.markdown(f"""<div class="kpi-wrap" style="border-left-color:{color}">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value" style="color:{color}">{value}</div>
                <div class="kpi-sub">{sub}</div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    brand_agg=df_ov.groupby("brand").agg(forecast=("forecast","sum"),actual=("actual","sum")).reset_index()
    brand_agg["달성률"]=np.where(brand_agg["forecast"]>0,(brand_agg["actual"]/brand_agg["forecast"]*100).round(1),0)

    col_l,col_r=st.columns([3,2])
    with col_l:
        st.markdown('<div class="section-card"><div class="section-title">브랜드별 예측 vs 실수주</div>', unsafe_allow_html=True)
        fig_bar=go.Figure()
        fig_bar.add_trace(go.Bar(name="예측 수요",x=brand_agg["brand"],y=brand_agg["forecast"],marker_color="#93C5FD",text=brand_agg["forecast"].apply(fmt_int),textposition="outside"))
        fig_bar.add_trace(go.Bar(name="실 수주",x=brand_agg["brand"],y=brand_agg["actual"],marker_color="#34D399",text=brand_agg["actual"].apply(fmt_int),textposition="outside"))
        fig_bar.update_layout(barmode="group",template="plotly_white",height=320,margin=dict(l=0,r=0,t=10,b=0),font=dict(size=14),legend=dict(orientation="h",yanchor="bottom",y=1.02),yaxis=dict(showgrid=True,gridcolor="#F3F4F6"))
        st.plotly_chart(fig_bar,use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="section-card"><div class="section-title">브랜드별 달성률</div>', unsafe_allow_html=True)
        bar_colors=["#22C55E" if v>=95 else "#F59E0B" if v>=80 else "#EF4444" for v in brand_agg["달성률"]]
        st.markdown('''<div style="display:flex;gap:16px;margin-bottom:8px;font-size:12px;font-weight:600;">
            <span style="display:flex;align-items:center;gap:5px;"><span style="width:12px;height:12px;border-radius:3px;background:#22C55E;display:inline-block;"></span> 95% 이상 (목표 달성)</span>
            <span style="display:flex;align-items:center;gap:5px;"><span style="width:12px;height:12px;border-radius:3px;background:#F59E0B;display:inline-block;"></span> 80~95% (주의)</span>
            <span style="display:flex;align-items:center;gap:5px;"><span style="width:12px;height:12px;border-radius:3px;background:#EF4444;display:inline-block;"></span> 80% 미만 (미달)</span>
        </div>''', unsafe_allow_html=True)
        fig_rate=go.Figure(go.Bar(x=brand_agg["달성률"],y=brand_agg["brand"],orientation="h",marker_color=bar_colors,text=[f"{v:.1f}%" for v in brand_agg["달성률"]],textposition="outside"))
        fig_rate.add_vline(x=100,line_dash="dot",line_color="#94A3B8",annotation_text="100%",annotation_font_size=13)
        fig_rate.update_layout(template="plotly_white",height=320,margin=dict(l=0,r=50,t=10,b=0),font=dict(size=14),xaxis=dict(range=[0,max(135,brand_agg["달성률"].max()+20)]),yaxis=dict(tickfont=dict(size=15,color="#0F172A")))
        st.plotly_chart(fig_rate,use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    col_pie,col_rep=st.columns([1,2])
    with col_pie:
        st.markdown('<div class="section-card"><div class="section-title">공급단별 예측 비중 (부품류 제외)</div>', unsafe_allow_html=True)
        _PARTS_KEYWORDS = ['ACCESSORY','악세사리','이지리페어','EASY REPAIR','EASYREPAIR','부품','PARTS','PART','리페어','REPAIR','패브릭','FABRIC','가스','실린더']
        _parts_mask = df_ov["series"].astype(str).str.upper().apply(
            lambda s: any(kw.upper() in s for kw in _PARTS_KEYWORDS)
        )
        sup_agg=(df_ov[~_parts_mask & (df_ov["supply"] != "<NA>")].groupby("supply")["forecast"].sum().reset_index())
        if not sup_agg.empty:
            fig_pie=go.Figure(go.Pie(labels=sup_agg["supply"],values=sup_agg["forecast"],hole=0.5,textinfo="label+percent",textfont=dict(size=14),marker=dict(colors=["#60A5FA","#34D399","#FBBF24","#A78BFA"])))
            fig_pie.update_layout(height=290,margin=dict(l=0,r=0,t=10,b=0),showlegend=True,legend=dict(font=dict(size=13)))
            st.plotly_chart(fig_pie,use_container_width=True)
        else:
            st.info("공급단 데이터 없음")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_rep:
        st.markdown('<div class="section-card"><div class="section-title">자동 분석 요약</div>', unsafe_allow_html=True)
        sr_agg2=df_ov.groupby("series").agg(f=("forecast","sum"),a=("actual","sum")).reset_index()
        sr_agg2["달성률"]=np.where(sr_agg2["f"]>0,(sr_agg2["a"]/sr_agg2["f"]*100).round(1),0)
        sr_agg2["오차량"]=(sr_agg2["a"]-sr_agg2["f"]).abs()
        top_err=sr_agg2.sort_values("오차량",ascending=False).head(3)
        under_s=sr_agg2[sr_agg2["달성률"]<90].sort_values("달성률").head(3)
        over_s=sr_agg2[sr_agg2["달성률"]>110].sort_values("달성률",ascending=False).head(3)
        color_r="#10B981" if t_r>=100 else "#EF4444"; trend_w="초과달성" if t_r>=100 else "미달"
        html_r=f"""<div class="report-box"><b>{month_label}</b> 전체 달성률 <b style="color:{color_r};font-size:16px">{fmt_pct(t_r)}</b> — 예측 대비 <b style="color:{color_r}">{trend_w}</b> 상태입니다.<br><br>"""
        if not top_err.empty:
            html_r+="<b>📍 오차 상위 시리즈</b><br>"
            for _,row in top_err.iterrows():
                if row["달성률"]<90:    tag='<span class="report-tag-bad">과소예측</span>'
                elif row["달성률"]>110: tag='<span class="report-tag-warn">과대예측</span>'
                else:                  tag='<span class="report-tag-ok">양호</span>'
                html_r+=f"&nbsp;&nbsp;{tag} <b>{row['series']}</b> 달성률 {row['달성률']:.1f}% (오차 {fmt_int(row['오차량'])}ea)<br>"
        if not under_s.empty: html_r+=f"<br><b>⚠️ 과소예측 (&lt;90%)</b>: {', '.join(under_s['series'].tolist())}<br>"
        if not over_s.empty:  html_r+=f"<b>🔺 과대예측 (&gt;110%)</b>: {', '.join(over_s['series'].tolist())}<br>"
        html_r+="""<br><b>💡 권장 조치</b><br>&nbsp;&nbsp;① 오차 상위 품목 재고·채널 현황 즉시 점검<br>&nbsp;&nbsp;② 과소예측 품목은 반품·납기 원인 확인<br>&nbsp;&nbsp;③ 다음 예측 주기에 최근 3개월 추세 가중치 반영</div>"""
        st.markdown(html_r, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  탭2: 월별 추이
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab2:
    # 단일 월 모드에서는 전체 기간 데이터로 추이를 보여줌
    df_ts=apply_filters(mg_all, ym_range=sel_ym_range, brands=sel_brands, supply=sel_supply)
    if view_mode == "단일 월":
        st.info(f"📌 현재 **단일 월({sel_ym})** 조회 중입니다. 사이드바에서 **기간 범위** 모드로 전환하면 여러 달의 추이를 비교할 수 있습니다.")
        df_ts = apply_filters(mg_all, brands=sel_brands, supply=sel_supply)  # 추이는 전체 기간 표시
    if df_ts.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    else:
        st.markdown('<div class="filter-card">', unsafe_allow_html=True)
        fc1,fc2=st.columns([1,4])
        with fc1: ts_mode=st.radio("📐 집계 기준",["브랜드별","시리즈별"],horizontal=False)
        with fc2:
            group_col="brand" if ts_mode=="브랜드별" else "series"
            choices=sorted(df_ts[group_col].unique()); default_c=choices[:4] if len(choices)>4 else choices
            ts_sel=st.multiselect(f"📌 표시할 {ts_mode[:-1]} 선택",choices,default=default_c)
        st.markdown('</div>', unsafe_allow_html=True)

        if not ts_sel:
            st.info(f"위에서 {ts_mode[:-1]}을 하나 이상 선택하세요.")
        else:
            agg_ts=(df_ts[df_ts[group_col].isin(ts_sel)].groupby(["ym_dt",group_col]).agg(forecast=("forecast","sum"),actual=("actual","sum")).reset_index().sort_values("ym_dt"))
            PAL_F=["#93C5FD","#86EFAC","#FDE68A","#DDD6FE","#FBCFE8"]
            PAL_A=["#1D4ED8","#15803D","#B45309","#6D28D9","#BE185D"]

            st.markdown('<div class="section-card"><div class="section-title">월별 예측 vs 실수주 추이</div>', unsafe_allow_html=True)
            fig_ts=go.Figure()
            for i,item in enumerate(ts_sel):
                d=agg_ts[agg_ts[group_col]==item].sort_values("ym_dt")
                fig_ts.add_trace(go.Scatter(x=d["ym_dt"],y=d["forecast"],name=f"{item} 예측",mode="lines+markers",line=dict(dash="dot",color=PAL_F[i%len(PAL_F)],width=2),marker=dict(size=7)))
                fig_ts.add_trace(go.Scatter(x=d["ym_dt"],y=d["actual"],name=f"{item} 실적",mode="lines+markers",line=dict(color=PAL_A[i%len(PAL_A)],width=2.5),marker=dict(size=8)))
            fig_ts.update_layout(template="plotly_white",height=380,margin=dict(l=0,r=0,t=10,b=0),font=dict(size=14),xaxis=dict(title="기준월",showgrid=False),yaxis=dict(title="수량",showgrid=True,gridcolor="#F3F4F6"),legend=dict(orientation="h",yanchor="bottom",y=1.02),hovermode="x unified")
            st.plotly_chart(fig_ts,use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-card"><div class="section-title">월별 달성률 추이</div>', unsafe_allow_html=True)
            rate_ts=agg_ts.copy()
            rate_ts["달성률"]=np.where(rate_ts["forecast"]>0,(rate_ts["actual"]/rate_ts["forecast"]*100).round(1),0)
            fig_rt=go.Figure()
            for i,item in enumerate(ts_sel):
                d=rate_ts[rate_ts[group_col]==item].sort_values("ym_dt")
                fig_rt.add_trace(go.Scatter(x=d["ym_dt"],y=d["달성률"],name=item,mode="lines+markers",line=dict(color=PAL_A[i%len(PAL_A)],width=2.5),marker=dict(size=8)))
            fig_rt.add_hline(y=100,line_dash="dot",line_color="#94A3B8",annotation_text="100% 기준",annotation_font_size=13)
            fig_rt.update_layout(template="plotly_white",height=280,margin=dict(l=0,r=0,t=10,b=0),font=dict(size=14),xaxis=dict(title="기준월",showgrid=False),yaxis=dict(title="달성률 (%)",showgrid=True,gridcolor="#F3F4F6"),legend=dict(orientation="h",yanchor="bottom",y=1.02),hovermode="x unified")
            st.plotly_chart(fig_rt,use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  탭3: 시리즈 분석
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab3:
    df_sr=apply_filters(mg_all,ym=sel_ym if not sel_ym_range else None,ym_range=sel_ym_range,brands=sel_brands,supply=sel_supply)
    if df_sr.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    else:
        st.markdown('<div class="filter-card">', unsafe_allow_html=True)
        sf1,sf2,sf3=st.columns([1,1,2])
        with sf1: top_n=st.slider("📊 Top N",5,30,20,key="sr_topn")
        with sf2:
            sr_sort=st.selectbox("🔃 정렬 기준",["차이량(실-예측) 큰 순","예측수요 큰 순","실수주 큰 순","달성률 높은 순","달성률 낮은 순"],key="sr_sort")
        with sf3:
            st.markdown(f"<div style='padding-top:36px;font-size:15px;color:#1D4ED8;font-weight:600'>상위 <b style='font-size:20px'>{top_n}</b>개 시리즈 · 정렬: <b>{sr_sort}</b></div>",unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        sr_agg=df_sr.groupby("series").agg(forecast=("forecast","sum"),actual=("actual","sum")).reset_index()
        sr_agg["차이량"]=sr_agg["actual"]-sr_agg["forecast"]
        sr_agg["오차량"]=sr_agg["차이량"].abs()
        sr_agg["달성률(%)"]=np.where(sr_agg["forecast"]>0,(sr_agg["actual"]/sr_agg["forecast"]*100).round(1),0)
        sr_sort_map={"차이량(실-예측) 큰 순":("오차량",False),"예측수요 큰 순":("forecast",False),"실수주 큰 순":("actual",False),"달성률 높은 순":("달성률(%)",False),"달성률 낮은 순":("달성률(%)",True)}
        ss_col,ss_asc=sr_sort_map[sr_sort]
        sr_top=sr_agg.sort_values(ss_col,ascending=ss_asc).head(top_n)
        sr_plot=sr_top.sort_values("forecast",ascending=True)
        chart_h=max(420,top_n*32)

        col_l,col_r=st.columns(2)
        with col_l:
            st.markdown(f'<div class="section-card"><div class="section-title">예측수요 / 실수주 / 차이량 (Top {top_n})</div>', unsafe_allow_html=True)
            fig_3bar=go.Figure()
            fig_3bar.add_trace(go.Bar(y=sr_plot["series"],x=sr_plot["forecast"],name="예측수요",orientation="h",marker_color="#5B8DEF",text=sr_plot["forecast"].apply(fmt_int),textposition="outside",textfont=dict(size=11)))
            fig_3bar.add_trace(go.Bar(y=sr_plot["series"],x=sr_plot["actual"],name="실수주",orientation="h",marker_color="#34D399",text=sr_plot["actual"].apply(fmt_int),textposition="outside",textfont=dict(size=11)))
            diff_colors=["#60A5FA" if v>=0 else "#F87171" for v in sr_plot["차이량"]]
            fig_3bar.add_trace(go.Bar(y=sr_plot["series"],x=sr_plot["차이량"],name="차이량(실-예측)",orientation="h",marker_color=diff_colors,text=[f"+{fmt_int(v)}" if v>=0 else fmt_int(v) for v in sr_plot["차이량"]],textposition="outside",textfont=dict(size=11)))
            fig_3bar.update_layout(barmode="group",template="plotly_white",height=chart_h,margin=dict(l=0,r=80,t=10,b=0),font=dict(size=13),xaxis=dict(showgrid=True,gridcolor="#F3F4F6",zeroline=True,zerolinecolor="#CBD5E1"),yaxis=dict(tickfont=dict(size=13,color="#1F2937")),legend=dict(orientation="h",yanchor="bottom",y=1.01,font=dict(size=12)))
            st.plotly_chart(fig_3bar,use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_r:
            st.markdown(f'<div class="section-card"><div class="section-title">달성률 (Top {top_n})</div>', unsafe_allow_html=True)
            rate_colors=["#34D399" if v>=100 else "#FBBF24" if v>=90 else "#F87171" for v in sr_plot["달성률(%)"]]
            fig_rate=go.Figure(go.Bar(y=sr_plot["series"],x=sr_plot["달성률(%)"],orientation="h",marker_color=rate_colors,text=[f"{v:.1f}%" for v in sr_plot["달성률(%)"]],textposition="outside",textfont=dict(size=12)))
            fig_rate.add_vline(x=100,line_dash="dash",line_color="#94A3B8",annotation_text="100%",annotation_position="top")
            x_max=max(150,float(sr_plot["달성률(%)"].max())+30)
            fig_rate.update_layout(template="plotly_white",height=chart_h,margin=dict(l=0,r=70,t=10,b=0),font=dict(size=13),xaxis=dict(range=[0,x_max],showgrid=True,gridcolor="#F3F4F6",ticksuffix="%"),yaxis=dict(tickfont=dict(size=13,color="#1F2937")))
            st.plotly_chart(fig_rate,use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        sum_col,tbl_col=st.columns([1,3])
        with sum_col:
            st.markdown('<div class="section-card"><div class="section-title">달성률 구간 분포</div>', unsafe_allow_html=True)
            bins=[0,70,90,100,110,9999]; blabels=["70% 미만","70~90%","90~100%","100~110%","110% 초과"]
            sr_agg["구간"]=pd.cut(sr_agg["달성률(%)"],bins=bins,labels=blabels,right=False)
            bin_cnt=sr_agg["구간"].value_counts().reindex(blabels,fill_value=0).reset_index()
            bin_cnt.columns=["구간","건수"]
            fig_bin=go.Figure(go.Bar(x=bin_cnt["구간"],y=bin_cnt["건수"],marker_color=["#EF4444","#F87171","#FBBF24","#34D399","#059669"],text=bin_cnt["건수"],textposition="outside",textfont=dict(size=14)))
            fig_bin.update_layout(template="plotly_white",height=260,margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig_bin,use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tbl_col:
            st.markdown('<div class="section-card"><div class="section-title">시리즈별 상세 수치</div>', unsafe_allow_html=True)
            disp=sr_top.rename(columns={"series":"시리즈","forecast":"예측수요","actual":"실수주","차이량":"차이량(실-예측)","달성률(%)":"달성률(%)"})[["시리즈","예측수요","실수주","차이량(실-예측)","달성률(%)"]].copy()
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
            styled=(disp.style.format({"예측수요":"{:,.0f}","실수주":"{:,.0f}","차이량(실-예측)":"{:+,.0f}","달성률(%)":"{:.1f}%"}).applymap(color_rate,subset=["달성률(%)"]).applymap(color_diff,subset=["차이량(실-예측)"]))
            st.dataframe(styled,use_container_width=True,height=280)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── 시리즈 드릴다운 ──
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔍 시리즈 드릴다운 — 품목별 상세</div>', unsafe_allow_html=True)
        drill_series = st.selectbox(
            "조회할 시리즈 선택 (달성률 낮은 순)",
            options=sr_top.sort_values("달성률(%)")["series"].tolist(),
            format_func=lambda s: f"{s}  ·  달성률 {sr_top.loc[sr_top['series']==s,'달성률(%)'].values[0]:.1f}%  |  오차 {sr_top.loc[sr_top['series']==s,'오차량'].values[0]:,.0f}",
            key="sr_drill"
        )
        if drill_series:
            df_drill = df_sr[df_sr["series"] == drill_series].copy()
            df_drill = df_drill[["ym","brand","combo","name","supply","forecast","actual","차이","달성률(%)"]].sort_values("달성률(%)")
            df_drill["supply"] = df_drill["supply"].replace({"<NA>": "미분류"})
            d_f = int(df_drill["forecast"].sum())
            d_a = int(df_drill["actual"].sum())
            d_r = round(d_a/d_f*100,1) if d_f>0 else 0.0
            d_d = d_a - d_f
            kpi_color = "#10B981" if d_r>=100 else "#F59E0B" if d_r>=90 else "#EF4444"
            sign = "+" if d_d>=0 else ""
            kpi_html = (
                '<div style="display:flex;gap:12px;margin-bottom:14px;flex-wrap:wrap;">' +
                f'<div style="background:#EFF6FF;border-radius:10px;padding:12px 20px;border-left:4px solid #3B82F6;min-width:120px;"><div style="font-size:11px;color:#64748B;font-weight:700;margin-bottom:4px;">예측수요</div><div style="font-size:22px;font-weight:900;color:#3B82F6;">{d_f:,}</div></div>' +
                f'<div style="background:#F0FDF4;border-radius:10px;padding:12px 20px;border-left:4px solid #10B981;min-width:120px;"><div style="font-size:11px;color:#64748B;font-weight:700;margin-bottom:4px;">실수주</div><div style="font-size:22px;font-weight:900;color:#10B981;">{d_a:,}</div></div>' +
                f'<div style="background:#FFF7ED;border-radius:10px;padding:12px 20px;border-left:4px solid {kpi_color};min-width:120px;"><div style="font-size:11px;color:#64748B;font-weight:700;margin-bottom:4px;">달성률</div><div style="font-size:22px;font-weight:900;color:{kpi_color};">{d_r:.1f}%</div></div>' +
                f'<div style="background:#FFF1F2;border-radius:10px;padding:12px 20px;border-left:4px solid #F43F5E;min-width:120px;"><div style="font-size:11px;color:#64748B;font-weight:700;margin-bottom:4px;">오차</div><div style="font-size:22px;font-weight:900;color:{"#10B981" if d_d>=0 else "#EF4444"};">{sign}{d_d:,}</div></div>' +
                f'<div style="background:#F8FAFF;border-radius:10px;padding:12px 20px;border-left:4px solid #8B5CF6;min-width:120px;"><div style="font-size:11px;color:#64748B;font-weight:700;margin-bottom:4px;">품목 수</div><div style="font-size:22px;font-weight:900;color:#8B5CF6;">{len(df_drill):,}건</div></div>' +
                '</div>'
            )
            st.markdown(kpi_html, unsafe_allow_html=True)
            def cr(v):
                if isinstance(v,(int,float)):
                    if v>=100: return "background:#D1FAE5;color:#065F46;font-weight:700"
                    if v>=90:  return "background:#FEF9C3;color:#92400E;font-weight:700"
                    return "background:#FEE2E2;color:#991B1B;font-weight:700"
                return ""
            def cd(v):
                if isinstance(v,(int,float)):
                    if v>0: return "color:#059669;font-weight:600"
                    if v<0: return "color:#DC2626;font-weight:600"
                return ""
            styled_drill = (
                df_drill.rename(columns={"ym":"월","brand":"브랜드","combo":"콤보","name":"품목명",
                                         "supply":"공급단","forecast":"예측수요","actual":"실수주",
                                         "차이":"차이(실-예측)","달성률(%)":"달성률(%)"})
                .style
                .format({"예측수요":"{:,.0f}","실수주":"{:,.0f}","차이(실-예측)":"{:+,.0f}","달성률(%)":"{:.1f}%"})
                .applymap(cr, subset=["달성률(%)"])
                .applymap(cd, subset=["차이(실-예측)"])
            )
            st.dataframe(styled_drill, use_container_width=True, height=min(400, 40+len(df_drill)*35))
        st.markdown('</div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  탭4: 상세 데이터
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab4:
    df_det=apply_filters(mg_all,ym=sel_ym if not sel_ym_range else None,ym_range=sel_ym_range,brands=sel_brands,supply=sel_supply)
    if df_det.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    else:
        st.markdown('<div class="filter-card">', unsafe_allow_html=True)
        dc1,dc2,dc3=st.columns([2,2,1])
        with dc1: search=st.text_input("🔍 검색",placeholder="콤보코드 / 시리즈명 / 품목명...")
        with dc2: sort_by=st.selectbox("🔃 정렬 기준",["오차량 큰 순","예측수요 큰 순","실수주 큰 순","달성률 높은 순","달성률 낮은 순"])
        with dc3: show_n=st.slider("📋 표시 행 수",10,300,50)
        st.markdown('</div>', unsafe_allow_html=True)

        sort_map={"오차량 큰 순":("오차량",False),"예측수요 큰 순":("forecast",False),"실수주 큰 순":("actual",False),"달성률 높은 순":("달성률(%)",False),"달성률 낮은 순":("달성률(%)",True)}
        sc,sa=sort_map[sort_by]
        df_det2=df_det.sort_values(sc,ascending=sa)
        if search:
            mask=(df_det2["combo"].str.contains(search,case=False,na=False)|df_det2["series"].str.contains(search,case=False,na=False)|df_det2["name"].str.contains(search,case=False,na=False))
            df_det2=df_det2[mask]

        total_rows=len(df_det2)
        st.markdown(f"<div style='font-size:14px;color:#64748B;margin-bottom:8px'>조건에 맞는 데이터 <b style='color:#1D4ED8'>{total_rows:,}건</b> 중 상위 <b style='color:#1D4ED8'>{min(show_n,total_rows)}건</b> 표시</div>",unsafe_allow_html=True)

        cols_show=["ym","brand","series","combo","name","supply","forecast","actual","차이","달성률(%)"]
        display_det=df_det2[cols_show].head(show_n).copy()
        display_det["supply"]=display_det["supply"].replace({"<NA>":"미분류"})
        styled_det=(display_det.style.format({"forecast":"{:,.0f}","actual":"{:,.0f}","차이":"{:,.0f}","달성률(%)":"{:.1f}%"}).applymap(lambda v:"background:#FEE2E2;color:#991B1B" if isinstance(v,(int,float)) and v<0 else "",subset=["차이"]))
        st.dataframe(styled_det,use_container_width=True,height=400)
        csv_data=df_det2[cols_show].to_csv(index=False,encoding="utf-8-sig")
        st.download_button("⬇️  CSV 다운로드",data=csv_data,file_name=f"forecast_detail_{period_label.replace(' ','').replace('~','_')}.csv",mime="text/csv")

        st.markdown("<div style='height:24px'></div>",unsafe_allow_html=True)

        if not df_det2.empty:
            t_fc=int(df_det2["forecast"].sum()); t_ac=int(df_det2["actual"].sum())
            t_diff=t_ac-t_fc; t_rate=round(t_ac/t_fc*100,1) if t_fc>0 else 0.0
            n_rows=len(df_det2)
            over110=df_det2[df_det2["달성률(%)"]>110]; ok90_110=df_det2[(df_det2["달성률(%)"]>=90)&(df_det2["달성률(%)"]<=110)]; under90=df_det2[df_det2["달성률(%)"]<90]
            top5_err=df_det2.nlargest(5,"오차량")[["series","combo","name","forecast","actual","차이","달성률(%)"]]
            top3_over=df_det2[df_det2["차이"]>0].nlargest(3,"차이")[["series","combo","name","forecast","actual","차이"]]
            top3_under=df_det2[df_det2["차이"]<0].nsmallest(3,"차이")[["series","combo","name","forecast","actual","차이"]]
            brand_sum=df_det2.groupby("brand").agg(forecast=("forecast","sum"),actual=("actual","sum")).reset_index()
            brand_sum["rate"]=np.where(brand_sum["forecast"]>0,(brand_sum["actual"]/brand_sum["forecast"]*100).round(1),0)
            sr_sum=df_det2.groupby(["combo","name","series"],as_index=False).agg(forecast=("forecast","sum"),actual=("actual","sum"))
            sr_sum["rate"]=np.where(sr_sum["forecast"]>0,(sr_sum["actual"]/sr_sum["forecast"]*100).round(1),0)
            month_label2 = period_label
            filter_desc = month_label2
            if sel_supply!="전체": filter_desc+=f" · {sel_supply}"
            if search: filter_desc+=f" · 검색: '{search}'"
            if t_rate>=100: rate_color="highlight-green";rate_word="초과달성"
            elif t_rate>=90: rate_color="highlight-warn";rate_word="근접"
            else: rate_color="highlight-red";rate_word="미달"
            diff_sign="+" if t_diff>=0 else ""; diff_color="highlight-green" if t_diff>=0 else "highlight-red"
            summary_html=f"""<div class="an-summary"><b>{filter_desc}</b> 기준 <b>{n_rows:,}건</b> 품목 분석 결과, 예측 수요 <b class="highlight-blue">{fmt_int(t_fc)}</b>개 대비 실 수주 <b class="highlight-blue">{fmt_int(t_ac)}</b>개 — 달성률 <b class="{rate_color}">{t_rate:.1f}% ({rate_word})</b>, 오차 <b class="{diff_color}">{diff_sign}{fmt_int(t_diff)}</b>개. &nbsp;·&nbsp; 달성률 구간: <span style="color:#EF4444;font-weight:700">미달(&lt;90%) {len(under90)}건</span> / <span style="color:#D97706;font-weight:700">근접(90~110%) {len(ok90_110)}건</span> / <span style="color:#059669;font-weight:700">초과(&gt;110%) {len(over110)}건</span></div>"""

            st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="analysis-title">🔬 현재 조건 상세 분석 · <span style="font-size:13px;color:#64748B;font-weight:500">정렬: {sort_by}</span></div>',unsafe_allow_html=True)
            st.markdown(summary_html,unsafe_allow_html=True)
            st.markdown("<div style='height:16px'></div>",unsafe_allow_html=True)

            col_a,col_b=st.columns([3,2])
            with col_a:
                st.markdown('<div class="an-section"><div class="an-section-title">📌 오차 상위 5개 품목</div>',unsafe_allow_html=True)
                for _,row in top5_err.iterrows():
                    if row["달성률(%)"]>110: badge_cls,badge_txt="badge-over","초과"
                    elif row["달성률(%)"]>=90: badge_cls,badge_txt="badge-ok","근접"
                    else: badge_cls,badge_txt="badge-danger","미달"
                    sign="+"; diff_c="#059669" if row["차이"]>=0 else "#DC2626"
                    if row["차이"]<0: sign=""
                    combo_str=str(row["combo"]); name_str=str(row.get("name","")) if str(row.get("name","")) not in ("nan","") else "—"; series_str=str(row.get("series",""))
                    st.markdown(f"<div class='an-row' style='align-items:flex-start;gap:12px;padding:14px 16px'><span class='an-badge {badge_cls}' style='margin-top:2px;flex-shrink:0'>{badge_txt} {row['달성률(%)']:.0f}%</span><div style='min-width:0;flex:1'><div style='font-size:16px;font-weight:900;color:#1D4ED8;margin-bottom:2px'>{combo_str}</div><div style='font-size:13px;font-weight:700;color:#0F172A;margin-bottom:5px'>{name_str}</div><div style='margin-bottom:6px'><span style='font-size:11px;background:#F1F5F9;color:#64748B;border-radius:4px;padding:2px 7px;font-weight:600'>{series_str}</span></div><div style='font-size:13px;color:#475569'>예측 <b>{fmt_int(row['forecast'])}</b> → 실적 <b>{fmt_int(row['actual'])}</b> <b style='color:{diff_c}'>({sign}{fmt_int(row['차이'])})</b></div></div></div>",unsafe_allow_html=True)
                st.markdown('</div>',unsafe_allow_html=True)

            with col_b:
                st.markdown('<div class="an-section"><div class="an-section-title">🏷️ 브랜드별 달성률</div>',unsafe_allow_html=True)
                for _,row in brand_sum.sort_values("rate",ascending=False).iterrows():
                    if row["rate"]>=100: bc,bw="#D1FAE5","#065F46"
                    elif row["rate"]>=90: bc,bw="#FEF9C3","#92400E"
                    else: bc,bw="#FEE2E2","#991B1B"
                    bar_pct=min(int(row["rate"]),200)
                    st.markdown(f"<div class='an-row' style='display:block;padding:10px 14px'><div style='display:flex;justify-content:space-between;margin-bottom:6px'><b style='color:#0F172A'>{row['brand']}</b><b style='background:{bc};color:{bw};padding:2px 10px;border-radius:99px;font-size:13px'>{row['rate']:.1f}%</b></div><div style='background:#F1F5F9;border-radius:4px;height:8px;overflow:hidden'><div style='width:{bar_pct/2}%;height:8px;background:{'#34D399' if row['rate']>=100 else '#FBBF24' if row['rate']>=90 else '#F87171'};border-radius:4px'></div></div><div style='font-size:12px;color:#94A3B8;margin-top:4px'>예측 {fmt_int(row['forecast'])} / 실적 {fmt_int(row['actual'])}</div></div>",unsafe_allow_html=True)
                st.markdown('</div>',unsafe_allow_html=True)

            st.markdown("<div style='height:12px'></div>",unsafe_allow_html=True)
            col_c,col_d=st.columns(2)
            with col_c:
                st.markdown('<div class="an-section"><div class="an-section-title">🔺 예측 초과 상위 3개</div>',unsafe_allow_html=True)
                if top3_over.empty:
                    st.markdown("<div style='color:#94A3B8;font-size:14px;padding:8px'>초과 품목 없음</div>",unsafe_allow_html=True)
                else:
                    for _,row in top3_over.iterrows():
                        name_str=str(row.get("name","")) if str(row.get("name","")) not in ("nan","") else "—"
                        st.markdown(f"<div class='an-row' style='align-items:flex-start;gap:12px;padding:14px 16px'><span class='an-badge badge-over' style='margin-top:2px;flex-shrink:0'>+{fmt_int(row['차이'])}</span><div><div style='font-size:15px;font-weight:900;color:#1D4ED8'>{str(row['combo'])}</div><div style='font-size:13px;font-weight:700;color:#0F172A'>{name_str}</div><div style='font-size:13px;color:#475569;margin-top:4px'>예측 <b>{fmt_int(row['forecast'])}</b> → 실적 <b>{fmt_int(row['actual'])}</b></div></div></div>",unsafe_allow_html=True)
                st.markdown('</div>',unsafe_allow_html=True)

            with col_d:
                st.markdown('<div class="an-section"><div class="an-section-title">🔻 예측 미달 상위 3개</div>',unsafe_allow_html=True)
                if top3_under.empty:
                    st.markdown("<div style='color:#94A3B8;font-size:14px;padding:8px'>미달 품목 없음</div>",unsafe_allow_html=True)
                else:
                    for _,row in top3_under.iterrows():
                        name_str=str(row.get("name","")) if str(row.get("name","")) not in ("nan","") else "—"
                        st.markdown(f"<div class='an-row' style='align-items:flex-start;gap:12px;padding:14px 16px'><span class='an-badge badge-danger' style='margin-top:2px;flex-shrink:0'>{fmt_int(row['차이'])}</span><div><div style='font-size:15px;font-weight:900;color:#DC2626'>{str(row['combo'])}</div><div style='font-size:13px;font-weight:700;color:#0F172A'>{name_str}</div><div style='font-size:13px;color:#475569;margin-top:4px'>예측 <b>{fmt_int(row['forecast'])}</b> → 실적 <b>{fmt_int(row['actual'])}</b></div></div></div>",unsafe_allow_html=True)
                st.markdown('</div>',unsafe_allow_html=True)

            st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
            col_e,col_f=st.columns(2)
            with col_e:
                st.markdown('<div class="an-section"><div class="an-section-title">⚠️ 달성률 하위 품목 TOP 5</div>',unsafe_allow_html=True)
                bot5_item=sr_sum[sr_sum["forecast"]>0].nsmallest(5,"rate")
                for _,row in bot5_item.iterrows():
                    pct=min(int(row["rate"]),200); name_str=str(row.get("name","")) if str(row.get("name","")) not in ("nan","") else "—"
                    st.markdown(f"<div class='an-row' style='display:block;padding:12px 14px'><div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:3px'><b style='font-size:14px;color:#DC2626'>{str(row['combo'])}</b><b style='color:#DC2626;font-size:14px'>{row['rate']:.1f}%</b></div><div style='font-size:12px;font-weight:700;color:#0F172A;margin-bottom:4px'>{name_str}</div><div style='margin-bottom:6px'><span style='font-size:11px;background:#F1F5F9;color:#64748B;border-radius:4px;padding:2px 7px;font-weight:600'>{str(row.get('series',''))}</span></div><div style='background:#F1F5F9;border-radius:4px;height:6px;overflow:hidden'><div style='width:{pct/2}%;height:6px;background:#F87171;border-radius:4px'></div></div><div style='font-size:12px;color:#94A3B8;margin-top:4px'>예측 {fmt_int(row['forecast'])} / 실적 {fmt_int(row['actual'])}</div></div>",unsafe_allow_html=True)
                st.markdown('</div>',unsafe_allow_html=True)

            with col_f:
                st.markdown('<div class="an-section"><div class="an-section-title">✅ 달성률 상위 품목 TOP 5</div>',unsafe_allow_html=True)
                top5_item=sr_sum[sr_sum["forecast"]>0].nlargest(5,"rate")
                for _,row in top5_item.iterrows():
                    pct=min(int(row["rate"]),200); name_str=str(row.get("name","")) if str(row.get("name","")) not in ("nan","") else "—"
                    st.markdown(f"<div class='an-row' style='display:block;padding:12px 14px'><div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:3px'><b style='font-size:14px;color:#059669'>{str(row['combo'])}</b><b style='color:#059669;font-size:14px'>{row['rate']:.1f}%</b></div><div style='font-size:12px;font-weight:700;color:#0F172A;margin-bottom:4px'>{name_str}</div><div style='margin-bottom:6px'><span style='font-size:11px;background:#F1F5F9;color:#64748B;border-radius:4px;padding:2px 7px;font-weight:600'>{str(row.get('series',''))}</span></div><div style='background:#F1F5F9;border-radius:4px;height:6px;overflow:hidden'><div style='width:{pct/2}%;height:6px;background:#34D399;border-radius:4px'></div></div><div style='font-size:12px;color:#94A3B8;margin-top:4px'>예측 {fmt_int(row['forecast'])} / 실적 {fmt_int(row['actual'])}</div></div>",unsafe_allow_html=True)
                st.markdown('</div>',unsafe_allow_html=True)

            st.markdown('</div>',unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  도움말 탭
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_help:

    st.markdown("""
    <style>
    .help-hero {
        background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%);
        border-radius: 20px; padding: 36px 40px; color: white; margin-bottom: 28px;
        box-shadow: 0 8px 32px rgba(29,78,216,0.25);
    }
    .help-hero-title { font-size: 28px; font-weight: 900; letter-spacing: -0.02em; margin-bottom: 8px; }
    .help-hero-sub   { font-size: 16px; opacity: 0.85; line-height: 1.7; }
    .help-step-card {
        background: white; border-radius: 16px; padding: 24px 28px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06); margin-bottom: 16px;
        border-left: 5px solid;
    }
    .help-step-num {
        display: inline-flex; align-items: center; justify-content: center;
        width: 32px; height: 32px; border-radius: 50%;
        font-size: 15px; font-weight: 900; color: white;
        margin-right: 10px; flex-shrink: 0;
    }
    .help-step-title { font-size: 17px; font-weight: 800; color: #0F172A; }
    .help-step-body  { font-size: 14px; color: #475569; line-height: 2.0; margin-top: 10px; padding-left: 42px; }
    .help-tag {
        display: inline-block; padding: 3px 12px; border-radius: 99px;
        font-size: 12px; font-weight: 700; margin: 2px 3px;
    }
    .help-tab-card {
        background: white; border-radius: 14px; padding: 20px 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); height: 100%;
        border-top: 4px solid;
    }
    .help-tab-icon  { font-size: 28px; margin-bottom: 8px; }
    .help-tab-name  { font-size: 15px; font-weight: 800; color: #0F172A; margin-bottom: 6px; }
    .help-tab-desc  { font-size: 13px; color: #64748B; line-height: 1.8; }
    .help-faq-q { font-size: 15px; font-weight: 700; color: #1D4ED8; margin-bottom: 6px; }
    .help-faq-a { font-size: 14px; color: #475569; line-height: 1.9; margin-bottom: 20px; padding-left: 4px; border-left: 3px solid #BFDBFE; padding-left: 12px; }
    .help-tip-box {
        background: linear-gradient(135deg, #F0FDF4 0%, #ECFDF5 100%);
        border-radius: 12px; padding: 18px 22px;
        border: 1.5px solid #A7F3D0; font-size: 14px;
        color: #065F46; line-height: 2.0;
    }
    </style>

    <!-- 히어로 배너 -->
    <div class="help-hero">
        <div class="help-hero-title">📦 수요예측 모니터링 대시보드</div>
        <div class="help-hero-sub">
            예측 수요와 실수주 데이터를 한눈에 비교하고,<br>
            AI 어시스턴트와 함께 인사이트를 도출하는 분석 도구입니다.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── STEP 가이드 ──
    st.markdown("### 🚀 시작하기 — 3단계")

    steps = [
        ("#3B82F6", "#DBEAFE", "1", "데이터 준비",
         """CSV 파일 2개를 앱과 같은 폴더에 위치시키세요.<br>
         <span class='help-tag' style='background:#DBEAFE;color:#1D4ED8'>forecast_data.csv</span> — 예측 데이터 (ym, brand, series, combo, name, supply, forecast 컬럼)<br>
         <span class='help-tag' style='background:#DBEAFE;color:#1D4ED8'>actual_data.csv</span> — 실수주 데이터 (ym, combo, actual 컬럼)<br>
         📌 파일이 없어도 샘플 데이터로 자동 실행됩니다."""),
        ("#10B981", "#D1FAE5", "2", "필터 설정",
         """사이드바에서 분석 조건을 선택하세요.<br>
         <span class='help-tag' style='background:#D1FAE5;color:#065F46'>📅 기준 년월</span> 분석할 월 선택 (최신순 정렬)<br>
         <span class='help-tag' style='background:#D1FAE5;color:#065F46'>🏷️ 브랜드</span> 보고 싶은 브랜드만 선택 (다중 선택 가능)<br>
         <span class='help-tag' style='background:#D1FAE5;color:#065F46'>🏭 공급단</span> 특정 공급처만 필터링 (전체 선택 시 전부 표시)"""),
        ("#8B5CF6", "#EDE9FE", "3", "AI 챗봇 활성화 (선택)",
         """사이드바 하단에서 Gemini API 키를 입력하면 AI 분석이 활성화됩니다.<br>
         <span class='help-tag' style='background:#EDE9FE;color:#5B21B6'>🔑 API 키 발급</span> aistudio.google.com → Get API key → Create API key<br>
         <span class='help-tag' style='background:#EDE9FE;color:#5B21B6'>💬 빠른 질문</span> 버튼 클릭 또는 직접 질문 입력<br>
         📌 API 키 없이도 앱의 모든 차트·분석 기능은 정상 사용 가능합니다."""),
    ]

    for color, bg, num, title, body in steps:
        st.markdown(f"""
        <div class="help-step-card" style="border-left-color:{color}">
            <div style="display:flex;align-items:center">
                <span class="help-step-num" style="background:{color}">STEP {num}</span>
                <span class="help-step-title">{title}</span>
            </div>
            <div class="help-step-body">{body}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── 탭별 기능 소개 ──
    st.markdown("### 📑 탭별 기능 소개")
    c1, c2, c3, c4 = st.columns(4)
    tab_info = [
        (c1, "#3B82F6", "📊", "개요",
         "선택 월의 핵심 KPI(예측/실수주/달성률/오차)와 브랜드별 비교 차트, 공급단 비중, 자동 분석 요약을 한눈에 확인"),
        (c2, "#10B981", "📈", "월별 추이",
         "브랜드 또는 시리즈별로 여러 달의 예측·실적 추이를 꺾은선 차트로 비교. 달성률 변화 추이도 함께 확인 가능"),
        (c3, "#F59E0B", "🔎", "시리즈 분석",
         "시리즈별 예측·실수주·차이량을 Top N으로 정렬해 수평 막대차트로 표시. 달성률 구간 분포와 상세 표 제공"),
        (c4, "#8B5CF6", "📋", "상세 데이터",
         "품목 단위 전체 데이터 조회·검색·정렬. CSV 다운로드 및 오차 상위/하위 품목 동적 분석 카드 제공"),
    ]
    for col, color, icon, name, desc in tab_info:
        with col:
            st.markdown(f"""
            <div class="help-tab-card" style="border-top-color:{color}">
                <div class="help-tab-icon">{icon}</div>
                <div class="help-tab-name">{name}</div>
                <div class="help-tab-desc">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # ── FAQ ──
    st.markdown("### ❓ 자주 묻는 질문")
    col_faq1, col_faq2 = st.columns(2)

    with col_faq1:
        st.markdown("""
        <div class='help-faq-q'>Q. 데이터 파일은 어디에 넣어야 하나요?</div>
        <div class='help-faq-a'>앱 파일(app.py)과 같은 폴더에 <b>forecast_data.csv</b>와 <b>actual_data.csv</b>를 넣으면 자동으로 불러옵니다. 파일이 없으면 샘플 데이터로 실행됩니다.</div>

        <div class='help-faq-q'>Q. 달성률은 어떻게 계산되나요?</div>
        <div class='help-faq-a'><b>달성률(%) = 실수주 ÷ 예측수요 × 100</b><br>
        100% 이상이면 초과달성(초록), 90~100%는 근접(노랑), 90% 미만은 미달(빨강)으로 표시됩니다.</div>

        <div class='help-faq-q'>Q. 브랜드를 여러 개 선택할 수 있나요?</div>
        <div class='help-faq-a'>네! 사이드바 브랜드 필터에서 원하는 브랜드를 다중 선택할 수 있습니다. 선택을 모두 해제하면 전체 브랜드가 표시됩니다.</div>
        """, unsafe_allow_html=True)

    with col_faq2:
        st.markdown("""
        <div class='help-faq-q'>Q. AI 챗봇이 답변을 못하면 어떻게 되나요?</div>
        <div class='help-faq-a'>Gemini API 키가 없거나 한도 초과 시에도 앱의 모든 차트와 분석 기능은 정상 동작합니다. 챗봇 기능만 비활성화됩니다.</div>

        <div class='help-faq-q'>Q. CSV 다운로드는 어디서 하나요?</div>
        <div class='help-faq-a'><b>📋 상세 데이터</b> 탭 하단의 <b>⬇️ CSV 다운로드</b> 버튼을 클릭하면 현재 필터·검색 조건이 적용된 데이터를 저장할 수 있습니다.</div>

        <div class='help-faq-q'>Q. 탭 순서를 바꿀 수 있나요?</div>
        <div class='help-faq-a'>네! 상단 탭을 <b>드래그 앤 드롭</b>으로 원하는 순서로 재배치할 수 있습니다.</div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── 팁 박스 ──
    st.markdown("""
    <div class="help-tip-box">
        💡 <b>사용 팁</b><br>
        &nbsp;&nbsp;① 사이드바 필터를 바꾸면 <b>모든 탭이 실시간으로 업데이트</b>됩니다.<br>
        &nbsp;&nbsp;② AI 챗봇에 <b>"이번 달 요약해줘"</b>라고 물어보면 현재 필터 기준 데이터를 자동 분석해줍니다.<br>
        &nbsp;&nbsp;③ 시리즈 분석 탭의 <b>Top N 슬라이더</b>로 표시 품목 수를 조절할 수 있습니다.<br>
        &nbsp;&nbsp;④ 상세 데이터 탭의 <b>검색창</b>에 콤보코드·시리즈명·품목명을 입력해 빠르게 찾을 수 있습니다.
    </div>
    """, unsafe_allow_html=True)
