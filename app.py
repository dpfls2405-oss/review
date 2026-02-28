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
        background-color: #F8FAFC; border-radius: 12px; padding: 25px; 
        border: 1px solid #E2E8F0; border-left: 6px solid #2563EB; margin-bottom: 30px; line-height: 1.8;
    }
    .item-card { 
        background: white; padding: 15px 20px; border-radius: 10px; 
        margin-top: 12px; border: 1px solid #E2E8F0; box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    code { color: #2563EB; background: #EFF6FF; padding: 2px 5px; border-radius: 4px; font-weight: bold; }
    .section-header { font-size: 19px; font-weight: bold; color: #0F172A; margin: 25px 0 10px 0; border-bottom: 2px solid #F1F5F9; padding-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 초정밀 정제 (숫자 시리즈 및 결측치 완전 제거)
@st.cache_data
def load_data():
    f = pd.read_csv("forecast_data.csv")
    a = pd.read_csv("actual_data.csv")
    
    def clean_df(df):
        # 1. 필수 값(시리즈, 공급단) 없는 행 삭제
        df = df.dropna(subset=['series', 'supply'])
        
        # 2. 모든 문자열 공백 제거
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
            
        # 3. [핵심] 숫자만 있는 시리즈(예: 107) 및 유효하지 않은 명칭 삭제
        # 숫자로만 구성되었거나 2글자 미만인 시리즈 제외
        df = df[~df['series'].str.isnumeric()]
        df = df[df['series'].str.len() >= 2]
        
        invalid_list = ["nan", "None", "미분류", "ETC", "기타", "0", "1"]
        df = df[~df['series'].isin(invalid_list)]
        df = df[~df['supply'].isin(invalid_list)]
        
        return df

    return clean_df(f), clean_df(a)

f_df, a_df = load_data()

# 3. 사이드바 필터
st.sidebar.title("🔍 분석 필터 설정")
sel_ym = st.sidebar.selectbox("📅 기준 년월", sorted(f_df["ym"].unique(), reverse=True))

all_brands = sorted(f_df["brand"].unique().tolist())
sel_br = st.sidebar.multiselect("🏷️ 브랜드 선택", all_brands, default=all_brands)

# 깨끗하게 정제된 시리즈만 추출
filtered_f = f_df[f_df["brand"].isin(sel_br)]
all_series = sorted(filtered_f["series"].unique().tolist())
sel_sr = st.sidebar.multiselect("🪑 시리즈 선택", all_series, default=all_series)

all_supplies = sorted(f_df["supply"].unique().tolist())
sel_sp = st.sidebar.multiselect("🏭 공급단 선택", all_supplies, default=all_supplies)

# 4. 데이터 병합 및 계산
f_sel = f_df[(f_df["ym"] == sel_ym) & (f_df["brand"].isin(sel_br)) & 
             (f_df["series"].isin(sel_sr)) & (f_df["supply"].isin(sel_sp))].copy()

a_sel = a_df[a_df["ym"] == sel_ym].copy()
mg = pd.merge(f_sel, a_sel[["combo", "actual"]], on="combo", how="left")
mg["actual"] = mg["actual"].fillna(0)
mg["오차량"] = (mg["actual"] - mg["forecast"]).abs() # 오차의 크기 계산
mg["차이"] = mg["actual"] - mg["forecast"]
mg["달성률(%)"] = np.where(mg["forecast"] > 0, (mg["actual"] / mg["forecast"] * 100).round(1), 0)

# 5. 메인 화면 - 오차 수량이 큰 상위 5품목 리포트
st.title(f"📊 {sel_ym} 수요 분석 리포트")

if not mg.empty:
    total_f, total_a = mg['forecast'].sum(), mg['actual'].sum()
    avg_rate = mg['달성률(%)'].mean()
    
    # 오차 수량이 큰 순서로 정렬 (상위 5개)
    top_err_5 = mg.sort_values(by="오차량", ascending=False).head(5)
    
    item_html = ""
    for i, (_, row) in enumerate(top_err_5.iterrows(), 1):
        cb = str(row['combo'])
        # 단품코드 S60, 색상 XX 형태로 분리 (하이픈 기준)
        code_part = cb.split('-')[0] if '-' in cb else cb
        color_part = cb.split('-')[1] if '-' in cb else "정보없음"
        
        item_html += f"""
        <div class="item-card">
            <strong>{i}. {row['name']}</strong><br>
            • <strong>상세 정보:</strong> 시리즈: <code>{row['series']}</code> | 단품코드: <code>{code_part}</code> | 색상: <code>{color_part}</code><br>
            • <strong>분석 수치:</strong> 예측 대비 실적 <strong>{int(row['actual']):,}</strong>으로 달성률 <strong>{row['달성률(%)']:.1f}%</strong> 기록 (오차: {int(row['차이']):,})
        </div>"""

    st.markdown(f"""
    <div class="analysis-box">
        <strong>💡 종합 데이터 요약</strong><br>
        1. <strong>전체 현황:</strong> 총 예측 <strong>{int(total_f):,}</strong> 대비 실제 수주 <strong>{int(total_a):,}</strong> (달성률 {avg_rate:.1f}%)<br>
        2. <strong>시리즈 분석:</strong> 현재 필터 내에서 예측 대비 실적 오차가 가장 큰 상위 5개 품목 리포트입니다.<br><br>
        <strong>🔍 오차 수량이 큰 5품목 상세 분석</strong><br>
        {item_html}
    </div>
    """, unsafe_allow_html=True)

# 6. 시리즈별 차이량 및 달성률 시각화
st.markdown('<div class="section-header">📈 시리즈별 수급 차이 및 달성률 현황</div>', unsafe_allow_html=True)
s_agg = mg.groupby('series').agg({'forecast':'sum', 'actual':'sum', '차이':'sum'}).reset_index()
s_agg['달성률(%)'] = (s_agg['actual'] / s_agg['forecast'] * 100).round(1)

fig = go.Figure()
fig.add_trace(go.Bar(x=s_agg['series'], y=s_agg['차이'], name='예측 대비 차이량', marker_color='#fb7185'))
fig.add_trace(go.Scatter(x=s_agg['series'], y=s_agg['달성률(%)'], name='달성률(%)', yaxis='y2', line=dict(color='#2563eb', width=3)))

fig.update_layout(
    template='plotly_white', height=400,
    yaxis=dict(title="차이량 (실적-예측)"),
    yaxis2=dict(title="달성률 (%)", overlaying='y', side='right', range=[0, 150]),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig, use_container_width=True)

# 7. 상세 데이터 표
st.markdown('<div class="section-header">📋 품목별 상세 현황</div>', unsafe_allow_html=True)
display_df = mg.rename(columns={
    "brand": "브랜드", "series": "시리즈", "combo": "단품코드", "name": "품목명", "forecast": "예측", "actual": "실적"
})[["브랜드", "시리즈", "단품코드", "품목명", "예측", "실적", "차이", "달성률(%)"]]

st.dataframe(display_df, use_container_width=True, hide_index=True)
