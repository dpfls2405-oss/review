import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

# 1. 페이지 설정 및 라이트 모드 커스텀 스타일 (배경을 밝게)
st.set_page_config(page_title="수요예측 대시보드", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    /* 전체 배경 밝게 */
    .stApp { background-color: #f8fafc; color: #1e293b; }
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e8f0; }
    /* 제목 및 헤더 스타일 */
    h1, h2, h3 { color: #0f172a; font-family: 'Apple SD Gothic Neo', sans-serif; }
    .section-header { 
        font-size: 18px; font-weight: bold; margin: 25px 0 10px 0; 
        color: #2563eb; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; 
    }
    /* 카드 스타일 (표/차트 배경) */
    .stDataFrame, .js-plotly-plot { background-color: white; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드
@st.cache_data
def load_data():
    f = pd.read_csv("forecast_data.csv")
    a = pd.read_csv("actual_data.csv")
    f['combo'] = f['combo'].str.strip()
    a['combo'] = a['combo'].str.strip()
    return f, a

f_df, a_df = load_data()

# 3. 사이드바 검색 및 드롭다운 필터 활성화
st.sidebar.title("🔎 필터 및 검색")

# (1) 년월 선택
ym_list = sorted(f_df["ym"].unique(), reverse=True)
sel_ym = st.sidebar.selectbox("📅 기준 년월 선택", ym_list)

# (2) 브랜드별 드롭다운 (멀티 선택 가능)
brands = sorted(f_df["brand"].unique().tolist())
sel_br = st.sidebar.multiselect("🏷️ 브랜드 선택", brands, default=brands)

# (3) 공급단별 드롭다운 (멀티 선택 가능)
supplies = sorted(f_df["supply"].unique().tolist())
sel_sp = st.sidebar.multiselect("🏭 공급단 선택", supplies, default=supplies)

# (4) 검색 기능 (품목명/코드)
search_query = st.sidebar.text_input("📝 품목명 또는 코드 검색", "")

# 4. 데이터 필터링 로직
f_sel = f_df[f_df["ym"] == sel_ym].copy()
a_sel = a_df[a_df["ym"] == sel_ym].copy()

# 드롭다운 필터 적용
if sel_br:
    f_sel = f_sel[f_sel["brand"].isin(sel_br)]
    a_sel = a_sel[a_sel["brand"].isin(sel_br)]
if sel_sp:
    f_sel = f_sel[f_sel["supply"].isin(sel_sp)]
    a_sel = a_sel[a_sel["supply"].isin(sel_sp)]

# 검색어 필터 적용
if search_query:
    f_sel = f_sel[
        f_sel["name"].str.contains(search_query, case=False, na=False) | 
        f_sel["combo"].str.contains(search_query, case=False, na=False)
    ]

# 5. 데이터 병합 및 계산
mg = pd.merge(f_sel, a_sel[["combo", "actual"]], on="combo", how="left")
mg["actual"] = mg["actual"].fillna(0)
mg["diff"] = mg["actual"] - mg["forecast"]
mg["rate"] = np.where(mg["forecast"] > 0, (mg["actual"] / mg["forecast"] * 100).round(1), 0)

# 6. 메인 화면 구성
st.title("📊 수요예측 vs 실적 분석 보고서")

# 📥 데이터 다운로드 버튼
st.markdown('<div class="section-header">📥 데이터 내보내기</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    buf = io.BytesIO()
    mg.to_csv(buf, index=False, encoding="utf-8-sig")
    st.download_button(f"📄 현재 {sel_ym} 데이터 받기", buf.getvalue(), f"data_{sel_ym}.csv", "text/csv")
with col2:
    all_buf = io.BytesIO()
    f_df.to_csv(all_buf, index=False, encoding="utf-8-sig")
    st.download_button("📂 전체 원본 데이터 받기", all_buf.getvalue(), "total_forecast.csv", "text/csv")

# 7. 상세 내역 표
st.markdown(f'<div class="section-header">📋 {sel_ym} 상세 내역 (총 {len(mg)}건)</div>', unsafe_allow_html=True)
display_cols = ["brand", "series", "combo", "name", "supply", "forecast", "actual", "diff", "rate"]
st.dataframe(mg[display_cols], use_container_width=True, hide_index=True)

# 8. 요약 차트 (라이트 모드용 테마 적용)
if not mg.empty:
    st.markdown('<div class="section-header">📈 주요 품목별 비교 (Top 15)</div>', unsafe_allow_html=True)
    chart_data = mg.head(15)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=chart_data['name'], y=chart_data['forecast'], name='예측량', marker_color='#94a3b8'))
    fig.add_trace(go.Bar(x=chart_data['name'], y=chart_data['actual'], name='실적량', marker_color='#2563eb'))
    fig.update_layout(
        barmode='group', 
        template='plotly_white', 
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)
