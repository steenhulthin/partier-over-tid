from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from shiny import App, render, ui


APP_DIR = Path(__file__).parent
DATA_PATH = APP_DIR / "data" / "folketing_partier_over_tid.csv"

df = pd.read_csv(DATA_PATH, parse_dates=["election_date", "next_election_date"])
df["election_year"] = df["election_date"].dt.year
df["label"] = df["election_date"].dt.strftime("%Y-%m-%d")

SOURCE_TEXT = (
    "Kilde: Danmarks Statistik, temaet Folketingsvalg samt historiske oversigter i Statistisk Aarbog. "
    "Note: Ved folketingsvalget 1994 blev Jacob Haugaard valgt uden for partierne og er ikke talt med som parti."
)


app_ui = ui.page_fillable(
    ui.tags.head(
        ui.tags.script(src="https://cdn.plot.ly/plotly-2.35.2.min.js")
    ),
    ui.tags.style(
        """
        :root {
            --bg: #f7f2e8;
            --panel: #fffaf0;
            --ink: #1d2b2a;
            --accent: #bc4b32;
            --accent-soft: #e6b17e;
            --grid: #d9cdbd;
        }
        body {
            background:
                radial-gradient(circle at top left, rgba(230, 177, 126, 0.28), transparent 32%),
                linear-gradient(180deg, #f9f4eb 0%, #f2eadb 100%);
            color: var(--ink);
            font-family: Georgia, "Times New Roman", serif;
        }
        .app-shell {
            max-width: 1100px;
            margin: 0 auto;
            padding: 1.25rem 1.1rem 2rem;
        }
        .app-title {
            margin-bottom: 0.2rem;
            font-size: 2.2rem;
            letter-spacing: 0.01em;
        }
        .app-subtitle {
            margin-top: 0;
            margin-bottom: 1.2rem;
            max-width: 70ch;
            line-height: 1.5;
            color: #514d45;
        }
        .shiny-card {
            background: rgba(255, 250, 240, 0.92);
            border: 1px solid rgba(188, 75, 50, 0.14);
            box-shadow: 0 18px 38px rgba(61, 41, 24, 0.08);
            border-radius: 18px;
            overflow: hidden;
        }
        .card-header {
            background: transparent;
            border-bottom: 1px solid rgba(188, 75, 50, 0.1);
            font-weight: 700;
            letter-spacing: 0.02em;
        }
        .source-note {
            margin: 0;
            padding: 0.2rem 1rem 1rem;
            color: #5b544b;
            font-size: 0.93rem;
            line-height: 1.45;
        }
        """
    ),
    ui.div(
        {"class": "app-shell"},
        ui.h1("Partier i Folketinget ved valg", class_="app-title"),
        ui.p(
            "Tidsserien viser antal partier ved hvert folketingsvalg. Nederst ses sammenhaengen mellem "
            "valgperiodens laengde og antallet af partier ved valget. Sidste observation bruger "
            "2026-03-24 som foreloebig naeste valgdato.",
            class_="app-subtitle",
        ),
        ui.layout_column_wrap(
            ui.card(
                ui.card_header("Udvikling over tid"),
                ui.output_ui("timeline_plot"),
                ui.p(SOURCE_TEXT, class_="source-note"),
                full_screen=True,
            ),
            ui.card(
                ui.card_header("Valgperiode i dage og antal partier"),
                ui.output_ui("scatter_plot"),
                ui.p(SOURCE_TEXT, class_="source-note"),
                full_screen=True,
            ),
            width=1,
            gap="1rem",
        ),
    ),
)


def _common_layout(title: str) -> dict:
    return {
        "title": {"text": title, "x": 0, "xanchor": "left"},
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "#fffaf0",
        "font": {"family": 'Georgia, "Times New Roman", serif', "color": "#1d2b2a"},
        "margin": {"l": 60, "r": 24, "t": 60, "b": 56},
        "hoverlabel": {"bgcolor": "#fffaf0", "font": {"color": "#1d2b2a"}},
    }


def _plotly_div(fig: go.Figure, height: int) -> ui.Tag:
    fig.update_layout(height=height)
    return ui.HTML(
        fig.to_html(
            full_html=False,
            include_plotlyjs=False,
            config={"responsive": True, "displayModeBar": False},
        )
    )


def server(input, output, session):
    @output
    @render.ui
    def timeline_plot():
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["election_date"],
                y=df["parties_in_folketing"],
                mode="lines+markers+text",
                text=[
                    f"{year}: {parties}" if year in {1945, 1973, 1977, 2022} else ""
                    for year, parties in zip(df["election_year"], df["parties_in_folketing"])
                ],
                textposition="top center",
                line={"color": "#bc4b32", "width": 3},
                marker={
                    "size": 9,
                    "color": "#fffaf0",
                    "line": {"color": "#bc4b32", "width": 2},
                },
                fill="tozeroy",
                fillcolor="rgba(230, 177, 126, 0.22)",
                customdata=df[["days_to_next_election", "note"]].fillna("").values,
                hovertemplate=(
                    "<b>Valg:</b> %{x|%Y-%m-%d}<br>"
                    "<b>Partier:</b> %{y}<br>"
                    "<b>Dage til naeste valg:</b> %{customdata[0]}<br>"
                    "<b>Note:</b> %{customdata[1]}<extra></extra>"
                ),
            )
        )
        fig.update_layout(**_common_layout("Antal partier ved folketingsvalg"))
        fig.update_xaxes(
            title="Valgdato",
            showgrid=False,
            tickformat="%Y",
            dtick="M60",
            linecolor="#a89b8d",
        )
        fig.update_yaxes(
            title="Partier",
            tickmode="linear",
            dtick=1,
            rangemode="tozero",
            gridcolor="#d9cdbd",
            linecolor="#a89b8d",
        )
        return _plotly_div(fig, 420)

    @output
    @render.ui
    def scatter_plot():
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["days_to_next_election"],
                y=df["parties_in_folketing"],
                mode="markers+text",
                text=df["election_year"].astype(str),
                textposition="top center",
                marker={
                    "size": 13,
                    "color": df["election_year"],
                    "colorscale": [
                        [0.0, "#e6b17e"],
                        [0.5, "#bc4b32"],
                        [1.0, "#5e3023"],
                    ],
                    "line": {"color": "#6f3b26", "width": 1},
                    "showscale": False,
                },
                customdata=df[["label", "note"]].fillna("").values,
                hovertemplate=(
                    "<b>Valg:</b> %{customdata[0]}<br>"
                    "<b>Dage til naeste valg:</b> %{x}<br>"
                    "<b>Partier:</b> %{y}<br>"
                    "<b>Note:</b> %{customdata[1]}<extra></extra>"
                ),
            )
        )
        fig.update_layout(**_common_layout("Valgperiodens laengde og antal partier"))
        fig.update_xaxes(
            title="Dage til naeste valg",
            gridcolor="#d9cdbd",
            linecolor="#a89b8d",
        )
        fig.update_yaxes(
            title="Partier ved valget",
            tickmode="linear",
            dtick=1,
            rangemode="tozero",
            linecolor="#a89b8d",
        )
        return _plotly_div(fig, 460)


app = App(app_ui, server)
