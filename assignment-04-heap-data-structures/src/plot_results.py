"""
Reads results/sorting.csv and results/scheduler.csv (written by benchmark.py)
and draws results/heap_results.png.

Run from the assignment folder:
    python src/plot_results.py
"""

import csv
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
DISTRIBUTIONS = ["Random", "Sorted", "Reverse-sorted", "Few unique values"]
ALGORITHMS = ["Heapsort", "Quicksort (randomized)", "Merge sort"]
COLORS = {"Heapsort": "#d1495b", "Quicksort (randomized)": "#2a6fdb", "Merge sort": "#2e933c"}
MARKERS = {"Heapsort": "o", "Quicksort (randomized)": "s", "Merge sort": "^"}
POLICY_COLORS = {"FIFO": "#888888", "Priority": "#d1495b", "Priority + aging": "#2a6fdb", "EDF": "#2e933c"}


def read_csv(name):
    with open(os.path.join(RESULTS_DIR, name), newline="") as f:
        return list(csv.DictReader(f))


def main():
    sorting = read_csv("sorting.csv")
    sched = read_csv("scheduler.csv")

    fig, axes = plt.subplots(2, 3, figsize=(17, 10))
    fig.suptitle("Assignment 4: Heapsort and Priority Queue Scheduling", fontsize=15, fontweight="bold")

    # Panels 1-4: running time per input distribution.
    for ax, kind in zip(axes.flat[:4], DISTRIBUTIONS):
        rows = [r for r in sorting if r["distribution"] == kind]
        ns = [int(r["n"]) for r in rows]
        for name in ALGORITHMS:
            ax.plot(ns, [float(r[name]) for r in rows], marker=MARKERS[name], color=COLORS[name], label=name)
        ax.set_title(f"{kind} input")
        ax.set_xlabel("n (array size)")
        ax.set_ylabel("time (ms, best of several runs)")
        ax.grid(alpha=0.3)
        ax.legend(frameon=False, fontsize=9)

    # Panel 5: heapsort comparisons normalized by n log2 n.
    ax = axes.flat[4]
    for kind, c in zip(DISTRIBUTIONS, ["#444444", "#2a6fdb", "#e0663a", "#8f5bd6"]):
        rows = [r for r in sorting if r["distribution"] == kind]
        ax.plot([int(r["n"]) for r in rows], [float(r["comparisons_per_nlogn"]) for r in rows],
                marker="o", color=c, label=kind)
    ax.axhline(2, color="gray", ls="--", lw=1, label="2 n log2 n (worst-case bound)")
    ax.set_title("Heapsort comparisons divided by n log2 n")
    ax.set_xlabel("n (array size)")
    ax.set_ylabel("comparisons / (n log2 n)")
    ax.set_ylim(0, 2.3)
    ax.grid(alpha=0.3)
    ax.legend(frameon=False, fontsize=9, loc="lower right")

    # Panel 6: scheduler waiting time by priority level.
    ax = axes.flat[5]
    levels = [5, 4, 3, 2, 1]
    width = 0.2
    for k, row in enumerate(sched):
        xs = [x + (k - 1.5) * width for x in range(len(levels))]
        miss = float(row["deadline_miss_rate"]) * 100
        ax.bar(xs, [float(row[f"avg_wait_P{p}"]) for p in levels], width,
               color=POLICY_COLORS.get(row["policy"], "black"),
               label=f"{row['policy']} ({miss:.0f}% deadlines missed)")
    ax.set_xticks(range(len(levels)))
    ax.set_xticklabels([f"P{p}" + (" (high)" if p == 5 else " (low)" if p == 1 else "") for p in levels])
    ax.set_title("Scheduler: average waiting time by task priority")
    ax.set_ylabel("average wait (time units)")
    ax.grid(alpha=0.3, axis="y")
    ax.legend(frameon=False, fontsize=9, loc="upper left")

    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out = os.path.join(RESULTS_DIR, "heap_results.png")
    fig.savefig(out, dpi=130)
    print(f"Saved {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
