import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# -----------------------
# 페이지 설정 및 스타일
# -----------------------
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
        background-color: #F8FAFC; border-radius: 12px; padding: 20px; 
        border: 1px solid #E2E8F0; line-height: 1.6; color: #1E293B;
    }
    .item-card { 
        background: white; padding: 14px; border-radius: 10px; 
        margin-top: 12px; border: 1px solid #E2E8F0; box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    code { background:#f1f5f9; padding:2px 6px; border-radius:4px; }
    </style>
    """, unsafe_allow_html=True)

# -----------------------
# 데이터 로드 및 정제
# -----------------------
@st.cache_data
def load_data():
    try:
        f = pd.read_csv("forecast_data.csv", dtype={"combo": str})
        a = pd.read_csv("actual_data.csv", dtype={"combo": str})
    except Exception:
        # 더미 데이터 (파일이 없을 때)
        dates = ["2025-06","2025-07","2025-08","2025-09","2025-10","2025-11","2025-12","2026-01","2026-02"]
        brands = ["데스커", "일룸", "퍼시스", "시디즈"]
        rows = []
        for ym in dates:
            for b in brands:
                for s in ["ACCESSORY","IBLE","SPOON","SODA","T60","RINGO","T20","GX","AROUND","PLT"]:
                    rows.append({
                        'ym': ym,
                        'brand': b,
                        'series': s,
                        'combo': f"{s[:6]}-{b[:2]}",
                        'name': f"{s}품목",
                        'forecast': np.random.randint(100, 5000),
                        # 일부러 NaN 섞음
                        'supply': np.random.choice(['시디즈제품','의자양지상품','베트남제품', np.nan], p=[0.3,0.3,0.3,0.1])
                    })
        f = pd.DataFrame(rows)
        a_rows = []
        for ym in dates:
            for b in brands:
                for s in ["ACCESSORY","IBLE","SPOON","SODA","T60","RINGO","T20","GX","AROUND","PLT"]:
                    a_rows.append({'ym': ym, 'combo': f"{s[:6]}-{b[:2]}", 'actual': max(0, int(np.random.normal(800, 600)))})
        a = pd.DataFrame(a_rows)

    def clean_df(df):
        # 필수 컬럼 보장
        for col in ['ym','series','brand','combo','supply','name']:
            if col not in df.columns:
                df[col] = np.nan
        df = df.dropna(subset=['series','brand','combo'])
        # 문자열 정리
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
        # supply 컬럼: 빈 문자열 또는 'nan' 문자열을 실제 NaN으로 변환
        df['supply'] = df['supply'].replace({'': np.nan, 'nan': np.nan})
        # 숫자형 시리즈 제거 및 길이 필터
        df = df[~df['series'].str.isnumeric()]
        df = df[df['series'].str.len() >= 2]
        return df

    return clean_df(f), clean_df(a)

f_df, a_df = load_data()

# -----------------------
# 공통 병합 및 지표 계산
# -----------------------
mg_all = pd.merge(f_df, a_df[["ym","combo","actual"]], on=["ym","combo"], how="left")
mg_all["actual"] = mg_all["actual"].fillna(0).astype(int)
mg_all["forecast"] = mg_all["forecast"].fillna(0).astype(int)
mg_all["차이"] = mg_all["actual"] - mg_all["forecast"]
mg_all["오차량"] = mg_all["차이"].abs()
mg_all["달성률(%)"] = np.where(mg_all["forecast"] > 0, (mg_all["actual"] / mg_all["forecast"] * 100).round(1), 0)

# -----------------------
# 사이드바: 한글 필터 (모두 expander로 구성)
# -----------------------
st.sidebar.title("필터 설정")

with st.sidebar.expander("공통 필터", expanded=True):
    sel_ym = st.selectbox("기준 년월", sorted(f_df["ym"].unique(), reverse=True))
    all_brands = sorted(f_df["brand"].unique().tolist())
    sel_br = st.multiselect("브랜드 선택", all_brands, default=all_brands)

# 공급단 옵션: 결측값(NaN)은 제외 (사용자가 '전체' 선택 시 모든 공급단 포함)
supply_values = []
if 'supply' in f_df.columns:
    supply_values = sorted(f_df['supply'].dropna().unique().tolist())

with st.sidebar.expander("메인 대시보드 필터", expanded=True):
    st.write("메인 탭에서 적용되는 필터입니다.")
    sel_supply_main = st.selectbox("공급단 선택 (메인)", ["전체"] + supply_values, index=0)
    # 시리즈 목록 (브랜드 선택에 따라 동적)
    available_series = sorted(f_df[f_df['brand'].isin(sel_br)]['series'].dropna().unique().tolist())
    series_count = len(available_series)
    st.write(f"시리즈 수: **{series_count}개**")
    if series_count == 0:
        st.info("선택된 브랜드에 시리즈 데이터가 없습니다.")
        sel_sr_main = []
    elif series_count <= 30:
        sel_sr_main = st.multiselect("시리즈 선택 (메인)", available_series, default=available_series)
    else:
        search_series_main = st.text_input("시리즈 검색 (메인)")
        top_n_default_main = 20
        series_agg_all = f_df[f_df['brand'].isin(sel_br)].groupby('series').agg({'forecast':'sum'}).reset_index()
        top_series_main = series_agg_all.sort_values('forecast', ascending=False).head(top_n_default_main)['series'].tolist()
        if search_series_main:
            filtered_series_main = [s for s in available_series if search_series_main.lower() in s.lower()]
            sel_sr_main = st.multiselect("검색 결과에서 선택 (메인)", filtered_series_main, default=filtered_series_main[:top_n_default_main])
        else:
            sel_sr_main = st.multiselect("시리즈 선택 (메인 기본 상위)", available_series, default=top_series_main)
    sort_metric_main = st.selectbox("정렬 지표 (메인)", 
                                   ["차이량(|실-예측|) 큰 순", "차이량(실-예측) 큰 순", "실수주량 큰 순", "예측수요 큰 순", "달성률 큰 순"])
    top_n_main = st.slider("Top N 표시 수 (메인)", 5, 50, 10)
    search_term_main = st.text_input("검색 (메인: 단품코드/명칭)")

with st.sidebar.expander("시계열 추이 필터", expanded=False):
    ts_mode = st.radio("표시 기준 (시계열)", ("브랜드별", "시리즈별"))
    ts_choices = sorted(mg_all['brand'].unique()) if ts_mode == "브랜드별" else sorted(mg_all['series'].unique())
    ts_target = st.multiselect("표시할 항목 선택 (시계열)", ts_choices, default=None)

with st.sidebar.expander("시리즈 상세 필터", expanded=False):
    sel_brand_series = st.selectbox("브랜드 선택 (시리즈 상세)", ["전체"] + all_brands, index=0)
    sel_supply_series = st.selectbox("공급단 선택 (시리즈 상세)", ["전체"] + supply_values, index=0)
    top_n_series = st.slider("표시할 시리즈 수 (Top N, 시리즈 상세)", 5, 50, 20)

with st.sidebar.expander("전체 데이터 필터", expanded=False):
    sel_supply_all = st.selectbox("공급단 선택 (전체 데이터)", ["전체"] + supply_values, index=0)

with st.sidebar.expander("수주대비 실적 분석 필터", expanded=False):
    perf_threshold_low = st.number_input("과소예측 기준(달성률 미만)", value=90, min_value=1, max_value=100)
    perf_threshold_high = st.number_input("과대예측 기준(달성률 초과)", value=110, min_value=100, max_value=1000)

# -----------------------
# 탭 구성 (메인 탭 맨 앞)
# -----------------------
tab_main, tab_ts, tab_series, tab_all, tab_perf = st.tabs([
    "🏠 메인 대시보드", "📈 시계열 추이", "🔎 시리즈 상세", "📋 전체 데이터", "🧾 수주대비 실적 분석"
])

# -----------------------
# 유틸: 숫자 포맷 적용 (DataFrame -> Styler)
# -----------------------
def style_number_df(df, int_cols=None, float_cols=None):
    """정수 컬럼과 소수 컬럼을 천단위 콤마로 포맷한 pandas Styler 반환"""
    if int_cols is None:
        int_cols = []
    if float_cols is None:
        float_cols = []
    fmt = {}
    for c in int_cols:
        if c in df.columns:
            fmt[c] = "{:,.0f}"
    for c in float_cols:
        if c in df.columns:
            fmt[c] = "{:,.1f}"
    return df.style.format(fmt)

# -----------------------
# 탭: 메인 대시보드
# -----------------------
with tab_main:
    st.header("메인 대시보드")
    st.write("사이드바의 '메인 대시보드 필터'에서 공급단·시리즈 등을 접어서 선택할 수 있습니다.")

    # 필터 적용: 공급단 선택이 '전체'이면 모든 공급단 포함, 아니면 해당 공급단만
    if not sel_sr_main:
        st.warning("사이드바의 '메인 대시보드 필터'에서 시리즈를 선택하세요.")
    else:
        df_main = f_df[(f_df["ym"] == sel_ym) & (f_df["brand"].isin(sel_br)) & (f_df["series"].isin(sel_sr_main))].copy()
        # 공급단 필터 적용 (메인) — '전체'이면 필터 적용 안 함
        if sel_supply_main != "전체":
            df_main = df_main[df_main['supply'] == sel_supply_main]

        # 병합: 실제값은 a_df에서 가져오되, 공급단이 NaN인 행은 유지하되 '전체' 선택 시 포함
        a_sel = a_df[a_df["ym"] == sel_ym].copy()
        mg_main = pd.merge(df_main, a_sel[["combo", "actual"]], on="combo", how="left")
        mg_main["actual"] = mg_main["actual"].fillna(0).astype(int)
        mg_main["forecast"] = mg_main["forecast"].fillna(0).astype(int)
        mg_main["차이"] = mg_main["actual"] - mg_main["forecast"]
        mg_main["오차량"] = mg_main["차이"].abs()
        mg_main["달성률(%)"] = np.where(mg_main["forecast"] > 0, (mg_main["actual"] / mg_main["forecast"] * 100).round(1), 0)

        # 정렬
        sort_map = {
            "차이량(|실-예측|) 큰 순": ("오차량", False),
            "차이량(실-예측) 큰 순": ("차이", False),
            "실수주량 큰 순": ("actual", False),
            "예측수요 큰 순": ("forecast", False),
            "달성률 큰 순": ("달성률(%)", False)
        }
        mg_main = mg_main.sort_values(by=sort_map[sort_metric_main][0], ascending=sort_map[sort_metric_main][1])

        # 검색 필터
        if search_term_main:
            mg_main = mg_main[mg_main['combo'].str.contains(search_term_main, case=False) | mg_main['name'].str.contains(search_term_main, case=False)]

        # 요약 카드 (천단위 콤마 적용)
        t_f = int(mg_main['forecast'].sum())
        t_a = int(mg_main['actual'].sum())
        t_d = int(t_a - t_f)
        t_r = (t_a / t_f * 100) if t_f > 0 else 0

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">예측수요 합계</div><div class="metric-value">{t_f:,}</div><div class="metric-sub">(역산)</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">실수주량 합계</div><div class="metric-value">{t_a:,}</div><div class="metric-sub">{sel_ym.split("-")[1]}월</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">차이량 합계</div><div class="metric-value" style="color:#fb7185">{t_d:,}</div><div class="metric-sub">예측대비 차이</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-card"><div class="metric-label">전체 달성률</div><div class="metric-value">{t_r:.1f}%</div><div class="metric-sub">실수주 / 예측</div></div>', unsafe_allow_html=True)

        # 차트: Top N
        st.write("")
        c1, c2 = st.columns(2)
        chart_data = mg_main.head(top_n_main)

        with c1:
            st.subheader(f"상위 Top {top_n_main} 수량 분석")
            fig1 = go.Figure()
            fig1.add_trace(go.Bar(x=chart_data['series'], y=chart_data['forecast'], name='예측수요', marker_color='#3b82f6'))
            fig1.add_trace(go.Bar(x=chart_data['series'], y=chart_data['actual'], name='실수주량', marker_color='#fb7185'))
            fig1.add_trace(go.Bar(x=chart_data['series'], y=chart_data['차이'], name='차이량', marker_color='#f59e0b'))
            fig1.update_layout(barmode='group', template='plotly_white', height=420, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig1, use_container_width=True)

        with c2:
            st.subheader(f"달성률 현황 (Top {top_n_main})")
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=chart_data['series'], y=chart_data['달성률(%)'], name='달성률', marker_color='#0ea5e9'))
            fig2.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="목표(100%)")
            fig2.update_layout(template='plotly_white', height=420, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig2, use_container_width=True)

        # 데이터 테이블: 숫자 포맷 적용
        display_df = mg_main.copy()
        cols_show = ['ym','brand','series','combo','name','supply','forecast','actual','차이','달성률(%)']
        display_df = display_df[cols_show].fillna("")
        st.subheader("상세 데이터")
        st.dataframe(style_number_df(display_df, int_cols=['forecast','actual','차이'], float_cols=['달성률(%)']), use_container_width=True)

# -----------------------
# 탭: 시계열 추이
# -----------------------
with tab_ts:
    st.header("시계열 추이")
    st.write("사이드바의 '시계열 추이 필터'로 제어됩니다.")

    mg_time = mg_all.copy()
    try:
        mg_time['ym_dt'] = pd.to_datetime(mg_time['ym'] + "-01", format="%Y-%m-%d")
    except Exception:
        mg_time['ym_dt'] = mg_time['ym']

    group_col = "brand" if ts_mode == "브랜드별" else "series"
    agg = mg_time.groupby(['ym_dt', group_col]).agg({'forecast':'sum','actual':'sum'}).reset_index()

    if ts_target:
        agg = agg[agg[group_col].isin(ts_target)]
    else:
        top_items = mg_time.groupby(group_col)['forecast'].sum().abs().sort_values(ascending=False).head(4).index.tolist()
        agg = agg[agg[group_col].isin(top_items)]

    if agg.empty:
        st.info("선택한 조건에 해당하는 시계열 데이터가 없습니다.")
    else:
        fig = go.Figure()
        items = agg[group_col].unique()
        for it in items:
            df_it = agg[agg[group_col] == it].sort_values('ym_dt')
            fig.add_trace(go.Scatter(x=df_it['ym_dt'], y=df_it['forecast'], mode='lines+markers', name=f"{it} 예측", line=dict(dash='dash')))
            fig.add_trace(go.Scatter(x=df_it['ym_dt'], y=df_it['actual'], mode='lines+markers', name=f"{it} 실적"))
        fig.update_layout(title="월별 예측 vs 실적 추이", xaxis_title="기준월", yaxis_title="수량", template='plotly_white', height=520)
        st.plotly_chart(fig, use_container_width=True)

# -----------------------
# 탭: 시리즈 상세
# -----------------------
with tab_series:
    st.header("시리즈 상세")
    st.write("사이드바의 '시리즈 상세 필터'로 제어됩니다.")

    df_series = f_df.copy()
    if sel_brand_series != "전체":
        df_series = df_series[df_series['brand'] == sel_brand_series]
    if sel_supply_series != "전체":
        df_series = df_series[df_series['supply'] == sel_supply_series]

    series_agg = df_series.groupby('series').agg({'forecast':'sum'}).reset_index().sort_values('forecast', ascending=False)
    if series_agg.empty:
        st.info("선택한 조건에 해당하는 시리즈 데이터가 없습니다.")
    else:
        plot_df = series_agg.head(top_n_series).sort_values('forecast')

        fig_s = go.Figure(go.Bar(x=plot_df['forecast'], y=plot_df['series'], orientation='h', marker_color='#3b82f6'))
        fig_s.update_layout(title=f"시리즈별 예측량 (Top {top_n_series})", xaxis_title="예측수량", yaxis_title="시리즈", template='plotly_white', height=520)
        st.plotly_chart(fig_s, use_container_width=True)

        actual_map = mg_all.groupby('series').agg({'actual':'sum'}).reset_index()
        merged_series = series_agg.merge(actual_map, on='series', how='left').fillna(0)
        merged_series['달성률(%)'] = np.where(merged_series['forecast']>0, (merged_series['actual']/merged_series['forecast']*100).round(1), 0)
        st.subheader("시리즈별 예측/실적 (전체 기간 합계)")
        st.dataframe(style_number_df(merged_series.rename(columns={'forecast':'예측수요','actual':'실수주'}), int_cols=['예측수요','실수주'], float_cols=['달성률(%)']), use_container_width=True)

# -----------------------
# 탭: 전체 데이터
# -----------------------
with tab_all:
    st.header("전체 데이터")
    st.write("사이드바의 '전체 데이터 필터'로 제어됩니다.")

    df_all = f_df.copy()
    if sel_supply_all != "전체":
        df_all = df_all[df_all['supply'] == sel_supply_all]

    # NaN(결측) supply는 그룹화에서 제외하여 '기타'가 보이지 않음
    supply_agg = df_all.dropna(subset=['supply']).groupby('supply').agg({'forecast':'sum'}).reset_index()
    total_forecast = int(supply_agg['forecast'].sum()) if not supply_agg.empty else 0
    if supply_agg.empty or total_forecast == 0:
        st.info("공급단별 집계 데이터가 없습니다.")
    else:
        fig_pie = go.Figure(data=[go.Pie(labels=supply_agg['supply'], values=supply_agg['forecast'], hole=0.45,
                                         marker=dict(colors=['#60a5fa','#fb7185','#34d399','#f59e0b']))])
        fig_pie.update_layout(title=f"공급단별 예측 비중 (총합: {total_forecast:,})", height=420, template='plotly_white')
        st.plotly_chart(fig_pie, use_container_width=True)

        pivot = df_all.dropna(subset=['supply']).pivot_table(index='brand', columns='supply', values='forecast', aggfunc='sum', fill_value=0)
        pivot['총합'] = pivot.sum(axis=1)
        pivot = pivot.sort_values('총합', ascending=False).drop(columns=['총합'])
        st.subheader("브랜드 × 공급단 예측량")
        pivot_display = pivot.astype(int).reset_index()
        int_cols = [c for c in pivot_display.columns if c != 'brand']
        st.dataframe(style_number_df(pivot_display, int_cols=int_cols), use_container_width=True)

# -----------------------
# 탭: 수주대비 실적 분석 (한글 서술형 리포트)
# -----------------------
def generate_narrative(mg_perf, low_thr=90, high_thr=110):
    total_forecast = int(mg_perf['forecast'].sum())
    total_actual = int(mg_perf['actual'].sum())
    total_diff = total_actual - total_forecast
    total_rate = (total_actual / total_forecast * 100) if total_forecast > 0 else 0.0

    series_perf = mg_perf.groupby('series').agg({'forecast':'sum','actual':'sum'}).reset_index()
    series_perf['달성률'] = np.where(series_perf['forecast']>0, (series_perf['actual']/series_perf['forecast']*100).round(1), 0)
    series_perf['오차량'] = (series_perf['actual'] - series_perf['forecast']).abs()
    worst = series_perf.sort_values('오차량', ascending=False).head(5)

    under = series_perf[series_perf['달성률'] < low_thr].sort_values('달성률').head(5)
    over = series_perf[series_perf['달성률'] > high_thr].sort_values('달성률', ascending=False).head(5)

    html = f"""
    <div class="analysis-box">
      <strong>요약</strong><br>
      기준월 전체 예측수요는 <strong>{total_forecast:,}</strong>건, 실제 수주는 <strong>{total_actual:,}</strong>건입니다.
      전체 차이는 <strong>{total_diff:,}</strong>건이며, 전체 달성률은 <strong>{total_rate:.1f}%</strong>입니다.<br><br>
      <strong>핵심 관찰</strong><br>
      - 전체 달성률이 {total_rate:.1f}%로, 예측 대비 실수주가 {'부족' if total_rate<100 else '초과'}한 경향입니다.<br>
      - 아래 상위 오차 품목 5개는 예측과 실제의 차이가 커서 우선 원인 분석이 필요합니다.<br><br>
      <strong>상위 오차 품목 (절대 오차 기준)</strong><br>
    """
    if worst.empty:
        html += "해당 없음<br>"
    else:
        for _, row in worst.iterrows():
            html += f"- {row['series']}: 예측 {int(row['forecast']):,} → 실제 {int(row['actual']):,} (오차 {int(row['오차량']):,}, 달성률 {row['달성률']:.1f}%)<br>"

    html += "<br><strong>과소/과대 예측 요약</strong><br>"
    if under.empty:
        html += f"- 과소예측(달성률 < {low_thr}%) 항목: 없음<br>"
    else:
        html += "- 과소예측 상위: " + ", ".join([f"{r['series']}({r['달성률']}%)" for _, r in under.iterrows()]) + "<br>"
    if over.empty:
        html += f"- 과대예측(달성률 > {high_thr}%) 항목: 없음<br>"
    else:
        html += "- 과대예측 상위: " + ", ".join([f"{r['series']}({r['달성률']}%)" for _, r in over.iterrows()]) + "<br>"

    html += """
      <br><strong>권장 조치 (우선순위)</strong><br>
      1. 상위 오차 품목의 재고·프로모션·납기·채널별 판매 현황을 즉시 확인하세요.<br>
      2. 과소예측 품목은 수요 감소 원인(반품·납기지연·채널 축소 등)을 점검하세요.<br>
      3. 과대예측 품목은 판촉·대량발주 여부를 확인하고 다음 예측에 반영하세요.<br>
      4. 반복 오차 시 별도 모니터링 대상으로 지정해 알림을 설정하세요.<br>
    </div>
    """
    return html

with tab_perf:
    st.header("수주대비 실적 분석")
    st.write("사이드바의 필터로 제어됩니다. (기준 년월 / 브랜드 / 공급단 등)")

    mg_perf = mg_all[(mg_all['ym'] == sel_ym) & (mg_all['brand'].isin(sel_br))].copy()
    if sel_supply_main != "전체":
        mg_perf = mg_perf[mg_perf['supply'] == sel_supply_main]

    if mg_perf.empty:
        st.info("선택한 조건에 해당하는 데이터가 없습니다.")
    else:
        total_forecast = int(mg_perf['forecast'].sum())
        total_actual = int(mg_perf['actual'].sum())
        total_diff = total_actual - total_forecast
        total_rate = (total_actual / total_forecast * 100) if total_forecast > 0 else 0

        st.subheader("요약 지표")
        p1, p2, p3, p4 = st.columns(4)
        with p1:
            st.metric("예측수요 합계", f"{total_forecast:,}")
        with p2:
            st.metric("실수주 합계", f"{total_actual:,}")
        with p3:
            st.metric("차이(실-예측)", f"{total_diff:,}", delta=f"{total_diff:,}")
        with p4:
            st.metric("전체 달성률", f"{total_rate:.1f}%")

        series_perf = mg_perf.groupby('series').agg({'forecast':'sum','actual':'sum'}).reset_index()
        series_perf['달성률(%)'] = np.where(series_perf['forecast']>0, (series_perf['actual']/series_perf['forecast']*100).round(1), 0)
        series_perf['오차량'] = (series_perf['actual'] - series_perf['forecast']).abs()
        st.subheader("시리즈별 성과 (요약)")
        st.dataframe(style_number_df(series_perf.rename(columns={'forecast':'예측수요','actual':'실수주'}), int_cols=['예측수요','실수주','오차량'], float_cols=['달성률(%)']), use_container_width=True)

        st.subheader("자동 분석 리포트 (요약)")
        narrative_html = generate_narrative(mg_perf, low_thr=perf_threshold_low, high_thr=perf_threshold_high)
        st.markdown(narrative_html, unsafe_allow_html=True)

# -----------------------
# 하단: 원본 데이터 미리보기 (공통)
# -----------------------
st.markdown("---")
st.subheader("원본 데이터 미리보기 (선택된 브랜드/월 기준)")
preview = mg_all.copy()
preview = preview[preview['brand'].isin(sel_br)]
preview = preview[preview['ym'] == sel_ym]
if sel_supply_main != "전체":
    preview = preview[preview['supply'] == sel_supply_main]
if preview.empty:
    st.info("선택한 조건에 해당하는 원본 데이터가 없습니다.")
else:
    cols_show = ['ym','brand','series','combo','name','supply','forecast','actual','차이','달성률(%)']
    preview = preview[cols_show].fillna("")
    st.dataframe(style_number_df(preview, int_cols=['forecast','actual','차이'], float_cols=['달성률(%)']), use_container_width=True)
