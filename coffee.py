"""Simulate one morning (7:00-11:00) at a coffee shop with one barista."""

import numpy as np

OPEN_MINUTES = 4 * 60      # 7:00 to 11:00
MEAN_INTERARRIVAL = 3.0    # about one customer every three minutes
MIN_ORDER, MAX_ORDER = 1.0, 4.0


def simulate(rng):
    # Draw more gaps than we could need, then keep arrivals before closing.
    gaps = rng.exponential(MEAN_INTERARRIVAL, size=int(OPEN_MINUTES / MEAN_INTERARRIVAL * 3))
    arrivals = np.cumsum(gaps)
    arrivals = arrivals[arrivals < OPEN_MINUTES]

    order_times = rng.uniform(MIN_ORDER, MAX_ORDER, size=arrivals.size)

    waits = np.empty(arrivals.size)
    barista_free_at = 0.0
    for i, (arrival, order_time) in enumerate(zip(arrivals, order_times)):
        start = max(arrival, barista_free_at)
        waits[i] = start - arrival
        barista_free_at = start + order_time

    return waits


def main():
    rng = np.random.default_rng()
    waits = simulate(rng)
    print(f"Customers served: {waits.size}")
    if waits.size:
        print(f"Average wait: {waits.mean():.2f} minutes")


if __name__ == "__main__":
    main()
