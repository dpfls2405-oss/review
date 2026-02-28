import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

# 1. 페이지 설정 및 라이트 모드 디자인
st.set_page_config(page_title="수요예측 대시보드", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #1E293B !important; }
    [data-testid="stSidebar"] { background-color: #F8FAFC !important; border-right: 1px solid #E2E8F0; }
    .section-header { 
        font-size: 18px; font-weight: bold; margin: 20px 0 10px 0; 
        color: #2563EB; border-bottom: 2px solid #E2E8F0; padding-bottom: 5px; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 전처리
@st.cache_data
def load_data():
    f = pd.read_csv("forecast_data.csv")
    a = pd.read_csv("actual_data.csv")
    for df in [f, a]:
        for col in ['ym', 'brand', 'series', 'combo', 'name', 'supply']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
    return f, a

f_df, a_df = load_data()

# 3. 사이드바 검색 및 필터 (드롭다운 강화)
st.sidebar.title("🔍 필터 및 검색")

# (1) 기본 필터
sel_ym = st.sidebar.selectbox("📅 기준 년월", sorted(f_df["ym"].unique(), reverse=True))
all_brands = sorted(f_df["brand"].unique().tolist())
sel_br = st.sidebar.multiselect("🏷️ 브랜드 선택", all_brands, default=all_brands)

# (2) 시리즈 드롭다운 추가
current_f = f_df[f_df["brand"].isin(sel_br)] if sel_br else f_df
all_series = sorted(current_f["series"].unique().tolist())
sel_sr = st.sidebar.multiselect("🪑 시리즈 선택", all_series, default=all_series)

# (3) 공급단 드롭다운
all_supplies = sorted(f_df["supply"].unique().tolist())
sel_sp = st.sidebar.multiselect("🏭 공급단 선택", all_supplies, default=all_supplies)

# (4) 정렬 지표 선택 드롭다운 (요청 사항)
sort_metric = st.sidebar.selectbox("🔢 정렬 기준", ["예측량 높은순", "실적량 높은순", "달성률 높은순", "차이 큰순"])

# (5) 품목 검색
search_query = st.sidebar.text_input("📝 품목명/코드 검색", "")

# 4. 데이터 필터링 로직
f_sel = f_df[(f_df["ym"] == sel_ym) & (f_df["brand"].isin(sel_br)) & (f_df["series"].isin(sel_sr)) & (f_df["supply"].isin(sel_sp))].copy()
a_sel = a_df[a_df["ym"] == sel_ym].copy()

if search_query:
    f_sel = f_sel[f_sel["name"].str.contains(search_query, case=False) | f_sel["combo"].str.contains(search_query, case=False)]

# 5. 데이터 병합 및 계산
mg = pd.merge(f_sel, a_sel[["combo", "actual"]], on="combo", how="left")
mg["actual"] = mg["actual"].fillna(0)
mg["차이"] = mg["actual"] - mg["forecast"]
mg["달성률(%)"] = np.where(mg["forecast"] > 0, (mg["actual"] / mg["forecast"] * 100).round(1), 0)

# 6. 정렬 적용
sort_map = {
    "예측량 높은순": ("forecast", False), "실적량 높은순": ("actual", False),
    "달성률 높은순": ("달성률(%)", False), "차이 큰순": ("차이", True)
}
col, asc = sort_map[sort_metric]
mg = mg.sort_values(by=col, ascending=asc)

# 7. 메인 화면 구성
st.title("📊 수요예측 분석 대시보드")

# 요약 지표 (KPI)
c1, c2, c3 = st.columns(3)
c1.metric("총 예측량", f"{int(mg['forecast'].sum()):,}")
c2.metric("총 실적량", f"{int(mg['actual'].sum()):,}")
c3.metric("평균 달성률", f"{mg['달성률(%)'].mean():.1f}%")

# 📥 다운로드 버튼
buf = io.BytesIO()
mg.to_csv(buf, index=False, encoding="utf-8-sig")
st.download_button(f"⬇️ {sel_ym} 데이터 다운로드", buf.getvalue(), f"data_{sel_ym}.csv", "text/csv")

# 8. 간략한 데이터 집계표 (HTML 버전 느낌)
st.markdown(f'<div class="section-header">📋 {sel_ym} 요약 집계 내역</div>', unsafe_allow_html=True)

# 표에 노출할 핵심 열만 선택 (간략하게)
summary_df = mg.rename(columns={
    "brand": "브랜드", "series": "시리즈", "name": "품목명", 
    "forecast": "예측", "actual": "실적"
})[["브랜드", "시리즈", "품목명", "예측", "실적", "차이", "달성률(%)"]]

st.dataframe(summary_df, use_container_width=True, hide_index=True)

# 9. 상위 10개 시각화
if not mg.empty:
    st.markdown('<div class="section-header">📈 항목별 실적 비교</div>', unsafe_allow_html=True)
    chart_data = mg.head(10)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=chart_data['name'], y=chart_data['forecast'], name='예측', marker_color='#94A3B8'))
    fig.add_trace(go.Bar(x=chart_data['name'], y=chart_data['actual'], name='실적', marker_color='#2563EB'))
    fig.update_layout(template='plotly_white', barmode='group', height=350, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
