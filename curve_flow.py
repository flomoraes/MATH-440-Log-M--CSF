import math
import random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

N = 10


# making random decagon
def random_decagon(seed=None):
    """Random decagon: random angles with random radii.
    keeps the polygon from crossing itself."""
    if seed is not None:
        random.seed(seed)
    angles = sorted(random.uniform(0, 2 * math.pi) for _ in range(N))
    pts = []
    for a in angles:
        r = random.uniform(0.6, 1.4)
        pts.append([r * math.cos(a), r * math.sin(a)])
    return pts


def regular_decagon():
    return [[math.cos(2 * math.pi * i / N), math.sin(2 * math.pi * i / N)]
            for i in range(N)]


# finite differences
def edge_lengths(X):
    """h[i] = |X[i+1] - X[i]|  (indices wrap around: closed curve)"""
    h = []
    for i in range(N):
        dx = X[(i + 1) % N][0] - X[i][0]
        dy = X[(i + 1) % N][1] - X[i][1]
        h.append(math.sqrt(dx * dx + dy * dy))
    return h


def slopes_at_midpoints(X, h):
    """Slope at Z_i = (X[i+1] - X[i]) / h[i]"""
    s = []
    for i in range(N):
        sx = (X[(i + 1) % N][0] - X[i][0]) / h[i]
        sy = (X[(i + 1) % N][1] - X[i][1]) / h[i]
        s.append([sx, sy])
    return s


def second_derivative(X):
    """Xss at X[i] = (slope at Z_i - slope at Z_{i-1}) / average of the two
    neighbouring edge lengths (distance from Z_{i-1} to Z_i)."""
    h = edge_lengths(X)
    for length in h:
        if length < 1e-12:
            return None  # two points collided
    s = slopes_at_midpoints(X, h)
    Xss = []
    for i in range(N):
        dist = 0.5 * (h[i] + h[i - 1])
        Xss.append([(s[i][0] - s[i - 1][0]) / dist,
                    (s[i][1] - s[i - 1][1]) / dist])
    return Xss


# time step
def step(X, dt):
    """X_{t+dt} = X_t + dt * Xss"""
    Xss = second_derivative(X)
    if Xss is None:
        return None
    return [[X[i][0] + dt * Xss[i][0], X[i][1] + dt * Xss[i][1]]
            for i in range(N)]


# failure checks
def total_length(X):
    return sum(edge_lengths(X))


def cross(ax, ay, bx, by):
    return ax * by - ay * bx


def segments_cross(p1, p2, p3, p4):
    d1 = cross(p4[0] - p3[0], p4[1] - p3[1], p1[0] - p3[0], p1[1] - p3[1])
    d2 = cross(p4[0] - p3[0], p4[1] - p3[1], p2[0] - p3[0], p2[1] - p3[1])
    d3 = cross(p2[0] - p1[0], p2[1] - p1[1], p3[0] - p1[0], p3[1] - p1[1])
    d4 = cross(p2[0] - p1[0], p2[1] - p1[1], p4[0] - p1[0], p4[1] - p1[1])
    return (d1 * d2 < 0) and (d3 * d4 < 0)


def self_intersects(X):
    for i in range(N):
        for j in range(i + 2, N):
            if i == 0 and j == N - 1:
                continue  # these edges share a vertex
            if segments_cross(X[i], X[(i + 1) % N], X[j], X[(j + 1) % N]):
                return True
    return False


def check_failure(X, prev_length):
    """Returns a reason string if the run has failed, else None."""
    for p in X:
        if math.isnan(p[0]) or math.isnan(p[1]) or abs(p[0]) > 1e6 or abs(p[1]) > 1e6:
            return "blew up (NaN / huge values)"
    if self_intersects(X):
        return "curve crossed itself"
    if total_length(X) > prev_length * (1 + 1e-9):
        return "length increased (curve shortening should only decrease it)"
    return None


# one full run
def run(X0, dt, max_steps=200000, stop_length=0.05, snapshot_every=None):
    """Run the flow with a FIXED dt.
    Returns (status, step_number, time, snapshots, final_X).
    status is 'failed: ...' or 'shrank to a point (success)'."""
    X = [p[:] for p in X0]
    snapshots = [(0, [p[:] for p in X])]
    prev_length = total_length(X)
    for n in range(1, max_steps + 1):
        newX = step(X, dt)
        if newX is None:
            return "failed: points collided", n, n * dt, snapshots, X
        reason = check_failure(newX, prev_length)
        if reason:
            snapshots.append((n, newX))
            return "failed: " + reason, n, n * dt, snapshots, newX
        X = newX
        prev_length = total_length(X)
        if snapshot_every and n % snapshot_every == 0:
            snapshots.append((n, [p[:] for p in X]))
        if prev_length < stop_length:
            return "shrank to a point (success)", n, n * dt, snapshots, X
    return "hit max_steps without failing", max_steps, max_steps * dt, snapshots, X


# plotting
def plot_run(X0, dt, title, filename, snapshot_every=None):
    status, n, t, snaps, Xf = run(X0, dt, snapshot_every=snapshot_every)
    fig, ax = plt.subplots(figsize=(6, 6))
    for k, (step_no, X) in enumerate(snaps):
        xs = [p[0] for p in X] + [X[0][0]]
        ys = [p[1] for p in X] + [X[0][1]]
        is_last = (k == len(snaps) - 1)
        if is_last and status.startswith("failed"):
            ax.plot(xs, ys, "r-o", lw=2, ms=4, label="failing step %d" % step_no)
        else:
            shade = 0.85 - 0.75 * k / max(1, len(snaps) - 1)
            ax.plot(xs, ys, "-", color=str(shade), lw=1)
    xs0 = [p[0] for p in X0] + [X0[0][0]]
    ys0 = [p[1] for p in X0] + [X0[0][1]]
    ax.plot(xs0, ys0, "b-o", lw=2, ms=4, label="start")
    ax.set_aspect("equal")
    ax.set_title("%s\ndt=%g  ->  %s (step %d, t=%.4f)" % (title, dt, status, n, t),
                 fontsize=9)
    ax.legend(loc="upper right", fontsize=8)
    fig.savefig(filename, dpi=110)
    plt.close(fig)
    return status, n, t


# main experiment
if __name__ == "__main__":
    # 1) Regular decagon: watch it shrink (small dt, should succeed)
    dec = regular_decagon()
    print("REGULAR DECAGON")
    s, n, t = plot_run(dec, 0.001, "Regular decagon", "regular_decagon.png",
                       snapshot_every=20)
    print("  dt=0.001 ->", s, "| step", n, "| t = %.4f" % t)

    # 2) Random decagon, same shape reused for every dt
    shape = random_decagon(seed=3)
    print("\nRANDOM DECAGON: sweep over dt (same dt used for every step)")
    dts = [0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05]
    for dt in dts:
        fname = "random_dt_%g.png" % dt
        s, n, t = plot_run(shape, dt, "Random decagon", fname, snapshot_every=25)
        print("  dt=%-7g -> %s | step %d | t = %.4f" % (dt, s, n, t))
