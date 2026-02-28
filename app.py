import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

# 1. 페이지 설정 및 다크 테마 스타일링 (HTML 느낌 재현)
st.set_page_config(page_title="수요예측 대시보드", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b1020; color: #eef2ff; }
    [data-testid="stSidebar"] { background-color: #121a33 !important; }
    .section-header { font-size: 20px; font-weight: bold; margin: 20px 0; color: #34d399; border-bottom: 2px solid #263156; padding-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 (캐싱 적용)
@st.cache_data
def load_data():
    f = pd.read_csv("forecast_data.csv")
    a = pd.read_csv("actual_data.csv")
    # 콤보 키를 기준으로 병합을 용이하게 하기 위해 공백 제거 등 전처리
    f['combo'] = f['combo'].str.strip()
    a['combo'] = a['combo'].str.strip()
    return f, a

f_df, a_df = load_data()

# 3. 사이드바 검색 및 필터 설정
st.sidebar.title("🔍 검색 및 필터")
search_query = st.sidebar.text_input("품목명/코드/시리즈 검색", "") # 사라졌던 검색창 복구

ym_list = sorted(f_df["ym"].unique(), reverse=True)
sel_ym = st.sidebar.selectbox("기준 년월", ym_list)

brands = ["전체"] + sorted(f_df["brand"].unique().tolist())
sel_br = st.sidebar.multiselect("브랜드", brands, default=["전체"])

# 4. 데이터 필터링 로직
f_sel = f_df[f_df["ym"] == sel_ym].copy()
a_sel = a_df[a_df["ym"] == sel_ym].copy()

# 브랜드 필터 적용
if "전체" not in sel_br and sel_br:
    f_sel = f_sel[f_sel["brand"].isin(sel_br)]
    a_sel = a_sel[a_sel["brand"].isin(sel_br)]

# 🚨 검색어 필터 적용 (HTML의 검색 기능 재현)
if search_query:
    f_sel = f_sel[
        f_sel["name"].str.contains(search_query, case=False, na=False) | 
        f_sel["combo"].str.contains(search_query, case=False, na=False) |
        f_sel["series"].str.contains(search_query, case=False, na=False)
    ]

# 5. 데이터 병합 및 오류 방지 계산
mg = pd.merge(f_sel, a_sel[["combo", "actual"]], on="combo", how="left")
mg["actual"] = mg["actual"].fillna(0)
has_act = a_sel["actual"].sum() > 0

if not has_act:
    mg["diff"] = 0
    mg["rate"] = 0
else:
    mg["diff"] = mg["actual"] - mg["forecast"]
    mg["rate"] = np.where(mg["forecast"] > 0, (mg["actual"] / mg["forecast"] * 100).round(1), 0)

# 6. 메인 화면 구성
st.title("📊 수요예측 vs 실적 분석")

# 📥 다운로드 버튼 섹션 (요청하신 기능)
st.markdown('<div class="section-header">📥 데이터 내보내기</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    buf = io.BytesIO()
    mg.to_csv(buf, index=False, encoding="utf-8-sig")
    st.download_button(f"⬇️ {sel_ym} 필터 결과 다운로드 (CSV)", buf.getvalue(), f"report_{sel_ym}.csv", "text/csv")
with c2:
    # 전체 데이터 다운로드
    all_buf = io.BytesIO()
    pd.merge(f_df, a_df[['combo','actual']], on='combo', how='left').to_csv(all_buf, index=False, encoding="utf-8-sig")
    st.download_button("⬇️ 전체 기간 원본 데이터 다운로드", all_buf.getvalue(), "total_data.csv", "text/csv")

# 7. 상세 데이터 표 (HTML 표 스타일)
st.markdown(f'<div class="section-header">{sel_ym} 상세 내역 (검색결과: {len(mg)}건)</div>', unsafe_allow_html=True)

# 표에 표시할 열 선택
display_cols = ["brand", "series", "combo", "name", "supply", "forecast", "actual", "diff", "rate"]
st.dataframe(mg[display_cols], use_container_width=True, hide_index=True)

# 8. 간단한 요약 차트 (HTML에 있던 차트 느낌)
if not mg.empty:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=mg['series'].head(10), y=mg['forecast'].head(10), name='예측량'))
    fig.add_trace(go.Bar(x=mg['series'].head(10), y=mg['actual'].head(10), name='실적량'))
    fig.update_layout(barmode='group', template='plotly_dark', title="상위 10개 시리즈 비교")
    st.plotly_chart(fig, use_container_width=True)
