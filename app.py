import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. 페이지 설정 및 디자인 정의
st.set_page_config(page_title="수요예측 대시보드", page_icon="📈", layout="wide")

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
    code { background:#f1f5f9; padding:2px 6px; border-radius:4px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 정밀 정제 (숫자 시리즈 제거)
@st.cache_data
def load_data():
    try:
        f = pd.read_csv("forecast_data.csv")
        a = pd.read_csv("actual_data.csv")
    except:
        dates = ["2026-02"] * 10
        brands = ["데스커", "일룸", "퍼시스"] * 4
        series = ["IBLE", "VIM", "AROUND", "T60", "107", "15"]
        f = pd.DataFrame({'ym': dates[:6], 'brand': brands[:6], 'series': series, 
                          'combo': [f"C{i}-R" for i in range(6)], 'name': [f"품목{i}" for i in range(6)],
                          'forecast': [1000, 1500, 800, 1200, 500, 300], 'supply': ['본사']*6})
        a = pd.DataFrame({'ym': dates[:6], 'combo': [f"C{i}-R" for i in range(6)], 
                          'actual': [950, 1600, 400, 1100, 480, 200]})

    def clean_df(df):
        df = df.dropna(subset=['series', 'brand', 'combo'])
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
        df = df[~df['series'].str.isnumeric()]
        df = df[df['series'].str.len() >= 2]
        return df

    return clean_df(f), clean_df(a)

f_df, a_df = load_data()

# 3. 사이드바 및 상단 컨트롤러
st.sidebar.title("🔍 필터 설정")
sel_ym = st.sidebar.selectbox("📅 기준 년월", sorted(f_df["ym"].unique(), reverse=True))

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
col1, col2, col3 = st.columns([2, 2, 3])
with col1:
    sort_metric = st.selectbox("📌 정렬 지표", 
                               ["차이량(|실-예측|) 큰 순", "차이량(실-예측) 큰 순", "실수주량 큰 순", "예측수요 큰 순", "달성률 큰 순"])
with col2:
    top_n = st.slider("🎯 Top N", 5, len(mg) if len(mg) > 5 else 10, 10)
with col3:
    search_term = st.text_input("🔎 검색 (단품코드/명칭)", placeholder="예: S60 / 바퀴형 의자")

sort_map = {
    "차이량(|실-예측|) 큰 순": ("오차량", False),
    "차이량(실-예측) 큰 순": ("차이", False),
    "실수주량 큰 순": ("actual", False),
    "예측수요 큰 순": ("forecast", False),
    "달성률 큰 순": ("달성률(%)", False)
}
mg = mg.sort_values(by=sort_map[sort_metric][0], ascending=sort_map[sort_metric][1])

if search_term:
    mg = mg[mg['combo'].str.contains(search_term, case=False) | mg['name'].str.contains(search_term, case=False)]

tab1, tab2 = st.tabs(["📊 데이터 대시보드", "📝 상세 분석 리포트"])

with tab1:
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

    st.dataframe(mg.drop(columns=['오차량']), use_container_width=True, hide_index=True)

with tab2:
    st.subheader(f"📋 {sel_ym} 수요 예측 대비 실적 분석 보고")

    # 안전한 처리: mg가 비어있으면 안내 메시지 출력
    if mg.empty:
        st.info("선택한 조건에 해당하는 데이터가 없습니다. 필터를 확인해 주세요.")
    else:
        # 전체 요약 수치
        t_f = mg['forecast'].sum()
        t_a = mg['actual'].sum()
        t_r = (t_a / t_f * 100) if t_f > 0 else 0

        # 오차 절대값 기준 상위 5개 추출 (데이터가 5개 미만이면 있는 만큼만)
        top_5_err = mg.sort_values(by="오차량", ascending=False).head(5).reset_index(drop=True)

        # 리포트 HTML 생성 함수
        def make_item_comment(row):
            diff = int(row['차이'])
            abs_err = int(row['오차량'])
            forecast = int(row['forecast'])
            actual = int(row['actual'])
            rate = row['달성률(%)']

            # 해석 문구
            if diff < 0:
                interpretation = f"실적이 예측보다 낮습니다. (예측이 실제보다 {abs_err:,}만큼 높게 잡힘)"
            elif diff > 0:
                interpretation = f"실적이 예측보다 높습니다. (실제 수주가 예측보다 {abs_err:,}만큼 많음)"
            else:
                interpretation = "실적이 예측과 거의 일치합니다."

            # 권장 조치 (간단한 규칙 기반)
            actions = []
            # 과대예측(달성률 < 90) / 과소예측(달성률 > 110) 기준 예시
            if rate < 90:
                actions.append("재고·프로모션 상태 확인")
                actions.append("다음 예측 시 보수적(낮게) 보정 고려")
            elif rate > 110:
                actions.append("판촉·채널 영향 확인")
                actions.append("다음 예측 시 최근 판매 증가 반영")
            else:
                actions.append("채널별 판매 추세 모니터링")
                actions.append("단기 보정 필요 여부 검토")

            return interpretation, actions

        # HTML 조립
        report_html = ""
        for i, row in top_5_err.iterrows():
            idx = i + 1
            combo = str(row.get('combo', ''))
            code = combo.split('-')[0] if '-' in combo else combo
            color = combo.split('-')[1] if '-' in combo else "기본"
            series = row.get('series', '')
            name = row.get('name', '')
            forecast = int(row.get('forecast', 0))
            actual = int(row.get('actual', 0))
            rate = row.get('달성률(%)', 0.0)
            abs_err = int(row.get('오차량', 0))
            diff = int(row.get('차이', 0))

            interpretation, actions = make_item_comment(row)

            # 각 항목 카드
            report_html += f"""
            <div class="item-card">
                <strong>{idx}. {series} 시리즈 — {name}</strong><br>
                <div>단품코드: <code>{code}</code> &nbsp; 색상: <code>{color}</code></div>
                <div>예측: <strong>{forecast:,}</strong> &nbsp; 실제: <strong>{actual:,}</strong> &nbsp; 달성률: <strong>{rate:.1f}%</strong> &nbsp; 오차량: <strong>{abs_err:,}</strong></div>
                <div style="margin-top:8px;"><em>해석:</em> {interpretation}</div>
                <div style="margin-top:6px;"><em>권장 조치:</em> {'; '.join(actions)}</div>
            </div>
            """

        # 전체 요약 및 권장 사항
        summary_html = f"""
        <div class="analysis-box">
            이번 분석 대상(기준 월): <strong>{sel_ym}</strong><br>
            예측수요 합계: <strong>{int(t_f):,}</strong> &nbsp; 실제수주 합계: <strong>{int(t_a):,}</strong> &nbsp; 전체 달성률: <strong>{t_r:.1f}%</strong><br><br>
            아래는 오차(절대값)가 큰 상위 {len(top_5_err)}개 품목의 요약입니다. 각 항목에 대해 간단한 해석과 즉시 실행 가능한 권장 조치를 제시합니다.<br><br>
            <strong>🔍 상위 오차 품목 상세</strong>
            {report_html}
            <br>
            <strong>종합 권장 사항</strong><br>
            - 상위 오차 품목의 재고·프로모션·납기·채널별 판매 현황을 우선 점검하세요.<br>
            - 다음 예측 주기에는 상위 변동 시리즈에 대해 가중치 보정 또는 최근 3개월 추세 반영을 권장합니다.<br>
            - 달성률이 80% 미만 또는 120% 초과인 품목은 알림 기준으로 설정해 조기 대응 체계를 마련하세요.
        </div>
        """

        st.markdown(summary_html, unsafe_allow_html=True)
