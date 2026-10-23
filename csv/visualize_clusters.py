#!/usr/bin/env python3
"""Plot clustered vehicle trajectories from a traffic-simulation CSV file.

Example:
    python3 csv/visualize_clusters.py csv/base_clustered.csv
"""

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


# Tableau colors remain distinguishable on both light and dark displays.  Only
# the first N colors are used when the file contains N clusters (up to 16).
PALETTE = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
    "#bcbd22", "#17becf", "#393b79", "#637939",
    "#8c6d31", "#843c39", "#7b4173", "#3182bd",
]
REQUIRED_COLUMNS = {"cluster", "x_initial", "y_initial", "x_final", "y_final"}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create a color-coded trajectory plot from a clustered CSV."
    )
    parser.add_argument("input_csv", type=Path, help="CSV containing a cluster column")
    parser.add_argument(
        "-o", "--output", type=Path,
        help="PNG path (default: <input name>_plot.png)",
    )
    parser.add_argument("--show", action="store_true", help="Also open the plot window")
    return parser.parse_args()


def main():
    args = parse_args()
    trajectories = []
    with args.input_csv.open(newline="") as input_file:
        reader = csv.DictReader(input_file)
        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS.difference(fieldnames)
        if missing:
            raise SystemExit(f"Missing required CSV columns: {', '.join(sorted(missing))}")

        for row_number, row in enumerate(reader, start=2):
            try:
                trajectories.append((
                    row["cluster"],
                    float(row["x_initial"]), float(row["y_initial"]),
                    float(row["x_final"]), float(row["y_final"]),
                ))
            except (TypeError, ValueError):
                print(f"Skipping incomplete trajectory on CSV row {row_number}")

    if not trajectories:
        raise SystemExit("No complete clustered trajectories found in the CSV.")

    clusters = sorted({trajectory[0] for trajectory in trajectories}, key=str)
    if len(clusters) > len(PALETTE):
        raise SystemExit(
            f"Found {len(clusters)} clusters, but the visualizer has only "
            f"{len(PALETTE)} distinct colors."
        )
    color_for_cluster = dict(zip(clusters, PALETTE[:len(clusters)]))

    fig, ax = plt.subplots(figsize=(11, 8))
    for cluster in clusters:
        data = [trajectory for trajectory in trajectories if trajectory[0] == cluster]
        color = color_for_cluster[cluster]
        x_initial = [trajectory[1] for trajectory in data]
        y_initial = [trajectory[2] for trajectory in data]
        dx = [trajectory[3] - trajectory[1] for trajectory in data]
        dy = [trajectory[4] - trajectory[2] for trajectory in data]
        ax.quiver(
            x_initial, y_initial, dx, dy,
            angles="xy", scale_units="xy", scale=1, color=color,
            alpha=0.70, width=0.0025, headwidth=4, headlength=5,
        )
        ax.scatter(x_initial, y_initial, color=color, s=10, alpha=0.8)

    legend = [
        Line2D([0], [0], color=color_for_cluster[cluster], lw=3,
               label=f"Cluster {cluster}")
        for cluster in clusters
    ]
    ax.legend(handles=legend, title=f"Clusters ({len(clusters)})", loc="best")
    ax.set_title("Clustered Motion Trajectories")
    ax.set_xlabel("Image x coordinate (pixels)")
    ax.set_ylabel("Image y coordinate (pixels)")
    ax.set_aspect("equal", adjustable="datalim")
    ax.invert_yaxis()  # Match the conventional top-left image origin.
    ax.grid(alpha=0.2)
    fig.tight_layout()

    output = args.output or args.input_csv.with_name(f"{args.input_csv.stem}_plot.png")
    fig.savefig(output, dpi=180)
    print(f"Plotted {len(trajectories)} trajectories across {len(clusters)} clusters: {output}")
    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
