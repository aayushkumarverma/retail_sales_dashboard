import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(page_title="RetailIQ | Sales Intelligence", page_icon="📊", layout="wide")
REQ=["Date","OrderID","Product","Category","Quantity","Unit Price","Unit Cost","Discount"]

@st.cache_data
def load_data(file):
    d=pd.read_csv(file)
    missing=[c for c in REQ if c not in d.columns]
    if missing: raise ValueError("Missing columns: "+", ".join(missing))
    d["Date"]=pd.to_datetime(d["Date"],errors="coerce")
    for c in ["Quantity","Unit Price","Unit Cost","Discount"]: d[c]=pd.to_numeric(d[c],errors="coerce")
    d=d.dropna(subset=REQ)
    d["Revenue"]=d.Quantity*d["Unit Price"]*(1-d.Discount/100)
    d["Cost"]=d.Quantity*d["Unit Cost"]
    d["Profit"]=d.Revenue-d.Cost
    d["Margin"]=d.Profit.div(d.Revenue.where(d.Revenue!=0)).fillna(0)*100
    d["Month"]=d.Date.dt.to_period("M").astype(str)
    return d

def rupee(x): return f"₹{x:,.0f}"
def style():
    plt.rcParams.update({"figure.facecolor":"#111827","axes.facecolor":"#111827","axes.edgecolor":"#334155","axes.labelcolor":"#cbd5e1","xtick.color":"#cbd5e1","ytick.color":"#cbd5e1","text.color":"#f8fafc","grid.color":"#334155"})

st.markdown("""<style>
.stApp{background:#0b1120;color:#e5e7eb}
[data-testid="stSidebar"]{background:#111827;border-right:1px solid #263449}
.block-container{padding-top:2rem;max-width:1500px}
.hero{padding:25px 28px;border:1px solid #263449;border-radius:18px;background:linear-gradient(120deg,#172554,#111827 60%,#164e63);margin-bottom:22px}
.eyebrow{color:#67e8f9;letter-spacing:2px;font-size:11px;font-weight:700}
.hero p{color:#cbd5e1;margin:0}
div[data-testid="stMetric"]{background:#111c2e;border:1px solid #263449;padding:15px;border-radius:14px}
</style>""",unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 📊 RetailIQ")
    st.caption("Sales Intelligence Suite")
    page=st.radio("WORKSPACE",["Overview","Sales Analytics","Loss & Slow-Mover Detector","Profit Simulator","Data Explorer"])
    st.divider()
    upload=st.file_uploader("Upload sales CSV",type=["csv"])
    st.caption("Required: Date, OrderID, Product, Category, Quantity, Unit Price, Unit Cost, Discount")

source=upload if upload else Path(__file__).with_name("sales.csv")
try: df=load_data(source)
except Exception as e: st.error(str(e)); st.stop()
if df.empty: st.warning("No valid records in this file."); st.stop()

st.markdown('<div class="hero"><div class="eyebrow">RETAIL PERFORMANCE WORKSPACE</div><h1>Retail Sales Intelligence</h1><p>Understand performance. Detect hidden risks. Make better pricing decisions.</p></div>',unsafe_allow_html=True)

if page=="Overview":
    st.subheader("Business at a glance")
    st.caption(f"{len(df):,} sales records · {df.Date.min():%d %b %Y} – {df.Date.max():%d %b %Y}")
    a,b,c,d=st.columns(4)
    a.metric("Total revenue",rupee(df.Revenue.sum()))
    b.metric("Total profit",rupee(df.Profit.sum()))
    c.metric("Units sold",f"{df.Quantity.sum():,.0f}")
    d.metric("Average margin",f"{df.Margin.mean():.1f}%")
    l,r=st.columns([1.5,1])
    style()
    with l:
        st.markdown("### Revenue over time")
        m=df.groupby("Month").Revenue.sum()
        fig,ax=plt.subplots(figsize=(8,3.2)); m.plot(ax=ax,marker="o",color="#22d3ee",linewidth=2.5)
        ax.set_ylabel("Revenue (₹)"); ax.grid(alpha=.25); ax.tick_params(axis="x",rotation=25); fig.tight_layout()
        st.pyplot(fig,use_container_width=True); plt.close(fig)
    with r:
        st.markdown("### Revenue by category")
        x=df.groupby("Category").Revenue.sum().sort_values()
        fig,ax=plt.subplots(figsize=(5,3.2)); x.plot(kind="barh",ax=ax,color="#818cf8")
        ax.set_xlabel("Revenue (₹)"); ax.grid(axis="x",alpha=.25); fig.tight_layout()
        st.pyplot(fig,use_container_width=True); plt.close(fig)
    st.markdown("### Top products")
    t=df.groupby("Product").agg(Revenue=("Revenue","sum"),Profit=("Profit","sum"),Units=("Quantity","sum")).sort_values("Revenue",ascending=False).head(5)
    st.dataframe(t.style.format({"Revenue":"₹{:,.2f}","Profit":"₹{:,.2f}","Units":"{:,.0f}"}),use_container_width=True)

elif page=="Sales Analytics":
    st.subheader("Sales Analytics")
    c1,c2=st.columns(2)
    cat=c1.selectbox("Category",["All"]+sorted(df.Category.unique()))
    prod=c2.selectbox("Product",["All"]+sorted(df.Product.unique()))
    v=df.copy()
    if cat!="All": v=v[v.Category==cat]
    if prod!="All": v=v[v.Product==prod]
    a,b,c=st.columns(3); a.metric("Revenue",rupee(v.Revenue.sum())); b.metric("Profit",rupee(v.Profit.sum())); c.metric("Units",f"{v.Quantity.sum():,.0f}")
    l,r=st.columns(2); style()
    with l:
        st.markdown("#### Monthly revenue")
        fig,ax=plt.subplots(figsize=(6,3.2)); v.groupby("Month").Revenue.sum().plot(ax=ax,marker="o",color="#22d3ee")
        ax.set_ylabel("Revenue (₹)"); ax.grid(alpha=.25); ax.tick_params(axis="x",rotation=25); fig.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close(fig)
    with r:
        st.markdown("#### Profit by category")
        fig,ax=plt.subplots(figsize=(6,3.2)); v.groupby("Category").Profit.sum().sort_values().plot(kind="bar",ax=ax,color="#34d399")
        ax.set_ylabel("Profit (₹)"); ax.grid(axis="y",alpha=.25); fig.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close(fig)
    table=v.groupby(["Product","Category"]).agg(Units=("Quantity","sum"),Revenue=("Revenue","sum"),Profit=("Profit","sum"),Avg_Margin=("Margin","mean")).reset_index().sort_values("Revenue",ascending=False)
    st.dataframe(table.style.format({"Revenue":"₹{:,.2f}","Profit":"₹{:,.2f}","Avg_Margin":"{:.1f}%"}),use_container_width=True)

elif page=="Loss & Slow-Mover Detector":
    st.subheader("Silent Loss & Slow-Mover Detector")
    st.write("Identify low-margin products, discount pressure and falling sales momentum.")
    p=df.groupby("Product").agg(Category=("Category","first"),Units=("Quantity","sum"),Revenue=("Revenue","sum"),Profit=("Profit","sum"),Margin=("Margin","mean"),Avg_Discount=("Discount","mean")).reset_index()
    p["Risk"]=p.apply(lambda x:"Low margin" if x.Margin<10 else ("Discount pressure" if x.Avg_Discount>=20 and x.Margin<15 else "Healthy"),axis=1)
    months=sorted(df.Month.unique())
    if len(months)>=4:
        recent=df[df.Month.isin(months[-2:])].groupby("Product").Quantity.sum()
        prior=df[df.Month.isin(months[-4:-2])].groupby("Product").Quantity.sum()
        trend=pd.concat([prior.rename("Previous units"),recent.rename("Recent units")],axis=1).fillna(0)
        trend["Change %"]=(trend["Recent units"]-trend["Previous units"])/trend["Previous units"].replace(0,pd.NA)*100
        p=p.merge(trend,left_on="Product",right_index=True,how="left")
        p[["Previous units","Recent units","Change %"]]=p[["Previous units","Recent units","Change %"]].fillna(0)
        p.loc[p["Change %"]<=-40,"Risk"]="Sales declining"
    else:
        p["Previous units"]=0;p["Recent units"]=0;p["Change %"]=0
        st.info("Four distinct months are required to compare two recent months with the previous two.")
    flagged=p[p.Risk!="Healthy"].sort_values("Margin")
    a,b,c=st.columns(3);a.metric("Products analysed",len(p));b.metric("Products flagged",len(flagged));c.metric("Healthy products",len(p)-len(flagged))
    if flagged.empty: st.success("No risk flags detected with these thresholds.")
    else:
        st.warning("Flags are indicators for review, not proof of actual inventory loss.")
        st.dataframe(flagged.style.format({"Revenue":"₹{:,.2f}","Profit":"₹{:,.2f}","Margin":"{:.1f}%","Avg_Discount":"{:.1f}%","Change %":"{:.1f}%"}),use_container_width=True)
    with st.expander("Detection logic"):
        st.markdown("- Low margin: average margin below 10%.\n- Discount pressure: average discount at least 20% and margin below 15%.\n- Sales declining: latest two months' units are at least 40% below the previous two months.\n\nNo stock-on-hand field is available, so this detects sales slowdowns—not confirmed unsold stock.")

elif page=="Profit Simulator":
    st.subheader("What-If Profit Simulator")
    st.write("Change a product's price and discount to estimate the impact on profit.")
    product=st.selectbox("Select product",sorted(df.Product.unique()))
    p=df[df.Product==product]; avg_price=float(p["Unit Price"].mean()); cost=float(p["Unit Cost"].mean()); disc=float(p.Discount.mean()); units=float(p.Quantity.sum())
    price=st.number_input("Proposed unit selling price (₹)",min_value=0.0,value=round(avg_price,2),step=1.0)
    discount=st.slider("Proposed discount (%)",0,80,min(80,int(round(disc))))
    revenue=units*price*(1-discount/100); profit=revenue-units*cost; old=float(p.Profit.sum())
    a,b,c=st.columns(3);a.metric("Estimated revenue",rupee(revenue));b.metric("Estimated profit",rupee(profit),f"{rupee(profit-old)} vs current");c.metric("Estimated margin",f"{profit/revenue*100 if revenue else 0:.1f}%")
    st.caption(f"Based on {units:,.0f} historical units and average unit cost {rupee(cost)}.")
    if profit<0: st.error("This scenario estimates a loss before overheads.")
    elif profit>=old: st.success("Estimated profit is higher than the historical result.")
    else: st.warning("Estimated profit is lower than the historical result.")
    st.info("Assumes sales volume remains unchanged. This is a scenario estimate, not a demand forecast. Taxes and operating overheads are excluded.")

else:
    st.subheader("Data Explorer")
    st.caption("Inspect calculated values and export the processed dataset.")
    st.dataframe(df,use_container_width=True,hide_index=True)
    st.download_button("⬇ Download processed CSV",df.to_csv(index=False).encode(), "retail_sales_processed.csv","text/csv")
    st.markdown("### Dataset summary")
    st.dataframe(df.describe(include="all").transpose(),use_container_width=True)
