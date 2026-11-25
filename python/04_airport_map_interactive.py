import pandas as pd
import plotly.express as px

DATA = "data/processed/airport_concentration_as_reported.csv"
AIRPORTS = "data/external/airports.dat"
OUT = "figures/04_airport_map_interactive.html"

FONT = "Helvetica Neue, Arial, sans-serif"
INK, MUTED, BG = "#1F2937", "#6B7280", "#FFFFFF"

airports = pd.read_csv(
    AIRPORTS, header=None, na_values="\\N",
    usecols=[4, 6, 7], names=["airport", "lat", "lon"], index_col=False,
)

conc = pd.read_csv(DATA)
conc = conc[conc["enplanements"] >= 500_000].merge(airports, on="airport", how="inner")
conc = conc[(conc["lat"] > 24) & (conc["lat"] < 72) & (conc["lon"] > -170) & (conc["lon"] < -66)]
conc = conc.sort_values(["year", "enplanements"], ascending=[True, False])

conc["top_share_pct"] = (conc["top_share"] * 100).round(0)
conc["boardings_m"] = (conc["enplanements"] / 1e6).round(2)
conc["top_carrier"] = conc["top_carrier"].str.replace(
    r"\s+(Inc\.|Co\.|Corporation|Air Lines|Airlines|Air Lines Inc\.)$", "", regex=True
)

fig = px.scatter_geo(
    conc,
    lat="lat", lon="lon",
    size="enplanements", size_max=34,
    color="top_share",
    color_continuous_scale=[[0, "#CBD5E1"], [0.5, "#64748B"], [1, "#1E293B"]],
    range_color=(0.2, 1),
    animation_frame="year",
    scope="usa",
    hover_name="airport",
    custom_data=["city", "top_carrier", "top_share_pct", "boardings_m"],
)

fig.update_traces(
    marker=dict(line=dict(width=0.5, color=MUTED), opacity=0.9),
    hovertemplate=(
        "<b>%{hovertext}</b> (%{customdata[0]})<br>"
        "Largest airline: %{customdata[1]}<br>"
        "Its share of passengers: %{customdata[2]:.0f}%<br>"
        "Boardings per year: %{customdata[3]:.1f}M"
        "<extra></extra>"
    ),
)

for frame in fig.frames:
    for trace in frame.data:
        trace.hovertemplate = fig.data[0].hovertemplate
        trace.marker.line = dict(width=0.5, color=MUTED)
        trace.marker.opacity = 0.9

fig.update_geos(
    landcolor="#F3F4F6", bgcolor=BG, showlakes=False,
    subunitcolor="#D1D5DB", showsubunits=True,
)

fig.update_layout(
    title=dict(
        text="<b>Who dominates your airport?</b>"
             "<br><sup>Airports with at least 500,000 boardings a year. Drag the slider or press play to move through the years.</sup>",
        x=0.01, xanchor="left",
    ),
    paper_bgcolor=BG,
    font=dict(family=FONT, color=INK),
    coloraxis_colorbar=dict(
        title="Share held by<br>largest airline", tickformat=".0%",
        len=0.6, thickness=14,
    ),
    margin=dict(l=10, r=10, t=90, b=70),
    annotations=[dict(
        text="Source: U.S. Bureau of Transportation Statistics, T-100 Domestic Market (U.S. carriers); airport coordinates: OpenFlights. "
             "Marker size = passengers boarding per year.",
        x=0, y=-0.08, xref="paper", yref="paper", showarrow=False, xanchor="left",
        font=dict(size=11, color=MUTED),
    )],
    sliders=[dict(currentvalue=dict(prefix="Year: "))],
)

html = fig.to_html(include_plotlyjs=True, full_html=True)
assets = open("data/external/plotly-geo-assets.js", encoding="utf-8").read()
html = html.replace("<head>", "<head><script>" + assets + "</script>", 1)
open(OUT, "w", encoding="utf-8").write(html)