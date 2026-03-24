from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MaxNLocator
from shiny import App, render, ui


APP_DIR = Path(__file__).parent
DATA_PATH = APP_DIR / "data" / "folketing_partier_over_tid.csv"

df = pd.read_csv(DATA_PATH, parse_dates=["election_date", "next_election_date"])
df["election_year"] = df["election_date"].dt.year


app_ui = ui.page_fillable(
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
        """
    ),
    ui.div(
        {"class": "app-shell"},
        ui.h1("Partier i Folketinget ved valg", class_="app-title"),
        ui.p(
            "Tidsserien viser antal partier ved hvert folketingsvalg. Nederst ses sammenhaengen mellem "
            "antal partier og antallet af dage til det efterfoelgende valg. Sidste observation bruger "
            "2026-03-24 som naeste valgdato.",
            class_="app-subtitle",
        ),
        ui.layout_column_wrap(
            ui.card(
                ui.card_header("Udvikling over tid"),
                ui.output_plot("timeline_plot", width="100%", height="380px"),
                full_screen=True,
            ),
            ui.card(
                ui.card_header("Antal partier vs. dage til naeste valg"),
                ui.output_plot("scatter_plot", width="100%", height="420px"),
                full_screen=True,
            ),
            width=1,
            gap="1rem",
        ),
    ),
)


def _apply_common_style(ax):
    ax.set_facecolor("#fffaf0")
    ax.grid(True, axis="y", color="#d9cdbd", linewidth=0.9, alpha=0.85)
    ax.grid(False, axis="x")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#a89b8d")
    ax.spines["bottom"].set_color("#a89b8d")
    ax.tick_params(colors="#3e4a49")


def _finish_figure(fig):
    fig.tight_layout()
    return fig


def server(input, output, session):
    @output
    @render.plot(alt="Linjegraf over antal partier ved hvert folketingsvalg.")
    def timeline_plot():
        fig, ax = plt.subplots(figsize=(11, 4.2))
        ax.plot(
            df["election_date"],
            df["parties_in_folketing"],
            color="#bc4b32",
            linewidth=2.8,
            marker="o",
            markersize=6,
            markerfacecolor="#fffaf0",
            markeredgewidth=2,
        )
        ax.fill_between(
            df["election_date"],
            df["parties_in_folketing"],
            [df["parties_in_folketing"].min()] * len(df),
            color="#e6b17e",
            alpha=0.22,
        )
        ax.set_title("Antal partier ved folketingsvalg", loc="left", fontsize=15, pad=14)
        ax.set_ylabel("Partier")
        ax.set_xlabel("Valgdato")
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.xaxis.set_major_locator(mdates.YearLocator(base=5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        for year in [1945, 1973, 1977, 2022]:
            row = df.loc[df["election_year"] == year].iloc[0]
            ax.annotate(
                f"{year}: {row['parties_in_folketing']}",
                (row["election_date"], row["parties_in_folketing"]),
                xytext=(0, 12),
                textcoords="offset points",
                ha="center",
                fontsize=9,
                color="#5a3a2f",
            )
        _apply_common_style(ax)
        return _finish_figure(fig)

    @output
    @render.plot(alt="Scatterplot over antal partier og dage til det efterfoelgende valg.")
    def scatter_plot():
        fig, ax = plt.subplots(figsize=(11, 4.6))
        colors = plt.cm.copper_r(
            (df["election_year"] - df["election_year"].min())
            / (df["election_year"].max() - df["election_year"].min())
        )
        ax.scatter(
            df["parties_in_folketing"],
            df["days_to_next_election"],
            s=115,
            c=colors,
            edgecolors="#6f3b26",
            linewidths=0.9,
            alpha=0.95,
        )
        for _, row in df.iterrows():
            ax.annotate(
                str(row["election_year"]),
                (row["parties_in_folketing"], row["days_to_next_election"]),
                xytext=(6, 6),
                textcoords="offset points",
                fontsize=8,
                color="#4c4038",
            )
        ax.set_title("Flere partier og kortere eller laengere valgperioder?", loc="left", fontsize=15, pad=14)
        ax.set_xlabel("Antal partier")
        ax.set_ylabel("Dage til naeste valg")
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        _apply_common_style(ax)
        return _finish_figure(fig)


app = App(app_ui, server)
