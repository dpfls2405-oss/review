import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# 1. 페이지 설정 및 세련된 라이트 디자인 (CSS)
st.set_page_config(page_title="수요분석 리포트", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    /* 전체 배경 및 폰트 */
    .stApp { background-color: #F8FAFC; }
    
    /* 세련된 KPI 카드 */
    .metric-card {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #E2E8F0;
        text-align: center;
    }
    .metric-label { font-size: 14px; color: #64748B; font-weight: 600; margin-bottom: 8px; }
    .metric-value { font-size: 28px; font-weight: 800; color: #1E293B; }
    .metric-sub { font-size: 12px; color: #94A3B8; margin-top: 4px; }
    
    /* 리포트 분석 박스 */
    .analysis-box { 
        background-color: white; border-radius: 12px; padding: 30px; 
        border: 1px solid #E2E8F0; line-height: 1.8; color: #334155;
    }
    .item-card { 
        background: #F8FAFC; padding: 18px; border-radius: 10px; 
        margin-top: 15px; border-left: 5px solid #3B82F6;
    }
    code { color: #2563EB; background: #EFF6FF; padding: 2px 4px; border-radius:
