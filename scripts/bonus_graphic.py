import json
import pandas as pd

CONC = "data/processed/airport_concentration_as_reported.csv"
D3 = "data/external/d3.v7.min.js"
OUT = "figures/07_airport_migration_bonus.html"

AIRLINES = {
    "American": "#D2232A", "US Airways": "#DD5A5F", "America West": "#E89194", "TWA": "#F2C1C3",
    "Delta": "#0B2A57", "Northwest": "#607592",
    "United": "#0A5DC2", "Continental": "#78A6DD",
    "Southwest": "#F2A900", "AirTran": "#F8D480",
    "Alaska": "#00A0AF", "Virgin America": "#7FD0D7",
    "JetBlue": "#5CB8E6", "Spirit": "#E5C200", "Frontier": "#2E8B57", "Hawaiian": "#6B3FA0",
    "Regionals": "#9CA3AF", "Other airlines": "#D1D5DB",
}
RULES = [
    ("american airlines", "American"), ("us airways", "US Airways"), ("usair", "US Airways"),
    ("america west", "America West"), ("trans world", "TWA"),
    ("delta air", "Delta"), ("northwest", "Northwest"),
    ("united air", "United"), ("continental air", "Continental"),
    ("southwest", "Southwest"), ("airtran", "AirTran"),
    ("alaska airlines", "Alaska"), ("virgin america", "Virgin America"),
    ("jetblue", "JetBlue"), ("spirit air", "Spirit"), ("frontier", "Frontier"), ("lynx", "Frontier"),
    ("hawaiian airlines", "Hawaiian"), ("regional (independent)", "Independent regionals"),
]


def airline_of(name):
    n = str(name).lower()
    for key, label in RULES:
        if key in n:
            return label
    return "Other airlines"


conc = pd.read_csv(CONC)
y0 = conc["year"].min()
fixed = conc[(conc["year"] == y0) & (conc["enplanements"] >= 500_000)]["airport"].unique()
c = conc[conc["airport"].isin(fixed)].copy()
c["airline"] = c["top_carrier"].map(airline_of)
years = [int(y) for y in sorted(c["year"].unique())]

rows = []
for code, g in c.groupby("airport"):
    g = g.drop_duplicates("year").set_index("year")
    h = [[round(float(g.loc[y, "top_share"]), 4), g.loc[y, "airline"], float(g.loc[y, "enplanements"])]
         if y in g.index else None for y in years]
    rows.append(dict(a=code, city=str(g["city"].iloc[0]), h=h,
                     peak=max(x[2] for x in h if x)))
big = {r["a"] for r in sorted(rows, key=lambda r: -r["peak"])[:12]}
for r in rows:
    r["big"] = r["a"] in big
    del r["peak"]

TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Airport migration</title>
<style>
body{margin:0;background:#FFFFFF;color:#1F2937;font-family:"Helvetica Neue",Arial,sans-serif}
.wrap{max-width:900px;margin:0 auto;padding:10px 12px}
h1{font-size:19px;margin:0 0 4px}
p.sub{margin:0 0 10px;color:#6B7280;font-size:13px;line-height:1.4}
#ctl{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-bottom:6px}
button{font:inherit;font-size:13px;padding:5px 10px;border:1px solid #D1D5DB;background:#fff;color:#1F2937;border-radius:4px;cursor:pointer}
button.on{background:#1F2937;color:#fff;border-color:#1F2937}
#note{font-size:13px;min-height:18px;margin:2px 0 4px}
.src{font-size:11px;color:#6B7280;margin-top:6px;line-height:1.4}
#tip{position:fixed;pointer-events:none;background:#fff;border:1px solid #D1D5DB;padding:6px 8px;font-size:12px;border-radius:4px;display:none;max-width:270px;box-shadow:0 1px 4px rgba(0,0,0,.12);line-height:1.4}
svg{width:100%;height:auto;display:block}
</style></head><body><div class="wrap">
<h1>Did the same airports recover?</h1>
<p class="sub">Each dot is one of the 99 airports that had at least 500,000 boardings in 2000, followed through time. Dots sort into columns by how much of the airport's traffic the largest airline carries. If you use the widgets, the outlined dots changed column since the previous year shown. Dot size = boardings per year. Hover for details.</p>
<div id="ctl"></div><div id="note"></div><div id="chart"></div>
<div class="src">Source: U.S. Bureau of Transportation Statistics, T-100 Domestic Market (U.S. carriers); author's calculations. Largest airline is shown as reported in each year, so merged carriers appear under their old names until the merger. Airports without data in a year are hidden.</div>
</div><div id="tip"></div>
<script>__D3__</script>
<script>(()=>{
const D=__DATA__, COL=__COLORS__, INK="#1F2937", MUTED="#6B7280";
const years=D.years, rows=D.rows;
const W=900,H=520,top=76,bot=H-14,cx=[160,450,740],bw=270;
const bands=[["Competitive","largest airline under 40%"],["Mixed","largest airline 40% to 60%"],["Dominated","largest airline over 60%"]];
const bandOf=s=>s<0.4?0:(s<=0.6?1:2);
const pl=n=>n+(n===1?" airport":" airports");
const svg=d3.select("#chart").append("svg").attr("viewBox",`0 0 ${W} ${H+70}`)
  .attr("role","img").attr("aria-label","Airports sorted into competitive, mixed and dominated columns by year");
bands.forEach((b,k)=>{
  svg.append("rect").attr("x",cx[k]-bw/2).attr("y",top).attr("width",bw).attr("height",bot-top).attr("rx",6).attr("fill","#F3F4F6");
  svg.append("text").attr("x",cx[k]).attr("y",18).attr("text-anchor","middle").attr("font-weight","bold").attr("font-size",15).attr("fill",INK).text(b[0]);
  svg.append("text").attr("x",cx[k]).attr("y",35).attr("text-anchor","middle").attr("font-size",11.5).attr("fill",MUTED).text(b[1]);
  svg.append("text").attr("id","cnt"+k).attr("x",cx[k]).attr("y",58).attr("text-anchor","middle").attr("font-size",13).attr("fill",INK);
});
const maxE=d3.max(rows,r=>d3.max(r.h,d=>d?d[2]:0));
const rs=d3.scaleSqrt().domain([5e5,maxE]).range([4,15]).clamp(true);
const nodes=rows.map(r=>({...r,x:cx[1]+(Math.random()-.5)*60,y:(top+bot)/2+(Math.random()-.5)*60,r:0,tx:cx[1],d:null,moved:false}));
const g=svg.append("g").selectAll("g").data(nodes).join("g");
const circ=g.append("circle").attr("r",0).attr("opacity",0);
const lab=g.filter(d=>d.big).append("text").attr("text-anchor","middle").attr("font-size",10).attr("fill",INK).attr("pointer-events","none").text(d=>d.a);
const used=Array.from(new Set(nodes.flatMap(n=>n.h.filter(Boolean).map(x=>x[1])))).sort((a,b)=>Object.keys(COL).indexOf(a)-Object.keys(COL).indexOf(b));
const lg=svg.append("g");
used.forEach((u,i)=>{
  const x=10+(i%7)*126,y=H+20+Math.floor(i/7)*20;
  lg.append("circle").attr("cx",x+5).attr("cy",y).attr("r",5).attr("fill",COL[u]||"#D1D5DB").attr("stroke",MUTED).attr("stroke-width",.6);
  lg.append("text").attr("x",x+15).attr("y",y+4).attr("font-size",11.5).attr("fill",INK).text(u);
});
svg.append("text").attr("x",10).attr("y",H+6).attr("font-size",11.5).attr("fill",MUTED).text("Largest airline at the airport:");
function tick(){
  g.attr("transform",d=>{d.y=Math.max(top+d.r+2,Math.min(bot-d.r-2,d.y));return `translate(${d.x},${d.y})`;});
  lab.attr("y",d=>-d.r-3);
}
const sim=d3.forceSimulation(nodes).stop().alphaDecay(.03).velocityDecay(.4)
  .force("y",d3.forceY((top+bot)/2).strength(.05)).on("tick",tick);
let cur=0,timer=null;
function show(i){
  cur=i;const prev=i>0?i-1:null;let up=0,down=0;const cnt=[0,0,0];
  nodes.forEach(n=>{
    const d=n.h[i];n.d=d;n.r=d?rs(d[2]):0;n.moved=false;
    if(d){const b=bandOf(d[0]);cnt[b]++;n.tx=cx[b];
      if(prev!==null&&n.h[prev]){const pb=bandOf(n.h[prev][0]);if(b!==pb){n.moved=true;b>pb?up++:down++;}}
    }else n.tx=n.x;
  });
  const tot=d3.sum(cnt);
  cnt.forEach((c,k)=>d3.select("#cnt"+k).text(`${pl(c)} (${Math.round(100*c/tot)}%)`));
  d3.select("#note").text(prev===null
    ? `${years[i]}: starting point. All ${rows.length} airports are shown.`
    : `${years[i]}: since ${years[prev]}, ${pl(down)} became less concentrated and ${pl(up)} more concentrated (outlined dots).`);
  circ.transition().duration(600)
    .attr("r",d=>d.r).attr("opacity",d=>d.d?.95:0)
    .attr("fill",d=>d.d?(COL[d.d[1]]||"#D1D5DB"):"#fff")
    .attr("stroke",d=>d.moved?INK:MUTED).attr("stroke-width",d=>d.moved?2.4:.6);
  lab.transition().duration(600).attr("opacity",d=>d.d?1:0);
  sim.force("x",d3.forceX(d=>d.tx).strength(.14)).force("c",d3.forceCollide(d=>d.r+1.4).strength(.9));
  sim.alpha(.9).restart();
  d3.selectAll("#ctl .yr").classed("on",(d,j)=>j===i);
}
const ctl=d3.select("#ctl");
const play=ctl.append("button").text("Play").on("click",()=>{
  if(timer){stop();return;}
  play.text("Pause");let i=cur>=years.length-1?-1:cur;
  const step=()=>{i++;show(i);if(i>=years.length-1)stop();};
  step();timer=setInterval(step,1900);
});
function stop(){clearInterval(timer);timer=null;play.text("Play");}
ctl.selectAll(".yr").data(years).join("button").attr("class","yr").text(d=>d).on("click",(e,d)=>{stop();show(years.indexOf(d));});
const tip=d3.select("#tip");
g.on("mousemove",(e,d)=>{
  if(!d.d){tip.style("display","none");return;}
  const hist=d.h.map((x,j)=>x?`${years[j]}: ${Math.round(x[0]*100)}%`:null).filter(Boolean).join(" · ");
  tip.style("display","block").style("left",(e.clientX+14)+"px").style("top",(e.clientY+14)+"px")
    .html(`<b>${d.a}</b> (${d.city})<br>${years[cur]}: ${d.d[1]}, ${Math.round(d.d[0]*100)}% of passengers<br>${(d.d[2]/1e6).toFixed(1)}M boardings<br><span style="color:#6B7280">Largest airline's share over time:<br>${hist}</span>`);
}).on("mouseleave",()=>tip.style("display","none"));
show(0);
})();
</script></body></html>"""

html = (TEMPLATE
        .replace("__DATA__", json.dumps(dict(years=years, rows=rows)))
        .replace("__COLORS__", json.dumps(AIRLINES))
        .replace("__D3__", open(D3, encoding="utf-8").read()))
open(OUT, "w", encoding="utf-8").write(html)
print("wrote", OUT, "|", len(rows), "airports |", years)