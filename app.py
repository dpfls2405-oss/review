import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# 1. 페이지 설정 및 세련된 라이트 디자인 (CSS)
st.set_page_config(page_title="수요분석 리포트", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    /* KPI 카드 스타일 */
    .metric-card {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #E2E8F0;
        text-align: center;
    }
    .metric-label { font-size: 14px; color: #64748B; font-weight: 600; margin-bottom: 8px; }
    .metric-value { font-size: 28px; font-weight: 800; color: #1E293B; }
    .metric-sub { font-size: 12px; color: #94A3B8; margin-top: 4px; }
    
    /* 리포트 분석 박스 */
    .analysis-box { 
        background-color: white; border-radius: 12px; padding: 30px; 
        border: 1px solid #E2E8F0; line-height: 1.8; color: #334155;
    }
    .item-card { 
        background: #F8FAFC; padding: 18px; border-radius: 10px; 
        margin-top: 15px; border-left: 5px solid #3B82F6;
    }
    code { color: #2563EB; background: #EFF6FF; padding: 2px 4px; border-radius: 4px; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 정밀 정제 (오류 방지)
@st.cache_data
def load_data():
    try:
        f = pd.read_csv("forecast_data.csv")
        a = pd.read_csv("actual_data.csv")
    except:
        st.error("데이터 파일을 찾을 수 없습니다. (forecast_data.csv, actual_data.csv 확인 필요)")
        return pd.DataFrame(), pd.DataFrame()

    def clean_df(df):
        # [KeyError 방지] supplier/supply 컬럼명 자동 매칭
        if 'supplier' not in df.columns and 'supply' in df.columns:
            df = df.rename(columns={'supply': 'supplier'})
        elif 'supplier' not in df.columns:
            df['supplier'] = '미분류'
            
        # [이미지 요청 반영] 숫자 형태의 시리즈 삭제 및 공백 제거
        if 'series' in df.columns:
            df['series'] = df['series'].astype(str).str.strip()
            df = df[~df['series'].str.isnumeric()]
            df = df[df['series'].str.len() >= 2]
        return df

    return clean_df(f), clean_df(a)

f_df, a_df = load_data()

# 3. 사이드바 필터
if not f_df.empty:
    st.sidebar.title("🔍 필터 설정")
    sel_ym = st.sidebar.selectbox("📅 기준 년월", sorted(f_df["ym"].unique(), reverse=True))
    
    all_brands = sorted(f_df["brand"].unique().tolist())
    sel_br = st.sidebar.multiselect("🏷️ 브랜드", all_brands, default=all_brands)
    
    all_sups = sorted(f_df["supplier"].unique().tolist())
    sel_sup = st.sidebar.multiselect("🏭 공급단", all_sups, default=all_sups)

    # 데이터 병합 및 계산
    f_sel = f_df[(f_df["ym"] == sel_ym) & (f_df["brand"].isin(sel_br)) & (f_df["supplier"].isin(sel_sup))].copy()
    a_sel = a_df[a_df["ym"] == sel_ym].copy()
    mg = pd.merge(f_sel, a_sel[['combo', 'actual']], on="combo", how="left").fillna(0)

    mg["차이"] = mg["actual"] - mg["forecast"]
    mg["오차량"] = mg["차이"].abs()
    mg["달성률(%)"] = np.where(mg["forecast"] > 0, (mg["actual"] / mg["forecast"] * 100).round(1), 0)

    # --- 메인 화면 구성 ---
    st.title(f"📊 {sel_ym} 수요 수급 분석 대시보드")

    # 상단 요약 지표 (KPI)
    t_f, t_a = mg['forecast'].sum(), mg['actual'].sum()
    t_d, t_r = t_a - t_f, (t_a / t_f * 100) if t_f > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f'<div class="metric-card"><div class="metric-label">예측수요 합계</div><div class="metric-value">{int(t_f):,}</div><div class="metric-sub">FCST Total</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card"><div class="metric-label">실수주량 합계</div><div class="metric-value">{int(t_a):,}</div><div class="metric-sub">Actual Total</div></div>', unsafe_allow_html=True)
    color = "#fb7185" if t_d < 0 else "#10B981"
    m3.markdown(f'<div class="metric-card"><div class="metric-label">차이량 합계</div><div class="metric-value" style="color:{color}">{int(t_d):,}</div><div class="metric-sub">Variance</div></div>', unsafe_allow_html=True)
    m4.markdown(f'<div class="metric-card"><div class="metric-label">전체 달성률</div><div class="metric-value">{t_r:.1f}%</div><div class="metric-sub">Achievement</div></div>', unsafe_allow_html=True)

    st.write("---")

    # 4. 추가된 3가지 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(["🏛️ 브랜드·공급단 분석", "📈 시계열 추이", "🔍 시리즈 상세", "📝 상세 분석 리포트"])

    with tab1:
        st.subheader("브랜드 및 공급단별 분포")
        c1, c2 = st.columns(2)
        with c1:
            fig_b = px.bar(mg.groupby('brand')['forecast'].sum().reset_index(), x='brand', y='forecast', 
                           color='brand', title="브랜드별 예측량", template='plotly_white')
            st.plotly_chart(fig_b, use_container_width=True)
        with c2:
            fig_p = px.pie(mg.groupby('supplier')['forecast'].sum().reset_index(), values='forecast', 
                           names='supplier', hole=0.4, title="공급단별 비중", template='plotly_white')
            st.plotly_chart(fig_p, use_container_width=True)
        
        st.subheader("브랜드 × 공급단 분석 테이블")
        pv = mg.pivot_table(index='brand', columns='supplier', values='forecast', aggfunc='sum', fill_value=0)
        st.dataframe(pv.style.format("{:,.0f}").background_gradient(cmap='Blues'), use_container_width=True)

    with tab2:
        st.subheader("월별 수요 및 실적 추이")
        # 시계열 데이터 가공
        ts_f = f_df[f_df['brand'].isin(sel_br)].groupby('ym')['forecast'].sum()
        ts_a = pd.merge(a_df, f_df[['combo', 'brand']].drop_duplicates(), on='combo')
        ts_a = ts_a[ts_a['brand'].isin(sel_br)].groupby('ym')['actual'].sum()
        
        fig_ts = go.Figure()
        fig_ts.add_trace(go.Scatter(x=ts_f.index, y=ts_f.values, name="예측 수요", line=dict(color='#3B82F6', width=3)))
        fig_ts.add_trace(go.Scatter(x=ts_a.index, y=ts_a.values, name="실제 수주", line=dict(color='#F43F5E', width=3, dash='dot')))
        fig_ts.update_layout(template='plotly_white', hovermode='x unified')
        st.plotly_chart(fig_ts, use_container_width=True)

    with tab3:
        st.subheader("시리즈별 상세 분석")
        target_br = st.selectbox("분석 브랜드 선택", sel_br)
        br_detail = mg[mg['brand'] == target_br].groupby('series')[['forecast', 'actual']].sum().sort_values('forecast', ascending=False)
        fig_detail = px.bar(br_detail.reset_index(), x='series', y=['forecast', 'actual'], barmode='group', template='plotly_white')
        st.plotly_chart(fig_detail, use_container_width=True)
        st.dataframe(mg[mg['brand']==target_br][['series','name','combo','forecast','actual','차이','달성률(%)']], use_container_width=True)

    with tab4:
        st.subheader("📋 실무자용 상세 분석 리포트")
        top_5 = mg.sort_values('오차량', ascending=False).head(5)
        
        report_html = ""
        for i, (_, row) in enumerate(top_5.iterrows(), 1):
            cb = str(row['combo'])
            code = cb.split('-')[0] if '-' in cb else cb
            color = cb.split('-')[1] if '-' in cb else "기본"
            
            report_html += f"""
            <div class="item-card">
                <strong>{i}. {row['series']} 시리즈 : {row['name']}</strong> (공급처: {row['supplier']})<br>
                단품코드 <code>{code}</code> (색상: {color}) 품목은 이번 달 예측 대비 실제 수주 
                <strong>{int(row['actual']):,}</strong>건을 기록했습니다.<br>
                최종 <strong>달성률은 {row['달성률(%)']:.1f}%</strong>이며, 예측치와 약 {int(abs(row['차이'])):,}만큼의 차이가 발생하여 정밀한 수급 확인이 필요합니다.
            </div>
            """

        st.markdown(f"""
        <div class="analysis-box">
            안녕하세요, {sel_ym} 수요 분석 결과입니다.<br><br>
            이번 달 전체 예측 수요 <strong>{int(t_f):,}</strong> 대비 실제 수주량은 <strong>{int(t_a):,}</strong>로 집계되었습니다. 
            전체 달성률은 <strong>{t_r:.1f}%</strong>이며, 특히 아래 5개 품목에서 큰 오차가 발생했습니다.<br><br>
            <strong>🔍 중점 관리 품목 리포트</strong>
            {report_html}
            <br>
            위 리스트는 오차 절대값이 큰 순서로 추출되었습니다. 생산 일정 및 자재 수급 계획 수립 시 해당 시리즈의 변동성을 우선적으로 검토하시길 바랍니다.
        </div>
        """, unsafe_allow_html=True)

else:
    st.warning("데이터가 비어있습니다. CSV 파일 내용을 확인해주세요.")
