import matplotlib.pyplot as plt
import pandas as pd
import sys

if len(sys.argv) < 2:
    print("Error: Please provide a filename when launching.")
    sys.exit(1)

if ".csv" not in sys.argv[1]:
    print("Error: Please provide a .csv file.")

file_to_process = sys.argv[1]

df = pd.read_csv(file_to_process)

cluster_colors = {
    0: "tab:blue",
    1: "tab:orange",
    2: "tab:green",
    3: "tab:red",
    4: "tab:purple",
    5: "tab:pink",
}

plt.figure(figsize=(8, 8))

# Plot arrows
for _, row in df.iterrows():
    c = cluster_colors[row["cluster"]]

    x0 = row["x_initial"]
    y0 = row["y_initial"]
    dx = row["x_final"] - row["x_initial"]
    dy = row["y_final"] - row["y_initial"]

    plt.arrow(
        x0, y0, dx, dy,
        color=c,
        alpha=0.7,
        length_includes_head=True,
        head_width=10,
        head_length=10
    )

# Plot points
for cluster, color in cluster_colors.items():
    sub = df[df["cluster"] == cluster]
    plt.scatter(sub["x_initial"], sub["y_initial"], s=10, color=color)
    plt.scatter(sub["x_final"], sub["y_final"], s=10, color=color)

plt.title("Motion Vectors (Image Coordinates)")
plt.axis("equal")
plt.gca().invert_yaxis()

plt.show()
