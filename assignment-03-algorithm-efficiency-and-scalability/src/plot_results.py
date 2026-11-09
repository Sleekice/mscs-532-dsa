
import csv
from pathlib import Path

import matplotlib.pyplot as plt

results_dir = Path("results")
csv_path = results_dir / "quicksort.csv"

data = {}

with csv_path.open(newline="") as file:
    for row in csv.DictReader(file):
        distribution = row["distribution"]
        algorithm = row["algorithm"]

        data.setdefault(distribution, {})
        data[distribution].setdefault(algorithm, [])

        data[distribution][algorithm].append(
            (int(row["n"]), float(row["median_ms"]))
        )

fig, axes = plt.subplots(2, 2, figsize=(11, 8))

for ax, (distribution, algorithms) in zip(
    axes.flat, data.items()
):
    for algorithm, measurements in algorithms.items():
        measurements.sort()

        sizes = [n for n, _ in measurements]
        times = [ms for _, ms in measurements]

        label = (
            "Randomized Quicksort"
            if algorithm == "randomized"
            else "First-pivot Quicksort"
        )

        ax.plot(sizes, times, marker="o", label=label)

    ax.set_title(distribution.capitalize())
    ax.set_xlabel("Array size")
    ax.set_ylabel("Median runtime (ms)")
    ax.legend()
    ax.grid(True, alpha=0.3)

fig.suptitle("Quicksort Performance Comparison")
fig.tight_layout()

output = results_dir / "quicksort_comparison.png"
fig.savefig(output, dpi=150)
plt.close(fig)

print(f"Graph saved to {output}")
