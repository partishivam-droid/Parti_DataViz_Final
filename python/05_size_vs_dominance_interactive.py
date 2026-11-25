import numpy as np
import pandas as pd
import plotly.express as px

DATA = "data/processed/airport_concentration_as_reported.csv"
OUT = "figures/05_size_vs_dominance_interactive.html"

FONT = "Helvetica Neue, Arial, sans-serif"
INK, MUTED, GRID, BG = "#1F2937", "#6B7280", "#E5E7EB", "#FFFFFF"

FAMILIES = [
    ("American", ("american airlines", "us airways", "usair", "america west", "trans world")),
    ("Delta", ("delta air", "northwest", "comair", "endeavor")),
    ("United", ("united air", "continental")),
    ("Southwest", ("southwest", "airtran")),
    ("Alaska", ("alaska airlines", "horizon air")),
    ("JetBlue", ("jetblue",)),
    ("Spirit", ("spirit",)),
    ("Frontier", ("frontier",)),
    ("Hawaiian", ("hawaiian",)),
    ("Several regional airlines (grouped)", ("regional (independent)",)),
]

COLOURS = {
    "American": "#D2232A", "Delta": "#0B2A57", "United": "#0A5DC2", "Southwest": "#F2A900",
    "Alaska": "#00A0AF", "JetBlue": "#5CB8E6", "Spirit": "#E5C200", "Frontier": "#2E8B57",
    "Hawaiian": "#6B3FA0",
    "Several regional airlines (grouped)": "#9CA3AF", "Others": "#D1D5DB",
}


def family(name):
    n = str(name).lower()
    for label, keys in FAMILIES:
        if any(k in n for k in keys):
            return label
    return "Others"


d = pd.read_csv(DATA)
d = d[d["enplanements"] >= 500_000].copy()
d["company"] = d["top_carrier"].map(family)
d["boardings_m"] = d["enplanements"] / 1e6
d["share_pct"] = (d["top_share"] * 100).round(0)
d["label"] = np.where(d.groupby("year")["enplanements"].rank(ascending=False) <= 12, d["airport"], "")
d["top_carrier_short"] = d["top_carrier"].str.replace(r"\s+(Inc\.|Co\.|Corporation)$", "", regex=True)

order = [c for c in COLOURS if c in d["company"].unique()]

fig = px.scatter(
    d.sort_values(["year", "enplanements"], ascending=[True, False]),
    x="boardings_m", y="top_share",
    color="company", color_discrete_map=COLOURS, category_orders={"company": order},
    animation_frame="year",
    text="label", hover_name="airport",
    custom_data=["city", "top_carrier_short", "share_pct", "boardings_m", "n_carriers"],
    log_x=True, range_x=[0.45, 70], range_y=[0, 1.05],
    labels={"company": "Largest airline at the airport"},
)

hover = (
    "<b>%{hovertext}</b> (%{customdata[0]})<br>"
    "Largest airline: %{customdata[1]}<br>"
    "Its share of passengers: %{customdata[2]:.0f}%<br>"
    "Boardings per year: %{customdata[3]:.1f}M<br>"
    "Airlines serving the airport: %{customdata[4]}"
    "<extra></extra>"
)

def style(trace):
    trace.update(
        marker=dict(size=11, opacity=0.9, line=dict(width=0.8, color=MUTED)),
        textposition="top center", textfont=dict(size=10, color=INK),
        hovertemplate=hover, mode="markers+text",
    )

fig.for_each_trace(style)
for frame in fig.frames:
    for trace in frame.data:
        style(trace)

fig.add_hline(y=0.5, line=dict(color=MUTED, width=1, dash="dash"))
fig.add_annotation(x=1, xref="paper", y=0.5, text="Half of all passengers", showarrow=False,
                   xanchor="right", yanchor="bottom", font=dict(size=10.5, color=MUTED))

fig.update_layout(
    title=dict(
        text="<b>Do bigger airports have more competition?</b>"
             "<br><sup>Each dot is an airport. Higher on the chart means one airline carries more of its passengers. "
             "Press play or drag the year slider; hover for details.</sup>",
        x=0.01, xanchor="left", y=0.97, yanchor="top",
    ),
    height=720,
    paper_bgcolor=BG, plot_bgcolor=BG,
    font=dict(family=FONT, color=INK),
    xaxis=dict(
        title="Passengers boarding per year (millions, log scale)",
        tickvals=[0.5, 1, 2, 5, 10, 20, 50], ticktext=["0.5M", "1M", "2M", "5M", "10M", "20M", "50M"],
        gridcolor=GRID,
    ),
    yaxis=dict(title="Share of passengers on the largest airline", tickformat=".0%", gridcolor=GRID),
    legend=dict(title="Largest airline at the airport", orientation="h", x=0, y=-0.28, yanchor="top"),
    margin=dict(l=70, r=20, t=125, b=170),
    sliders=[dict(currentvalue=dict(prefix="Year: "), pad=dict(t=40))],
    annotations=list(fig.layout.annotations) + [dict(
        text="Source: U.S. Bureau of Transportation Statistics, T-100 Domestic Market (U.S. carriers)."
             "<br>Airports with at least 500,000 boardings a year. Airlines are counted separately until they merged. "
             "Grey dots are airports where the largest group is several independent regional airlines combined.",
        x=0, y=-0.43, xref="paper", yref="paper", showarrow=False, xanchor="left", yanchor="top", align="left",
        font=dict(size=10.5, color=MUTED),
    )],
)

fig.write_html(OUT, include_plotlyjs=True, full_html=True, auto_play=False)