import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

# 1. 페이지 설정 및 디자인 (라이트 테마 기반)
st.set_page_config(page_title="수요예측 분석 리포트", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #1E293B !important; }
    [data-testid="stSidebar"] { background-color: #F8FAFC !important; border-right: 1px solid #E2E8F0; }
    .analysis-box { 
        background-color: #F8FAFC; border-radius: 12px; padding: 30px; 
        border: 1px solid #E2E8F0; border-left: 6px solid #2563EB; margin-bottom: 30px; line-height: 1.8;
    }
    .item-card { 
        background: white; padding: 20px; border-radius: 10px; 
        margin-top: 15px; border: 1px solid #E2E8F0; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    code { color: #2563EB; background: #EFF6FF; padding: 2px 5px; border-radius: 4px; font-weight: bold; }
    .section-header { font-size: 20px; font-weight: bold; color: #0F172A; margin: 30px 0 15px 0; border-bottom: 2px solid #F1F5F9; padding-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 정밀 정제 (이상한 숫자 시리즈 및 결측치 제거)
@st.cache_data
def load_data():
    try:
        f = pd.read_csv("forecast_data.csv")
        a = pd.read_csv("actual_data.csv")
    except FileNotFoundError:
        st.error("데이터 파일(CSV)을 찾을 수 없습니다. 경로를 확인해주세요.")
        return pd.DataFrame(), pd.DataFrame()
    
    def clean_df(df):
        # 필수 값 누락 행 삭제
        df = df.dropna(subset=['series', 'brand', 'combo'])
        # 문자열 공백 제거
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
        
        # [핵심] '107' 같은 숫자 시리즈나 너무 짧은 명칭, 의미 없는 값 필터링
        df = df[~df['series'].str.isnumeric()]
        df = df[df['series'].str.len() >= 2]
        invalid_list = ["nan", "None", "미분류", "ETC", "기타", "0", "1"]
        df = df[~df['series'].isin(invalid_list)]
        
        return df

    return clean_df(f), clean_df(a)

f_df, a_df = load_data()

# 3. 사이드바 필터 설정
if not f_df.empty:
    st.sidebar.title("🔍 분석 필터")
    sel_ym = st.sidebar.selectbox("📅 기준 년월", sorted(f_df["ym"].unique(), reverse=True))

    # 브랜드 및 시리즈 동적 필터
    all_brands = sorted(f_df["brand"].unique().tolist())
    sel_br = st.sidebar.multiselect("🏷️ 브랜드 선택", all_brands, default=all_brands)

    filtered_f = f_df[f_df["brand"].isin(sel_br)]
    all_series = sorted(filtered_f["series"].unique().tolist())
    sel_sr = st.sidebar.multiselect("🪑 시리즈 선택", all_series, default=all_series)

    # 4. 데이터 병합 및 수치 계산
    f_sel = f_df[(f_df["ym"] == sel_ym) & (f_df["brand"].isin(sel_br)) & (f_df["series"].isin(sel_sr))].copy()
    a_sel = a_df[a_df["ym"] == sel_ym].copy()

    mg = pd.merge(f_sel, a_sel[["combo", "actual"]], on="combo", how="left")
    mg["actual"] = mg["actual"].fillna(0)
    mg["차이"] = mg["actual"] - mg["forecast"]
    mg["오차량"] = mg["차이"].abs() # 오차 절댓값 계산
    mg["달성률(%)"] = np.where(mg["forecast"] > 0, (mg["actual"] / mg["forecast"] * 100).round(1), 0)

    # 5. 메인 분석 리포트 (구어체 보고서 형식)
    st.title(f"📊 {sel_ym} 수요 예측 및 실적 분석 보고")

    if not mg.empty:
        total_f, total_a = mg['forecast'].sum(), mg['actual'].sum()
        avg_rate = mg['달성률(%)'].mean()
        
        # 오차 수량이 가장 큰 상위 5개 품목 추출
        top_err_df = mg.sort_values(by="오차량", ascending=False).head(5)
        
        item_reports = ""
        for i, (_, row) in enumerate(top_err_df.iterrows(), 1):
            cb = str(row['combo'])
            code = cb.split('-')[0] if '-' in cb else cb
            color = cb.split('-')[1] if '-' in cb else "기본"
            
            # 사람이 직접 보고하듯 자연스러운 문장 구성
            item_reports += f"""
            <div class="item-card">
                <strong>{i}순위 관리 품목: {row['series']} 시리즈의 '{row['name']}' 모델</strong><br>
                해당 품목(단품코드: {code}, 색상: {color})은 예측 대비 실제 수주량이 <strong>{int(row['actual']):,}</strong>건을 기록했습니다. 
                이에 따라 현재 <strong>{row['달성률(%)']:.1f}%의 달성률</strong>을 보이고 있으며, 
                예측치와 실제 수요 사이에 약 <strong>{int(abs(row['차이'])):,}</strong>만큼의 오차가 발생하여 수급 관리가 시급한 상황입니다.
            </div>
            """

        st.markdown(f"""
        <div class="analysis-box">
            <strong>💡 데이터 종합 분석 요약</strong><br>
            선택하신 조건의 전체 예측량은 <strong>{int(total_f):,}</strong>이며, 실제 수주량은 <strong>{int(total_a):,}</strong>으로 집계되었습니다. 
            전체 품목의 평균 달성률은 <strong>{avg_rate:.1f}%</strong>를 기록하고 있습니다.<br><br>
            
            <strong>🔍 예측 오차가 큰 5개 주요 품목 상세 분석</strong><br>
            데이터 분석 결과, 예측과 실제 수요의 간극이 가장 커서 생산 계획 및 재고 운영에 직접적인 영향을 줄 수 있는 5가지 모델은 다음과 같습니다.
            {item_reports}
            <br>
            위 품목들은 현재 예측 범위를 벗어난 수급 불균형이 가장 두드러지게 나타나고 있습니다. 
            차순위 계획 수립 시 해당 품목들의 자재 확보 상태와 물류 흐름을 우선적으로 점검해 주시기 바랍니다.
        </div>
        """, unsafe_allow_html=True)

    # 6. 시각화 (시리즈별 차이 및 달성률)
    st.markdown('<div class="section-header">📈 시리즈별 수급 차이 및 달성률 현황</div>', unsafe_allow_html=True)
    s_agg = mg.groupby('series').agg({'forecast':'sum', 'actual':'sum', '차이':'sum'}).reset_index()
    s_agg['달성률(%)'] = (s_agg['actual'] / s_agg['forecast'] * 100).round(1)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=s_agg['series'], y=s_agg['차이'], name='예측 대비 차이량', marker_color='#fb7185'))
    fig.add_trace(go.Scatter(x=s_agg['series'], y=s_agg['달성률(%)'], name='달성률(%)', yaxis='y2', line=dict(color='#2563eb', width=3)))

    fig.update_layout(
        template='plotly_white', height=450,
        yaxis=dict(title="차이량 (실적-예측)"),
        yaxis2=dict(title="달성률 (%)", overlaying='y', side='right', range=[0, 150]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

    # 7. 상세 데이터 표
    st.markdown('<div class="section-header">📋 품목별 상세 현황 리스트</div>', unsafe_allow_html=True)
    display_df = mg.rename(columns={
        "brand": "브랜드", "series": "시리즈", "combo": "단품코드", "name": "품목명", "forecast": "예측", "actual": "실적"
    })[["브랜드", "시리즈", "단품코드", "품목명", "예측", "실적", "차이", "달성률(%)"]]

    st.dataframe(display_df, use_container_width=True, hide_index=True)

else:
    st.warning("데이터 로드에 실패했습니다. CSV 파일을 확인해주세요.")
