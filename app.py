import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# 1. 페이지 설정 및 디자인 (이미지 57bab5 및 575cfc의 밝은 버전 스타일)
st.set_page_config(page_title="SCM 수급 분석 리포트", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    /* KPI 카드 스타일 */
    .metric-card {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #E2E8F0;
        text-align: center;
    }
    .metric-label { font-size: 14px; color: #64748B; font-weight: 600; }
    .metric-value { font-size: 24px; font-weight: 800; color: #1E293B; margin-top: 8px; }
    /* 리포트 박스 스타일 (사람이 읽는용) */
    .analysis-report {
        background-color: white; border-radius: 12px; padding: 25px;
        border: 1px solid #E2E8F0; line-height: 1.8; color: #334155;
    }
    .item-highlight {
        background-color: #F1F5F9; padding: 15px; border-radius: 10px;
        margin-top: 10px; border-left: 5px solid #3B82F6;
    }
    code { color: #2563EB; background: #EFF6FF; padding: 2px 5px; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 에러 방지 (Safe Loader)
@st.cache_data
def load_data_safe():
    try:
        f = pd.read_csv("forecast_data.csv")
        a = pd.read_csv("actual_data.csv")
        
        def preprocess(df):
            # 1. 컬럼명 유연화 (KeyError 방지)
            rename_map = {'supply': 'supplier', '공급처': 'supplier'}
            df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
            if 'supplier' not in df.columns: df['supplier'] = '전체공급단'
            
            # 2. 숫자 시리즈 제거 (이미지 57d0fe 이슈 해결)
            if 'series' in df.columns:
                df['series'] = df['series'].astype(str).str.strip()
                df = df[~df['series'].str.isnumeric()]
            return df

        return preprocess(f), preprocess(a)
    except Exception as e:
        # 파일이 없거나 읽기 실패 시 빈 데이터프레임 반환하여 필터 UI라도 유지
        return pd.DataFrame(columns=['ym', 'brand', 'supplier', 'series', 'combo', 'forecast']), pd.DataFrame()

f_df, a_df = load_data_safe()

# 3. 사이드바 필터 (이미지 575cd7 스타일 복구)
st.sidebar.title("🔍 필터 설정")

# 데이터가 비었을 때를 대비한 기본값 처리
ym_list = sorted(f_df["ym"].unique(), reverse=True) if not f_df.empty else ["데이터없음"]
sel_ym = st.sidebar.selectbox("📅 기준 년월", ym_list)

brand_list = sorted(f_df["brand"].unique().tolist()) if not f_df.empty else []
sel_br = st.sidebar.multiselect("🏷️ 브랜드", brand_list, default=brand_list)

sup_list = sorted(f_df["supplier"].unique().tolist()) if not f_df.empty else []
sel_sup = st.sidebar.multiselect("🏭 공급단", sup_list, default=sup_list)

unit = st.sidebar.radio("📊 분석 단위", ["시리즈별", "품목별"], horizontal=True)

# 4. 데이터 계산 및 검색/정렬 (이미지 5832b3 기능 포함)
if not f_df.empty and not a_df.empty:
    # 필터링
    f_filtered = f_df[(f_df["ym"] == sel_ym) & (f_df["brand"].isin(sel_br)) & (f_df["supplier"].isin(sel_sup))]
    mg = pd.merge(f_filtered, a_df[['combo', 'actual']], on='combo', how='left').fillna(0)
    
    mg["차이"] = mg["actual"] - mg["forecast"]
    mg["오차량"] = mg["차이"].abs()
    mg["달성률(%)"] = np.where(mg["forecast"] > 0, (mg["actual"] / mg["forecast"] * 100).round(1), 0)

    # 상단 컨트롤 (정렬 및 검색)
    c_head1, c_head2, c_head3 = st.columns([2, 2, 3])
    with c_head1:
        sort_col = st.selectbox("📌 정렬 지표", ["차이량(|실-예측|) 큰 순", "실수주량 큰 순", "달성률 큰 순"])
    with c_head2:
        top_n = st.slider("🎯 Top N 표시", 5, 50, 15)
    with c_head3:
        search_q = st.text_input("🔎 명칭/코드 검색", placeholder="예: IBLE, S60...")

    # 정렬 적용
    sort_map = {"차이량(|실-예측|) 큰 순": "오차량", "실수주량 큰 순": "actual", "달성률 큰 순": "달성률(%)"}
    mg = mg.sort_values(sort_map[sort_col], ascending=False)
    if search_q:
        mg = mg[mg['name'].str.contains(search_q, case=False) | mg['combo'].str.contains(search_q, case=False)]

    # 5. KPI 요약 (이미지 57bab5 디자인)
    st.write("---")
    k1, k2, k3, k4 = st.columns(4)
    t_f, t_a = mg['forecast'].sum(), mg['actual'].sum()
    k1.markdown(f'<div class="metric-card"><div class="metric-label">예측수요 합계</div><div class="metric-value">{t_f:,.0f}</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="metric-card"><div class="metric-label">실수주량 합계</div><div class="metric-value">{t_a:,.0f}</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="metric-card"><div class="metric-label">차이량(실-예)</div><div class="metric-value" style="color:#EF4444">{(t_a-t_f):,.0f}</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="metric-card"><div class="metric-label">전체 달성률</div><div class="metric-value">{(t_a/t_f*100 if t_f>0 else 0):.1f}%</div></div>', unsafe_allow_html=True)

    # 6. 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(["📊 브랜드·공급단 분석", "📈 시계열 추이", "🔍 시리즈 상세", "📝 분석 리포트"])

    with tab1:
        st.subheader("브랜드 × 공급단 분석")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            fig_b = px.bar(mg.groupby('brand')['forecast'].sum().reset_index(), x='brand', y='forecast', title="브랜드별 예측량", template="plotly_white")
            st.plotly_chart(fig_b, use_container_width=True)
        with col_b2:
            fig_p = px.pie(mg.groupby('supplier')['forecast'].sum().reset_index(), values='forecast', names='supplier', hole=0.4, title="공급단 비중", template="plotly_white")
            st.plotly_chart(fig_p, use_container_width=True)
        
        pivot_table = mg.pivot_table(index='brand', columns='supplier', values='forecast', aggfunc='sum', fill_value=0)
        st.dataframe(pivot_table.style.format("{:,.0f}").background_gradient(cmap='Blues'), use_container_width=True)

    with tab2:
        st.subheader("월별 수요/실적 시계열 추이")
        # 시계열용 전체 데이터 병합 (간소화)
        ts_data = f_df[f_df['brand'].isin(sel_br)].groupby('ym')['forecast'].sum().reset_index()
        fig_ts = px.line(ts_data, x='ym', y='forecast', title="전체 수요 트렌드", markers=True, template="plotly_white")
        st.plotly_chart(fig_ts, use_container_width=True)

    with tab3:
        st.subheader("시리즈별 상세 현황")
        target_br = st.selectbox("브랜드 선택", sel_br)
        br_data = mg[mg['brand'] == target_br].groupby('series')[['forecast', 'actual']].sum().head(top_n).reset_index()
        fig_series = px.bar(br_data, x='series', y=['forecast', 'actual'], barmode='group', template="plotly_white")
        st.plotly_chart(fig_series, use_container_width=True)

    with tab4:
        st.subheader("📋 담당자용 상세 분석 리포트")
        top_items = mg.head(5)
        
        item_html = ""
        for i, (_, row) in enumerate(top_items.iterrows(), 1):
            code = row['combo'].split('-')[0] if '-' in row['combo'] else row['combo']
            color = row['combo'].split('-')[1] if '-' in row['combo'] else "정보없음"
            item_html += f"""
            <div class="item-highlight">
                <strong>{i}. {row['name']}</strong> (시리즈: {row['series']})<br>
                품목코드 <code>{code}</code>, 색상 <code>{color}</code> 제품으로, 
                이번 달 예측 대비 실제 수주는 <strong>{int(row['actual']):,}</strong>건이 발생했습니다. 
                현재 <strong>달성률 {row['달성률(%)']:.1f}%</strong> 상태이며, 예측치와 약 {int(abs(row['차이'])):,} 정도의 차이를 보입니다.
            </div>"""

        st.markdown(f"""
        <div class="analysis-report">
            안녕하세요. {sel_ym} 데이터 기반 분석 리포트입니다.<br><br>
            선택하신 조건의 전체 예측치는 <strong>{int(t_f):,}</strong>이나 실적은 <strong>{int(t_a):,}</strong>로 확인되어, 
            약 <strong>{t_a/t_f*100:.1f}%의 수급 달성률</strong>을 보이고 있습니다.<br><br>
            오차 범위가 커서 집중 관리가 필요한 상위 5개 품목 리스트입니다:
            {item_html}
            <br>위 리스트는 현재 설정하신 <strong>{sort_col}</strong> 기준으로 추출되었습니다. 
            생산 및 재고 계획 수립 시 해당 품목들의 변동성을 우선적으로 검토해 주시기 바랍니다.
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("사이드바에서 필터를 선택하거나 데이터를 확인해주세요.")
