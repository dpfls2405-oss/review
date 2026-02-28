import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# 1. 페이지 설정 및 세련된 라이트 디자인 (CSS)
st.set_page_config(page_title="수요분석 리포트", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F9FAFB; }
    .metric-container {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #E5E7EB;
        text-align: center;
    }
    .metric-label { font-size: 14px; color: #6B7280; font-weight: 500; }
    .metric-value { font-size: 26px; font-weight: 800; color: #111827; margin-top: 5px; }
    .analysis-card {
        background-color: white; border-radius: 12px; padding: 25px;
        border: 1px solid #E5E7EB; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        line-height: 1.7; color: #374151; margin-bottom: 20px;
    }
    .item-highlight {
        background-color: #F3F4F6; padding: 15px; border-radius: 8px;
        margin-top: 10px; border-left: 4px solid #3B82F6;
    }
    code { color: #2563EB; background: #EFF6FF; padding: 2px 4px; border-radius: 4px; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 정제 (컬럼명 대응 강화)
@st.cache_data
def load_data():
    try:
        f = pd.read_csv("forecast_data.csv")
        a = pd.read_csv("actual_data.csv")
    except:
        st.error("데이터 파일을 찾을 수 없습니다. 파일명을 확인해주세요.")
        return pd.DataFrame(), pd.DataFrame()

    def clean_df(df):
        # 1. 'supplier' 컬럼 대응 (KeyError 방지)
        if 'supplier' not in df.columns:
            if 'supply' in df.columns:
                df = df.rename(columns={'supply': 'supplier'})
            else:
                df['supplier'] = '미분류'
        
        # 2. 시리즈 정제 (숫자 시리즈 제거 및 공백 제거)
        if 'series' in df.columns:
            df['series'] = df['series'].astype(str).str.strip()
            df = df[~df['series'].str.isnumeric()]
            df = df[df['series'].str.len() > 1]
        return df

    return clean_df(f), clean_df(a)

f_df, a_df = load_data()

# 3. 사이드바 필터 설정
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

    # 4. 상단 컨트롤 바 (정렬/검색 기능 복구)
    st.title(f"📊 {sel_ym} 수요 수급 분석 대시보드")
    
    c_head1, c_head2, c_head3 = st.columns([2, 2, 3])
    with c_head1:
        sort_metric = st.selectbox("📌 정렬 지표", ["오차량 큰 순", "실수주량 큰 순", "예측수요 큰 순", "달성률 낮은 순"])
    with c_head2:
        top_n = st.slider("🎯 표시 개수 (Top N)", 5, 50, 10)
    with c_head3:
        search_q = st.text_input("🔎 검색 (코드/명칭)", placeholder="검색어를 입력하세요...")

    # 정렬 및 검색 적용
    sort_map = {"오차량 큰 순": ("오차량", False), "실수주량 큰 순": ("actual", False), 
                "예측수요 큰 순": ("forecast", False), "달성률 낮은 순": ("달성률(%)", True)}
    mg = mg.sort_values(by=sort_map[sort_metric][0], ascending=sort_map[sort_metric][1])
    if search_q:
        mg = mg[mg['name'].str.contains(search_q, case=False) | mg['combo'].str.contains(search_q, case=False)]

    # 상단 요약 지표 (KPI)
    t_f, t_a = mg['forecast'].sum(), mg['actual'].sum()
    t_diff = t_a - t_f
    t_rate = (t_a / t_f * 100) if t_f > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-container"><div class="metric-label">예측수요 합계</div><div class="metric-value">{t_f:,.0f}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-container"><div class="metric-label">실수주량 합계</div><div class="metric-value">{t_a:,.0f}</div></div>', unsafe_allow_html=True)
    with m3:
        color = "#EF4444" if t_diff < 0 else "#10B981"
        st.markdown(f'<div class="metric-container"><div class="metric-label">차이량 합계</div><div class="metric-value" style="color:{color}">{t_diff:,.0f}</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-container"><div class="metric-label">전체 달성률</div><div class="metric-value">{t_rate:.1f}%</div></div>', unsafe_allow_html=True)

    st.write("---")

    # 5. 메인 탭 구성 (요청하신 3가지 탭 + 리포트 추가)
    tab1, tab2, tab3, tab4 = st.tabs(["🏛️ 브랜드·공급단 분석", "📈 시계열 추이", "🔍 시리즈 상세", "📝 상세 분석 리포트"])

    # Tab 1: 브랜드 및 공급단별 분석
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("브랜드별 예측 현황")
            fig_b = px.bar(mg.groupby('brand')['forecast'].sum().reset_index(), 
                           x='brand', y='forecast', color='brand', template='plotly_white', text_auto=',.0f')
            st.plotly_chart(fig_b, use_container_width=True)
        with c2:
            st.subheader("공급단별 예측 비중")
            fig_p = px.pie(mg.groupby('supplier')['forecast'].sum().reset_index(), 
                           values='forecast', names='supplier', hole=0.4, template='plotly_white')
            st.plotly_chart(fig_p, use_container_width=True)
        
        st.subheader("브랜드 × 공급단 분석 테이블")
        pv = mg.pivot_table(index='brand', columns='supplier', values='forecast', aggfunc='sum', fill_value=0)
        st.dataframe(pv.style.format("{:,.0f}").background_gradient(cmap='Blues'), use_container_width=True)

    # Tab 2: 시계열 추이 분석
    with tab2:
        st.subheader("월별 수요 및 실적 추이")
        # 시계열 데이터를 위해 전체 데이터 활용
        ts_f = f_df[f_df['brand'].isin(sel_br)].groupby('ym')['forecast'].sum()
        # 실적 데이터 매칭
        ts_a = pd.merge(a_df, f_df[['combo', 'brand']].drop_duplicates(), on='combo')
        ts_a = ts_a[ts_a['brand'].isin(sel_br)].groupby('ym')['actual'].sum()
        
        fig_ts = go.Figure()
        fig_ts.add_trace(go.Scatter(x=ts_f.index, y=ts_f.values, name="예측 수요", line=dict(color='#3B82F6', width=3)))
        fig_ts.add_trace(go.Scatter(x=ts_a.index, y=ts_a.values, name="실제 수주", line=dict(color='#F43F5E', width=3, dash='dot')))
        fig_ts.update_layout(template='plotly_white', hovermode='x unified', margin=dict(l=20,r=20,t=20,b=20))
        st.plotly_chart(fig_ts, use_container_width=True)

    # Tab 3: 시리즈 상세 분석
    with tab3:
        st.subheader("브랜드 내 시리즈별 분석")
        target_br = st.selectbox("분석할 브랜드 선택", sel_br)
        br_detail = mg[mg['brand'] == target_br].groupby('series')[['forecast', 'actual']].sum().sort_values('forecast', ascending=False).head(top_n)
        fig_detail = px.bar(br_detail.reset_index(), x='series', y=['forecast', 'actual'], barmode='group', template='plotly_white')
        st.plotly_chart(fig_detail, use_container_width=True)
        st.dataframe(mg[mg['brand'] == target_br][['시리즈', '단품코드', '명칭', 'forecast', 'actual', '차이', '달성률(%)']].head(top_n), use_container_width=True)

    # Tab 4: 상세 분석 리포트 (사람이 읽는 서술형)
    with tab4:
        st.subheader("📋 담당자 분석 리포트")
        top_items = mg.head(5)
        
        report_html = ""
        for i, (_, row) in enumerate(top_items.iterrows(), 1):
            cb = str(row['combo'])
            code, color = (cb.split('-')[0], cb.split('-')[1]) if '-' in cb else (cb, "기본")
            
            report_html += f"""
            <div class="item-highlight">
                <strong>{i}. {row['name']}</strong> (공급단: {row['supplier']})<br>
                이 품목은 <code>시리즈: {row['series']}</code>, <code>단품코드: {code}</code>, <code>색상: {color}</code>인 
                <strong>'{row['name']}'</strong> 모델입니다.<br>
                이번 달 예측 대비 실제 수주는 <strong>{int(row['actual']):,}</strong>건으로 기록되며 
                최종 <strong>달성률 {row['달성률(%)']:.1f}%</strong>를 기록했습니다. 
                (예측치와 약 {int(abs(row['차이'])):,}만큼의 차이가 발생했습니다.)
            </div>
            """

        st.markdown(f"""
        <div class="analysis-card">
            안녕하세요, {sel_ym} 수급 데이터 분석 결과입니다.<br><br>
            이번 달 선택된 품목들의 총 예측 수량은 <strong>{int(t_f):,}</strong>이며, 
            실제 수주량은 <strong>{int(t_a):,}</strong>로 집계되어 전체 <strong>{t_rate:.1f}%의 달성률</strong>을 기록 중입니다.<br><br>
            
            데이터 분석 결과, 예측과 실제 수요의 간격이 커서 <strong>우선적인 재고 점검</strong>이 필요한 상위 5개 모델은 다음과 같습니다.
            {report_html}
            <br>
            위 리스트는 현재 설정하신 <strong>{sort_metric}</strong> 기준으로 정렬되었습니다. 
            수급 불균형이 두드러지는 품목들을 위주로 생산 일정이나 자재 상황을 우선적으로 검토하시길 권장드립니다.
        </div>
        """, unsafe_allow_html=True)

else:
    st.warning("데이터를 불러올 수 없습니다. 파일명이나 컬럼명을 확인해주세요.")
