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
        for col in ['ym','series','brand','combo','supply']:
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
mg_all = pd.merge(f_df, a_df[["ym","combo","actual"]], on=["ym","combo"], how="left").fillna(0)
mg_all["차이"] = mg_all["actual"] - mg_all["forecast"]
mg_all["오차량"] = mg_all["차이"].abs()
mg_all["달성률(%)"] = np.where(mg_all["forecast"] > 0, (mg_all["actual"] / mg_all["forecast"] * 100).round(1), 0)

# -----------------------
# 사이드바: 공통 필터 + 탭별 필터을 사이드바 expander로 배치
# -----------------------
st.sidebar.title("필터 설정")

# 공통 필터
sel_ym = st.sidebar.selectbox("기준 년월", sorted(f_df["ym"].unique(), reverse=True))
all_brands = sorted(f_df["brand"].unique().tolist())
sel_br = st.sidebar.multiselect("브랜드 선택", all_brands, default=all_brands)

# supply 옵션: NaN(결측)은 제외하여 '기타'가 보이지 않도록 함
supply_options = ["전체"]
if 'supply' in f_df.columns:
    supply_values = f_df['supply'].dropna().unique().tolist()
    supply_options += sorted(supply_values)

# 시리즈 목록 (브랜드 선택에 따라 동적)
available_series = sorted(f_df[f_df['brand'].isin(sel_br)]['series'].dropna().unique().tolist())
series_count = len(available_series)

# 탭별 필터을 사이드바 expander로 구성
with st.sidebar.expander("메인 대시보드 필터", expanded=True):
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
    sel_supply_series = st.selectbox("공급단 선택 (시리즈 상세)", supply_options, index=0)
    top_n_series = st.slider("표시할 시리즈 수 (Top N, 시리즈 상세)", 5, 50, 20)

with st.sidebar.expander("전체 데이터 필터", expanded=False):
    sel_supply_all = st.selectbox("공급단 선택 (전체 데이터)", supply_options, index=0)

with st.sidebar.expander("수주대비 실적 분석 필터", expanded=False):
    perf_threshold_low = st.number_input("과소예측 기준(달성률 미만)", value=90, min_value=1, max_value=100)
    perf_threshold_high = st.number_input("과대예측 기준(달성률 초과)", value=110, min_value=100, max_value=1000)

# -----------------------
# 탭 구성: 메인 탭을 맨 앞에 배치
# -----------------------
tab_main, tab_ts, tab_series, tab_all, tab_perf = st.tabs([
    "🏠 메인 대시보드", "📈 시계열 추이", "🔎 시리즈 상세", "📋 전체 데이터", "🧾 수주대비 실적 분석"
])

# -----------------------
# 탭: 메인 대시보드 (맨 앞)
# -----------------------
with tab_main:
    st.header("메인 대시보드")
    st.write("사이드바의 '메인 대시보드 필터'로 제어됩니다.")

    # 필터 적용 (메인 탭은 사이드바에서 선택된 시리즈 사용)
    if not sel_sr_main:
        st.warning("사이드바의 '메인 대시보드 필터'에서 시리즈를 선택하세요.")
    else:
        f_sel = f_df[(f_df["ym"] == sel_ym) & (f_df["brand"].isin(sel_br)) & (f_df["series"].isin(sel_sr_main))].copy()
        a_sel = a_df[a_df["ym"] == sel_ym].copy()
        mg_main = pd.merge(f_sel, a_sel[["combo", "actual"]], on="combo", how="left").fillna(0)

        mg_main["차이"] = mg_main["actual"] - mg_main["forecast"]
        mg_main["오차량"] = mg_main["차이"].abs()
        mg_main["달성률(%)"] = np.where(mg_main["forecast"] > 0, (mg_main["actual"] / mg_main["forecast"] * 100).round(1), 0)

        # 정렬 맵
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

        # 데이터 테이블
        st.dataframe(mg_main.drop(columns=['오차량']), use_container_width=True, hide_index=True)

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
        # supply 선택이 '전체'가 아닌 경우, NaN(결측)은 이미 제외된 옵션만 존재하므로 필터 적용
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
        st.dataframe(merged_series.rename(columns={'forecast':'예측수요','actual':'실수주'}).sort_values('예측수요', ascending=False), use_container_width=True, hide_index=True)

# -----------------------
# 탭: 전체 데이터
# -----------------------
with tab_all:
    st.header("전체 데이터")
    st.write("사이드바의 '전체 데이터 필터'로 제어됩니다.")

    if 'supply' not in f_df.columns:
        st.info("데이터에 'supply' 컬럼이 없어 공급단별 분석을 표시할 수 없습니다.")
    else:
        df_all = f_df.copy()
        if sel_supply_all != "전체":
            df_all = df_all[df_all['supply'] == sel_supply_all]

        # NaN(결측) supply는 그룹화에서 제외되어 '기타'가 보이지 않음
        supply_agg = df_all.dropna(subset=['supply']).groupby('supply').agg({'forecast':'sum'}).reset_index()
        total_forecast = supply_agg['forecast'].sum()
        if supply_agg.empty or total_forecast == 0:
            st.info("공급단별 집계 데이터가 없습니다.")
        else:
            fig_pie = go.Figure(data=[go.Pie(labels=supply_agg['supply'], values=supply_agg['forecast'], hole=0.45,
                                             marker=dict(colors=['#60a5fa','#fb7185','#34d399','#f59e0b']))])
            fig_pie.update_layout(title=f"공급단별 예측 비중 (총합: {int(total_forecast):,})", height=420, template='plotly_white')
            st.plotly_chart(fig_pie, use_container_width=True)

            pivot = df_all.dropna(subset=['supply']).pivot_table(index='brand', columns='supply', values='forecast', aggfunc='sum', fill_value=0)
            pivot['총합'] = pivot.sum(axis=1)
            pivot = pivot.sort_values('총합', ascending=False).drop(columns=['총합'])
            st.subheader("브랜드 × 공급단 예측량")
            st.dataframe(pivot.astype(int), use_container_width=True)

# -----------------------
# 탭: 수주대비 실적 분석 (간단)
# -----------------------
with tab_perf:
    st.header("수주대비 실적 분석")
    st.write("사이드바의 '수주대비 실적 분석 필터'로 제어됩니다.")

    mg_perf = mg_all[(mg_all['ym'] == sel_ym) & (mg_all['brand'].isin(sel_br))].copy()
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

        series_perf = mg_perf.groupby('series').agg({'forecast':'sum','actual':'sum'}).reset_index()
        series_perf['달성률(%)'] = np.where(series_perf['forecast']>0, (series_perf['actual']/series_perf['forecast']*100).round(1), 0)
        series_perf['오차량'] = (series_perf['actual'] - series_perf['forecast']).abs()

        under = series_perf[series_perf['달성률(%)'] < perf_threshold_low].sort_values('달성률(%)').head(5)
        over = series_perf[series_perf['달성률(%)'] > perf_threshold_high].sort_values('달성률(%)', ascending=False).head(5)
        worst = series_perf.sort_values('오차량', ascending=False).head(5)

        st.write("")
        st.subheader("달성률 기준: 과소/과대 예측 (간단 리스트)")
        col_u, col_o = st.columns(2)
        with col_u:
            st.markdown(f"**과소예측 (달성률 < {perf_threshold_low}%) — 실적이 예측보다 적음**")
            if under.empty:
                st.write("해당 없음")
            else:
                st.table(under[['series','forecast','actual','달성률(%)']].rename(columns={'series':'시리즈','forecast':'예측','actual':'실수주'}).astype({'예측':int,'실수주':int}))
        with col_o:
            st.markdown(f"**과대예측 (달성률 > {perf_threshold_high}%) — 실적이 예측보다 많음**")
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

        st.write("")
        st.subheader("간단 권장 조치")
        st.markdown("""
        - **우선 점검**: 상위 오차 품목의 재고·프로모션·납기·채널별 판매 현황을 확인하세요.  
        - **단기 보정**: 달성률이 임계값을 벗어난 시리즈는 단기 보정 대상으로 지정하세요.  
        - **모니터링**: 다음 예측 주기에는 상위 변동 시리즈에 대해 최근 3개월 추세를 반영하세요.
        """)

# -----------------------
# 하단: 원본 데이터 미리보기 (공통)
# -----------------------
st.markdown("---")
st.subheader("원본 데이터 미리보기 (선택된 브랜드/월 기준)")
preview = mg_all.copy()
preview = preview[preview['brand'].isin(sel_br)]
preview = preview[preview['ym'] == sel_ym]
if preview.empty:
    st.info("선택한 조건에 해당하는 원본 데이터가 없습니다.")
else:
    # supply 컬럼의 결측값은 그대로 NaN으로 남아있으므로 화면에 '기타'가 표시되지 않음
    st.dataframe(preview.drop(columns=['오차량']), use_container_width=True, hide_index=True)
