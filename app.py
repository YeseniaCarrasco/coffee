"""Web page that runs one simulated coffee-shop morning per page load."""

import base64
import io

import matplotlib
matplotlib.use("Agg")  # render to images, no display needed
import matplotlib.pyplot as plt
import numpy as np
from flask import Flask, render_template_string

from coffee import OPEN_MINUTES, simulate_morning

app = Flask(__name__)

SURFACE = "#fcfcfb"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e4e3df"
SERIES = "#2a78d6"

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Coffee Shop Morning</title>
  <style>
    body { margin: 0; padding: 24px 16px; background: {{ surface }}; color: {{ text }};
           font-family: system-ui, sans-serif; }
    main { max-width: 860px; margin: 0 auto; }
    h1 { font-size: 1.5rem; margin: 0 0 4px; }
    p.sub { color: {{ text2 }}; margin: 0 0 20px; }
    .stats { display: flex; gap: 32px; flex-wrap: wrap; margin-bottom: 20px; }
    .stat .label { color: {{ text2 }}; font-size: 0.9rem; }
    .stat .value { font-size: 2rem; font-weight: 600; font-variant-numeric: tabular-nums; }
    img { width: 100%; height: auto; }
    a { color: {{ series }}; }
  </style>
</head>
<body>
<main>
  <h1>Coffee Shop Morning</h1>
  <p class="sub">One simulated morning, 7:00–11:00, one barista.
     <a href="/">Run another morning</a></p>
  <div class="stats">
    <div class="stat"><div class="label">Customers served</div>
      <div class="value">{{ served }}</div></div>
    <div class="stat"><div class="label">Average wait</div>
      <div class="value">{{ avg_wait }}</div></div>
  </div>
  {% if chart %}
  <img src="data:image/png;base64,{{ chart }}"
       alt="Line chart of each customer's wait in minutes by arrival time">
  {% endif %}
</main>
</body>
</html>"""


def clock_label(minutes, _pos=None):
    hour, minute = divmod(int(round(minutes)), 60)
    return f"{7 + hour}:{minute:02d}"


def wait_chart(arrivals, waits):
    """Return a base64-encoded PNG of each customer's wait by arrival time."""
    fig, ax = plt.subplots(figsize=(8.6, 4), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    ax.plot(arrivals, waits, color=SERIES, linewidth=2, marker="o", markersize=4,
            markeredgecolor=SURFACE, markeredgewidth=1)

    ax.set_xlim(0, OPEN_MINUTES)
    ax.set_xticks(np.arange(0, OPEN_MINUTES + 1, 30))
    ax.xaxis.set_major_formatter(clock_label)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Arrival time", color=TEXT_SECONDARY)
    ax.set_ylabel("Wait (minutes)", color=TEXT_SECONDARY)
    ax.set_title("Each customer's wait through the morning", loc="left",
                 color=TEXT_PRIMARY, fontsize=12)

    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=TEXT_SECONDARY, length=0)

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=SURFACE)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


@app.route("/")
def index():
    arrivals, waits = simulate_morning(np.random.default_rng())
    return render_template_string(
        PAGE,
        served=waits.size,
        avg_wait=f"{waits.mean():.2f} min" if waits.size else "—",
        chart=wait_chart(arrivals, waits) if waits.size else None,
        surface=SURFACE, text=TEXT_PRIMARY, text2=TEXT_SECONDARY, series=SERIES,
    )


if __name__ == "__main__":
    app.run(debug=True)
