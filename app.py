import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# 1. 페이지 설정 및 다크 테마 스타일링
st.set_page_config(page_title="SCM 수요분석 대시보드", layout="wide")

st.markdown("""
    <style>
    /* 다크 테마 기반의 전문적인 스타일 */
    .stApp { background-color: #0F172A; color: #F8FAFC; }
    [data-testid="stSidebar"] { background-color: #1E293B; border-right: 1px solid #334155; }
    .metric-card {
        background-color: #1E293B; border-radius: 10px; padding: 20px;
        border: 1px solid #334155; text-align: center;
    }
    .metric-value { font-size: 28px; font-weight: bold; color: #38BDF8; }
    .analysis-box { 
        background-color: #1E293B; border-radius: 12px; padding: 25px; 
        border: 1px solid #334155; line-height: 1.8; color: #E2E8F0;
    }
    .item-card { 
        background: #334155; padding: 20px; border-radius: 10px; 
        margin-top: 15px; border-left: 5px solid #38BDF8;
    }
    code { color: #F472B6; background: #4D1D39; padding: 2px 5px; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 전처리 (숫자 시리즈 제거 및 공급단 추가 가정)
@st.cache_data
def load_data():
    # 파일 로드 (실제 환경에서는 pd.read_csv 사용)
    try:
        f = pd.read_csv("forecast_data.csv")
        a = pd.read_csv("actual_data.csv")
    except:
        # 데모용 샘플 데이터 생성
        months = pd.date_range(start="2025-06-01", periods=9, freq='M').strftime("%Y-%m").tolist()
        data = []
        for m in months:
            for b in ["시디즈", "퍼시스", "일룸", "데스커"]:
                for s in ["시디즈제품", "의자양지상품", "베트남제품"]:
                    data.append({
                        'ym': m, 'brand': b, 'supplier': s, 'series': 'IBLE', 
                        'combo': f'C1-{b}', 'name': f'{b} 사무용 의자', 
                        'forecast': np.random.randint(500, 2000), 
                        'actual': np.random.randint(400, 2200)
                    })
        f = pd.DataFrame(data)
        a = f[['ym', 'combo', 'actual']].copy()
        f = f.drop(columns=['actual'])

    def clean_df(df):
        df = df.dropna(subset=['series', 'brand'])
        # [요청 반영] 숫자만 있는 시리즈(107, 15 등) 필터링
        df['series'] = df['series'].astype(str).str.strip()
        df = df[~df['series'].str.isnumeric()]
        return df

    return clean_df(f), clean_df(a)

f_df, a_df = load_data()

# 3. 사이드바 필터
st.sidebar.title("🔎 필터 설정")
sel_ym = st.sidebar.selectbox("📅 기준 년월", sorted(f_df["ym"].unique(), reverse=True))
all_brands = sorted(f_df["brand"].unique().tolist())
sel_br = st.sidebar.multiselect("🏷️ 브랜드", all_brands, default=all_brands)
all_sups = sorted(f_df["supplier"].unique().tolist())
sel_sup = st.sidebar.multiselect("🏭 공급단", all_sups, default=all_sups)

# 데이터 병합
f_sel = f_df[(f_df["ym"] == sel_ym) & (f_df["brand"].isin(sel_br)) & (f_df["supplier"].isin(sel_sup))].copy()
a_sel = a_df[a_df["ym"] == sel_ym].copy()
mg = pd.merge(f_sel, a_sel, on=["ym", "combo"], how="left").fillna(0)
mg["차이"] = mg["actual"] - mg["forecast"]
mg["오차량"] = mg["차이"].abs()
mg["달성률(%)"] = np.where(mg["forecast"] > 0, (mg["actual"] / mg["forecast"] * 100).round(1), 0)

# --- 메인 대시보드 ---

# 상단 요약 지표 (이미지 57bab5 스타일)
t_f, t_a = mg['forecast'].sum(), mg['actual'].sum()
st.markdown(f"### 📊 {sel_ym} 수요 분석 요약")
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="metric-card"><div style="color:#94A3B8">예측수요 합계</div><div class="metric-value">{t_f:,.0f}</div></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="metric-card"><div style="color:#94A3B8">실수주량 합계</div><div class="metric-value">{t_a:,.0f}</div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="metric-card"><div style="color:#94A3B8">차이량 합계</div><div class="metric-value" style="color:#FB7185">{(t_a-t_f):,.0f}</div></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="metric-card"><div style="color:#94A3B8">전체 달성률</div><div class="metric-value">{(t_a/t_f*100 if t_f>0 else 0):.1f}%</div></div>', unsafe_allow_html=True)

# 탭 구성 (이미지 575cfc 스타일 반영)
tab1, tab2, tab3, tab4 = st.tabs(["📊 브랜드·공급단 분석", "📈 시계열 추이", "🔍 시리즈 상세", "📝 상세 분석 리포트"])

# Tab 1: 브랜드 및 공급단 분석
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("브랜드별 예측 현황")
        b_df = mg.groupby('brand')['forecast'].sum().reset_index()
        fig_b = px.bar(b_df, x='brand', y='forecast', text_auto=',.0f', color='brand', template="plotly_dark")
        st.plotly_chart(fig_b, use_container_width=True)
    with col2:
        st.subheader("공급단별 예측 비중")
        s_df = mg.groupby('supplier')['forecast'].sum().reset_index()
        fig_s = px.pie(s_df, values='forecast', names='supplier', hole=0.5, template="plotly_dark")
        st.plotly_chart(fig_s, use_container_width=True)
    
    st.subheader("브랜드 × 공급단 예측량")
    pivot_df = mg.pivot_table(index='brand', columns='supplier', values='forecast', aggfunc='sum').fillna(0)
    st.dataframe(pivot_df.style.format("{:,.0f}").background_gradient(cmap='Blues'), use_container_width=True)

# Tab 2: 시계열 추이
with tab2:
    st.subheader("월별 수요예측 및 실적 추이")
    # 시계열용 데이터 재병합
    ts_f = f_df[f_df['brand'].isin(sel_br)].groupby('ym')['forecast'].sum()
    ts_a = a_df.merge(f_df[['ym', 'combo', 'brand']], on=['ym', 'combo'])
    ts_a = ts_a[ts_a['brand'].isin(sel_br)].groupby('ym')['actual'].sum()
    
    fig_ts = go.Figure()
    fig_ts.add_trace(go.Scatter(x=ts_f.index, y=ts_f.values, name="예측 수요", line=dict(color='#38BDF8', width=3)))
    fig_ts.add_trace(go.Scatter(x=ts_a.index, y=ts_a.values, name="실제 수주", line=dict(color='#FB7185', width=3, dash='dot')))
    fig_ts.update_layout(template="plotly_dark", hovermode="x unified")
    st.plotly_chart(fig_ts, use_container_width=True)

# Tab 3: 시리즈 상세
with tab3:
    st.subheader("브랜드 내 시리즈별 분석")
    sel_br_detail = st.selectbox("분석할 브랜드 선택", sel_br)
    detail_df = mg[mg['brand'] == sel_br_detail].groupby('series')['forecast'].sum().sort_values(ascending=True).reset_index()
    fig_detail = px.bar(detail_df, x='forecast', y='series', orientation='h', color_discrete_sequence=['#38BDF8'], template="plotly_dark")
    st.plotly_chart(fig_detail, use_container_width=True)

# Tab 4: 상세 분석 리포트 (사람이 말하듯 수정)
with tab4:
    st.subheader(f"📋 {sel_ym} 담당자 분석 보고서")
    
    # 오차량이 큰 상위 5개 추출
    top_5_err = mg.sort_values(by="오차량", ascending=False).head(5)
    
    report_items = ""
    for i, (_, row) in enumerate(top_5_err.iterrows(), 1):
        cb = str(row['combo'])
        code = cb.split('-')[0] if '-' in cb else cb
        color = cb.split('-')[1] if '-' in cb else "기본"
        
        # [요청 문구 반영] 시리즈, 단품코드, 색상, 명칭 포함
        report_items += f"""
        <div class="item-card">
            <strong>{i}. {row['name']}</strong> (공급단: {row['supplier']})<br>
            이 품목은 <code>시리즈: {row['series']}</code>, <code>단품코드: {code}</code>, <code>색상: {color}</code>인 
            <strong>단품명칭: {row['name']}</strong> 모델입니다.<br>
            이번 달 예측 대비 실적은 <strong>{int(row['actual']):,}</strong>를 기록하여, 최종적으로 
            <strong>달성률 {row['달성률(%)']:.1f}%</strong>로 분석되었습니다. 
            예측치보다 약 {int(abs(row['차이'])):,}만큼 {'더 많이' if row['차이'] > 0 else '적게'} 수주되어 관리가 필요한 상태입니다.
        </div>
        """

    st.markdown(f"""
    <div class="analysis-box">
        안녕하세요, {sel_ym} 수급 분석 결과입니다.<br><br>
        이번 달 필터링된 데이터 기준으로 전체 예측 수요는 <strong>{int(t_f):,}</strong>건이었으나, 
        실제로는 <strong>{int(t_a):,}</strong>건이 수주되어 전체 <strong>{t_a/t_f*100:.1f}%의 달성률</strong>을 보이고 있습니다.<br><br>
        
        특히 예측과 실적의 간극이 커서 <strong>재고 부족이나 과잉이 우려되는 상위 5개 품목</strong>을 정리해 드립니다. 
        해당 품목들은 생산 계획을 긴급히 점검해 보시는 것이 좋겠습니다.
        {report_items}
        <br>
        위 리스트를 바탕으로 차기 수요 예측 시에는 해당 시리즈들의 변동성을 보정값에 반영하시길 제언드립니다.
    </div>
    """, unsafe_allow_html=True)
