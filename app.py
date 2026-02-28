import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# -----------------------
# 페이지 설정 및 공통 스타일
# -----------------------
st.set_page_config(page_title="수요예측 대시보드", page_icon="📈", layout="wide")

st.markdown("""
<style>
.metric-card { background-color:#1E293B; border-radius:10px; padding:14px; color:#fff; text-align:center; }
.metric-label { font-size:13px; color:#94A3B8; }
.metric-value { font-size:22px; font-weight:700; }
.metric-sub { font-size:11px; color:#94A3B8; }
.analysis-box { background:#F8FAFC; border-radius:10px; padding:18px; border:1px solid #E2E8F0; color:#0f172a; }
.item-card { background:#fff; padding:12px; border-radius:8px; border:1px solid #E2E8F0; margin-top:10px; }
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
        # 테스트용 더미 데이터 (파일 없을 때)
        dates = ["2026-02","2026-01","2025-12","2025-11"]
        brands = ["시디즈","퍼시스","일룸","데스커"]
        supplies = ["시디즈제품","의자양지상품","베트남제품", None]
        rows = []
        for ym in dates:
            for b in brands:
                for s in ["IBLE","T60","RINGO","ACCESSORY","T20"]:
                    rows.append({
                        "ym": ym,
                        "brand": b,
                        "series": s,
                        "combo": f"{s[:6]}-{b[:2]}",
                        "name": f"{s} 품목명",
                        "forecast": np.random.randint(50, 3000),
                        "supply": np.random.choice(supplies, p=[0.35,0.25,0.25,0.15])
                    })
        f = pd.DataFrame(rows)
        a_rows = []
        for ym in dates:
            for b in brands:
                for s in ["IBLE","T60","RINGO","ACCESSORY","T20"]:
                    a_rows.append({"ym": ym, "combo": f"{s[:6]}-{b[:2]}", "actual": max(0, int(np.random.normal(400, 300)))})
        a = pd.DataFrame(a_rows)

    # 기본 정제: 문자열 정리, 시리즈 숫자 제거
    def clean(df):
        for c in df.select_dtypes(include=['object']).columns:
            df[c] = df[c].astype(str).str.strip()
        # supply 결측은 NaN으로 유지 (사용자 요청: '기타' 제거)
        df['supply'] = df['supply'].replace({'nan': np.nan, 'None': np.nan})
        # series 숫자형 제거
        df = df[~df['series'].str.isnumeric()]
        df = df[df['series'].str.len() >= 2]
        return df

    return clean(f), clean(a)

f_df, a_df = load_data()

# -----------------------
# 공통 병합 및 지표 계산
# -----------------------
mg_all = pd.merge(f_df, a_df[["ym","combo","actual"]], on=["ym","combo"], how="left")
mg_all["actual"] = mg_all["actual"].fillna(0).astype(int)
mg_all["forecast"] = mg_all["forecast"].fillna(0).astype(int)
mg_all["차이"] = mg_all["actual"] - mg_all["forecast"]
mg_all["오차량"] = mg_all["차이"].abs()
mg_all["달성률(%)"] = np.where(mg_all["forecast"] > 0, (mg_all["actual"] / mg_all["forecast"] * 100).round(1), 0.0)

# -----------------------
# 사이드바: 간결하고 직관적인 필터 (모든 탭에서 사용)
# - 모든 필터는 expander로 묶어 탭별로 접을 수 있게 구성
# -----------------------
st.sidebar.title("필터 설정")

with st.sidebar.expander("공통 필터", expanded=True):
    sel_ym = st.selectbox("기준 년월", sorted(f_df["ym"].unique(), reverse=True))
    all_brands = sorted(f_df["brand"].dropna().unique().tolist())
    sel_br = st.multiselect("브랜드 선택", all_brands, default=all_brands)

# 공급단 옵션: 결측값(NaN)은 목록에서 제외 (요청대로 '기타' 없음)
supply_values = []
if 'supply' in f_df.columns:
    supply_values = sorted(f_df['supply'].dropna().unique().tolist())

with st.sidebar.expander("메인 대시보드 필터", expanded=True):
    st.write("메인 탭에 적용되는 필터입니다.")
    sel_supply_main = st.selectbox("공급단 선택 (메인)", ["전체"] + supply_values, index=0)
    # 시리즈 선택: 브랜드 선택에 따라 동적
    available_series = sorted(f_df[f_df['brand'].isin(sel_br)]['series'].dropna().unique().tolist())
    if len(available_series) == 0:
        st.info("선택된 브랜드에 시리즈 데이터가 없습니다.")
        sel_sr_main = []
    else:
        # 적은 수면 전체 선택, 많으면 검색 + 기본 상위 선택
        if len(available_series) <= 30:
            sel_sr_main = st.multiselect("시리즈 선택 (메인)", available_series, default=available_series)
        else:
            search_series_main = st.text_input("시리즈 검색 (메인)")
            top_default = 20
            series_rank = f_df[f_df['brand'].isin(sel_br)].groupby('series')['forecast'].sum().sort_values(ascending=False).head(top_default).index.tolist()
            if search_series_main:
                filtered = [s for s in available_series if search_series_main.lower() in s.lower()]
                sel_sr_main = st.multiselect("검색 결과에서 선택 (메인)", filtered, default=filtered[:top_default])
            else:
                sel_sr_main = st.multiselect("시리즈 선택 (메인 기본 상위)", available_series, default=series_rank)
    sort_metric_main = st.selectbox("정렬 지표 (메인)", ["오차 절대값 큰 순","차이(실-예측) 큰 순","실수주량 큰 순","예측수요 큰 순","달성률 큰 순"])
    top_n_main = st.slider("Top N 표시 수 (메인)", 5, 50, 10)
    search_term_main = st.text_input("검색 (메인: 단품코드/명칭)")

with st.sidebar.expander("시계열 추이 필터", expanded=False):
    ts_mode = st.radio("표시 기준 (시계열)", ("브랜드별","시리즈별"))
    ts_choices = sorted(mg_all['brand'].unique()) if ts_mode == "브랜드별" else sorted(mg_all['series'].unique())
    ts_target = st.multiselect("표시할 항목 (시계열)", ts_choices, default=None)

with st.sidebar.expander("시리즈 상세 필터", expanded=False):
    sel_brand_series = st.selectbox("브랜드 선택 (시리즈 상세)", ["전체"] + all_brands, index=0)
    sel_supply_series = st.selectbox("공급단 선택 (시리즈 상세)", ["전체"] + supply_values, index=0)
    top_n_series = st.slider("표시할 시리즈 수 (Top N)", 5, 50, 20)

with st.sidebar.expander("수주대비 실적 분석 필터", expanded=False):
    perf_threshold_low = st.number_input("과소예측 기준 (달성률 미만 %)", value=90, min_value=1, max_value=100)
    perf_threshold_high = st.number_input("과대예측 기준 (달성률 초과 %)", value=110, min_value=100, max_value=1000)

# -----------------------
# 탭 구성 (메인 탭을 맨 앞에)
# -----------------------
tab_main, tab_ts, tab_series, tab_all, tab_perf = st.tabs([
    "🏠 메인 대시보드", "📈 시계열 추이", "🔎 시리즈 상세", "📋 전체 데이터", "🧾 수주대비 실적 분석"
])

# -----------------------
# 유틸: 숫자 포맷 (천단위 콤마)
# -----------------------
def format_df_numbers(df, int_cols=None, float_cols=None):
    df2 = df.copy()
    if int_cols:
        for c in int_cols:
            if c in df2.columns:
                df2[c] = df2[c].apply(lambda x: f"{int(x):,}" if pd.notna(x) and str(x) != "" else "")
    if float_cols:
        for c in float_cols:
            if c in df2.columns:
                df2[c] = df2[c].apply(lambda x: f"{x:,.1f}" if pd.notna(x) and str(x) != "" else "")
    return df2

# -----------------------
# 탭: 메인 대시보드
# - 간결한 레이아웃, 공급단 '전체' 선택 시 모든 공급단(시디즈/베트남/의자양지 등) 포함
# -----------------------
with tab_main:
    st.header("메인 대시보드")
    st.write("사이드바의 '메인 대시보드 필터'에서 공급단·시리즈를 접어서 선택하세요.")

    if not sel_sr_main:
        st.warning("사이드바에서 시리즈를 선택해 주세요.")
    else:
        # 기본 필터: 기준월, 브랜드, 시리즈
        df_main = f_df[(f_df["ym"] == sel_ym) & (f_df["brand"].isin(sel_br)) & (f_df["series"].isin(sel_sr_main))].copy()

        # 공급단 필터: '전체'이면 supply가 결측이든 아니든 모두 포함하되,
        # 공급단별 집계/피벗에서는 결측(supply==NaN)은 제외하여 '기타'가 보이지 않도록 처리
        if sel_supply_main != "전체":
            df_main = df_main[df_main['supply'] == sel_supply_main]

        # 실제값 병합
        a_sel = a_df[a_df["ym"] == sel_ym].copy()
        mg_main = pd.merge(df_main, a_sel[["combo","actual"]], on="combo", how="left")
        mg_main["actual"] = mg_main["actual"].fillna(0).astype(int)
        mg_main["forecast"] = mg_main["forecast"].fillna(0).astype(int)
        mg_main["차이"] = mg_main["actual"] - mg_main["forecast"]
        mg_main["오차량"] = mg_main["차이"].abs()
        mg_main["달성률(%)"] = np.where(mg_main["forecast"]>0, (mg_main["actual"]/mg_main["forecast"]*100).round(1), 0.0)

        # 정렬 맵 (한글)
        sort_map = {
            "오차 절대값 큰 순": ("오차량", False),
            "차이(실-예측) 큰 순": ("차이", False),
            "실수주량 큰 순": ("actual", False),
            "예측수요 큰 순": ("forecast", False),
            "달성률 큰 순": ("달성률(%)", False)
        }
        # 사용자가 선택한 정렬 텍스트가 기존 옵션과 다를 수 있으므로 안전하게 매핑
        sort_key = "오차량"
        ascending = False
        if sort_metric_main in sort_map:
            sort_key, ascending = sort_map[sort_metric_main]
        mg_main = mg_main.sort_values(by=sort_key, ascending=ascending)

        # 검색 필터
        if search_term_main:
            mg_main = mg_main[mg_main['combo'].str.contains(search_term_main, case=False) | mg_main['name'].str.contains(search_term_main, case=False)]

        # 요약 카드 (숫자 포맷)
        t_f = int(mg_main['forecast'].sum())
        t_a = int(mg_main['actual'].sum())
        t_d = int(t_a - t_f)
        t_r = (t_a / t_f * 100) if t_f > 0 else 0.0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">예측수요 합계</div><div class="metric-value">{t_f:,}</div><div class="metric-sub">Forecast</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">실수주 합계</div><div class="metric-value">{t_a:,}</div><div class="metric-sub">{sel_ym.split("-")[1]}월</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">차이 합계</div><div class="metric-value" style="color:#fb7185">{t_d:,}</div><div class="metric-sub">Actual - Forecast</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="metric-card"><div class="metric-label">전체 달성률</div><div class="metric-value">{t_r:.1f}%</div><div class="metric-sub">Actual / Forecast</div></div>', unsafe_allow_html=True)

        # 차트: Top N (간결하게 시리즈별 비교)
        st.write("")
        left, right = st.columns(2)
        chart_data = mg_main.groupby('series').agg({'forecast':'sum','actual':'sum'}).reset_index().sort_values('forecast', ascending=False).head(top_n_main)

        with left:
            st.subheader(f"상위 Top {top_n_main} 수량 분석 (시리즈)")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=chart_data['series'], y=chart_data['forecast'], name='예측수요', marker_color='#3b82f6'))
            fig.add_trace(go.Bar(x=chart_data['series'], y=chart_data['actual'], name='실수주량', marker_color='#fb7185'))
            fig.update_layout(barmode='group', template='plotly_white', height=420)
            st.plotly_chart(fig, use_container_width=True)

        with right:
            st.subheader("달성률 현황 (Top)")
            chart_rate = chart_data.copy()
            chart_rate['달성률(%)'] = np.where(chart_rate['forecast']>0, (chart_rate['actual']/chart_rate['forecast']*100).round(1), 0.0)
            fig2 = go.Figure(go.Bar(x=chart_rate['series'], y=chart_rate['달성률(%)'], marker_color='#0ea5e9'))
            fig2.add_hline(y=100, line_dash="dash", line_color="red")
            fig2.update_layout(template='plotly_white', height=420)
            st.plotly_chart(fig2, use_container_width=True)

        # 상세 테이블: supply 결측값은 빈칸으로 표시하되 '기타' 컬럼은 만들지 않음
        cols_show = ['ym','brand','series','combo','name','supply','forecast','actual','차이','달성률(%)']
        display_df = mg_main[cols_show].fillna("")
        display_df = format_df_numbers(display_df, int_cols=['forecast','actual','차이'], float_cols=['달성률(%)'])
        st.subheader("상세 데이터")
        st.dataframe(display_df, use_container_width=True)

# -----------------------
# 탭: 시계열 추이 (간단)
# -----------------------
with tab_ts:
    st.header("시계열 추이")
    st.write("월별 예측과 실적 추이를 브랜드/시리즈별로 간단히 확인합니다.")

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
        top_items = mg_time.groupby(group_col)['forecast'].sum().sort_values(ascending=False).head(4).index.tolist()
        agg = agg[agg[group_col].isin(top_items)]

    if agg.empty:
        st.info("선택한 조건에 해당하는 시계열 데이터가 없습니다.")
    else:
        fig = go.Figure()
        for it in agg[group_col].unique():
            df_it = agg[agg[group_col]==it].sort_values('ym_dt')
            fig.add_trace(go.Scatter(x=df_it['ym_dt'], y=df_it['forecast'], mode='lines+markers', name=f"{it} 예측", line=dict(dash='dash')))
            fig.add_trace(go.Scatter(x=df_it['ym_dt'], y=df_it['actual'], mode='lines+markers', name=f"{it} 실적"))
        fig.update_layout(title="월별 예측 vs 실적", xaxis_title="기준월", yaxis_title="수량", template='plotly_white', height=520)
        st.plotly_chart(fig, use_container_width=True)

# -----------------------
# 탭: 시리즈 상세
# -----------------------
with tab_series:
    st.header("시리즈 상세")
    st.write("브랜드/공급단 필터로 시리즈별 예측량을 확인하세요.")

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
        fig_s.update_layout(title=f"시리즈별 예측량 (Top {top_n_series})", xaxis_title="예측수량", template='plotly_white', height=520)
        st.plotly_chart(fig_s, use_container_width=True)

        # 시리즈별 예측/실적 표 (전체 기간 합계)
        actual_map = mg_all.groupby('series').agg({'actual':'sum'}).reset_index()
        merged = series_agg.merge(actual_map, on='series', how='left').fillna(0)
        merged['달성률(%)'] = np.where(merged['forecast']>0, (merged['actual']/merged['forecast']*100).round(1), 0.0)
        merged_display = merged.rename(columns={'forecast':'예측수요','actual':'실수주'})
        merged_display = format_df_numbers(merged_display, int_cols=['예측수수','예측수수'] if False else ['예측수수'] )  # no-op safe
        # simpler formatting:
        merged_display = format_df_numbers(merged_display, int_cols=['예측수수'] if False else ['예측수수'])  # keep stable
        # show raw but formatted manually:
        merged_display = merged.rename(columns={'forecast':'예측수요','actual':'실수주'})
        merged_display = format_df_numbers(merged_display, int_cols=['예측수요','실수주'], float_cols=['달성률(%)'])
        st.subheader("시리즈별 예측/실적 (전체 기간 합계)")
        st.dataframe(merged_display, use_container_width=True)

# -----------------------
# 탭: 전체 데이터 (공급단 분포 및 피벗)
# -----------------------
with tab_all:
    st.header("전체 데이터")
    st.write("공급단별 예측 비중과 브랜드×공급단 피벗을 확인합니다.")

    df_all = f_df.copy()
    if sel_supply_all := (st.session_state.get("sel_supply_all") if "sel_supply_all" in st.session_state else None):
        pass  # placeholder (we use sidebar expander earlier)
    if 'sel_supply_all' in locals() and sel_supply_all != "전체":
        df_all = df_all[df_all['supply'] == sel_supply_all]

    supply_agg = df_all.dropna(subset=['supply']).groupby('supply').agg({'forecast':'sum'}).reset_index()
    if supply_agg.empty:
        st.info("공급단별 집계 데이터가 없습니다.")
    else:
        total_forecast = int(supply_agg['forecast'].sum())
        fig_pie = go.Figure(data=[go.Pie(labels=supply_agg['supply'], values=supply_agg['forecast'], hole=0.45)])
        fig_pie.update_layout(title=f"공급단별 예측 비중 (총합: {total_forecast:,})", template='plotly_white', height=420)
        st.plotly_chart(fig_pie, use_container_width=True)

        pivot = df_all.dropna(subset=['supply']).pivot_table(index='brand', columns='supply', values='forecast', aggfunc='sum', fill_value=0)
        pivot['총합'] = pivot.sum(axis=1)
        pivot = pivot.sort_values('총합', ascending=False).drop(columns=['총합'])
        pivot_display = pivot.astype(int).reset_index()
        int_cols = [c for c in pivot_display.columns if c != 'brand']
        pivot_display = format_df_numbers(pivot_display, int_cols=int_cols)
        st.subheader("브랜드 × 공급단 예측량")
        st.dataframe(pivot_display, use_container_width=True)

# -----------------------
# 탭: 수주대비 실적 분석 (한글 서술형 리포트)
# -----------------------
def generate_narrative(mg_perf, low_thr=90, high_thr=110):
    total_forecast = int(mg_perf['forecast'].sum())
    total_actual = int(mg_perf['actual'].sum())
    total_diff = total_actual - total_forecast
    total_rate = (total_actual / total_forecast * 100) if total_forecast > 0 else 0.0

    series_perf = mg_perf.groupby('series').agg({'forecast':'sum','actual':'sum'}).reset_index()
    series_perf['달성률'] = np.where(series_perf['forecast']>0, (series_perf['actual']/series_perf['forecast']*100).round(1), 0.0)
    series_perf['오차량'] = (series_perf['actual'] - series_perf['forecast']).abs()
    worst = series_perf.sort_values('오차량', ascending=False).head(5)

    under = series_perf[series_perf['달성률'] < low_thr].sort_values('달성률').head(5)
    over = series_perf[series_perf['달성률'] > high_thr].sort_values('달성률', ascending=False).head(5)

    html = f"""
    <div class="analysis-box">
      <strong>요약</strong><br>
      기준월 예측수요 <strong>{total_forecast:,}</strong>건, 실제수주 <strong>{total_actual:,}</strong>건, 차이 <strong>{total_diff:,}</strong>건, 전체 달성률 <strong>{total_rate:.1f}%</strong>입니다.<br><br>
      <strong>주요 관찰</strong><br>
      - 전체적으로 예측 대비 실수주가 {'부족' if total_rate < 100 else '초과'}한 경향입니다.<br>
      - 오차가 큰 상위 품목은 우선 원인(재고·프로모션·납기·채널)을 점검하세요.<br><br>
      <strong>상위 오차 품목 (절대값 기준)</strong><br>
    """
    if worst.empty:
        html += "해당 없음<br>"
    else:
        for _, r in worst.iterrows():
            html += f"- {r['series']}: 예측 {int(r['forecast']):,} → 실제 {int(r['actual']):,} (오차 {int(r['오차량']):,}, 달성률 {r['달성률']:.1f}%)<br>"

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
      <br><strong>권장 조치</strong><br>
      1) 상위 오차 품목의 재고·프로모션·납기·채널별 판매 현황을 우선 점검하세요.<br>
      2) 과소예측 품목은 수요 감소 원인(반품·납기지연 등)을 확인하세요.<br>
      3) 과대예측 품목은 판촉·대량발주 여부를 확인하고 다음 예측에 반영하세요.<br>
      4) 반복 오차 품목은 별도 모니터링 대상으로 지정하세요.<br>
    </div>
    """
    return html

with tab_perf:
    st.header("수주대비 실적 분석")
    st.write("사이드바 필터로 제어됩니다. (기준 년월 / 브랜드 / 공급단)")

    mg_perf = mg_all[(mg_all['ym'] == sel_ym) & (mg_all['brand'].isin(sel_br))].copy()
    if sel_supply_main != "전체":
        mg_perf = mg_perf[mg_perf['supply'] == sel_supply_main]

    if mg_perf.empty:
        st.info("선택한 조건에 해당하는 데이터가 없습니다.")
    else:
        total_forecast = int(mg_perf['forecast'].sum())
        total_actual = int(mg_perf['actual'].sum())
        total_diff = total_actual - total_forecast
        total_rate = (total_actual / total_forecast * 100) if total_forecast > 0 else 0.0

        p1, p2, p3, p4 = st.columns(4)
        p1.metric("예측수요 합계", f"{total_forecast:,}")
        p2.metric("실수주 합계", f"{total_actual:,}")
        p3.metric("차이(실-예측)", f"{total_diff:,}", delta=f"{total_diff:,}")
        p4.metric("전체 달성률", f"{total_rate:.1f}%")

        series_perf = mg_perf.groupby('series').agg({'forecast':'sum','actual':'sum'}).reset_index()
        series_perf['달성률(%)'] = np.where(series_perf['forecast']>0, (series_perf['actual']/series_perf['forecast']*100).round(1), 0.0)
        series_perf['오차량'] = (series_perf['actual'] - series_perf['forecast']).abs()
        st.subheader("시리즈별 성과")
        st.dataframe(format_df_numbers(series_perf.rename(columns={'forecast':'예측수요','actual':'실수주'}), int_cols=['예측수수'] if False else ['예측수수']), use_container_width=True)

        st.subheader("자동 분석 리포트 (요약)")
        st.markdown(generate_narrative(mg_perf, low_thr=perf_threshold_low, high_thr=perf_threshold_high), unsafe_allow_html=True)

# -----------------------
# 하단: 원본 데이터 미리보기
# -----------------------
st.markdown("---")
st.subheader("원본 데이터 미리보기 (선택된 브랜드/월 기준)")
preview = mg_all[(mg_all['brand'].isin(sel_br)) & (mg_all['ym'] == sel_ym)].copy()
if sel_supply_main != "전체":
    preview = preview[preview['supply'] == sel_supply_main]
if preview.empty:
    st.info("선택한 조건에 해당하는 원본 데이터가 없습니다.")
else:
    cols = ['ym','brand','series','combo','name','supply','forecast','actual','차이','달성률(%)']
    preview = preview[cols].fillna("")
    preview = format_df_numbers(preview, int_cols=['forecast','actual','차이'], float_cols=['달성률(%)'])
    st.dataframe(preview, use_container_width=True)
