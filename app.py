import streamlit as st
import pandas as pd
import numpy as np
import io

# 1. 페이지 설정 및 밝은 테마 커스텀 스타일링
st.set_page_config(page_title="수요예측 분석 리포트", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #1E293B !important; }
    [data-testid="stSidebar"] { background-color: #F8FAFC !important; border-right: 1px solid #E2E8F0; }
    .analysis-box { 
        background-color: #F1F5F9; border-radius: 12px; padding: 25px; 
        border-left: 6px solid #2563EB; margin-bottom: 30px; line-height: 1.8;
    }
    .section-header { 
        font-size: 19px; font-weight: bold; margin: 25px 0 12px 0; 
        color: #0F172A; border-bottom: 2px solid #E2E8F0; padding-bottom: 8px; 
    }
    .item-card { background: white; padding: 10px 15px; border-radius: 8px; margin-top: 10px; border: 1px solid #E2E8F0; }
    code { color: #2563EB; background: #EFF6FF; padding: 2px 5px; border-radius: 4px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 초정밀 전처리 (시리즈 오류 해결의 핵심)
@st.cache_data
def load_data():
    f = pd.read_csv("forecast_data.csv")
    a = pd.read_csv("actual_data.csv")
    
    # [수정] 공급단 NaN 행 제거 및 문자열 정제
    f = f.dropna(subset=['supply'])
    
    def clean_strings(df):
        # 모든 오브젝트 컬럼에 대해 공백 제거 및 결측치 처리
        cols = df.select_dtypes(include=['object']).columns
        for col in cols:
            df[col] = df[col].fillna("미분류").astype(str).str.strip()
        return df

    f = clean_strings(f)
    a = clean_strings(a)
    
    # [시리즈 오류 방지] 빈 값이나 이상한 값 보정
    f = f[f['series'] != ""]
    return f, a

f_df, a_df = load_data()

# 3. 사이드바 필터 설정
st.sidebar.title("🔍 필터 설정")
sel_ym = st.sidebar.selectbox("📅 기준 년월", sorted(f_df["ym"].unique(), reverse=True))

# 브랜드/시리즈 연동 필터 (시리즈 중복 및 오류 해결)
all_brands = sorted(f_df["brand"].unique().tolist())
sel_br = st.sidebar.multiselect("🏷️ 브랜드", all_brands, default=all_brands)

# 선택된 브랜드 내에 존재하는 시리즈만 추출 (중복 제거)
filtered_series_list = sorted(f_df[f_df["brand"].isin(sel_br)]["series"].unique().tolist())
sel_sr = st.sidebar.multiselect("🪑 시리즈", filtered_series_list, default=filtered_series_list)

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

# 5. 메인 화면 - [상세 요약 분석 리포트]
st.title(f"📊 {sel_ym} 수요 분석 리포트")

if not mg.empty:
    total_f = mg['forecast'].sum()
    total_a = mg['actual'].sum()
    avg_rate = mg['달성률(%)'].mean()
    
    # 주요 품목 TOP 5 리스트 생성
    top_5 = mg.head(5)
    item_analysis = ""
    
    for i, (_, row) in enumerate(top_5.iterrows(), 1):
        # 단품코드와 색상 분리 로직 (하이픈 기준)
        cb = str(row['combo'])
        code = cb.split('-')[0] if '-' in cb else cb
        color = cb.split('-')[1] if '-' in cb else "기본"
        
        item_analysis += f"""
        <div class="item-card">
            <strong>{i}. {row['name']}</strong> ({row['series']})<br>
            • <strong>식별 정보:</strong> 단품코드 <code>{code}</code> | 색상 <code>{color}</code><br>
            • <strong>수치 분석:</strong> 예측 <strong>{int(row['forecast']):,}</strong> 대비 실적 <strong>{int(row['actual']):,}</strong> 달성 (달성률 <strong>{row['달성률(%)']:.1f}%</strong>)
        </div>
        """

    st.markdown(f"""
    <div class="analysis-box">
        <strong>💡 필터 결과 요약 분석</strong><br>
        1. <strong>전체 현황:</strong> 총 예측량은 <strong>{int(total_f):,}</strong>건이며, 실제 수주량은 <strong>{int(total_a):,}</strong>건입니다.<br>
        2. <strong>평균 달성률:</strong> 분석 대상 품목의 평균 달성률은 <strong>{avg_rate:.1f}%</strong>입니다. 
        {' (예측 대비 실적이 목표치를 달성 중입니다)' if avg_rate >= 90 else ' (예측 대비 실적이 저조하여 수급 확인이 필요합니다)'}<br><br>
        <strong>🔍 주요 관리 품목 (TOP 5 상세)</strong><br>
        {item_analysis}
    </div>
    """, unsafe_allow_html=True)

# 6. KPI 지표 및 데이터 표
c1, c2, c3 = st.columns(3)
c1.metric("총 예측량", f"{int(mg['forecast'].sum()):,}")
c2.metric("총 실적량", f"{int(mg['actual'].sum()):,}")
c3.metric("평균 달성률", f"{mg['달성률(%)'].mean():.1f}%")

st.markdown('<div class="section-header">📋 상세 내역 데이터</div>', unsafe_allow_html=True)
display_df = mg.rename(columns={
    "brand": "브랜드", "series": "시리즈", "combo": "단품코드", "name": "품목명", "forecast": "예측", "actual": "실적"
})[["브랜드", "시리즈", "단품코드", "품목명", "예측", "실적", "차이", "달성률(%)"]]

st.dataframe(display_df, use_container_width=True, hide_index=True)

# 7. 다운로드 기능
buf = io.BytesIO()
mg.to_csv(buf, index=False, encoding="utf-8-sig")
st.download_button(f"⬇️ {sel_ym} 분석 결과 다운로드", buf.getvalue(), f"analysis_{sel_ym}.csv", "text/csv")
