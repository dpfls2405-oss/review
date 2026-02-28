import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

# 1. 페이지 설정 및 라이트 모드 디자인 고정
st.set_page_config(page_title="수요예측 분석 리포트", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #1E293B !important; }
    [data-testid="stSidebar"] { background-color: #F8FAFC !important; border-right: 1px solid #E2E8F0; }
    .analysis-box { 
        background-color: #F1F5F9; border-radius: 10px; padding: 20px; 
        border-left: 5px solid #2563EB; margin-bottom: 25px; line-height: 1.8;
    }
    .section-header { 
        font-size: 18px; font-weight: bold; margin: 25px 0 10px 0; 
        color: #0F172A; border-bottom: 2px solid #E2E8F0; padding-bottom: 5px; 
    }
    code { color: #EB5757; background: #F9F2F4; padding: 2px 4px; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 초강력 정제 (시리즈/공급단 오류 해결)
@st.cache_data
def load_data():
    f = pd.read_csv("forecast_data.csv")
    a = pd.read_csv("actual_data.csv")
    
    # [수정] 공급단 NaN 행 완전 제거 및 정제
    f = f.dropna(subset=['supply'])
    
    # 모든 문자열 컬럼 정제 함수
    def clean_df(df):
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna("미분류").astype(str).str.strip()
        return df

    return clean_df(f), clean_df(a)

f_df, a_df = load_data()

# 3. 사이드바 필터
st.sidebar.title("🔍 필터 설정")
sel_ym = st.sidebar.selectbox("📅 기준 년월", sorted(f_df["ym"].unique(), reverse=True))

# 브랜드 -> 시리즈 연동 (데이터 유실 방지)
all_brands = sorted(f_df["brand"].unique().tolist())
sel_br = st.sidebar.multiselect("🏷️ 브랜드", all_brands, default=all_brands)

filtered_f = f_df[f_df["brand"].isin(sel_br)]
all_series = sorted([s for s in filtered_f["series"].unique() if s != "미분류"])
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
    top_5 = mg.head(5)
    
    analysis_content = ""
    for i, (_, row) in enumerate(top_5.iterrows(), 1):
        # 콤보에서 코드와 색상 분리 (안전하게)
        combo_val = str(row['combo'])
        code_part = combo_val.split('-')[0] if '-' in combo_val else combo_val
        color_part = combo_val.split('-')[1] if '-' in combo_val else "기본"
        
        analysis_content += f"""
        {i}. <strong>{row['name']}</strong> ({row['series']})<br>
        &nbsp;&nbsp;&nbsp;• <strong>단품 정보:</strong> 코드 <code>{code_part}</code> | 색상 <code>{color_part}</code><br>
        &nbsp;&nbsp;&nbsp;• <strong>수치 분석:</strong> 예측 <strong>{int(row['forecast']):,}</strong> 대비 실적 <strong>{int(row['actual']):,}</strong> 달성 (달성률: {row['달성률(%)']:.1f}%)<br>
        """

    st.markdown(f"""
    <div class="analysis-box">
        <strong>💡 필터 결과 TOP 5 품목 분석</strong><br>
        현재 선택된 필터 내에서 {sort_metric} 기준으로 추출된 주요 품목 리포트입니다.<br><br>
        {analysis_content}
    </div>
    """, unsafe_allow_html=True)

# 6. KPI 및 상세 표
c1, c2, c3 = st.columns(3)
c1.metric("총 예측량", f"{int(mg['forecast'].sum()):,}")
c2.metric("총 실적량", f"{int(mg['actual'].sum()):,}")
c3.metric("평균 달성률", f"{mg['달성률(%)'].mean():.1f}%")

st.markdown('<div class="section-header">📋 상세 데이터 (핵심 요약)</div>', unsafe_allow_html=True)
display_df = mg.rename(columns={
    "brand": "브랜드", "series": "시리즈", "combo": "단품코드", "name": "품목명", "forecast": "예측", "actual": "실적"
})[["브랜드", "시리즈", "단품코드", "품목명", "예측", "실적", "차이", "달성률(%)"]]

st.dataframe(display_df, use_container_width=True, hide_index=True)

# 7. 다운로드
buf = io.BytesIO()
mg.to_csv(buf, index=False, encoding="utf-8-sig")
st.download_button(f"⬇️ {sel_ym} 분석 결과 CSV 저장", buf.getvalue(), f"analysis_{sel_ym}.csv", "text/csv")
