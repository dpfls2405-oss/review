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
        border-left: 5px solid #2563EB; margin-bottom: 25px; line-height: 1.6;
    }
    .section-header { 
        font-size: 18px; font-weight: bold; margin: 25px 0 10px 0; 
        color: #0F172A; border-bottom: 2px solid #E2E8F0; padding-bottom: 5px; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 정제 (시리즈 오류 및 NaN 해결)
@st.cache_data
def load_data():
    f = pd.read_csv("forecast_data.csv")
    a = pd.read_csv("actual_data.csv")
    
    # [수정] 공급단이 NaN이거나 비어있는 행 완전 제외
    f = f.dropna(subset=['supply'])
    f = f[f['supply'].astype(str).str.strip() != ""]
    
    # [핵심 수정] 모든 문자열 컬럼의 공백 제거 및 타입 고정 (시리즈 오류 방지)
    str_cols = ['ym', 'brand', 'series', 'combo', 'name', 'supply']
    for df in [f, a]:
        for col in str_cols:
            if col in df.columns:
                # NaN을 빈 문자열로 바꾸고 앞뒤 공백 제거
                df[col] = df[col].fillna("").astype(str).str.strip()
    
    # 시리즈명이 비어있는 경우 "미분류"로 표시
    f.loc[f['series'] == "", 'series'] = "미분류"
    
    return f, a

f_df, a_df = load_data()

# 3. 사이드바 필터
st.sidebar.title("🔍 필터 설정")
sel_ym = st.sidebar.selectbox("📅 기준 년월", sorted(f_df["ym"].unique(), reverse=True))

# 브랜드 -> 시리즈 연동 필터
all_brands = sorted(f_df["brand"].unique().tolist())
sel_br = st.sidebar.multiselect("🏷️ 브랜드", all_brands, default=all_brands)

filtered_f = f_df[f_df["brand"].isin(sel_br)]
all_series = sorted(filtered_f["series"].unique().tolist())
sel_sr = st.sidebar.multiselect("🪑 시리즈", all_series, default=all_series)

all_supplies = sorted(f_df["supply"].unique().tolist())
sel_sp = st.sidebar.multiselect("🏭 공급단", all_supplies, default=all_supplies)

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

# 5. 메인 화면 - [주요 품목 5가지 상세 분석]
st.title(f"📊 {sel_ym} 수요 분석 리포트")

if not mg.empty:
    # 상위 5개 품목 추출
    top_5 = mg.head(5)
    
    analysis_text = f"<strong>💡 필터 결과 요약 및 주요 품목(TOP 5) 분석</strong><br><br>"
    analysis_text += f"현재 선택된 조건에서 <strong>평균 달성률은 {mg['달성률(%)'].mean():.1f}%</strong>를 기록하고 있습니다.<br><hr>"
    
    for i, row in enumerate(top_5.itertuples(), 1):
        # 품목코드(combo)에서 보통 하이픈(-) 뒤가 색상코드인 경우가 많으므로 분리 시도
        parts = row.combo.split('-')
        code_part = parts[0]
        color_part = parts[1] if len(parts) > 1 else "정보없음"
        
        analysis_text += f"""
        {i}. <strong>{row.name}</strong> ({row.series} 시리즈)<br>
        &nbsp;&nbsp;&nbsp;• 단품코드: <code>{code_part}</code> | 색상: <code>{color_part}</code><br>
        &nbsp;&nbsp;&nbsp;• 분석수치: 예측 <strong>{int(row.forecast):,}</strong> vs 실적 <strong>{int(row.actual):,}</strong> (달성률: {row.target_rate:.1f}%)<br>
        """.replace('target_rate', 'getattr(row, "_10")') # Pandas itertuples 인덱스 처리

    # 실제 실행을 위해 구문을 수정하여 삽입
    st.markdown(f'<div class="analysis-box">{analysis_text}</div>', unsafe_allow_html=True)

# 6. KPI 지표 및 상세 표
c1, c2, c3 = st.columns(3)
c1.metric("총 예측량", f"{int(mg['forecast'].sum()):,}")
c2.metric("총 실적량", f"{int(mg['actual'].sum()):,}")
c3.metric("평균 달성률", f"{mg['달성률(%)'].mean():.1f}%")

st.markdown('<div class="section-header">📋 상세 내역 요약</div>', unsafe_allow_html=True)
display_df = mg.rename(columns={
    "brand": "브랜드", "series": "시리즈", "combo": "단품코드", "name": "품목명", "forecast": "예측", "actual": "실적"
})[["브랜드", "시리즈", "단품코드", "품목명", "예측", "실적", "차이", "달성률(%)"]]

st.dataframe(display_df, use_container_width=True, hide_index=True)

# 7. 다운로드 버튼
buf = io.BytesIO()
mg.to_csv(buf, index=False, encoding="utf-8-sig")
st.download_button(f"⬇️ {sel_ym} 결과 CSV 다운로드", buf.getvalue(), f"report_{sel_ym}.csv", "text/csv")
