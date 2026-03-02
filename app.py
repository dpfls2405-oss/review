import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import google.generativeai as genai
import time

# ══════════════════════════════════════════════
#  페이지 설정 및 스타일 (이미지 대시보드 테마 반영)
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="수요예측 모니터링 대시보드",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; background-color: #F8F9FC; }
.stApp { background-color: #F8F9FC; }

/* KPI 카드 스타일 - 이미지의 라운드 및 색상 반영 */
.kpi-wrap { background: white; border-radius: 12px; padding: 20px; border-left: 6px solid; box-shadow: 0 4px 12px rgba(0,0,0,0.05); height: 100%; }
.kpi-label { font-size: 14px; color: #858796; font-weight: 700; margin-bottom: 15px; }
.kpi-value { font-size: 30px; font-weight: 800; color: #4E73DF; }
.kpi-sub { font-size: 12px; color: #B7B9CC; margin-top: 10px; }

/* 섹션 카드 */
.section-card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.03); margin-bottom: 16px; border: 1px solid #E3E6F0; }
.section-title { font-size: 16px; font-weight: 700; color: #4E73DF; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  데이터 로드 및 '부품류 제외' 필터링 로직
# ══════════════════════════════════════════════
@st.cache_data
def load_and_preprocess_data():
    # 1. 원본 데이터 로드 (파일이 없을 경우 가상 데이터 생성)
    try:
        f = pd.read_csv("forecast_data.csv")
        a = pd.read_csv("actual_data.csv")
    except:
        # 가상 데이터 샘플 (테스트용)
        dates = ["2026-01", "2026-02"]
        brands = ["데스커", "일룸", "퍼시스", "시디즈"]
        series_pool = ["T50", "T80", "RINGO", "ACCESSORY", "악세사리", "부품세트", "가스실린더", "패브릭커버", "SODA"]
        rows, a_rows = [], []
        for ym in dates:
            for b in brands:
                for s in series_pool:
                    combo = f"{s}-{b[:2]}"
                    fc = np.random.randint(500, 3000)
                    ac = int(fc * np.random.uniform(0.8, 1.2))
                    rows.append({'ym': ym, 'brand': b, 'series': s, 'combo': combo, 'forecast': fc, 'supply': '시디즈(평택)'})
                    a_rows.append({'ym': ym, 'combo': combo, 'actual': ac})
        f, a = pd.DataFrame(rows), pd.DataFrame(a_rows)

    # 2. 데이터 병합
    mg = pd.merge(f, a, on=["ym", "combo"], how="left").fillna(0)
    
    # 3. ★ 핵심: 부품류 키워드 제외 필터링 ★
    exclude_keywords = [
        'ACCESSORY', '악세사리', '이지리페어', 'EASY REPAIR', 
        '부품', 'PARTS', '리페어', 'REPAIR', '패브릭', '가스', '실린더'
    ]
    # 키워드 중 하나라도 포함되어 있으면 제외 (대소문자 구분 안 함)
    pattern = '|'.join(exclude_keywords)
    mg = mg[~mg['series'].str.contains(pattern, case=False, na=False)]
    
    # 4. 파생 변수 계산
    mg["차이"] = mg["actual"] - mg["forecast"]
    mg["오차량"] = mg["차이"].abs()
    
    return mg

mg_all = load_and_preprocess_data()

# ══════════════════════════════════════════════
#  사이드바 및 필터 제어
# ══════════════════════════════════════════════
with st.sidebar:
    st.header("🔍 조회 조건")
    ym_opts = sorted(mg_all["ym"].unique(), reverse=True)
    sel_ym = st.selectbox("기준 월 선택", ym_opts)
    
    brands = sorted(mg_all["brand"].unique())
    sel_brands = st.multiselect("브랜드 선택", brands, default=brands)
    
    st.divider()
    api_key = st.text_input("Gemini API Key", type="password")

# 필터 적용 데이터
df_final = mg_all[(mg_all["ym"] == sel_ym) & (mg_all["brand"].isin(sel_brands))]

# ══════════════════════════════════════════════
#  메인 화면 - (제목에 '부품류 제외' 명시)
# ══════════════════════════════════════════════
st.title(f"📊 {sel_ym} 수요예측 모니터링 (부품류 제외)")

# 상단 탭 메뉴 (이미지 참고)
tabs = st.tabs(["📊 개요", "📈 월별 추이", "🔎 시리즈 분석", "📋 상세 데이터"])

with tabs[0]:
    # KPI 섹션
    f_sum = df_final["forecast"].sum()
    a_sum = df_final["actual"].sum()
    gap = a_sum - f_sum
    acc_rate = (a_sum / f_sum * 100) if f_sum > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'''<div class="kpi-wrap" style="border-left-color:#4E73DF;">
            <div class="kpi-label">예측 수요</div>
            <div class="kpi-value">{f_sum:,.0f}</div>
            <div class="kpi-sub">{sel_ym} 예측 합계</div>
        </div>''', unsafe_allow_html=True)
    with col2:
        st.markdown(f'''<div class="kpi-wrap" style="border-left-color:#1CC88A;">
            <div class="kpi-label">실 수주</div>
            <div class="kpi-value" style="color:#1CC88A;">{a_sum:,.0f}</div>
            <div class="kpi-sub">{sel_ym} 실 수주 합계</div>
        </div>''', unsafe_allow_html=True)
    with col3:
        gap_color = "#E74A3B" if gap < 0 else "#4E73DF"
        arrow = "▼" if gap < 0 else "▲"
        st.markdown(f'''<div class="kpi-wrap" style="border-left-color:#E74A3B;">
            <div class="kpi-label">예측 오차</div>
            <div class="kpi-value" style="color:{gap_color};">{arrow} {abs(gap):,.0f}</div>
            <div class="kpi-sub">실 수주 - 예측</div>
        </div>''', unsafe_allow_html=True)
    with col4:
        st.markdown(f'''<div class="kpi-wrap" style="border-left-color:#F6C23E;">
            <div class="kpi-label">달성률</div>
            <div class="kpi-value" style="color:#F6C23E;">{acc_rate:.1f}%</div>
            <div class="kpi-sub">실 수주 ÷ 예측 × 100</div>
        </div>''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 차트 섹션
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown('<div class="section-card"><div class="section-title">브랜드별 실적 (부품류 제외)</div>', unsafe_allow_html=True)
        brand_data = df_final.groupby("brand")[["forecast", "actual"]].sum().reset_index()
        fig = go.Figure([
            go.Bar(name='예측', x=brand_data['brand'], y=brand_data['forecast'], marker_color='#D1D3E2'),
            go.Bar(name='실적', x=brand_data['brand'], y=brand_data['actual'], marker_color='#4E73DF')
        ])
        fig.update_layout(barmode='group', height=350, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-card"><div class="section-title">오차 상위 Series (부품류 제외)</div>', unsafe_allow_html=True)
        top_error = df_final.groupby("series")["오차량"].sum().nlargest(5).reset_index()
        for i, row in top_error.iterrows():
            st.write(f"**{i+1}. {row['series']}** : {row['오차량']:,} 오차")
        st.markdown('</div>', unsafe_allow_html=True)

with tabs[3]:
    st.markdown('<div class="section-card"><div class="section-title">상세 데이터 내역</div>', unsafe_allow_html=True)
    st.dataframe(df_final.drop(columns=['combo']), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
