import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="수요 수급 분석 리포트", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .metric-container {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); border: 1px solid #E2E8F0;
        text-align: center;
    }
    .metric-label { font-size: 14px; color: #64748B; font-weight: 600; }
    .metric-value { font-size: 26px; font-weight: 800; color: #0F172A; margin-top: 5px; }
    .analysis-card {
        background-color: white; border-radius: 12px; padding: 25px;
        border: 1px solid #E2E8F0; line-height: 1.8; color: #334155; margin-bottom: 20px;
    }
    .item-highlight {
        background-color: #F1F5F9; padding: 15px; border-radius: 8px;
        margin-top: 10px; border-left: 4px solid #2563EB;
    }
    code { color: #2563EB; background: #EFF6FF; padding: 2px 4px; border-radius: 4px; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 정교한 전처리 (에러 방지 핵심)
@st.cache_data
def load_and_clean_data():
    try:
        # 파일 존재 여부 확인 후 로드
        f = pd.read_csv("forecast_data.csv") if "forecast_data.csv" in [f for f in __import__('os').listdir() if f.endswith('.csv')] else pd.DataFrame()
        a = pd.read_csv("actual_data.csv") if "actual_data.csv" in [f for f in __import__('os').listdir() if f.endswith('.csv')] else pd.DataFrame()
        
        if f.empty: return pd.DataFrame(), pd.DataFrame()

        def clean(df):
            # 컬럼명 표준화 (KeyError 방지)
            mapping = {'supply': 'supplier', '공급처': 'supplier', '공급단': 'supplier'}
            df = df.rename(columns={k: v for k, v in mapping.items() if k in df.columns})
            
            # 필수 컬럼 보장
            if 'supplier' not in df.columns: df['supplier'] = '전체공급단'
            if 'brand' not in df.columns: df['brand'] = '미분류'
            
            # 숫자 시리즈 및 노이즈 제거
            if 'series' in df.columns:
                df['series'] = df['series'].astype(str).str.strip()
                df = df[~df['series'].str.isnumeric()] # 숫자만 있는 시리즈 제거
                df = df[df['series'] != 'nan']
            
            # 날짜 형식 보장
            if 'ym' in df.columns: df['ym'] = df['ym'].astype(str)
            return df

        return clean(f), clean(a)
    except:
        return pd.DataFrame(), pd.DataFrame()

f_df, a_df = load_and_clean_data()

# 3. 사이드바 필터 (데이터 유무에 따른 동적 구성)
if not f_df.empty:
    st.sidebar.title("🔎 분석 필터")
    
    # 년월 필터
    ym_opts = sorted(f_df["ym"].unique(), reverse=True)
    sel_ym = st.sidebar.selectbox("📅 기준 년월", ym_opts)
    
    # 브랜드 필터
    br_opts = sorted(f_df["brand"].unique().tolist())
    sel_br = st.sidebar.multiselect("🏷️ 브랜드", br_opts, default=br_opts)
    
    # 공급단 필터 (자동 매칭된 supplier 사용)
    sup_opts = sorted(f_df["supplier"].unique().tolist())
    sel_sup = st.sidebar.multiselect("🏭 공급단", sup_opts, default=sup_opts)

    # 데이터 병합 및 계산
    f_filtered = f_df[(f_df["ym"] == sel_ym) & (f_df["brand"].isin(sel_br)) & (f_df["supplier"].isin(sel_sup))].copy()
    
    # 실적 데이터와 병합 (combo 기준)
    if not a_df.empty:
        a_ym = a_df[a_df["ym"] == sel_ym][['combo', 'actual']].groupby('combo').sum().reset_index()
        mg = pd.merge(f_filtered, a_ym, on="combo", how="left").fillna(0)
    else:
        mg = f_filtered.copy()
        mg['actual'] = 0

    mg["차이"] = mg["actual"] - mg["forecast"]
    mg["오차량"] = mg["차이"].abs()
    mg["달성률(%)"] = np.where(mg["forecast"] > 0, (mg["actual"] / mg["forecast"] * 100).round(1), 0)

    # 4. 상단 KPI 요약
    st.title(f"📊 {sel_ym} 수급 및 수요 분석")
    
    t_f, t_a = mg['forecast'].sum(), mg['actual'].sum()
    t_diff = t_a - t_f
    t_rate = (t_a / t_f * 100) if t_f > 0 else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="metric-container"><div class="metric-label">예측수요 합계</div><div class="metric-value">{t_f:,.0f}</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="metric-container"><div class="metric-label">실수주량 합계</div><div class="metric-value">{t_a:,.0f}</div></div>', unsafe_allow_html=True)
    diff_color = "#EF4444" if t_diff < 0 else "#10B981"
    k3.markdown(f'<div class="metric-container"><div class="metric-label">차이량 합계</div><div class="metric-value" style="color:{diff_color}">{t_diff:,.0f}</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="metric-container"><div class="metric-label">전체 달성률</div><div class="metric-value">{t_rate:.1f}%</div></div>', unsafe_allow_html=True)

    st.write("---")

    # 5. 메인 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(["🏛️ 브랜드·공급단 분석", "📈 시계열 추이", "🔍 시리즈 상세", "📝 상세 분석 리포트"])

    # Tab 1: 브랜드/공급단 (브랜드*공급단별로 볼 수 있음)
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("브랜드별 수요 현황")
            fig1 = px.bar(mg.groupby('brand')[['forecast','actual']].sum().reset_index(), 
                          x='brand', y=['forecast','actual'], barmode='group', template='plotly_white')
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            st.subheader("공급단별 비중")
            fig2 = px.pie(mg.groupby('supplier')['forecast'].sum().reset_index(), 
                          values='forecast', names='supplier', hole=0.4, template='plotly_white')
            st.plotly_chart(fig2, use_container_width=True)
        
        st.subheader("브랜드 × 공급단 교차 분석")
        pivot = mg.pivot_table(index='brand', columns='supplier', values='forecast', aggfunc='sum', fill_value=0)
        st.dataframe(pivot.style.format("{:,.0f}").background_gradient(cmap='Blues'), use_container_width=True)

    # Tab 2: 시계열 (시계열로 볼 수 있음)
    with tab2:
        st.subheader("월별 수요 및 실적 트렌드")
        ts_f = f_df[f_df['brand'].isin(sel_br)].groupby('ym')['forecast'].sum()
        if not a_df.empty:
            ts_a = pd.merge(a_df, f_df[['combo', 'brand']].drop_duplicates(), on='combo')
            ts_a = ts_a[ts_a['brand_y'].isin(sel_br)].groupby('ym')['actual'].sum()
            
            fig_ts = go.Figure()
            fig_ts.add_trace(go.Scatter(x=ts_f.index, y=ts_f.values, name="예측 수요", line=dict(color='#3B82F6', width=3)))
            fig_ts.add_trace(go.Scatter(x=ts_a.index, y=ts_a.values, name="실제 수주", line=dict(color='#F43F5E', width=2, dash='dot')))
            fig_ts.update_layout(template='plotly_white', hovermode='x unified')
            st.plotly_chart(fig_ts, use_container_width=True)
        else:
            st.info("시계열 분석을 위한 실적 데이터가 충분하지 않습니다.")

    # Tab 3: 시리즈 상세 (시리즈 상세로 볼 수 있음)
    with tab3:
        st.subheader("시리즈별 정밀 분석")
        target_br = st.selectbox("집중 분석할 브랜드 선택", sel_br)
        detail_data = mg[mg['brand'] == target_br].groupby('series')[['forecast', 'actual']].sum().sort_values('forecast', ascending=False)
        fig_detail = px.bar(detail_data.reset_index(), x='series', y=['forecast', 'actual'], barmode='group', template='plotly_white')
        st.plotly_chart(fig_detail, use_container_width=True)

    # Tab 4: 리포트 (사람이 이해하기 쉽게 수정)
    with tab4:
        st.subheader("📋 담당자용 맞춤형 분석 리포트")
        top_diff = mg.sort_values('오차량', ascending=False).head(5)
        
        report_items = ""
        for i, (_, row) in enumerate(top_diff.iterrows(), 1):
            cb = str(row['combo'])
            code, color = (cb.split('-')[0], cb.split('-')[1]) if '-' in cb else (cb, "기본")
            report_items += f"""
            <div class="item-highlight">
                <strong>{i}. {row['name']}</strong> (시리즈: {row['series']} / 공급단: {row['supplier']})<br>
                이 제품은 품목코드 <code>{code}</code>, 색상 <code>{color}</code> 사양입니다. 
                이번 달 예측 수량 <strong>{int(row['forecast']):,}</strong> 대비 실제 수주는 <strong>{int(row['actual']):,}</strong>건이 발생했습니다. 
                현재 <strong>달성률은 {row['달성률(%)']:.1f}%</strong>이며, 예측치보다 {int(abs(row['차이'])):,}개 {'더 많이' if row['차이']>0 else '더 적게'} 수주되었습니다.
            </div>
            """

        st.markdown(f"""
        <div class="analysis-card">
            안녕하세요, {sel_ym} 수급 분석 결과를 보고 드립니다.<br><br>
            현재 선택하신 필터 기준으로 전체 예측 총량은 <strong>{int(t_f):,}</strong>이며, 
            실제 수주량은 <strong>{int(t_a):,}</strong>로 집계되었습니다. 
            전체 수급 <strong>달성률은 {t_rate:.1f}%</strong> 수준입니다.<br><br>
            
            특히 예측과 실적의 간극이 커서 <strong>현장 수급 및 생산 계획 조정이 시급한 상위 5개 품목</strong>입니다:
            {report_items}
            <br>
            위 품목들은 현재 수급 불균형이 가장 심하므로, 해당 시리즈의 자재 재고 상황을 우선적으로 점검하시길 권장합니다.
        </div>
        """, unsafe_allow_html=True)

else:
    st.warning("분석할 데이터를 찾을 수 없습니다. CSV 파일과 컬럼명을 확인해주세요.")
