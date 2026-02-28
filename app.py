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

# -----------------------
# 데이터 로드 및 정제
# -----------------------
@st.cache_data
def load_data():
    try:
        f = pd.read_csv("forecast_data.csv")
        a = pd.read_csv("actual_data.csv")
    except Exception:
        # 파일이 없을 때 사용할 더미 데이터
        dates = ["2025-06","2025-07","2025-08","2025-09","2025-10","2025-11","2025-12","2026-01","2026-02"]
        brands = ["데스커", "일룸", "퍼시스", "시디즈"]
        rows = []
        for ym in dates:
            for b in brands:
                for s in ["ACCESSORY","IBLE","SPOON","SODA","T60","RINGO","T20","GX"]:
                    rows.append({
                        'ym': ym,
                        'brand': b,
                        'series': s,
                        'combo': f"{s[:6]}-{b[:2]}",
                        'name': f"{s}품목",
                        'forecast': np.random.randint(100, 5000),
                        'supply': np.random.choice(['시디즈제품','의자양지상품','베트남제품'])
                    })
        f = pd.DataFrame(rows)
        a_rows = []
        for ym in dates:
            for b in brands:
                for s in ["ACCESSORY","IBLE","SPOON","SODA","T60","RINGO","T20","GX"]:
                    a_rows.append({'ym': ym, 'combo': f"{s[:6]}-{b[:2]}", 'actual': max(0, int(np.random.normal(800, 600)))})
        a = pd.DataFrame(a_rows)

    def clean_df(df):
        # 필수 컬럼 보장
        for col in ['ym','series','brand','combo']:
            if col not in df.columns:
                df[col] = ""
        df = df.dropna(subset=['series','brand','combo'])
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
        # 숫자형 시리즈 제거 및 길이 필터
        df = df[~df['series'].str.isnumeric()]
        df = df[df['series'].str.len() >= 2]
        return df

    return clean_df(f), clean_df(a)

f_df, a_df = load_data()

# -----------------------
# 공통 계산: 병합 및 지표
# -----------------------
# 실제 데이터가 ym, combo 기준으로 합쳐져 있다고 가정
mg = pd.merge(f_df, a_df[["ym","combo","actual"]], on=["ym","combo"], how="left").fillna(0)
mg["차이"] = mg["actual"] - mg["forecast"]
mg["오차량"] = mg["차이"].abs()
mg["달성률(%)"] = np.where(mg["forecast"] > 0, (mg["actual"] / mg["forecast"] * 100).round(1), 0)

# -----------------------
# 사이드바: 공통 필터
# -----------------------
st.sidebar.title("🔍 필터 설정")
sel_ym = st.sidebar.selectbox("📅 기준 년월", sorted(f_df["ym"].unique(), reverse=True))
all_brands = sorted(f_df["brand"].unique().tolist())
sel_br = st.sidebar.multiselect("🏷️ 브랜드", all_brands, default=all_brands)
# 시리즈 필터는 각 탭에서 별도 제공 가능

# -----------------------
# 탭 구성: 이미지 탭들을 메인 탭으로 추가 + 기존 메인 + 간단 분석 탭
# 탭 순서: (이미지 탭들) / 메인 대시보드 / 수주대비 실적 분석
# -----------------------
tab_ts, tab_series, tab_all, tab_main, tab_perf = st.tabs([
    "📈 시계열 추이", "🔎 시리즈 상세", "📋 전체 데이터", "🏠 메인 대시보드", "🧾 수주대비 실적 분석"
])

# -----------------------
# 탭: 시계열 추이 (이미지 탭 중 하나)
# -----------------------
with tab_ts:
    st.header("시계열 추이")
    st.write("월별 예측과 실적의 추이를 브랜드/시리즈별로 비교합니다.")

    # 표시 기준 선택
    ts_mode = st.radio("표시 기준", ("브랜드별", "시리즈별"), horizontal=True)
    if ts_mode == "브랜드별":
        choices = sorted(mg['brand'].unique())
    else:
        choices = sorted(mg['series'].unique())

    ts_target = st.multiselect("표시할 항목 선택 (없으면 상위 4개)", choices, default=None)

    # 시간형 변환
    mg_time = mg.copy()
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
# 탭: 시리즈 상세 (이미지 탭 중 하나)
# -----------------------
with tab_series:
    st.header("시리즈 상세")
    st.write("브랜드와 공급단(또는 전체)을 선택하여 시리즈별 예측량을 확인합니다.")

    sel_brand_series = st.selectbox("브랜드 선택", ["전체"] + all_brands, index=0)
    supply_options = ["전체"]
    if 'supply' in f_df.columns:
        supply_options += sorted(f_df['supply'].dropna().unique().tolist())
    sel_supply = st.selectbox("공급단 선택", supply_options, index=0)

    df_series = f_df.copy()
    if sel_brand_series != "전체":
        df_series = df_series[df_series['brand'] == sel_brand_series]
    if sel_supply != "전체":
        df_series = df_series[df_series['supply'] == sel_supply]

    series_agg = df_series.groupby('series').agg({'forecast':'sum'}).reset_index().sort_values('forecast', ascending=False)
    if series_agg.empty:
        st.info("선택한 조건에 해당하는 시리즈 데이터가 없습니다.")
    else:
        max_n = max(5, min(50, len(series_agg)))
        top_n_series = st.slider("표시할 시리즈 수 (Top N)", 5, max_n, min(20, max_n))
        plot_df = series_agg.head(top_n_series).sort_values('forecast')

        fig_s = go.Figure(go.Bar(x=plot_df['forecast'], y=plot_df['series'], orientation='h', marker_color='#3b82f6'))
        fig_s.update_layout(title=f"시리즈별 예측량 (Top {top_n_series})", xaxis_title="예측수량", yaxis_title="시리즈", template='plotly_white', height=520)
        st.plotly_chart(fig_s, use_container_width=True)

        # 시리즈별 예측/실적 테이블 (전체 기간 합계)
        actual_map = mg.groupby('series').agg({'actual':'sum'}).reset_index()
        merged_series = series_agg.merge(actual_map, on='series', how='left').fillna(0)
        merged_series['달성률(%)'] = np.where(merged_series['forecast']>0, (merged_series['actual']/merged_series['forecast']*100).round(1), 0)
        st.dataframe(merged_series.rename(columns={'forecast':'예측수요','actual':'실수주'}).sort_values('예측수요', ascending=False), use_container_width=True, hide_index=True)

# -----------------------
# 탭: 전체 데이터 (이미지 탭 중 하나)
# -----------------------
with tab_all:
    st.header("전체 데이터")
    st.write("공급단별 예측 비중과 브랜드 × 공급단별 예측량을 확인합니다.")

    if 'supply' not in f_df.columns:
        st.info("데이터에 'supply' 컬럼이 없어 공급단별 분석을 표시할 수 없습니다.")
    else:
        supply_agg = f_df.groupby('supply').agg({'forecast':'sum'}).reset_index()
        total_forecast = supply_agg['forecast'].sum()
        if supply_agg.empty or total_forecast == 0:
            st.info("공급단별 집계 데이터가 없습니다.")
        else:
            fig_pie = go.Figure(data=[go.Pie(labels=supply_agg['supply'], values=supply_agg['forecast'], hole=0.45,
                                             marker=dict(colors=['#60a5fa','#fb7185','#34d399','#f59e0b']))])
            fig_pie.update_layout(title=f"공급단별 예측 비중 (총합: {int(total_forecast):,})", height=420, template='plotly_white')
            st.plotly_chart(fig_pie, use_container_width=True)

            pivot = f_df.pivot_table(index='brand', columns='supply', values='forecast', aggfunc='sum', fill_value=0)
            pivot['총합'] = pivot.sum(axis=1)
            pivot = pivot.sort_values('총합', ascending=False).drop(columns=['총합'])
            st.subheader("브랜드 × 공급단 예측량")
            st.dataframe(pivot.astype(int), use_container_width=True)

# -----------------------
# 탭: 메인 대시보드 (원래 사용하던 메인 화면)
# -----------------------
with tab_main:
    st.header("메인 대시보드")
    st.write("기본 필터로 선택된 브랜드/시리즈에 대한 요약과 차트, 테이블을 제공합니다.")

    # 기존의 상단 컨트롤(메인에서 사용하던 것과 유사하게)
    col1, col2, col3 = st.columns([2, 2, 3])
    with col1:
        sort_metric = st.selectbox("📌 정렬 지표", 
                                   ["차이량(|실-예측|) 큰 순", "차이량(실-예측) 큰 순", "실수주량 큰 순", "예측수요 큰 순", "달성률 큰 순"])
    with col2:
        top_n = st.slider("🎯 Top N", 5, len(mg) if len(mg) > 5 else 10, 10)
    with col3:
        search_term = st.text_input("🔎 검색 (단품코드/명칭)", placeholder="예: S60 / 바퀴형 의자")

    # 브랜드/시리즈 필터 (메인 탭 전용)
    filtered_f = f_df[f_df["brand"].isin(sel_br)]
    all_series = sorted(filtered_f["series"].unique().tolist())
    sel_sr = st.multiselect("🪑 시리즈 (메인)", all_series, default=all_series)

    # 데이터 선택 및 병합
    f_sel = f_df[(f_df["ym"] == sel_ym) & (f_df["brand"].isin(sel_br)) & (f_df["series"].isin(sel_sr))].copy()
    a_sel = a_df[a_df["ym"] == sel_ym].copy()
    mg_main = pd.merge(f_sel, a_sel[["combo", "actual"]], on="combo", how="left").fillna(0)

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
    mg_main = mg_main.sort_values(by=sort_map[sort_metric][0], ascending=sort_map[sort_metric][1])

    # 검색 필터
    if search_term:
        mg_main = mg_main[mg_main['combo'].str.contains(search_term, case=False) | mg_main['name'].str.contains(search_term, case=False)]

    # 요약 카드
    t_f = mg_main['forecast'].sum()
    t_a = mg_main['actual'].sum()
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

    # 차트
    st.write("")
    c1, c2 = st.columns(2)
    chart_data = mg_main.head(top_n)

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
    st.dataframe(mg_main.drop(columns=['오차량']), use_container_width=True, hide_index=True)

# -----------------------
# 탭: 수주대비 실적 분석 (간단한 분석 탭)
# -----------------------
with tab_perf:
    st.header("수주대비 실적 분석")
    st.write("선택한 기준월과 브랜드에 대해 간단히 실적(실수주) 대비 예측의 성과를 요약합니다.")

    # 기준 데이터
    mg_perf = mg[(mg['ym'] == sel_ym) & (mg['brand'].isin(sel_br))].copy()
    if mg_perf.empty:
        st.info("선택한 조건에 해당하는 데이터가 없습니다.")
    else:
        total_forecast = mg_perf['forecast'].sum()
        total_actual = mg_perf['actual'].sum()
        total_diff = total_actual - total_forecast
        total_rate = (total_actual / total_forecast * 100) if total_forecast > 0 else 0

        st.subheader("요약 지표")
        p1, p2, p3, p4 = st.columns(4)
        with p1:
            st.metric("예측수요 합계", f"{int(total_forecast):,}")
        with p2:
            st.metric("실수주 합계", f"{int(total_actual):,}")
        with p3:
            st.metric("차이(실-예측)", f"{int(total_diff):,}", delta=f"{int(total_diff):,}")
        with p4:
            st.metric("전체 달성률", f"{total_rate:.1f}%")

        # 상/하위 성과 시리즈
        series_perf = mg_perf.groupby('series').agg({'forecast':'sum','actual':'sum'}).reset_index()
        series_perf['달성률(%)'] = np.where(series_perf['forecast']>0, (series_perf['actual']/series_perf['forecast']*100).round(1), 0)
        series_perf['오차량'] = (series_perf['actual'] - series_perf['forecast']).abs()

        # 과대/과소 예측 상위
        under = series_perf[series_perf['달성률(%)'] < 90].sort_values('달성률(%)').head(5)
        over = series_perf[series_perf['달성률(%)'] > 110].sort_values('달성률(%)', ascending=False).head(5)
        worst = series_perf.sort_values('오차량', ascending=False).head(5)

        st.write("")
        st.subheader("달성률 기준: 과소/과대 예측 (간단 리스트)")
        col_u, col_o = st.columns(2)
        with col_u:
            st.markdown("**과소예측 (달성률 < 90%) — 실제가 예측보다 적음**")
            if under.empty:
                st.write("해당 없음")
            else:
                st.table(under[['series','forecast','actual','달성률(%)']].rename(columns={'series':'시리즈','forecast':'예측','actual':'실수주'}).astype({'예측':int,'실수주':int}))
        with col_o:
            st.markdown("**과대예측 (달성률 > 110%) — 실제가 예측보다 많음**")
            if over.empty:
                st.write("해당 없음")
            else:
                st.table(over[['series','forecast','actual','달성률(%)']].rename(columns={'series':'시리즈','forecast':'예측','actual':'실수주'}).astype({'예측':int,'실수주':int}))

        st.write("")
        st.subheader("오차량(절대값) 기준 상위 품목")
        if worst.empty:
            st.write("해당 없음")
        else:
            st.table(worst[['series','forecast','actual','오차량']].rename(columns={'series':'시리즈','forecast':'예측','actual':'실수주'}).astype({'예측':int,'실수주':int,'오차량':int}))

        # 간단 권장 조치
        st.write("")
        st.subheader("간단 권장 조치")
        st.markdown("""
        - **우선 점검**: 상위 오차 품목의 재고·프로모션·납기·채널별 판매 현황을 확인하세요.  
        - **단기 보정**: 달성률이 80% 미만 또는 120% 초과인 시리즈는 단기 보정 대상으로 지정하세요.  
        - **모니터링**: 다음 예측 주기에는 상위 변동 시리즈에 대해 최근 3개월 추세를 반영하세요.
        """)

# -----------------------
# 하단: 원본 데이터 미리보기 (공통)
# -----------------------
st.markdown("---")
st.subheader("원본 데이터 미리보기 (선택된 브랜드/월 기준)")
preview = mg.copy()
preview = preview[preview['brand'].isin(sel_br)]
preview = preview[preview['ym'] == sel_ym]
if preview.empty:
    st.info("선택한 조건에 해당하는 원본 데이터가 없습니다.")
else:
    st.dataframe(preview.drop(columns=['오차량']), use_container_width=True, hide_index=True)
