import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

# 1. 밝은 테마 강제 고정 및 스타일링
st.set_page_config(page_title="수요예측 대시보드", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    /* 전체 배경을 밝은 회색으로, 글자색을 검정으로 강제 고정 */
    .stApp { background-color: #FFFFFF !important; color: #1E293B !important; }
    [data-testid="stSidebar"] { background-color: #F8FAFC !important; border-right: 1px solid #E2E8F0; }
    /* 검색창 및 입력도구 스타일 */
    .stTextInput input, .stSelectbox div, .stMultiSelect div { background-color: white !important; color: black !important; border: 1px solid #CBD5E1 !important; }
    /* 헤더 스타일 */
    .section-header { 
        font-size: 18px; font-weight: bold; margin: 20px 0 10px 0; 
        color: #2563EB; border-bottom: 2px solid #E2E8F0; padding-bottom: 5px; 
    }
    /* 메트릭 카드 */
    [data-testid="stMetricValue"] { color: #1E293B !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 전처리 (데이터 유실 방지 핵심)
@st.cache_data
def load_data():
    f = pd.read_csv("forecast_data.csv")
    a = pd.read_csv("actual_data.csv")
    
    # 공백 제거 및 결측치 처리
    for df in [f, a]:
        df['combo'] = df['combo'].astype(str).str.strip()
        df['supply'] = df['supply'].fillna("미지정").astype(str).str.strip()
        df['brand'] = df['brand'].fillna("기타").astype(str).str.strip()
        
    return f, a

f_df, a_df = load_data()

# 3. 사이드바 검색 및 드롭다운 필터
st.sidebar.title("🔍 필터 및 검색")

# (1) 년월 선택
ym_list = sorted(f_df["ym"].unique(), reverse=True)
sel_ym = st.sidebar.selectbox("📅 기준 년월", ym_list)

# (2) 브랜드 선택 (드롭다운)
all_brands = sorted(f_df["brand"].unique().tolist())
sel_br = st.sidebar.multiselect("🏷️ 브랜드", all_brands, default=all_brands)

# (3) 공급단 선택 (드롭다운 - 작동 확인 완료)
all_supplies = sorted(f_df["supply"].unique().tolist())
sel_sp = st.sidebar.multiselect("🏭 공급단", all_supplies, default=all_supplies)

# (4) 검색어
search_query = st.sidebar.text_input("📝 품목명/코드 검색", "")

# 4. 데이터 필터링 로직 (데이터 유실 방지)
f_sel = f_df[f_df["ym"] == sel_ym].copy()
a_sel = a_df[a_df["ym"] == sel_ym].copy()

# 브랜드/공급단 필터 적용
if sel_br:
    f_sel = f_sel[f_sel["brand"].isin(sel_br)]
if sel_sp:
    f_sel = f_sel[f_sel["supply"].isin(sel_sp)]

# 검색어 필터
if search_query:
    f_sel = f_sel[f_sel["name"].str.contains(search_query, case=False, na=False) | 
                  f_sel["combo"].str.contains(search_query, case=False, na=False)]

# 5. 데이터 병합 (actual 데이터 유실 없도록 left join 수행)
# combo를 기준으로 예측량에 실적량을 붙입니다.
mg = pd.merge(f_sel, a_sel[["combo", "actual"]], on="combo", how="left")
mg["actual"] = mg["actual"].fillna(0)
mg["diff"] = mg["actual"] - mg["forecast"]
mg["rate"] = np.where(mg["forecast"] > 0, (mg["actual"] / mg["forecast"] * 100).round(1), 0)

# 6. 메인 화면 구성
st.title("📊 수요예측 vs 실적 분석 보고서")

# 요약 지표 (KPI)
c1, c2, c3 = st.columns(3)
c1.metric("총 예측량", f"{int(mg['forecast'].sum()):,}")
c2.metric("총 실적량", f"{int(mg['actual'].sum()):,}")
c3.metric("평균 달성률", f"{mg['rate'].mean():.1f}%")

# 📥 다운로드 버튼
st.markdown('<div class="section-header">📥 데이터 다운로드</div>', unsafe_allow_html=True)
buf = io.BytesIO()
mg.to_csv(buf, index=False, encoding="utf-8-sig")
st.download_button(f"⬇️ {sel_ym} 필터 결과 다운로드", buf.getvalue(), f"result_{sel_ym}.csv", "text/csv")

# 7. 데이터 표 (HTML 표 스타일)
st.markdown('<div class="section-header">📋 상세 내역</div>', unsafe_allow_html=True)
st.dataframe(mg, use_container_width=True, hide_index=True)

# 8. 시각화 (밝은 테마용)
if not mg.empty:
    st.markdown('<div class="section-header">📈 실적 비교 (Top 10)</div>', unsafe_allow_html=True)
    chart_data = mg.nlargest(10, 'forecast')
    fig = go.Figure()
    fig.add_trace(go.Bar(x=chart_data['name'], y=chart_data['forecast'], name='예측', marker_color='#94A3B8'))
    fig.add_trace(go.Bar(x=chart_data['name'], y=chart_data['actual'], name='실적', marker_color='#3B82F6'))
    fig.update_layout(template='plotly_white', barmode='group', height=400, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
