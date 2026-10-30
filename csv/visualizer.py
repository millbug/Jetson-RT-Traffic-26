import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("base_clustered11.csv")

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
for _, row in df.iterrows(): # iterating through each row (e.g. each identified object) of the dataframe
    c = cluster_colors[row["cluster"]]

    x0 = row["x_initial"] # initializing initial point, presumably object's first frame
    y0 = row["y_initial"]
    x1 = row["x_mid1"] # adding three mid points for new arrows
    y1 = row["y_mid1"]
    x2 = row["x_mid2"]
    y2 = row["y_mid2"]
    x3 = row["x_mid3"]
    y3 = row["y_mid3"]

    dx0 = row["x_mid1"] - row["x_initial"] # change(s) in x and y
    dy0 = row["y_mid1"] - row["y_initial"]
    dx1 = row["x_mid2"] - row["x_mid1"] 
    dy1 = row["y_mid2"] - row["y_mid1"]
    dx2 = row["x_mid3"] - row["x_mid2"] 
    dy2 = row["y_mid3"] - row["y_mid2"]
    dx3 = row["x_final"] - row["x_mid3"] 
    dy3 = row["y_final"] - row["y_mid3"]

    # plot several arrows going from point to point!
    plt.arrow(
        x0, y0, dx0, dy0, # x_coord, y_coord, changeInX, changeInY
        color=c,
        alpha=0.7,
        length_includes_head=True,
        head_width=10,
        head_length=10
    )
    plt.arrow(
        x1, y1, dx1, dy1,
        color=c,
        alpha=0.7,
        length_includes_head=True,
        head_width=10,
        head_length=10
    )
    plt.arrow(
        x2, y2, dx2, dy2,
        color=c,
        alpha=0.7,
        length_includes_head=True,
        head_width=10,
        head_length=10
    )
    plt.arrow(
        x3, y3, dx3, dy3,
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
    plt.scatter(sub["x_mid1"], sub["y_mid1"], s=10, color=color)
    plt.scatter(sub["x_mid2"], sub["y_mid2"], s=10, color=color)
    plt.scatter(sub["x_mid3"], sub["y_mid3"], s=10, color=color)
    plt.scatter(sub["x_final"], sub["y_final"], s=10, color=color)

plt.title("Motion Vectors (Image Coordinates)")
plt.axis("equal")
plt.gca().invert_yaxis()

plt.show()
