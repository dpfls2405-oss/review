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
brands = sorted(f_df["brand"].unique
