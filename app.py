import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io, os

# ─────────────────────────────────────────────
# [1] 기본 설정 및 데이터 로드
st.set_page_config(page_title="수요예측 대시보드", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    f = pd.read_csv("forecast_data.csv")
    a = pd.read_csv("actual_data.csv")
    return f, a

try:
    f_df, a_df = load_data()
except Exception as e:
    st.error(f"데이터 파일을 로드하는 중 오류가 발생했습니다: {e}")
    st.stop()

# ─────────────────────────────────────────────
# [2] 사이드바 필터 설정
st.sidebar.header("📂 필터 설정")
ym_list = sorted(f_df["ym"].unique(), reverse=True)
sel_ym = st.sidebar.selectbox("기준 년월", ym_list)

# 브랜드 및 공급단 필터 (기존 로직 유지)
brands = ["전체"] + list(f_df["brand"].unique())
sel_br = st.sidebar.multiselect("브랜드", brands, default=["전체"])
supplies = ["전체"] + list(f_df["supply"].unique())
sel_sp = st.sidebar.multiselect("공급단", supplies, default=["전체"])

# ─────────────────────────────────────────────
# [3] 데이터 필터링 및 안전장치 (오류 해결 핵심)
f_sel = f_df[f_df["ym"] == sel_ym].copy()
a_sel = a_df[a_df["ym"] == sel_ym].copy()

if "전체" not in sel_br:
    f_sel = f_sel[f_sel["brand"].isin(sel_br)]
    a_sel = a_sel[a_sel["brand"].isin(sel_br)]
if "전체" not in sel_sp:
    f_sel = f_sel[f_sel["supply"].isin(sel_sp)]
    a_sel = a_sel[a_sel["supply"].isin(sel_sp)]

# 🚨 예측 데이터조차 없는 경우 (안전장치 1)
if f_sel.empty:
    st.warning(f"⚠️ {sel_ym}에 해당하는 예측 데이터가 없습니다.")
    st.stop()

# 데이터 병합 및 계산
mg = pd.merge(f_sel, a_sel[["combo", "actual"]], on="combo", how="left")
mg["actual"] = mg["actual"].fillna(0)
has_act = a_sel["actual"].sum() > 0 # 실적 존재 여부 체크

# 🚨 실적이 없는 달을 위한 계산 보정 (안전장치 2: 오류 Line 245 해결)
if not has_act:
    mg["diff"] = 0
    mg["rate"] = 0
else:
    mg["diff"] = mg["actual"] - mg["forecast"]
    mg["rate"] = np.where(mg["forecast"] > 0, (mg["actual"] / mg["forecast"] * 100).round(1), 0)

# ─────────────────────────────────────────────
# [4] 대시보드 화면 구성
st.title("📊 수요예측 대비 실적 대시보드")

# 분석 요약 섹션 (분석 내용 추가)
st.info(f"💡 **{sel_ym} 분석 요약:** " + 
        (f"현재 실적이 예측 대비 양호합니다." if has_act and mg["rate"].mean() > 90 
         else "실적 데이터가 아직 집계되지 않았거나 보완이 필요합니다."))

# ─────────────────────────────────────────────
# [5] 데이터 다운로드 섹션 (요청하신 기능)
st.divider()
st.subheader("📥 데이터 내보내기")
col1, col2 = st.columns(2)

with col1:
    # 전체 통합 데이터 다운로드
    all_merge = pd.merge(f_df, a_df[["combo", "actual"]], on="combo", how="left").fillna(0)
    buf_all = io.BytesIO()
    all_merge.to_csv(buf_all, index=False, encoding="utf-8-sig")
    st.download_button(
        label="⬇️ 전체 기간 데이터 다운로드 (CSV)",
        data=buf_all.getvalue(),
        file_name="total_forecast_actual.csv",
        mime="text/csv"
    )

with col2:
    # 현재 선택된 월 데이터 다운로드
    buf_sel = io.BytesIO()
    mg.to_csv(buf_sel, index=False, encoding="utf-8-sig")
    st.download_button(
        label=f"⬇️ {sel_ym} 데이터 다운로드 (CSV)",
        data=buf_sel.getvalue(),
        file_name=f"data_{sel_ym}.csv",
        mime="text/csv"
    )

st.divider()
# (이후 시각화 차트 코드들...)
