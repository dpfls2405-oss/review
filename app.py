import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# 1. 페이지 설정 및 세련된 라이트 디자인 (CSS)
st.set_page_config(page_title="수요분석 리포트 v2", layout="wide")

st.markdown("""
    <style>
    /* 전체 배경 및 폰트 */
    .stApp { background-color: #F8FAFC; }
    
    /* 세련된 KPI 카드 */
    .kpi-card {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
        border: 1px solid #E2E8F0; text-align: center;
    }
    .kpi-label { font-size: 13px; color: #64748B; font-weight: 600; margin-bottom: 8px; }
    .kpi-value { font-size: 26px; font-weight: 800; color: #1E293B; }
    
    /* 리포트 카드 스타일 */
    .report-container {
        background-color: white; border-radius: 12px; padding: 30px;
        border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        line-height: 1.8; color: #334155;
    }
    .item-card {
        background-color: #F8FAFC; padding: 18px; border-radius: 10px;
        margin-top: 15px; border-left: 5px solid #3B82F6;
    }
    code { color: #2563EB; background: #EFF6FF; padding: 2px 4px; border-radius: 4px; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 오류 방지 정제
@st.cache_data
def load_data():
    try:
        f = pd.read_csv("forecast_data.csv")
        a = pd.read_csv("actual_data.csv")
    except:
        st.error("데이터 파일을 로드할 수 없습니다. 파일명을 확인해주세요.")
        return pd.DataFrame(), pd.DataFrame()

    def clean_df(df):
        # [KeyError 해결] supplier 컬럼명 자동 매칭
        if 'supplier' not in df.columns:
            if 'supply' in df.columns:
                df = df.rename(columns={'supply': 'supplier'})
            else:
                df['supplier'] = '전체공급단'
        
        # [이미지 57d0fe 반영] 숫자 시리즈 제거
        if 'series' in df.columns:
            df['series'] = df['series'].astype(str).str.strip()
            df = df[~df['series'].str.isnumeric()]
            
        return df

    return clean_df(f), clean_df(a)

f_df, a_df = load_data()

# 3. 사이드바 필터 설정 (복구 및 강화)
if not f_df.empty:
    st.sidebar.header("🔍 필터 설정")
    sel_ym = st.sidebar.selectbox("📅 기준 년월", sorted(f_df["ym"].unique(), reverse=True))
    
    # 브랜드 필터
    brands = sorted(f_df["brand"].unique().tolist())
    sel_br = st.sidebar.multiselect("🏷️ 브랜드", brands, default=brands)
    
    # 공급단 필터 (KeyError 없이 안전하게 로드)
    suppliers = sorted(f_df["supplier"].unique().tolist())
    sel_sup = st.sidebar.multiselect("🏭 공급단", suppliers, default=suppliers)
    
    # 분석 단위 (시리즈별 / 품목별)
    unit = st.sidebar.radio("📊 분석 단위", ["시리즈별", "품목별"], horizontal=True)

    # 4. 데이터 계산
    f_sel = f_df[(f_df["ym"] == sel_ym) & (f_df["brand"].isin(sel_br)) & (f_df["supplier"].isin(sel_sup))].copy()
    a_sel = a_df[a_df["ym"] == sel_ym].copy()
    
    mg = pd.merge(f_sel, a_sel[['combo', 'actual']], on="combo", how="left").fillna(0)
    mg["차이"] = mg["actual"] - mg["forecast"]
    mg["오차량"] = mg["차이"].abs()
    mg["달성률(%)"] = np.where(mg["forecast"] > 0, (mg["actual"] / mg["forecast"] * 100).round(1), 0)

    # 5. 상단 컨트롤 바 (이미지 5832b3, 57c8fd 반영)
    st.title(f"🚀 {sel_ym} 수요 분석 대시보드")
    
    ctrl1, ctrl2, ctrl3 = st.columns([2, 2, 3])
    with ctrl1:
        sort_idx = st.selectbox("📌 정렬 지표", ["차이량(|실-예측|) 큰 순", "차이량(실-예측) 큰 순", "실수주량 큰 순", "예측수요 큰 순", "달성률 큰 순"])
    with ctrl2:
        top_n = st.slider("🎯 Top N", 5, 50, 15)
    with ctrl3:
        search = st.text_input("🔎 검색 (코드/명칭)", placeholder="예: S60, IBLE...")

    # 정렬 및 검색 적용
    sort_map = {"차이량(|실-예측|) 큰 순": "오차량", "차이량(실-예측) 큰 순": "차이", "실수주량 큰 순": "actual", "예측수요 큰 순": "forecast", "달성률 큰 순": "달성률(%)"}
    mg = mg.sort_values(sort_map[sort_idx], ascending=(False if "큰 순" in sort_idx else True))
    if search:
        mg = mg[mg['combo'].str.contains(search, case=False) | mg['name'].str.contains(search, case=False)]

    # 6. KPI 요약 (이미지 57bab5 스타일)
    t_f, t_a = mg['forecast'].sum(), mg['actual'].sum()
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="kpi-card"><div class="kpi-label">예측수요 합계</div><div class="kpi-value">{t_f:,.0f}</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-card"><div class="kpi-label">실수주량 합계</div><div class="kpi-value">{t_a:,.0f}</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-card"><div class="kpi-label">차이량 합계</div><div class="kpi-value" style="color:#F43F5E">{t_a-t_f:,.0f}</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-card"><div class="kpi-label">전체 달성률</div><div class="kpi-value">{(t_a/t_f*100 if t_f>0 else 0):.1f}%</div></div>', unsafe_allow_html=True)

    st.write("---")

    # 7. 탭 구성 (이미지 575cfc, 575cd7, 575c98 스타일 반영)
    tab1, tab2, tab3, tab4 = st.tabs(["📊 브랜드·공급단 분석", "📈 시계열 추이", "🔍 시리즈 상세", "📝 상세 분석 리포트"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("브랜드별 예측 현황")
            fig_b = px.bar(mg.groupby('brand')['forecast'].sum().reset_index(), x='brand', y='forecast', color='brand', template='plotly_white')
            st.plotly_chart(fig_b, use_container_width=True)
        with c2:
            st.subheader("공급단별 예측 비중")
            fig_p = px.pie(mg.groupby('supplier')['forecast'].sum().reset_index(), values='forecast', names='supplier', hole=0.4, template='plotly_white')
            st.plotly_chart(fig_p, use_container_width=True)
        st.subheader("브랜드 × 공급단 분석")
        pivot = mg.pivot_table(index='brand', columns='supplier', values='forecast', aggfunc='sum', fill_value=0)
        st.dataframe(pivot.style.format("{:,.0f}").background_gradient(cmap='Blues'), use_container_width=True)

    with tab2:
        st.subheader("월별 수요 및 실적 추이")
        # 시계열 데이터 가공
        ts_f = f_df[f_df['brand'].isin(sel_br)].groupby('ym')['forecast'].sum()
        ts_a = pd.merge(a_df, f_df[['combo', 'brand']], on='combo').drop_duplicates()
        ts_a = ts_a[ts_a['brand'].isin(sel_br)].groupby('ym')['actual'].sum()
        
        fig_ts = go.Figure()
        fig_ts.add_trace(go.Scatter(x=ts_f.index, y=ts_f.values, name="예측 수요", line=dict(color='#3B82F6', width=3)))
        fig_ts.add_trace(go.Scatter(x=ts_a.index, y=ts_a.values, name="실제 수주", line=dict(color='#F43F5E', width=3, dash='dot')))
        fig_ts.update_layout(template='plotly_white', hovermode='x unified')
        st.plotly_chart(fig_ts, use_container_width=True)

    with tab3:
        st.subheader("시리즈별 상세 분석")
        target_br = st.selectbox("분석할 브랜드 선택", sel_br)
        br_data = mg[mg['brand'] == target_br].groupby('series')[['forecast', 'actual']].sum().head(top_n)
        fig_s = px.bar(br_data.reset_index(), x='series', y=['forecast', 'actual'], barmode='group', template='plotly_white')
        st.plotly_chart(fig_s, use_container_width=True)

    with tab4:
        st.subheader("📋 사람의 언어로 정리한 분석 보고")
        top_5 = mg.sort_values('오차량', ascending=False).head(5)
        
        report_items = ""
        for i, (_, row) in enumerate(top_5.iterrows(), 1):
            cb = str(row['combo'])
            code, color = (cb.split('-')[0], cb.split('-')[1]) if '-' in cb else (cb, "기본")
            
            # [이미지 582bae 등 반영] 사람 중심의 서술형 문구
            report_items += f"""
            <div class="item-card">
                <strong>{i}. {row['name']}</strong> (공급처: {row['supplier']})<br>
                이 제품은 <code>시리즈: {row['series']}</code>, <code>단품코드: {code}</code>, <code>색상: {color}</code> 정보를 가진 
                <strong>'{row['name']}'</strong> 모델입니다.<br>
                분석 결과, 이번 달 예측 대비 실제 수주는 <strong>{int(row['actual']):,}</strong>건으로 집계되었으며, 
                최종 <strong>달성률은 {row['달성률(%)']:.1f}%</strong>를 기록했습니다. 
                예측치와 약 {int(abs(row['차이'])):,}만큼의 차이가 발생하여 정밀한 수급 확인이 필요해 보입니다.
            </div>
            """

        st.markdown(f"""
        <div class="report-container">
            안녕하세요, 담당자님. {sel_ym} 수급 데이터 분석 요약입니다.<br><br>
            현재 선택된 기준에서 전체 예측 수요 <strong>{int(t_f):,}</strong> 대비 실제 수주는 <strong>{int(t_a):,}</strong>로 나타나 
            전체적으로 <strong>{t_a/t_f*100:.1f}%의 달성률</strong>을 보이고 있습니다.<br><br>
            
            특히 예측과 실적의 차이가 커서 <strong>현장에서 재고 과부하 혹은 부족이 우려되는 상위 5개 품목</strong>은 다음과 같습니다.
            {report_items}
            <br>
            위 품목들은 현재 오차 절대값이 가장 큰 순서로 나열되었습니다. 
            차기 수요 예측 및 생산 계획 수립 시, 해당 시리즈들의 최근 수주 경향을 우선적으로 반영해 주시길 권장드립니다.
        </div>
        """, unsafe_allow_html=True)
