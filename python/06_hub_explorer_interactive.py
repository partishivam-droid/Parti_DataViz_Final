import pathlib
import webbrowser

import pandas as pd
import plotly.graph_objects as go

SHARES = "data/processed/airport_carrier_shares_as_reported.csv"
CONC = "data/processed/airport_concentration_as_reported.csv"
OUT = "figures/06_hub_explorer_interactive.html"
N_AIRPORTS = 30
DEFAULT_AIRPORT = "CLT"

AIRLINES = {
    "American": "#D2232A", "US Airways": "#DD5A5F", "America West": "#E89194", "TWA": "#F2C1C3",
    "Delta": "#0B2A57", "Northwest": "#607592",
    "United": "#0A5DC2", "Continental": "#78A6DD",
    "Southwest": "#F2A900", "AirTran": "#F8D480",
    "Alaska": "#00A0AF", "Virgin America": "#7FD0D7",
    "JetBlue": "#5CB8E6", "Spirit": "#E5C200", "Frontier": "#2E8B57", "Hawaiian": "#6B3FA0",
    "Independent regionals": "#9CA3AF", "Other airlines": "#D1D5DB",
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


shares = pd.read_csv(SHARES)
shares["airline"] = shares["carrier"].map(airline_of)
shares = shares.groupby(["year", "airport", "airline"], as_index=False)["share"].sum()

conc = pd.read_csv(CONC)
latest = conc[conc["year"] == conc["year"].max()].sort_values("enplanements", ascending=False)
airports = latest.head(N_AIRPORTS)[["airport", "city"]].reset_index(drop=True)
years = sorted(shares["year"].unique())
order = list(AIRLINES)


def wide(code):
    w = (shares[shares["airport"] == code]
         .pivot(index="year", columns="airline", values="share")
         .reindex(index=years, columns=order))
    return w


def headline(code, city):
    w = wide(code).fillna(0)
    first, last = w.iloc[0], w.iloc[-1]
    return (f"{city}: largest airline was {first.idxmax()} ({first.max():.0%}) in {years[0]}, "
            f"{last.idxmax()} ({last.max():.0%}) in {years[-1]}")


def title(code, city):
    return (f"<b>Who carries the passengers at {code}?</b>"
            f"<br><sup>{headline(code, city)}. Pick another airport from the menu; hover for each year's shares.</sup>")


frames = {row.airport: wide(row.airport).where(lambda x: x >= 0.003) for row in airports.itertuples()}
start = DEFAULT_AIRPORT if DEFAULT_AIRPORT in frames else airports["airport"].iloc[0]
start_city = airports.set_index("airport").loc[start, "city"]

fig = go.Figure()
for airline in order:
    fig.add_trace(go.Scatter(
        x=years, y=frames[start][airline], name=airline, stackgroup="one", mode="lines",
        line=dict(width=0.8, color="white"), fillcolor=AIRLINES[airline],
        hovertemplate="<b>%{fullData.name}</b>: %{y:.0%}<extra></extra>",
    ))

buttons = []
for row in airports.itertuples():
    ys = [frames[row.airport][a].tolist() for a in order]
    buttons.append(dict(
        label=f"{row.airport} - {row.city}", method="update",
        args=[{"y": ys}, {"title.text": title(row.airport, row.city)}],
    ))

fig.update_layout(
    title=dict(text=title(start, start_city), x=0.01, xanchor="left", y=0.97, yanchor="top"),
    height=720,
    paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
    font=dict(color="#1F2937"),
    hovermode="x unified",
    xaxis=dict(tickmode="array", tickvals=years, showgrid=False, range=[min(years), max(years)]),
    yaxis=dict(title="Share of the airport's passengers", tickformat=".0%", range=[0, 1], gridcolor="#E5E7EB"),
    legend=dict(title="Airline", x=1.01, y=1, traceorder="reversed"),
    margin=dict(l=70, r=20, t=140, b=120),
    updatemenus=[dict(
        type="dropdown", buttons=buttons, active=int(airports.index[airports["airport"] == start][0]),
        x=0.01, y=1.0, xanchor="left", yanchor="bottom", bgcolor="white", bordercolor="#D1D5DB",
    )],
    annotations=[dict(
        text="Source: U.S. Bureau of Transportation Statistics, T-100 Domestic Market (U.S. carriers)."
             "<br>The 30 busiest airports in the latest year. Sample years only. Airlines are counted separately until they merged; "
             "owned regional carriers are counted with their parent."
             "<br>Independent regionals are several airlines grouped together. Shares under 0.3% are not shown.",
        x=0, y=-0.1, xref="paper", yref="paper", showarrow=False, xanchor="left", yanchor="top", align="left",
        font=dict(size=10.5, color="#6B7280"),
    )],
)

fig.write_html(OUT, include_plotlyjs="True", full_html=True)