import csv
import json
from pathlib import Path

from shiny import App, render, ui


APP_DIR = Path(__file__).parent
DATA_PATH = APP_DIR / "data" / "folketing_partier_over_tid.csv"


def load_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        row["parties_in_folketing"] = int(row["parties_in_folketing"])
        row["days_to_next_election"] = int(row["days_to_next_election"])
        row["election_year"] = int(row["election_date"][:4])
        row["label"] = row["election_date"]
        row["note"] = row["note"] or ""
    return rows


ROWS = load_rows(DATA_PATH)

ELECTION_DATES = [row["election_date"] for row in ROWS]
PARTIES = [row["parties_in_folketing"] for row in ROWS]
DAYS = [row["days_to_next_election"] for row in ROWS]
YEARS = [row["election_year"] for row in ROWS]
NOTES = [row["note"] for row in ROWS]
LABELS = [row["label"] for row in ROWS]


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def correlation(xs: list[float], ys: list[float]) -> float:
    x_mean = mean(xs)
    y_mean = mean(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    x_ss = sum((x - x_mean) ** 2 for x in xs)
    y_ss = sum((y - y_mean) ** 2 for y in ys)
    return numerator / (x_ss * y_ss) ** 0.5


CORRELATION = correlation(PARTIES, DAYS)
R_SQUARED = CORRELATION ** 2
X_MEAN = mean(DAYS)
Y_MEAN = mean(PARTIES)
COVARIANCE = sum((x - X_MEAN) * (y - Y_MEAN) for x, y in zip(DAYS, PARTIES))
VARIANCE_X = sum((x - X_MEAN) ** 2 for x in DAYS)
SLOPE = COVARIANCE / VARIANCE_X
INTERCEPT = Y_MEAN - SLOPE * X_MEAN

SOURCE_TEXT = (
    "Kilde: Danmarks Statistik, temaet Folketingsvalg samt historiske oversigter i Statistisk Årbog. "
    "Note: Ved folketingsvalget 1994 blev Jacob Haugaard valgt uden for partierne og er ikke talt med som parti."
)

if abs(CORRELATION) < 0.2:
    RELATION_TEXT = (
        f"Sammenhængen er meget svag. Korrelationskoefficienten er {CORRELATION:.2f}, "
        f"og en simpel lineær model forklarer kun cirka {R_SQUARED:.0%} af variationen. "
        "Det er derfor ikke rimeligt at sige, at flere partier ved et valg i sig selv hænger tydeligt sammen "
        "med, hvor lang tid der går til næste valg."
    )
elif abs(CORRELATION) < 0.4:
    RELATION_TEXT = (
        f"Sammenhængen er svag. Korrelationskoefficienten er {CORRELATION:.2f}, "
        f"og en simpel lineær model forklarer cirka {R_SQUARED:.0%} af variationen. "
        "Det peger på et mønster, men ikke på en stærk eller stabil sammenhæng."
    )
else:
    RELATION_TEXT = (
        f"Sammenhængen er tydeligere end svag. Korrelationskoefficienten er {CORRELATION:.2f}, "
        f"og en simpel lineær model forklarer cirka {R_SQUARED:.0%} af variationen."
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
        .analysis-note {
            margin: 0;
            padding: 0 1rem 1rem;
            color: #3f3a34;
            font-size: 0.98rem;
            line-height: 1.55;
        }
        .plot-host {
            width: 100%;
        }
        """
    ),
    ui.div(
        {"class": "app-shell"},
        ui.h1("Partier i Folketinget ved valg", class_="app-title"),
        ui.p(
            "Tidsserien viser antal partier ved hvert folketingsvalg. Nederst ses sammenhængen mellem "
            "valgperiodens længde og antallet af partier ved valget. Sidste observation bruger "
            "2026-03-24 som foreløbig næste valgdato.",
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
                ui.p(RELATION_TEXT, class_="analysis-note"),
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


def _plotly_div(div_id: str, figure: dict, height: int) -> ui.Tag:
    figure["layout"]["height"] = height
    figure_json = json.dumps(figure, ensure_ascii=False)
    return ui.HTML(
        f"""
        <div id="{div_id}" class="plot-host" style="height: {height}px;"></div>
        <script>
        (function() {{
          const fig = {figure_json};
          Plotly.newPlot(
            "{div_id}",
            fig.data,
            fig.layout,
            fig.config || {{ responsive: true, displayModeBar: false }}
          );
        }})();
        </script>
        """
    )


def server(input, output, session):
    @output
    @render.ui
    def timeline_plot():
        figure = {
            "data": [
                {
                    "type": "scatter",
                    "x": ELECTION_DATES,
                    "y": PARTIES,
                    "mode": "lines+markers",
                    "line": {"color": "#bc4b32", "width": 3},
                    "marker": {
                        "size": 9,
                        "color": "#fffaf0",
                        "line": {"color": "#bc4b32", "width": 2},
                    },
                    "fill": "tozeroy",
                    "fillcolor": "rgba(230, 177, 126, 0.22)",
                    "customdata": [[day, note] for day, note in zip(DAYS, NOTES)],
                    "hovertemplate": (
                        "<b>Valg:</b> %{x}<br>"
                        "<b>Partier:</b> %{y}<br>"
                        "<b>Dage til næste valg:</b> %{customdata[0]}<br>"
                        "<b>Note:</b> %{customdata[1]}<extra></extra>"
                    ),
                }
            ],
            "layout": {
                **_common_layout("Antal partier ved folketingsvalg"),
                "xaxis": {
                    "title": "Valgdato",
                    "showgrid": False,
                    "tickformat": "%Y",
                    "dtick": "M60",
                    "linecolor": "#a89b8d",
                    "type": "date",
                },
                "yaxis": {
                    "title": "Partier",
                    "tickmode": "linear",
                    "dtick": 1,
                    "rangemode": "tozero",
                    "gridcolor": "#d9cdbd",
                    "linecolor": "#a89b8d",
                },
            },
            "config": {"responsive": True, "displayModeBar": False},
        }
        return _plotly_div("timeline-plot", figure, 420)

    @output
    @render.ui
    def scatter_plot():
        trend_x = [min(DAYS), max(DAYS)]
        trend_y = [SLOPE * x + INTERCEPT for x in trend_x]
        figure = {
            "data": [
                {
                    "type": "scatter",
                    "x": DAYS,
                    "y": PARTIES,
                    "mode": "markers+text",
                    "text": [str(year) for year in YEARS],
                    "textposition": "top center",
                    "marker": {
                        "size": 13,
                        "color": YEARS,
                        "colorscale": [
                            [0.0, "#e6b17e"],
                            [0.5, "#bc4b32"],
                            [1.0, "#5e3023"],
                        ],
                        "line": {"color": "#6f3b26", "width": 1},
                        "showscale": False,
                    },
                    "customdata": [[label, note] for label, note in zip(LABELS, NOTES)],
                    "hovertemplate": (
                        "<b>Valg:</b> %{customdata[0]}<br>"
                        "<b>Dage til næste valg:</b> %{x}<br>"
                        "<b>Partier:</b> %{y}<br>"
                        "<b>Note:</b> %{customdata[1]}<extra></extra>"
                    ),
                },
                {
                    "type": "scatter",
                    "x": trend_x,
                    "y": trend_y,
                    "mode": "lines",
                    "line": {"color": "#5e3023", "width": 2, "dash": "dash"},
                    "hovertemplate": (
                        "<b>Trendlinje</b><br>"
                        f"<b>Korrelationskoefficient:</b> {CORRELATION:.2f}<br>"
                        f"<b>Forklaret variation (R²):</b> {R_SQUARED:.2%}<extra></extra>"
                    ),
                    "showlegend": False,
                },
            ],
            "layout": {
                **_common_layout("Valgperiodens længde og antal partier"),
                "xaxis": {
                    "title": "Dage til næste valg",
                    "gridcolor": "#d9cdbd",
                    "linecolor": "#a89b8d",
                },
                "yaxis": {
                    "title": "Partier ved valget",
                    "tickmode": "linear",
                    "dtick": 1,
                    "rangemode": "tozero",
                    "linecolor": "#a89b8d",
                },
            },
            "config": {"responsive": True, "displayModeBar": False},
        }
        return _plotly_div("scatter-plot", figure, 460)


app = App(app_ui, server)
