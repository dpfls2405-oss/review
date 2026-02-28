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
        # 더미 데이터 (파일이 없을 때)
        dates = ["2025-06","2025-07","2025-08","2025-09","2025-10","2025-11","2025-12","2026-01","2026-02"]
        brands = ["데스커", "일룸", "퍼시스", "시디즈"]
        rows = []
        for ym in dates:
            for b in brands:
                for s in ["IBLE","VIM","AROUND","GX"]:
                    rows.append({'ym': ym, 'brand': b, 'series': s, 'combo': f"{s[:3]}-{b[:2]}", 'name': f"{s}품목", 'forecast': np.random.randint(200, 800), 'supply': np.random.choice(['시디즈제품','의자양지상품','베트남제품'])})
        f = pd.DataFrame(rows)
        # 실제 데이터: 일부만 실제값 생성
        a_rows = []
        for ym in dates:
            for b in brands:
                for s in ["IBLE","VIM","AROUND","GX"]:
                    a_rows.append({'ym': ym, 'combo': f"{s[:3]}-{b[:2]}", 'actual': max(0, int(np.random.normal(500, 150)))})
        a = pd.DataFrame(a_rows)

    def clean_df(df):
        # 필수 컬럼 존재 확인 후 정리
        for col in ['ym','series','brand','combo']:
            if col not in df.columns:
                df[col] = ""
        df = df.dropna(subset=['series', 'brand', 'combo'])
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
        # 숫자형 시리즈 제거 및 길이 필터
        df = df[~df['series'].str.isnumeric()]
        df = df[df['series'].str.len() >= 2]
        return df

    return clean_df(f), clean_df(a)

f_df, a_df = load_data()

# 3. 사이드바 및 상단 컨트롤러 (공통)
st.sidebar.title("🔍 필터 설정")
sel_ym = st.sidebar.selectbox("📅 기준 년월 (메인)", sorted(f_df["ym"].unique(), reverse=True))

all_brands = sorted(f_df["brand"].unique().tolist())
sel_br = st.sidebar.multiselect("🏷️ 브랜드 (전체)", all_brands, default=all_brands)

# 공통 병합 (선택된 브랜드 기준)
f_sel_all = f_df[f_df["brand"].isin(sel_br)].copy()
a_sel_all = a_df.copy()
mg_all = pd.merge(f_sel_all, a_sel_all[["ym","combo","actual"]], on=["ym","combo"], how="left").fillna(0)
mg_all["차이"] = mg_all["actual"] - mg_all["forecast"]
mg_all["오차량"] = mg_all["차이"].abs()
mg_all["달성률(%)"] = np.where(mg_all["forecast"] > 0, (mg_all["actual"] / mg_all["forecast"] * 100).round(1), 0)

# --- 탭 구성: 시계열 추이 / 시리즈 상세 / 전체 데이터 ---
tab_ts, tab_series, tab_all = st.tabs(["📈 시계열 추이", "🔎 시리즈 상세", "📋 전체 데이터"])

# -----------------------
# 탭 1: 시계열 추이
# -----------------------
with tab_ts:
    st.header("시계열 추이")
    st.write("월별 예측과 실적의 추이를 브랜드/시리즈별로 비교합니다.")

    # 사용자 선택: 라인에 표시할 대상 (브랜드 또는 시리즈)
    ts_mode = st.radio("표시 기준", ("브랜드별", "시리즈별"), horizontal=True)
    ts_target = st.multiselect("표시할 항목 선택", sorted(f_df[ts_mode.lower().replace('별','')].unique()) if ts_mode=="시리즈별" else all_brands, default=None)

    # 시간 순 정렬
    mg_time = mg_all.copy()
    # ym을 날짜형으로 변환 시도 (YYYY-MM 형식 가정)
    try:
        mg_time['ym_dt'] = pd.to_datetime(mg_time['ym'] + "-01", format="%Y-%m-%d")
    except:
        mg_time['ym_dt'] = mg_time['ym']

    # 집계: ym, target, forecast/actual 합계
    if ts_mode == "브랜드별":
        group_col = "brand"
    else:
        group_col = "series"

    agg = mg_time.groupby(['ym_dt', group_col]).agg({'forecast':'sum','actual':'sum'}).reset_index()
    # 필터링: 선택 항목이 있으면 제한
    if ts_target:
        agg = agg[agg[group_col].isin(ts_target)]

    # 기본적으로 상위 4개 항목만 표시 (선택 없을 때)
    if not ts_target:
        top_items = (mg_time.groupby(group_col)['forecast'].sum().abs().sort_values(ascending=False).head(4).index.tolist())
        agg = agg[agg[group_col].isin(top_items)]

    if agg.empty:
        st.info("선택한 조건에 해당하는 시계열 데이터가 없습니다.")
    else:
        fig = go.Figure()
        items = agg[group_col].unique()
        for it in items:
            df_it = agg[agg[group_col]==it].sort_values('ym_dt')
            fig.add_trace(go.Scatter(x=df_it['ym_dt'], y=df_it['forecast'], mode='lines+markers', name=f"{it} 예측", line=dict(dash='dash')))
            fig.add_trace(go.Scatter(x=df_it['ym_dt'], y=df_it['actual'], mode='lines+markers', name=f"{it} 실적"))
        fig.update_layout(title="월별 예측 vs 실적 추이", xaxis_title="기준월", yaxis_title="수량", template='plotly_white', height=500)
        st.plotly_chart(fig, use_container_width=True)

    # 요약 카드 (선택한 기준월 기준)
    st.write("")
    st.subheader(f"{sel_ym} 요약 지표")
    mg_sel_month = mg_all[mg_all['ym']==sel_ym]
    t_f = mg_sel_month['forecast'].sum()
    t_a = mg_sel_month['actual'].sum()
    t_d = t_a - t_f
    t_r = (t_a / t_f * 100) if t_f > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">예측수요 합계</div><div class="metric-value">{int(t_f):,}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">실수주 합계</div><div class="metric-value">{int(t_a):,}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">차이 합계</div><div class="metric-value" style="color:#fb7185">{int(t_d):,}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">달성률</div><div class="metric-value">{t_r:.1f}%</div></div>', unsafe_allow_html=True)

# -----------------------
# 탭 2: 시리즈 상세
# -----------------------
with tab_series:
    st.header("시리즈 상세")
    st.write("브랜드와 공급단(또는 전체)을 선택하여 시리즈별 예측량을 확인합니다.")

    # 브랜드 선택 (탭 전용)
    sel_brand_series = st.selectbox("브랜드 선택", ["전체"] + all_brands, index=0)
    # 공급단 선택 (supply 컬럼이 있으면 사용)
    supply_options = ["전체"]
    if 'supply' in f_df.columns:
        supply_options += sorted(f_df['supply'].dropna().unique().tolist())
    sel_supply = st.selectbox("공급단 선택", supply_options, index=0)

    # 필터 적용
    df_series = f_df.copy()
    if sel_brand_series != "전체":
        df_series = df_series[df_series['brand']==sel_brand_series]
    if sel_supply != "전체":
        df_series = df_series[df_series['supply']==sel_supply]

    # 집계: 시리즈별 예측 합계 (최근 기준월 또는 전체)
    series_agg = df_series.groupby('series').agg({'forecast':'sum'}).reset_index().sort_values('forecast', ascending=False)
    if series_agg.empty:
        st.info("선택한 조건에 해당하는 시리즈 데이터가 없습니다.")
    else:
        # 수평 바 차트 (상위 30개)
        top_n_series = st.slider("표시할 시리즈 수 (Top N)", 5, min(50, max(5, len(series_agg))), min(20, len(series_agg)))
        plot_df = series_agg.head(top_n_series).sort_values('forecast')
        fig_s = go.Figure(go.Bar(x=plot_df['forecast'], y=plot_df['series'], orientation='h', marker_color='#3b82f6'))
        fig_s.update_layout(title=f"시리즈별 예측량 (Top {top_n_series})", xaxis_title="예측수량", yaxis_title="시리즈", template='plotly_white', height=500)
        st.plotly_chart(fig_s, use_container_width=True)

        # 테이블: 시리즈별 예측/실적(가능하면)
        # 실제값은 combo 기준으로 합쳐서 시리즈에 매핑
        # mg_all에 ym 컬럼이 있으므로 전체 기간 합계로 표시
        actual_map = mg_all.groupby('series').agg({'actual':'sum'}).reset_index()
        merged_series = series_agg.merge(actual_map, on='series', how='left').fillna(0)
        merged_series['달성률(%)'] = np.where(merged_series['forecast']>0, (merged_series['actual']/merged_series['forecast']*100).round(1), 0)
        st.dataframe(merged_series.rename(columns={'forecast':'예측수요','actual':'실수주'}).sort_values('예측수요', ascending=False), use_container_width=True, hide_index=True)

# -----------------------
# 탭 3: 전체 데이터 (공급단 분포, 브랜드×공급단 테이블)
# -----------------------
with tab_all:
    st.header("전체 데이터")
    st.write("공급단별 예측 비중과 브랜드 × 공급단별 예측량을 확인합니다.")

    # 공급단 분포 (forecast 기준)
    if 'supply' not in f_df.columns:
        st.info("데이터에 'supply' 컬럼이 없어 공급단별 분석을 표시할 수 없습니다.")
    else:
        supply_agg = f_df.groupby('supply').agg({'forecast':'sum'}).reset_index()
        total_forecast = supply_agg['forecast'].sum()
        if supply_agg.empty or total_forecast == 0:
            st.info("공급단별 집계 데이터가 없습니다.")
        else:
            # 도넛 차트
            fig_pie = go.Figure(data=[go.Pie(labels=supply_agg['supply'], values=supply_agg['forecast'], hole=0.45,
                                             marker=dict(colors=['#60a5fa','#fb7185','#34d399','#f59e0b']))])
            fig_pie.update_layout(title=f"공급단별 예측 비중 (총합: {int(total_forecast):,})", height=420, template='plotly_white')
            st.plotly_chart(fig_pie, use_container_width=True)

            # 브랜드 × 공급단 피벗 테이블
            pivot = f_df.pivot_table(index='brand', columns='supply', values='forecast', aggfunc='sum', fill_value=0)
            # 정렬: 총합 기준
            pivot['총합'] = pivot.sum(axis=1)
            pivot = pivot.sort_values('총합', ascending=False).drop(columns=['총합'])
            st.subheader("브랜드 × 공급단 예측량")
            st.dataframe(pivot.astype(int), use_container_width=True)

# -----------------------
# 하단: 전체 데이터 테이블 (공통)
# -----------------------
st.write("")
st.markdown("---")
st.subheader("원본 데이터 미리보기 (필터 적용된 결과)")
# 기본적으로 최근 선택된 브랜드/월 기준으로 mg_all 필터링된 결과 제공
preview = mg_all.copy()
preview = preview[preview['brand'].isin(sel_br)]
preview = preview[preview['ym']==sel_ym]
if preview.empty:
    st.info("선택한 조건에 해당하는 원본 데이터가 없습니다.")
else:
    st.dataframe(preview.drop(columns=['오차량']), use_container_width=True, hide_index=True)
