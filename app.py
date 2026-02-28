import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="수요예측 분석 리포트", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #1E293B !important; }
    [data-testid="stSidebar"] { background-color: #F8FAFC !important; border-right: 1px solid #E2E8F0; }
    .analysis-box { 
        background-color: #F1F5F9; border-radius: 10px; padding: 20px; 
        border-left: 5px solid #2563EB; margin-bottom: 25px;
    }
    .section-header { 
        font-size: 18px; font-weight: bold; margin: 25px 0 10px 0; 
        color: #0F172A; border-bottom: 2px solid #E2E8F0; padding-bottom: 5px; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 정제
@st.cache_data
def load_data():
    f = pd.read_csv("forecast_data.csv")
    a = pd.read_csv("actual_data.csv")
    
    # [수정] 공급단이 NaN이거나 비어있는 행 제거
    f = f.dropna(subset=['supply'])
    f = f[f['supply'].str.strip() != ""]
    
    # 모든 문자열 공백 제거
    for df in [f, a]:
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
    
    return f, a

f_df, a_df = load_data()

# 3. 사이드바 필터
st.sidebar.title("🔍 필터 설정")

# (1) 년월
sel_ym = st.sidebar.selectbox("📅 기준 년월", sorted(f_df["ym"].unique(), reverse=True))

# (2) 브랜드
all_brands = sorted(f_df["brand"].unique().tolist())
sel_br = st.sidebar.multiselect("🏷️ 브랜드", all_brands, default=all_brands)

# (3) 시리즈 (브랜드에 연동)
filtered_by_br = f_df[f_df["brand"].isin(sel_br)]
all_series = sorted(filtered_by_br["series"].unique().tolist())
sel_sr = st.sidebar.multiselect("🪑 시리즈", all_series, default=all_series)

# (4) 공급단 (NaN 제외됨)
all_supplies = sorted(f_df["supply"].unique().tolist())
sel_sp = st.sidebar.multiselect("🏭 공급단", all_supplies, default=all_supplies)

# (5) 정렬 및 검색
sort_metric = st.sidebar.selectbox("🔢 정렬 기준", ["예측량 높은순", "실적량 높은순", "달성률 높은순"])
search_query = st.sidebar.text_input("📝 품목명 검색", "")

# 4. 데이터 필터링 및 병합
f_sel = f_df[(f_df["ym"] == sel_ym) & (f_df["brand"].isin(sel_br)) & 
             (f_df["series"].isin(sel_sr)) & (f_df["supply"].isin(sel_sp))].copy()

if search_query:
    f_sel = f_sel[f_sel["name"].str.contains(search_query, case=False)]

a_sel = a_df[a_df["ym"] == sel_ym].copy()
mg = pd.merge(f_sel, a_sel[["combo", "actual"]], on="combo", how="left")
mg["actual"] = mg["actual"].fillna(0)
mg["차이"] = mg["actual"] - mg["forecast"]
mg["달성률(%)"] = np.where(mg["forecast"] > 0, (mg["actual"] / mg["forecast"] * 100).round(1), 0)

# 정렬 적용
sort_map = {"예측량 높은순": ("forecast", False), "실적량 높은순": ("actual", False), "달성률 높은순": ("달성률(%)", False)}
mg = mg.sort_values(by=sort_map[sort_metric][0], ascending=sort_map[sort_metric][1])

# 5. 메인 화면 - 자동 분석 섹션
st.title(f"📊 {sel_ym} 수요 분석 리포트")

if not mg.empty:
    total_f = mg['forecast'].sum()
    total_a = mg['actual'].sum()
    avg_rate = mg['달성률(%)'].mean()
    top_item = mg.iloc[0]['name']
    
    # 분석 내용 자동 생성
    st.markdown(f"""
    <div class="analysis-box">
        <strong>💡 필터 결과 요약 분석</strong><br>
        1. <strong>전체 현황:</strong> 현재 선택된 조건의 총 예측량은 <strong>{int(total_f):,}</strong>이며, 실제 수주량은 <strong>{int(total_a):,}</strong>입니다.<br>
        2. <strong>평균 달성률:</strong> 해당 품목들의 평균 달성률은 <strong>{avg_rate:.1f}%</strong>입니다. 
        {' (예측 대비 실적이 양호합니다)' if avg_rate >= 90 else ' (예측 대비 실적이 저조하여 재고 확인이 필요합니다)'}<br>
        3. <strong>주요 품목:</strong> 현재 정렬 기준 가장 상위 품목은 <strong>'{top_item}'</strong>입니다.
    </div>
    """, unsafe_allow_html=True)

# 6. KPI 지표
c1, c2, c3 = st.columns(3)
c1.metric("총 예측량", f"{int(mg['forecast'].sum()):,}")
c2.metric("총 실적량", f"{int(mg['actual'].sum()):,}")
c3.metric("평균 달성률", f"{mg['달성률(%)'].mean():.1f}%")

# 7. 요약 집계표 (간략화)
st.markdown('<div class="section-header">📋 상세 내역 요약</div>', unsafe_allow_html=True)
display_df = mg.rename(columns={
    "brand": "브랜드", "series": "시리즈", "name": "품목명", "forecast": "예측", "actual": "실적"
})[["브랜드", "시리즈", "품목명", "예측", "실적", "차이", "달성률(%)"]]
st.dataframe(display_df, use_container_width=True, hide_index=True)

# 8. 다운로드 버튼
buf = io.BytesIO()
mg.to_csv(buf, index=False, encoding="utf-8-sig")
st.download_button(f"⬇️ 현재 필터 결과 CSV 다운로드", buf.getvalue(), f"report_{sel_ym}.csv", "text/csv")
