import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io, os

# ─────────────────────────────────────────────
st.set_page_config(page_title="수요예측 대시보드", page_icon="📊",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=DM+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'Noto Sans KR',sans-serif;}
.stApp{background:#0d1117;}
[data-testid="stSidebar"]{background:#161b22!important;border-right:1px solid #21262d;}
[data-testid="stSidebar"] *{color:#c9d1d9!important;}
[data-testid="stSidebar"] label{color:#8b949e!important;font-size:11px;letter-spacing:1px;text-transform:uppercase;}
[data-testid="metric-container"]{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:16px 20px;}
[data-testid="metric-container"] label{color:#8b949e!important;font-size:11px;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#e6edf3!important;font-family:'DM Mono',monospace;font-size:26px;}
.section-header{font-size:11px;font-weight:700;color:#8b949e;letter-spacing:1.5px;text-transform:uppercase;padding:8px 0 4px;border-bottom:1px solid #21262d;margin-bottom:12px;}
.main-title{font-size:24px;font-weight:900;color:#e6edf3;letter-spacing:-0.5px;margin:0;}
.main-subtitle{font-size:12px;color:#6e7681;margin-top:4px;}
.insight-box{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:14px 18px;margin-bottom:10px;}
.insight-title{font-size:11px;color:#8b949e;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;}
.insight-item{font-size:13px;color:#c9d1d9;padding:4px 0;border-bottom:1px solid #21262d;}
.insight-item:last-child{border-bottom:none;}
.over{color:#58a6ff;} .under{color:#f85149;} .neutral{color:#8b949e;}
hr{border-color:#21262d!important;}
.stSelectbox>div>div{background:#0d1117!important;border-color:#30363d!important;color:#e6edf3!important;}
.stMultiSelect>div{background:#0d1117!important;border-color:#30363d!important;}
.stTextInput>div>div{background:#0d1117!important;border-color:#30363d!important;color:#e6edf3!important;}
</style>
""", unsafe_allow_html=True)

# ─── 상수 ───────────────────────────────────
BRANDS   = ["시디즈","퍼시스","일룸","데스커"]
SUPPLIES = ["시디즈제품","의자양지상품","베트남제품"]
BC = {"시디즈":"#58a6ff","퍼시스":"#3fb950","일룸":"#ffa657","데스커":"#bc8cff"}
SC = {"시디즈제품":"#58a6ff","의자양지상품":"#ffa657","베트남제품":"#3fb950"}
YML = {"2025-06":"'25.06","2025-07":"'25.07","2025-08":"'25.08",
       "2025-10":"'25.10","2025-11":"'25.11","2025-12":"'25.12",
       "2026-01":"'26.01","2026-02":"'26.02"}
YMF = {"2025-06":"2025년 06월","2025-07":"2025년 07월","2025-08":"2025년 08월",
       "2025-10":"2025년 10월","2025-11":"2025년 11월","2025-12":"2025년 12월",
       "2026-01":"2026년 01월","2026-02":"2026년 02월"}
PBG = dict(plot_bgcolor="#161b22", paper_bgcolor="#161b22", font_color="#c9d1d9")
GRD = dict(gridcolor="#21262d")

def ps(**kw):
    d = {**PBG, "xaxis": GRD, "yaxis": GRD, "margin": dict(t=30,b=0,l=0,r=0)}
    d.update(kw)
    return d

# ─── 데이터 로드 ─────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load():
    fc = pd.read_csv(os.path.join(BASE,"forecast_data.csv"), encoding="utf-8-sig")
    ac = pd.read_csv(os.path.join(BASE,"actual_data.csv"),   encoding="utf-8-sig")
    fc["forecast"] = pd.to_numeric(fc["forecast"], errors="coerce").fillna(0).astype(int)
    ac["actual"]   = pd.to_numeric(ac["actual"],   errors="coerce").fillna(0).astype(int)
    fc = fc[fc["ym"] != "2025-09"]
    ac = ac[ac["ym"] != "2025-09"]
    fc["supply"] = fc["supply"].fillna("").astype(str)
    ac["supply"] = ac["supply"].fillna("").astype(str)
    return fc, ac

df_fc, df_ac = load()
FC_M  = sorted(df_fc["ym"].unique())
AC_M  = sorted(df_ac["ym"].unique())
ALL_M = sorted(set(FC_M)|set(AC_M))

# ─── 사이드바 ────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 필터")
    st.markdown("---")
    sel_ym  = st.selectbox("기준 년월", ALL_M,
                           index=ALL_M.index("2026-02") if "2026-02" in ALL_M else len(ALL_M)-1,
                           format_func=lambda x: YMF.get(x,x))
    sel_br  = st.multiselect("브랜드",  BRANDS,   default=BRANDS)
    sel_sp  = st.multiselect("공급단", SUPPLIES, default=SUPPLIES)
    if not sel_br:  sel_br  = BRANDS
    if not sel_sp:  sel_sp  = SUPPLIES
    st.markdown("---")
    vmode   = st.radio("분석 단위", ["시리즈별","품목별"], horizontal=True)
    st.markdown("---")
    st.markdown("**🔎 검색**")
    skw     = st.text_input("품목명 / 코드 / 시리즈", placeholder="예: GC PRO, T60, 아이블...")
    st.markdown("---")
    st.markdown("""<div style='color:#6e7681;font-size:11px;'>
    📁 데이터 범위<br>예측: 2025.06~2026.02<br>실적: 2025.08~2026.02<br>※ 2025.09 예측자료 없음
    </div>""", unsafe_allow_html=True)

# ─── 헬퍼 ───────────────────────────────────
def kw_filter(df, kw):
    if not kw: return df
    kl = kw.lower()
    m  = pd.Series(False, index=df.index)
    for c in ["series","combo","name"]:
        if c in df.columns:
            m |= df[c].astype(str).str.lower().str.contains(kl, na=False)
    return df[m]

# ─── 필터 적용 ───────────────────────────────
fc_base = df_fc[df_fc["brand"].isin(sel_br) & df_fc["supply"].isin(sel_sp)].copy()
ac_base = df_ac[df_ac["brand"].isin(sel_br) & df_ac["supply"].isin(sel_sp)].copy()

fc_cur = kw_filter(fc_base[fc_base["ym"]==sel_ym].copy(), skw)
ac_cur = kw_filter(ac_base[ac_base["ym"]==sel_ym].copy(), skw)

has_act = sel_ym in AC_M

if has_act and not ac_cur.empty:
    ac_agg = ac_cur.groupby("combo")["actual"].sum().reset_index()
    mg = fc_cur.merge(ac_agg, on="combo", how="left")
    mg["actual"] = mg["actual"].fillna(0).astype(int)
else:
    mg = fc_cur.copy()
    mg["actual"] = 0
mg["diff"] = mg["actual"] - mg["forecast"]
mg["rate"] = np.where(mg["forecast"]>0, mg["actual"]/mg["forecast"], np.nan)

kpi_fc   = int(mg["forecast"].sum())
kpi_ac   = int(mg["actual"].sum()) if has_act else None
kpi_diff = kpi_ac - kpi_fc if has_act else None
kpi_rate = kpi_ac/kpi_fc if (has_act and kpi_fc>0) else None

# ─── 헤더 + KPI ─────────────────────────────
ct, cs = st.columns([4,1])
with ct:
    stxt = f' · 검색: "{skw}"' if skw else ""
    st.markdown(
        f'<div class="main-title">📊 수요예측 대시보드</div>'
        f'<div class="main-subtitle">{YMF.get(sel_ym,sel_ym)} · {", ".join(sel_br)} · {", ".join(sel_sp)}{stxt}</div>',
        unsafe_allow_html=True)
with cs:
    st.markdown("<br>", unsafe_allow_html=True)
    st.success("✅ 예측 + 실적") if has_act else st.info("📋 예측 전용")

st.markdown("---")
c1,c2,c3,c4,c5 = st.columns(5)
with c1: st.metric("📦 수요예측량", f"{kpi_fc:,}")
with c2:
    if has_act: st.metric("📬 실수주량", f"{kpi_ac:,}", delta=f"{kpi_diff:+,}" if kpi_diff else None)
    else:       st.metric("📬 실수주량", "실적 없음")
with c3:
    if has_act and kpi_rate: st.metric("📈 달성률", f"{kpi_rate*100:.1f}%", delta=f"{(kpi_rate-1)*100:+.1f}%p")
    else:                    st.metric("📈 달성률", "-")
with c4:
    if has_act:
        ov = int((mg["diff"]>0).sum()); os_ = int(mg[mg["diff"]>0]["diff"].sum())
        st.metric("🔵 예측초과", f"{ov}개", delta=f"+{os_:,}")
    else: st.metric("🔵 예측초과", "-")
with c5:
    if has_act:
        un = int((mg["diff"]<0).sum()); us = int(mg[mg["diff"]<0]["diff"].sum())
        st.metric("🔴 예측미달", f"{un}개", delta=f"{us:,}", delta_color="inverse")
    else: st.metric("📋 품목수", f"{len(mg[mg['forecast']>0]):,}개")
st.markdown("<br>", unsafe_allow_html=True)

# ─── 탭 ─────────────────────────────────────
t1,t2,t3,t4,t5 = st.tabs(["📊 브랜드·공급단","📈 시계열 추이","🔍 시리즈·품목 상세","💡 분석 요약","📋 전체 데이터"])

# ══ 탭1 : 브랜드·공급단 ══════════════════════
with t1:
    if mg.empty:
        st.warning("선택 조건에 데이터가 없습니다.")
    else:
        cl, cr = st.columns(2)

        # 브랜드별 예측 vs 실적
        with cl:
            st.markdown('<div class="section-header">브랜드별 예측 vs 실적</div>', unsafe_allow_html=True)
            ba = mg.groupby("brand").agg(forecast=("forecast","sum"), actual=("actual","sum")).reset_index()
            ba = ba[ba["brand"].isin(sel_br)]
            fig = go.Figure()
            bcs = [BC.get(b,"#8b949e") for b in ba["brand"]]
            fig.add_trace(go.Bar(x=ba["brand"], y=ba["forecast"], name="수요예측",
                                 marker_color=bcs, opacity=0.4,
                                 text=ba["forecast"].apply(lambda v: f"{v:,}"), textposition="outside"))
            if has_act:
                fig.add_trace(go.Bar(x=ba["brand"], y=ba["actual"], name="실수주",
                                     marker_color=bcs,
                                     text=ba["actual"].apply(lambda v: f"{v:,}"), textposition="outside"))
            fig.update_layout(**ps(barmode="group", height=300,
                                   legend=dict(orientation="h",y=1.12,x=0,font_size=11)))
            st.plotly_chart(fig, use_container_width=True)

        # 공급단 도넛
        with cr:
            st.markdown('<div class="section-header">공급단별 예측 비중</div>', unsafe_allow_html=True)
            sa = mg.groupby("supply")["forecast"].sum().reset_index()
            sa = sa[sa["forecast"]>0]
            if sa.empty:
                st.info("데이터 없음")
            else:
                fig2 = go.Figure(go.Pie(
                    labels=sa["supply"], values=sa["forecast"], hole=0.62,
                    marker_colors=[SC.get(s,"#8b949e") for s in sa["supply"]],
                    textfont_size=12, textinfo="label+percent"))
                fig2.update_layout(**PBG, height=300, showlegend=False,
                                   margin=dict(t=10,b=10,l=0,r=0),
                                   annotations=[dict(text=f"<b>{kpi_fc:,}</b>",x=0.5,y=0.5,
                                                     font_size=16,font_color="#e6edf3",showarrow=False)])
                st.plotly_chart(fig2, use_container_width=True)

        # 히트맵 (안전 버전)
        st.markdown('<div class="section-header">브랜드 × 공급단 예측량 히트맵</div>', unsafe_allow_html=True)
        pd_data = mg.groupby(["brand","supply"])["forecast"].sum().reset_index()
        if not pd_data.empty:
            pt = pd_data.pivot_table(index="brand", columns="supply",
                                     values="forecast", aggfunc="sum", fill_value=0)
            pt.columns.name = None
            # 없는 행/열 추가
            for b in sel_br:
                if b not in pt.index: pt.loc[b] = 0
            for s in sel_sp:
                if s not in pt.columns: pt[s] = 0
            # 선택된 것만
            rows = [b for b in sel_br if b in pt.index]
            cols_h = [s for s in sel_sp if s in pt.columns]
            if rows and cols_h:
                pt = pt.loc[rows, cols_h]
                fig3 = go.Figure(go.Heatmap(
                    z=pt.values, x=pt.columns.tolist(), y=pt.index.tolist(),
                    colorscale=[[0,"#161b22"],[0.5,"#1d4d8a"],[1,"#58a6ff"]],
                    text=[[f"{v:,.0f}" for v in row] for row in pt.values],
                    texttemplate="%{text}", textfont_size=13, showscale=False))
                fig3.update_layout(**PBG, height=max(180, len(rows)*50),
                                   margin=dict(t=10,b=0,l=0,r=0),
                                   xaxis=dict(side="top",gridcolor="#21262d"),
                                   yaxis=dict(autorange="reversed",gridcolor="#21262d"))
                st.plotly_chart(fig3, use_container_width=True)

        # 달성률
        if has_act:
            st.markdown('<div class="section-header">브랜드 × 공급단 달성률</div>', unsafe_allow_html=True)
            rd = mg.groupby(["brand","supply"]).agg(forecast=("forecast","sum"),actual=("actual","sum")).reset_index()
            rd["rate"] = np.where(rd["forecast"]>0, rd["actual"]/rd["forecast"]*100, 0)
            rd = rd[rd["forecast"]>0]
            if not rd.empty:
                fig4 = go.Figure()
                for sup in sel_sp:
                    rds = rd[rd["supply"]==sup].sort_values("brand")
                    if rds.empty: continue
                    fig4.add_trace(go.Bar(name=sup, x=rds["brand"], y=rds["rate"],
                                         marker_color=SC.get(sup,"#8b949e"),
                                         text=[f"{v:.1f}%" for v in rds["rate"]], textposition="outside"))
                fig4.add_hline(y=100, line_dash="dash", line_color="#8b949e", line_width=1,
                               annotation_text="100%", annotation_position="right")
                fig4.update_layout(**ps(barmode="group", height=300,
                                        legend=dict(orientation="h",y=1.12,x=0,font_size=11),
                                        yaxis=dict(gridcolor="#21262d",ticksuffix="%")))
                st.plotly_chart(fig4, use_container_width=True)

# ══ 탭2 : 시계열 추이 ═══════════════════════
with t2:
    cl2, cr2 = st.columns([2,1])

    with cl2:
        st.markdown('<div class="section-header">월별 브랜드별 예측 vs 실적 추이</div>', unsafe_allow_html=True)
        tfa = fc_base.groupby(["ym","brand"])["forecast"].sum().reset_index()
        taa = ac_base.groupby(["ym","brand"])["actual"].sum().reset_index()
        fig5 = go.Figure()
        for b in sel_br:
            bd  = tfa[tfa["brand"]==b].sort_values("ym")
            bda = taa[taa["brand"]==b].sort_values("ym")
            if not bd.empty:
                fig5.add_trace(go.Scatter(
                    x=bd["ym"].map(lambda x: YML.get(x,x)), y=bd["forecast"],
                    name=f"{b} 예측", mode="lines+markers",
                    line=dict(color=BC.get(b,"#8b949e"), width=2.5), marker=dict(size=7)))
            if not bda.empty:
                fig5.add_trace(go.Scatter(
                    x=bda["ym"].map(lambda x: YML.get(x,x)), y=bda["actual"],
                    name=f"{b} 실적", mode="lines+markers",
                    line=dict(color=BC.get(b,"#8b949e"), width=1.5, dash="dot"),
                    marker=dict(size=5, symbol="circle-open")))
        fig5.update_layout(**PBG, height=360, xaxis=GRD, yaxis=GRD,
                           margin=dict(t=10,b=60,l=0,r=0),
                           legend=dict(orientation="h",y=-0.28,x=0,font_size=10))
        st.plotly_chart(fig5, use_container_width=True)

    with cr2:
        st.markdown('<div class="section-header">월별 달성률 추이</div>', unsafe_allow_html=True)
        rts = []
        for ym in sorted(AC_M):
            fcs = fc_base[fc_base["ym"]==ym]["forecast"].sum()
            acs = ac_base[ac_base["ym"]==ym]["actual"].sum()
            if fcs>0: rts.append({"ym": YML.get(ym,ym), "rate": acs/fcs*100})
        if rts:
            dfr = pd.DataFrame(rts)
            fig_r = go.Figure(go.Bar(
                x=dfr["ym"], y=dfr["rate"],
                marker_color=["#58a6ff" if r>=100 else "#f85149" for r in dfr["rate"]],
                text=[f"{r:.1f}%" for r in dfr["rate"]], textposition="outside"))
            fig_r.add_hline(y=100, line_dash="dash", line_color="#8b949e", line_width=1)
            fig_r.update_layout(**PBG, height=360, xaxis=GRD,
                                yaxis=dict(gridcolor="#21262d",ticksuffix="%"),
                                margin=dict(t=10,b=60,l=0,r=10))
            st.plotly_chart(fig_r, use_container_width=True)
        else:
            st.info("달성률 데이터 없음")

    st.markdown('<div class="section-header">공급단별 월별 예측 추이</div>', unsafe_allow_html=True)
    ts_sup = fc_base.groupby(["ym","supply"])["forecast"].sum().reset_index()
    valid_sp = [s for s in sel_sp if not ts_sup[ts_sup["supply"]==s].empty]
    if valid_sp:
        fig6 = make_subplots(rows=1, cols=len(valid_sp), subplot_titles=valid_sp)
        for i, sup in enumerate(valid_sp):
            sd = ts_sup[ts_sup["supply"]==sup].sort_values("ym")
            fig6.add_trace(go.Bar(
                x=sd["ym"].map(lambda x: YML.get(x,x)), y=sd["forecast"],
                marker_color=SC.get(sup,"#8b949e"), name=sup, showlegend=False), row=1, col=i+1)
        fig6.update_layout(**PBG, height=280, margin=dict(t=40,b=0,l=0,r=0))
        for ax in list(fig6.layout):
            if str(ax).startswith("xaxis") or str(ax).startswith("yaxis"):
                fig6.layout[ax].gridcolor = "#21262d"
        st.plotly_chart(fig6, use_container_width=True)

# ══ 탭3 : 시리즈·품목 상세 ══════════════════
with t3:
    ca3, cb3, cc3 = st.columns([1,1,2])
    with ca3: sbd  = st.selectbox("브랜드", sel_br, key="d_br")
    with cb3: ssp  = st.selectbox("공급단", ["전체"]+SUPPLIES, key="d_sp")
    with cc3: skw3 = st.text_input("시리즈/코드/품목명", value=skw, key="d_kw",
                                    placeholder="예: GC PRO, T60, 아이블...")

    det = mg[mg["brand"]==sbd].copy()
    if ssp != "전체": det = det[det["supply"]==ssp]
    det = kw_filter(det, skw3)

    gc = ["series","supply"] if vmode=="시리즈별" else ["combo","name","series","supply"]
    lc = "series" if vmode=="시리즈별" else "combo"

    if det.empty:
        st.warning("해당 조건에 데이터가 없습니다.")
    else:
        ad = {"forecast":"sum"}
        if has_act: ad["actual"] = "sum"
        sagg = det.groupby(gc).agg(ad).reset_index()
        if has_act:
            sagg["diff"] = sagg["actual"] - sagg["forecast"]
            sagg["rate"] = np.where(sagg["forecast"]>0, sagg["actual"]/sagg["forecast"], np.nan)
            sagg = sagg.sort_values("diff", key=abs, ascending=False)

        st.markdown(
            f'<div class="section-header">{sbd} · {ssp} {vmode} ({len(sagg)}개)'
            f'{f" | 검색: {skw3}" if skw3 else ""}</div>', unsafe_allow_html=True)

        cch, ctb = st.columns([3,2])
        bclr = BC.get(sbd,"#58a6ff")

        with cch:
            if not sagg.empty:
                if has_act:
                    disp = sagg.head(25)
                    fig7 = go.Figure(go.Bar(
                        x=disp["diff"], y=disp[lc].astype(str), orientation="h",
                        marker_color=[bclr if d>=0 else "#f85149" for d in disp["diff"]],
                        text=[f"{int(d):+,}" for d in disp["diff"]], textposition="outside"))
                    fig7.add_vline(x=0, line_color="#30363d", line_width=1)
                    fig7.update_layout(**PBG, height=max(300, len(disp)*28),
                                       xaxis=dict(gridcolor="#21262d", title="차이량 (실수주 − 수요예측)"),
                                       yaxis=dict(gridcolor="#21262d", autorange="reversed"),
                                       margin=dict(t=30,b=20,l=0,r=80),
                                       title=dict(text="차이량 (실수주 − 수요예측)",
                                                  font_color="#8b949e",font_size=11,x=0))
                    st.plotly_chart(fig7, use_container_width=True)

                    disp2 = sagg.head(15)
                    fig8 = go.Figure()
                    fig8.add_trace(go.Bar(y=disp2[lc].astype(str), x=disp2["forecast"],
                                         orientation="h", name="예측", marker_color=bclr, opacity=0.45))
                    fig8.add_trace(go.Bar(y=disp2[lc].astype(str), x=disp2["actual"],
                                         orientation="h", name="실적", marker_color=bclr))
                    fig8.update_layout(**PBG, barmode="overlay",
                                       height=max(280, len(disp2)*28),
                                       yaxis=dict(gridcolor="#21262d", autorange="reversed"),
                                       xaxis=GRD,
                                       legend=dict(orientation="h",y=1.12,x=0,font_size=11),
                                       margin=dict(t=30,b=0,l=0,r=0),
                                       title=dict(text="예측 vs 실적 (상위 15개)",
                                                  font_color="#8b949e",font_size=11,x=0))
                    st.plotly_chart(fig8, use_container_width=True)
                else:
                    disp = sagg.head(25)
                    fig7 = go.Figure(go.Bar(
                        x=disp["forecast"], y=disp[lc].astype(str), orientation="h",
                        marker_color=bclr,
                        text=[f"{v:,}" for v in disp["forecast"]], textposition="outside"))
                    fig7.update_layout(**PBG, height=max(300,len(disp)*28),
                                       xaxis=GRD, yaxis=dict(gridcolor="#21262d",autorange="reversed"),
                                       margin=dict(t=10,b=0,l=0,r=80))
                    st.plotly_chart(fig7, use_container_width=True)

        with ctb:
            st.markdown('<div class="section-header">상세 테이블</div>', unsafe_allow_html=True)
            tcols = gc + (["forecast","actual","diff","rate"] if has_act else ["forecast"])
            tbl = sagg[tcols].copy()
            if has_act:
                tbl["달성률"] = tbl["rate"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "-")
                tbl["차이량"] = tbl["diff"].apply(lambda x: f"{int(x):+,}" if pd.notna(x) else "-")
                tbl = tbl.drop(columns=["diff","rate"])
            rn = {"series":"시리즈","combo":"코드조합","name":"품목명","supply":"공급단",
                  "forecast":"수요예측","actual":"실수주"}
            tbl.columns = [rn.get(c,c) for c in tbl.columns]
            st.dataframe(tbl, use_container_width=True, height=600)

# ══ 탭4 : 분석 요약 ═════════════════════════
with t4:
    st.markdown(f'<div class="section-header">📅 {YMF.get(sel_ym,sel_ym)} 분석 인사이트</div>',
                unsafe_allow_html=True)

    if has_act and not mg.empty and mg["forecast"].sum()>0:
        ci1, ci2 = st.columns(2)

        with ci1:
            st.markdown('<div class="insight-box"><div class="insight-title">🔵 예측 초과 TOP 5</div>',
                        unsafe_allow_html=True)
            to = mg[mg["diff"]>0].nlargest(5,"diff")
            if to.empty:
                st.markdown("<div class='insight-item neutral'>초과 품목 없음</div>", unsafe_allow_html=True)
            for _, r in to.iterrows():
                bcc = BC.get(r["brand"],"#58a6ff")
                st.markdown(
                    f"<div class='insight-item'>"
                    f"<span style='color:{bcc}'>[{r['brand']}]</span> "
                    f"<strong>{r['series']}</strong> · <span style='font-size:11px'>{str(r['combo'])[:22]}</span><br>"
                    f"<span class='neutral'>예측 {int(r['forecast']):,} → 실적 {int(r['actual']):,}</span> "
                    f"<span class='over'>(+{int(r['diff']):,})</span></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with ci2:
            st.markdown('<div class="insight-box"><div class="insight-title">🔴 예측 미달 TOP 5</div>',
                        unsafe_allow_html=True)
            tu = mg[mg["diff"]<0].nsmallest(5,"diff")
            if tu.empty:
                st.markdown("<div class='insight-item neutral'>미달 품목 없음</div>", unsafe_allow_html=True)
            for _, r in tu.iterrows():
                bcc = BC.get(r["brand"],"#58a6ff")
                st.markdown(
                    f"<div class='insight-item'>"
                    f"<span style='color:{bcc}'>[{r['brand']}]</span> "
                    f"<strong>{r['series']}</strong> · <span style='font-size:11px'>{str(r['combo'])[:22]}</span><br>"
                    f"<span class='neutral'>예측 {int(r['forecast']):,} → 실적 {int(r['actual']):,}</span> "
                    f"<span class='under'>({int(r['diff']):,})</span></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("실적 데이터가 있는 월(2025.08 ~ 2026.02)을 선택하면 인사이트가 표시됩니다.")

    st.markdown("---")
    st.markdown("### 📆 전체 기간 월별 × 브랜드별 요약")
    rows = []
    for ym in sorted(ALL_M):
        fc_ym = fc_base[fc_base["ym"]==ym]
        ac_ym = ac_base[ac_base["ym"]==ym]
        for b in sel_br:
            fv = int(fc_ym[fc_ym["brand"]==b]["forecast"].sum())
            av = int(ac_ym[ac_ym["brand"]==b]["actual"].sum()) if ym in AC_M else None
            rt = (av/fv*100) if (av is not None and fv>0) else None
            df_ = (av-fv) if av is not None else None
            rows.append({"년월":YMF.get(ym,ym),"브랜드":b,"수요예측":fv,
                         "실수주":av if av is not None else "-",
                         "차이량":f"{df_:+,}" if df_ is not None else "-",
                         "달성률(%)":f"{rt:.1f}%" if rt is not None else "-"})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, height=480)

    st.markdown("---")
    st.markdown("### 📦 시리즈별 분석 요약")
    if has_act and not mg.empty:
        ss = mg.groupby(["brand","series"]).agg(forecast=("forecast","sum"),actual=("actual","sum")).reset_index()
        ss["diff"] = ss["actual"]-ss["forecast"]
        ss["rate"] = np.where(ss["forecast"]>0, ss["actual"]/ss["forecast"]*100, np.nan)
        ss = ss[ss["brand"].isin(sel_br)].sort_values("diff", key=abs, ascending=False)
        for b in sel_br:
            bs = ss[ss["brand"]==b]
            if bs.empty: continue
            with st.expander(f"[{b}] 시리즈별 요약 ({len(bs)}개)", expanded=False):
                to2 = bs[bs["diff"]>0].nlargest(3,"diff")
                tu2 = bs[bs["diff"]<0].nsmallest(3,"diff")
                c1s,c2s = st.columns(2)
                with c1s:
                    st.markdown("**🔵 초과 상위**")
                    for _,r in to2.iterrows():
                        st.markdown(f"- **{r['series']}**: {int(r['forecast']):,}→{int(r['actual']):,} "
                                    f"<span class='over'>(+{int(r['diff']):,})</span>", unsafe_allow_html=True)
                with c2s:
                    st.markdown("**🔴 미달 상위**")
                    for _,r in tu2.iterrows():
                        st.markdown(f"- **{r['series']}**: {int(r['forecast']):,}→{int(r['actual']):,} "
                                    f"<span class='under'>({int(r['diff']):,})</span>", unsafe_allow_html=True)
                if len(bs)>0:
                    figs = go.Figure(go.Bar(
                        x=bs["diff"], y=bs["series"].astype(str), orientation="h",
                        marker_color=[BC.get(b,"#58a6ff") if d>=0 else "#f85149" for d in bs["diff"]],
                        text=[f"{int(d):+,}" for d in bs["diff"]], textposition="outside"))
                    figs.add_vline(x=0, line_color="#30363d")
                    figs.update_layout(**PBG, height=max(180,len(bs)*24),
                                       xaxis=GRD, yaxis=dict(gridcolor="#21262d",autorange="reversed"),
                                       margin=dict(t=10,b=10,l=0,r=60))
                    st.plotly_chart(figs, use_container_width=True)
    else:
        st.info("실적 데이터가 있는 월을 선택하면 분석 내용이 표시됩니다.")

# ══ 탭5 : 전체 데이터 ═══════════════════════
with t5:
    st.markdown('<div class="section-header">전체 데이터 조회 및 다운로드</div>', unsafe_allow_html=True)

    all_mg = fc_base.merge(
        ac_base.groupby(["ym","brand","combo"])["actual"].sum().reset_index(),
        on=["ym","brand","combo"], how="left")
    all_mg["actual"]   = all_mg["actual"].fillna(0).astype(int)
    all_mg["차이량"]   = all_mg["actual"]-all_mg["forecast"]
    all_mg["달성률(%)"] = np.where(all_mg["forecast"]>0,
                                   (all_mg["actual"]/all_mg["forecast"]*100).round(1), np.nan)
    all_mg["년월"] = all_mg["ym"].map(lambda x: YMF.get(x,x))

    cd1,cd2,_ = st.columns([1,1,3])
    with cd1:
        buf = io.BytesIO(); all_mg.to_csv(buf, index=False, encoding="utf-8-sig")
        st.download_button("⬇️ 전체 CSV 다운로드", buf.getvalue(),
                           file_name="forecast_vs_actual_all.csv", mime="text/csv")
    with cd2:
        buf2 = io.BytesIO(); mg.to_csv(buf2, index=False, encoding="utf-8-sig")
        st.download_button(f"⬇️ {YMF.get(sel_ym,'현재월')} CSV", buf2.getvalue(),
                           file_name=f"forecast_{sel_ym}.csv", mime="text/csv")

    st.markdown(f'<div class="section-header">{YMF.get(sel_ym,sel_ym)} 품목 상세 ({len(mg)}개)</div>',
                unsafe_allow_html=True)
    dc = ["brand","series","combo","name","supply","forecast"]
    if has_act: dc += ["actual","diff","rate"]
    dm = mg[dc].copy()
    if has_act:
        dm["rate"] = dm["rate"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "-")
    rn2 = {"brand":"브랜드","series":"시리즈","combo":"코드조합","name":"품목명",
           "supply":"공급단","forecast":"수요예측","actual":"실수주","diff":"차이량","rate":"달성률"}
    dm.columns = [rn2.get(c,c) for c in dm.columns]
    if "차이량" in dm.columns:
        dm = dm.sort_values("차이량", key=abs, ascending=False)
    st.dataframe(dm, use_container_width=True, height=500)
