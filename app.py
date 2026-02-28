import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# 1. 페이지 설정 및 세련된 라이트 디자인 (CSS 스타일링)
st.set_page_config(page_title="수요분석 리포트", layout="wide")

st.markdown("""
    <style>
    /* 전체 배경 및 폰트 설정 */
    .main { background-color: #F9FAFB; }
    .stApp { background-color: #F9FAFB; }
    
    /* KPI 카드 스타일 */
    .metric-container {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #E5E7EB;
        text-align: center;
    }
    .metric-label { font-size: 14px; color: #6B7280; font-weight: 500; }
    .metric-value { font-size: 26px; font-weight: 800; color: #111827; margin-top: 5px; }
    
    /* 리포트 박스 스타일 */
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

# 2. 데이터 로드 및 정밀 정제
@st.cache_data
def load_data():
    try:
        f = pd.read_csv("forecast_data.csv")
        a = pd.read_csv("actual_data.csv")
    except:
        # 파일이 없을 경우를 대비한 가상 데이터 구조 (에러 방지용)
        st.error("데이터 파일을 찾을 수 없습니다. 파일명을 확인해주세요.")
        return pd.DataFrame(), pd.DataFrame()

    def clean_df(df):
        # 필수 컬럼 존재 확인 및 필터링
        if 'series' in df.columns:
            df['series'] = df['series'].astype(str).str.strip()
            # 숫자 시리즈(107, 108 등) 제거
            df = df[~df['series'].str.isnumeric()]
            df = df[df['series'].str.len() > 1]
        
        # 'supplier' 컬럼이 없으면 'supply' 컬럼을 찾아서 변경 (KeyError 방지)
        if 'supplier' not in df.columns and 'supply' in df.columns:
            df = df.rename(columns={'supply': 'supplier'})
        elif 'supplier' not in df.columns:
            df['supplier'] = '미분류' # 기본값 할당
            
        return df

    return clean_df(f), clean_df(a)

f_df, a_df = load_data()

# 3. 사이드바 필터 (이미지 575cd7 스타일)
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

    # 상단 요약 지표 (KPI)
    st.title(f"📊 {sel_ym} 수요 수급 분석 대시보드")
    
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

    # 4. 메인 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(["🏛️ 브랜드·공급단 분석", "📈 시계열 추이", "🔍 시리즈 상세", "📝 상세 분석 리포트"])

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
        st.table(pv.style.format("{:,.0f}").background_gradient(cmap='Blues'))

    with tab2:
        st.subheader("월별 수요 및 실적 추이")
        # 시계열 데이터를 위해 f_df와 a_df 전체 사용
        ts_f = f_df[f_df['brand'].isin(sel_br)].groupby('ym')['forecast'].sum()
        # a_df는 combo 기준으로 f_df와 매칭하여 브랜드 정보 가져옴
        ts_a = pd.merge(a_df, f_df[['combo', 'brand']].drop_duplicates(), on='combo')
        ts_a = ts_a[ts_a['brand'].isin(sel_br)].groupby('ym')['actual'].sum()
        
        fig_ts = go.Figure()
        fig_ts.add_trace(go.Scatter(x=ts_f.index, y=ts_f.values, name="예측 수요", line=dict(color='#3B82F6', width=3)))
        fig_ts.add_trace(go.Scatter(x=ts_a.index, y=ts_a.values, name="실제 수주", line=dict(color='#F43F5E', width=3, dash='dot')))
        fig_ts.update_layout(template='plotly_white', hovermode='x unified')
        st.plotly_chart(fig_ts, use_container_width=True)

    with tab3:
        st.subheader("시리즈별 상세 분석")
        target_br = st.selectbox("브랜드 선택", sel_br)
        br_detail = mg[mg['brand'] == target_br].groupby('series')[['forecast', 'actual']].sum().sort_values('forecast', ascending=False)
        fig_detail = px.bar(br_detail.reset_index(), x='series', y=['forecast', 'actual'], barmode='group', template='plotly_white')
        st.plotly_chart(fig_detail, use_container_width=True)

    with tab4:
        st.subheader("📋 사람의 언어로 보는 상세 리포트")
        
        top_5 = mg.sort_values('오차량', ascending=False).head(5)
        
        report_html = ""
        for i, (_, row) in enumerate(top_5.iterrows(), 1):
            cb = str(row['combo'])
            code = cb.split('-')[0] if '-' in cb else cb
            color = cb.split('-')[1] if '-' in cb else "기본"
            
            report_html += f"""
            <div class="item-highlight">
                <strong>{i}. {row['name']}</strong> (공급단: {row['supplier']})<br>
                이 품목은 <code>시리즈: {row['series']}</code>, <code>단품코드: {code}</code>, <code>색상: {color}</code>인 
                <strong>'{row['name']}'</strong> 모델입니다.<br>
                이번 달 예측치 대비 실제 수주량은 <strong>{int(row['actual']):,}</strong>건을 기록하며 
                최종 <strong>달성률 {row['달성률(%)']:.1f}%</strong>로 마감되었습니다. 
                (예측치와 약 {int(abs(row['차이'])):,}만큼의 차이가 발생했습니다.)
            </div>
            """

        st.markdown(f"""
        <div class="analysis-card">
            안녕하세요, {sel_ym} 수급 데이터 분석 결과입니다.<br><br>
            이번 달 선택된 품목들의 총 예측 수량은 <strong>{int(t_f):,}</strong>이며, 
            실제 수주량은 <strong>{int(t_a):,}</strong>로 집계되어 전체 <strong>{t_rate:.1f}%의 달성률</strong>을 기록 중입니다.<br><br>
            
            데이터 분석 결과, 예측과 실제 수요의 간극이 가장 커서 <strong>우선적인 재고 점검</strong>이 필요한 상위 5개 모델은 다음과 같습니다.
            {report_html}
            <br>
            위 품목들은 현재 수급 불균형이 가장 두드러지게 나타나고 있습니다. 
            해당 시리즈의 생산 일정 조정이나 자재 수급 상황을 우선적으로 검토하시길 권장드립니다.
        </div>
        """, unsafe_allow_html=True)

else:
    st.warning("데이터를 불러올 수 없습니다. CSV 파일의 컬럼명(ym, brand, series, combo, forecast, actual 등)을 확인해주세요.")
