"""
Single-CPU, non-preemptive scheduler simulation built on PriorityQueue.

Policies: FIFO, Priority, Priority + aging, EDF (Earliest Deadline First).
"""

import random
import statistics

from priority_queue import PriorityQueue, Task

# ===========================================================================
#
# One CPU, non-preemptive: once a task starts it runs to completion. Tasks
# arrive over time. Whenever the CPU becomes free, the scheduler moves every
# task that has arrived into the priority queue and runs the one on top.
#
# Policies (all use the same PriorityQueue class, just configured differently):
#   FIFO              min-heap on arrival_time
#   Priority          max-heap on priority
#   Priority + aging  max-heap on priority, and any task that has waited
#                     `aging_interval` time units since its last boost gets
#                     increase_key(priority + 1). Stops low-priority starvation.
#   EDF               min-heap on deadline (Earliest Deadline First)

POLICIES = {
    "FIFO": dict(mode="min", key="arrival_time"),
    "Priority": dict(mode="max", key="priority"),
    "Priority + aging": dict(mode="max", key="priority"),
    "EDF": dict(mode="min", key="deadline"),
}


def generate_workload(n, utilization=0.95, levels=5, seed=0):
    """Poisson arrivals, exponential service times with mean 1, so the CPU is
    busy `utilization` of the time on average. Priority 1 (lowest) to `levels`
    (highest). Higher priority tasks get tighter deadlines."""
    rng = random.Random(seed)
    tasks, t = [], 0.0
    for i in range(n):
        t += rng.expovariate(utilization)
        duration = rng.expovariate(1.0)
        p = rng.randint(1, levels)
        slack = rng.uniform(2, 6) * (levels + 1 - p) * 2  # p=5: 4-12, p=1: 20-60
        tasks.append(Task(task_id=i, priority=p, arrival_time=t, duration=duration,
                          deadline=t + duration + slack, name=f"T{i}"))
    return tasks


def simulate(workload, policy, aging_interval=10.0, max_priority=10):
    """Run the workload under one policy. Returns the finished tasks."""
    tasks = [Task(task_id=w.task_id, priority=w.priority, arrival_time=w.arrival_time,
                  duration=w.duration, deadline=w.deadline, name=w.name) for w in workload]
    tasks.sort(key=lambda t: t.arrival_time)
    pq = PriorityQueue(**POLICIES[policy])
    aging = policy == "Priority + aging"
    clock, i, done = 0.0, 0, []
    while i < len(tasks) or not pq.is_empty():
        if pq.is_empty() and clock < tasks[i].arrival_time:
            clock = tasks[i].arrival_time  # CPU idle until the next arrival
        while i < len(tasks) and tasks[i].arrival_time <= clock:
            pq.insert(tasks[i])
            i += 1
        if aging:
            for t in pq.tasks():
                steps = int((clock - t.last_aged) // aging_interval)
                if steps > 0 and t.priority < max_priority:
                    pq.increase_key(t, min(max_priority, t.priority + steps))
                    t.last_aged += steps * aging_interval
        task = pq.extract()
        task.start_time = clock
        clock += task.duration
        task.finish_time = clock
        done.append(task)
    return done


def summarize(done, levels=5):
    waits = [t.waiting_time for t in done]
    by_level = {p: statistics.mean([t.waiting_time for t in done if t.base_priority == p])
                for p in range(1, levels + 1)}
    return {
        "avg_wait": statistics.mean(waits),
        "max_wait": max(waits),
        "p95_wait": sorted(waits)[int(0.95 * len(waits))],
        "miss_rate": sum(t.missed_deadline for t in done) / len(done),
        "wait_by_priority": by_level,
    }


def run_scheduler(n_tasks):
    workload = generate_workload(n_tasks)
    results = {}
    print(f"\nScheduler simulation: {n_tasks} tasks, 1 CPU, ~95% utilization, priorities 1 (low) to 5 (high)")
    header = f"{'Policy':<18}{'avg wait':>10}{'p95 wait':>10}{'max wait':>10}{'missed DL':>11}"
    header += "".join(f"{'P' + str(p) + ' wait':>10}" for p in range(5, 0, -1))
    print(header)
    for policy in POLICIES:
        s = summarize(simulate(workload, policy))
        results[policy] = s
        row = (f"{policy:<18}{s['avg_wait']:>10.2f}{s['p95_wait']:>10.2f}{s['max_wait']:>10.2f}"
               f"{s['miss_rate'] * 100:>10.1f}%")
        row += "".join(f"{s['wait_by_priority'][p]:>10.2f}" for p in range(5, 0, -1))
        print(row)
    return results
