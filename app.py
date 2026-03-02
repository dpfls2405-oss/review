import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import google.generativeai as genai
import time

# ══════════════════════════════════════════════
#  페이지 설정 및 스타일
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="수요예측 모니터링 대시보드",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; font-size: 15px; }
.stApp { background-color: #EAECF4; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0A1628 0%, #172035 100%); border-right: 1px solid #2A3A52; }
section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] label { color: #DDE3EE !important; }

/* KPI 카드 스타일 */
.kpi-wrap { background: white; border-radius: 16px; padding: 24px; border-left: 5px solid; box-shadow: 0 4px 16px rgba(0,0,0,0.07); height: 100%; }
.kpi-label { font-size: 13px; color: #64748B; font-weight: 700; text-transform: uppercase; margin-bottom: 10px; }
.kpi-value { font-size: 32px; font-weight: 900; line-height: 1; }
.kpi-sub { font-size: 12px; color: #94A3B8; margin-top: 8px; }

/* 섹션 카드 */
.section-card { background: white; border-radius: 16px; padding: 24px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 16px; }
.section-title { font-size: 17px; font-weight: 700; color: #0F172A; margin-bottom: 18px; padding-bottom: 12px; border-bottom: 2px solid #EFF6FF; }

/* 사이드바 챗봇 헤더 */
.sb-chat-header { background: linear-gradient(135deg, #1D4ED8, #1E40AF); border-radius: 10px; padding: 12px; margin-bottom: 10px; }
.sb-chat-header-title { font-size: 14px; font-weight: 900; color: white; }
.sb-chat-header-sub { font-size: 11px; color: rgba(255,255,255,0.7); margin-top: 2px; }

/* 버튼 커스텀 */
section[data-testid="stSidebar"] .stButton > button {
    background: #1C2B3F !important; border: 1.5px solid #3D5A80 !important;
    border-radius: 8px !important; color: #93C5FD !important; font-size: 12px !important;
    width: 100% !important; transition: all 0.2s;
}
section[data-testid="stSidebar"] .stButton > button:hover { background: #2563EB !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  데이터 로드 및 전처리
# ══════════════════════════════════════════════
@st.cache_data
def load_data():
    # CSV가 없을 경우를 대비한 가상 데이터 생성
    try:
        f = pd.read_csv("forecast_data.csv")
        a = pd.read_csv("actual_data.csv")
    except:
        dates = ["2025-11", "2025-12", "2026-01", "2026-02"]
        brands = ["데스커", "일룸", "퍼시스", "시디즈"]
        series = ["T50", "T80", "IBLE", "RINGO", "SODA"]
        rows, a_rows = [], []
        for ym in dates:
            for b in brands:
                for s in series:
                    combo = f"{s}-{b[:2]}"
                    fc = np.random.randint(500, 3000)
                    ac = int(fc * np.random.uniform(0.7, 1.3))
                    rows.append({'ym': ym, 'brand': b, 'series': s, 'combo': combo, 'forecast': fc, 'supply': '시디즈(평택)'})
                    a_rows.append({'ym': ym, 'combo': combo, 'actual': ac})
        f, a = pd.DataFrame(rows), pd.DataFrame(a_rows)
    return f, a

f_df, a_df = load_data()
mg_all = pd.merge(f_df, a_df, on=["ym", "combo"], how="left").fillna(0)
mg_all["차이"] = mg_all["actual"] - mg_all["forecast"]
mg_all["오차량"] = mg_all["차이"].abs()
mg_all["달성률(%)"] = np.where(mg_all["forecast"] > 0, (mg_all["actual"] / mg_all["forecast"] * 100).round(1), 0)

# ══════════════════════════════════════════════
#  유틸리티 및 AI 엔진
# ══════════════════════════════════════════════
def apply_filters(df, ym=None, ym_range=None, brands=None, supply=None):
    d = df.copy()
    if ym_range:
        d = d[(d["ym"] >= ym_range[0]) & (d["ym"] <= ym_range[1])]
    elif ym:
        d = d[d["ym"] == ym]
    if brands: d = d[d["brand"].isin(brands)]
    if supply and supply != "전체": d = d[d["supply"] == supply]
    return d

def call_gemini_with_retry(api_key, system_instruction, history, prompt, max_retries=3):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=system_instruction)
        chat = model.start_chat(history=history)
        for attempt in range(max_retries):
            try:
                response = chat.send_message(prompt, generation_config=genai.types.GenerationConfig(max_output_tokens=500, temperature=0.7))
                return response.text, None
            except Exception as e:
                err_msg = str(e)
                if ("429" in err_msg or "quota" in err_msg.lower()) and attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None, err_msg
    except Exception as e:
        return None, str(e)

def build_context(df, period_label):
    if df.empty: return "데이터 없음"
    t_f, t_a = int(df["forecast"].sum()), int(df["actual"].sum())
    t_r = round(t_a/t_f*100, 1) if t_f > 0 else 0
    return f"기간: {period_label}, 예측: {t_f:,}, 실적: {t_a:,}, 달성률: {t_r}%"

# ══════════════════════════════════════════════
#  사이드바 UI 및 챗봇
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div style="font-size:18px; font-weight:900; color:white; padding:10px 0;">📦 수요예측 엔진</div>', unsafe_allow_html=True)
    
    view_mode = st.radio("조회 방식", ["단일 월", "기간 범위"], horizontal=True)
    ym_opts = sorted(mg_all["ym"].unique(), reverse=True)
    
    sel_ym, sel_ym_range = None, None
    if view_mode == "단일 월":
        sel_ym = st.selectbox("기준 월", ym_opts)
        period_label = sel_ym
    else:
        col1, col2 = st.columns(2)
        with col1: start_m = st.selectbox("시작", sorted(ym_opts))
        with col2: end_m = st.selectbox("종료", ym_opts)
        sel_ym_range = (start_m, end_m)
        period_label = f"{start_m}~{end_m}"

    brands = sorted(mg_all["brand"].unique())
    sel_brands = st.multiselect("브랜드", brands, default=brands)
    sel_supply = st.selectbox("공급단", ["전체", "시디즈(평택)", "베트남", "외주/상품"])

    st.markdown("---")
    api_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...")
    
    st.markdown('<div class="sb-chat-header"><div class="sb-chat-header-title">🤖 AI 분석 어시스턴트</div></div>', unsafe_allow_html=True)
    
    if "messages" not in st.session_state: st.session_state.messages = []
    
    # 빠른 질문 버튼
    if st.button("📊 전체 현황 요약"): st.session_state.quick_query = "현재 필터링된 데이터의 전체 달성률과 주요 이슈를 요약해줘."
    if st.button("⚠️ 오차 원인 분석"): st.session_state.quick_query = "오차가 큰 품목들을 중심으로 원인을 추정하고 대책을 제안해줘."

    # 대화창 (최근 3개)
    for m in st.session_state.messages[-3:]:
        with st.chat_message(m["role"]):
            st.markdown(f'<div style="font-size:12px;">{m["content"]}</div>', unsafe_allow_html=True)

    chat_input = st.chat_input("데이터에 대해 물어보세요")
    
    prompt = None
    if chat_input: prompt = chat_input
    elif "quick_query" in st.session_state:
        prompt = st.session_state.quick_query
        del st.session_state.quick_query

    if prompt:
        if not api_key: st.warning("API 키를 입력하세요.")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            df_curr = apply_filters(mg_all, sel_ym, sel_ym_range, sel_brands, sel_supply)
            ctx = build_context(df_curr, period_label)
            sys_inst = f"당신은 공급망 분석가입니다. 다음 데이터를 기반으로 짧고 명확하게 답하세요: {ctx}"
            
            with st.spinner("생각 중..."):
                hist = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[-5:-1]]
                res, err = call_gemini_with_retry(api_key, sys_inst, hist, prompt)
                if res: st.session_state.messages.append({"role": "model", "content": res})
                else: st.error(f"Error: {err}")
            st.rerun()

# ══════════════════════════════════════════════
#  메인 대시보드 화면
# ══════════════════════════════════════════════
df_final = apply_filters(mg_all, sel_ym, sel_ym_range, sel_brands, sel_supply)

st.title(f"📊 {period_label} 수요예측 모니터링")

# KPI 섹션
k1, k2, k3, k4 = st.columns(4)
f_sum, a_sum = df_final["forecast"].sum(), df_final["actual"].sum()
acc_rate = (a_sum / f_sum * 100) if f_sum > 0 else 0

with k1: st.markdown(f'<div class="kpi-wrap" style="border-left-color:#3B82F6;"><div class="kpi-label">Forecast</div><div class="kpi-value">{f_sum:,.0f}</div></div>', unsafe_allow_html=True)
with k2: st.markdown(f'<div class="kpi-wrap" style="border-left-color:#10B981;"><div class="kpi-label">Actual</div><div class="kpi-value">{a_sum:,.0f}</div></div>', unsafe_allow_html=True)
with k3: 
    color = "#10B981" if 90 <= acc_rate <= 110 else "#EF4444"
    st.markdown(f'<div class="kpi-wrap" style="border-left-color:{color};"><div class="kpi-label">Achievement</div><div class="kpi-value" style="color:{color}">{acc_rate:.1f}%</div></div>', unsafe_allow_html=True)
with k4: st.markdown(f'<div class="kpi-wrap" style="border-left-color:#64748B;"><div class="kpi-label">Gap</div><div class="kpi-value">{(a_sum-f_sum):+,.0f}</div></div>', unsafe_allow_html=True)

st.markdown("---")

tab1, tab2 = st.tabs(["📈 시각화 분석", "📋 데이터 리스트"])

with tab1:
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown('<div class="section-card"><div class="section-title">브랜드별 실적 비교</div>', unsafe_allow_html=True)
        b_df = df_final.groupby("brand")[["forecast", "actual"]].sum().reset_index()
        fig = go.Figure([
            go.Bar(name='예측', x=b_df['brand'], y=b_df['forecast'], marker_color='#93C5FD'),
            go.Bar(name='실적', x=b_df['brand'], y=b_df['actual'], marker_color='#2563EB')
        ])
        fig.update_layout(barmode='group', height=400, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with c2:
        st.markdown('<div class="section-card"><div class="section-title">오차 상위 Series (Top 5)</div>', unsafe_allow_html=True)
        err_df = df_final.groupby("series")["오차량"].sum().nlargest(5).reset_index()
        for i, row in err_df.iterrows():
            st.write(f"**{i+1}. {row['series']}** : {row['오차량']:,} 수량 오차")
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.dataframe(df_final.drop(columns=['combo']), use_container_width=True, hide_index=True)
