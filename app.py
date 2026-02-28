import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. 페이지 설정 및 디자인 정의
st.set_page_config(page_title="수요예측 대시보드", page_icon="📈", layout="wide")

# CSS: 이미지와 유사한 상단 요약 카드 및 레이아웃 스타일링
st.markdown("""
    <style>
    .metric-card {
        background-color: #1E293B; border-radius: 10px; padding: 15px;
        color: white; border: 1px solid #334155; text-align: center;
    }
    .metric-label { font-size: 14px; color: #94A3B8; margin-bottom: 5px; }
    .metric-value { font-size: 24px; font-weight: bold; }
    .metric-sub { font-size: 12px; color: #64748B; margin-top: 5px; }
    
    .analysis-box { 
        background-color: #F8FAFC; border-radius: 12px; padding: 30px; 
        border: 1px solid #E2E8F0; line-height: 1.8; color: #1E293B;
    }
    .item-card { 
        background: white; padding: 18px; border-radius: 10px; 
        margin-top: 15px; border: 1px solid #E2E8F0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 정밀 정제 (숫자 시리즈 제거)
@st.cache_data
def load_data():
    # 실제 파일명에 맞게 수정 (forecast_data.csv, actual_data.csv)
    try:
        f = pd.read_csv("forecast_data.csv")
        a = pd.read_csv("actual_data.csv")
    except:
        # 테스트용 더미 데이터 생성 (파일이 없을 경우 대비)
        dates = ["2026-02"] * 10
        brands = ["데스커", "일룸", "퍼시스"] * 4
        series = ["IBLE", "VIM", "AROUND", "T60", "107", "15"] # 숫자 시리즈 포함
        f = pd.DataFrame({'ym': dates[:6], 'brand': brands[:6], 'series': series, 
                          'combo': [f"C{i}-R" for i in range(6)], 'name': [f"품목{i}" for i in range(6)],
                          'forecast': [1000, 1500, 800, 1200, 500, 300], 'supply': ['본사']*6})
        a = pd.DataFrame({'ym': dates[:6], 'combo': [f"C{i}-R" for i in range(6)], 
                          'actual': [950, 1600, 400, 1100, 480, 200]})

    def clean_df(df):
        df = df.dropna(subset=['series', 'brand', 'combo'])
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
        # [이미지 요청 반영] 숫자 형태의 시리즈 삭제
        df = df[~df['series'].str.isnumeric()]
        df = df[df['series'].str.len() >= 2]
        return df

    return clean_df(f), clean_df(a)

f_df, a_df = load_data()

# 3. 사이드바 및 상단 컨트롤러
st.sidebar.title("🔍 필터 설정")
sel_ym = st.sidebar.selectbox("📅 기준 년월", sorted(f_df["ym"].unique(), reverse=True))

# 브랜드/시리즈 필터
all_brands = sorted(f_df["brand"].unique().tolist())
sel_br = st.sidebar.multiselect("🏷️ 브랜드", all_brands, default=all_brands)
filtered_f = f_df[f_df["brand"].isin(sel_br)]
all_series = sorted(filtered_f["series"].unique().tolist())
sel_sr = st.sidebar.multiselect("🪑 시리즈", all_series, default=all_series)

# 4. 데이터 병합 및 기본 계산
f_sel = f_df[(f_df["ym"] == sel_ym) & (f_df["brand"].isin(sel_br)) & (f_df["series"].isin(sel_sr))].copy()
a_sel = a_df[a_df["ym"] == sel_ym].copy()
mg = pd.merge(f_sel, a_sel[["combo", "actual"]], on="combo", how="left").fillna(0)

mg["차이"] = mg["actual"] - mg["forecast"]
mg["오차량"] = mg["차이"].abs()
mg["달성률(%)"] = np.where(mg["forecast"] > 0, (mg["actual"] / mg["forecast"] * 100).round(1), 0)

# --- 메인 화면 구성 ---

# 상단 대시보드 헤더 컨트롤 (이미지 5832b3 반영)
col1, col2, col3 = st.columns([2, 2, 3])
with col1:
    sort_metric = st.selectbox("📌 정렬 지표", 
                               ["차이량(|실-예측|) 큰 순", "차이량(실-예측) 큰 순", "실수주량 큰 순", "예측수요 큰 순", "달성률 큰 순"])
with col2:
    top_n = st.slider("🎯 Top N", 5, len(mg) if len(mg) > 5 else 10, 10)
with col3:
    search_term = st.text_input("🔎 검색 (단품코드/명칭)", placeholder="예: S60 / 바퀴형 의자")

# 정렬 로직
sort_map = {
    "차이량(|실-예측|) 큰 순": ("오차량", False),
    "차이량(실-예측) 큰 순": ("차이", False),
    "실수주량 큰 순": ("actual", False),
    "예측수요 큰 순": ("forecast", False),
    "달성률 큰 순": ("달성률(%)", False)
}
mg = mg.sort_values(by=sort_map[sort_metric][0], ascending=sort_map[sort_metric][1])

# 검색 필터링
if search_term:
    mg = mg[mg['combo'].str.contains(search_term, case=False) | mg['name'].str.contains(search_term, case=False)]

# 탭 분리 (대시보드 / 상세 분석 리포트)
tab1, tab2 = st.tabs(["📊 데이터 대시보드", "📝 상세 분석 리포트"])

with tab1:
    # 5. 요약 지표 (이미지 57bab5 반영)
    t_f = mg['forecast'].sum()
    t_a = mg['actual'].sum()
    t_d = t_a - t_f
    t_r = (t_a / t_f * 100) if t_f > 0 else 0
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">예측수요 합계</div><div class="metric-value">{int(t_f):,}</div><div class="metric-sub">(역산)</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">실수주량 합계</div><div class="metric-value">{int(t_a):,}</div><div class="metric-sub">{sel_ym.split("-")[1]}월</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">차이량 합계</div><div class="metric-value" style="color:#fb7185">{int(t_d):,}</div><div class="metric-sub">예측대비 차이</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">전체 달성률</div><div class="metric-value">{t_r:.1f}%</div><div class="metric-sub">실수주 / 예측</div></div>', unsafe_allow_html=True)

    # 6. 차트 섹션 (이미지 5832b3 하단 반영)
    st.write("")
    c1, c2 = st.columns(2)
    chart_data = mg.head(top_n)
    
    with c1:
        st.subheader(f"상위 Top {top_n} 수량 분석")
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=chart_data['series'], y=chart_data['forecast'], name='예측수요', marker_color='#3b82f6'))
        fig1.add_trace(go.Bar(x=chart_data['series'], y=chart_data['actual'], name='실수주량', marker_color='#fb7185'))
        fig1.add_trace(go.Bar(x=chart_data['series'], y=chart_data['차이'], name='차이량', marker_color='#f59e0b'))
        fig1.update_layout(barmode='group', template='plotly_white', height=400, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.subheader(f"달성률 현황 (Top {top_n})")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=chart_data['series'], y=chart_data['달성률(%)'], name='달성률', marker_color='#0ea5e9'))
        fig2.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="목표(100%)")
        fig2.update_layout(template='plotly_white', height=400, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig2, use_container_width=True)

    # 데이터 테이블
    st.dataframe(mg.drop(columns=['오차량']), use_container_width=True, hide_index=True)

with tab2:
    # 7. 상세 분석 리포트 (서술형)
    st.subheader(f"📋 {sel_ym} 수요 예측 대비 실적 분석 보고")
    
    if not mg.empty:
        # 오차 수량이 큰 상위 5개 품목 추출
        top_5_err = mg.sort_values(by="오차량", ascending=False).head(5)
        
        report_html = ""
        for i, (_, row) in enumerate(top_5_err.iterrows(), 1):
            cb = str(row['combo'])
            code = cb.split('-')[0] if '-' in cb else cb
            color = cb.split('-')[1] if '-' in cb else "기본"
            
            report_html += f"""
            <div class="item-card">
                <strong>{i}. {row['series']} 시리즈 : {row['name']}</strong><br>
                이 품목(단품코드: <code>{code}</code>, 색상: <code>{color}</code>)은 이번 달 예측 대비 실적 
                <strong>{int(row['actual']):,}</strong>으로 집계되어, 최종 <strong>달성률 {row['달성률(%)']:.1f}%</strong>를 기록했습니다.<br>
                수치상으로는 예측치와 약 {int(abs(row['차이'])):,}만큼의 차이가 발생하여 중점 관리가 필요합니다.
            </div>
            """

        st.markdown(f"""
        <div class="analysis-box">
            이번 {sel_ym} 분석 결과, 전체 예측 수요 <strong>{int(t_f):,}</strong> 대비 실제 수주는 <strong>{int(t_a):,}</strong>로 나타났습니다. 
            전체 달성률은 <strong>{t_r:.1f}%</strong>이며, 특히 아래의 5개 품목에서 가장 큰 오차가 확인되었습니다.<br><br>
            <strong>🔍 오차 수량이 큰 5대 품목 상세 리포트</strong>
            {report_html}
            <br>
            위 리스트는 현재 오차 절대값이 큰 순서로 정리되었으며, 차순위 수요 예측 시 해당 시리즈의 변동성을 고려하여 반영해 주시기 바랍니다.
        </div>
        """, unsafe_allow_html=True)
