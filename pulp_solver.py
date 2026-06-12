import pulp
import math
import time

def backpack_problem(Z_vals, Pojemnosc_plecakow, mnozniki_liczb):
    if len(Pojemnosc_plecakow) != len(mnozniki_liczb):
        raise ValueError("Liczba plecaków i mnożników musi być taka sama")

    z = len(Z_vals)
    n_knap = len(Pojemnosc_plecakow)
    P = Pojemnosc_plecakow
    m = mnozniki_liczb

    prob = pulp.LpProblem("Plecak_z_mnoznikami", pulp.LpMinimize)

    x = [[pulp.LpVariable(f"x_{i}_{j}", cat="Binary") for j in range(z)] for i in range(n_knap)]

    objective = sum(Z_vals) - pulp.lpSum(x[i][j] * Z_vals[j] for i in range(n_knap) for j in range(z))
    prob += objective

    for j in range(z):
        prob += pulp.lpSum(x[i][j] for i in range(n_knap)) <= 1

    for i in range(n_knap):
        prob += pulp.lpSum(x[i][j] * abs(Z_vals[j] * m[i]) for j in range(z)) <= P[i]

    t_start = time.time()
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    elapsed = time.time() - t_start

    if prob.status != pulp.LpStatusOptimal:
        print(f"  Ostrzeżenie: solver nie osiągnął optimum (status {pulp.LpStatus[prob.status]})")
        return elapsed, None

    return elapsed, pulp.value(prob.objective)

def object_placement(Lokalizacje, p_referencyjne, n, koszty_lokalizacji, max_koszt):
    if len(Lokalizacje) != len(koszty_lokalizacji):
        raise ValueError("Liczba lokalizacji i kosztów musi być równa")

    L = Lokalizacje
    K = p_referencyjne
    n2 = len(L)
    p2 = n
    c = koszty_lokalizacji
    V = max_koszt

    def min_dist(loc, refs):
        return min(math.hypot(loc[0]-r[0], loc[1]-r[1]) for r in refs)

    dist = [min_dist(L[i], K) for i in range(n2)]

    prob = pulp.LpProblem("Rozmieszczenie_budzet", pulp.LpMinimize)
    x = [pulp.LpVariable(f"x_{i}", cat="Binary") for i in range(n2)]

    prob += pulp.lpSum(x[i] * dist[i] for i in range(n2))
    prob += pulp.lpSum(x[i] for i in range(n2)) == p2
    prob += pulp.lpSum(x[i] * c[i] for i in range(n2)) <= V

    t_start = time.time()
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    elapsed = time.time() - t_start

    if prob.status != pulp.LpStatusOptimal:
        print(f"  Ostrzeżenie: solver nie osiągnął optimum (status {pulp.LpStatus[prob.status]})")
        return elapsed, None

    return elapsed, pulp.value(prob.objective)

def object_placement_distance_minimize(Lokalizacje, p_referencyjne, n):
    L = Lokalizacje
    K = p_referencyjne
    l = len(L)
    P = n

    def sum_dist(loc, refs):
        return sum(math.hypot(loc[0]-r[0], loc[1]-r[1]) for r in refs)

    dist = [sum_dist(L[i], K) for i in range(l)]

    prob = pulp.LpProblem("Rozmieszczenie_suma", pulp.LpMinimize)
    x = [pulp.LpVariable(f"x_{i}", cat="Binary") for i in range(l)]

    prob += pulp.lpSum(x[i] * dist[i] for i in range(l))
    prob += pulp.lpSum(x[i] for i in range(l)) == P

    t_start = time.time()
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    elapsed = time.time() - t_start

    if prob.status != pulp.LpStatusOptimal:
        print(f"  Ostrzeżenie: solver nie osiągnął optimum (status {pulp.LpStatus[prob.status]})")
        return elapsed, None

    return elapsed, pulp.value(prob.objective)

# ========== SAMODZIELNE URUCHOMIENIE ==========
if __name__ == "__main__":
    print("=" * 60)
    print("SOLVER: PuLP + CBC (standalone test)")
    print("=" * 60)

    Z_vals = [2, 4, -2, 1, 4, -4]
    P = [10, 5]
    m = [2, 1]
    t1, obj1 = backpack_problem(Z_vals, P, m)
    print(f"\n--- ZADANIE 1 ---")
    print(f"  Czas: {t1*1000:.2f} ms, Cel: {obj1:.4f}")

    L2 = [[24,46],[15,40],[2,29],[47,17],[26,29],[2,30]]
    K2 = [[17,6],[34,50],[33,38]]
    c2 = [20, 34, 5, 64, 21, 43]
    V2 = 100
    t2, obj2 = object_placement(L2, K2, 2, c2, V2)
    print(f"\n--- ZADANIE 2 ---")
    print(f"  Czas: {t2*1000:.2f} ms, Cel: {obj2:.4f}")

    L3 = [[24,46],[15,40],[2,29],[47,17],[26,29],[2,30],[43,25],[25,36],
          [47,9],[0,43],[4,18],[6,3],[21,10],[47,25],[50,33],[2,29],[16,44],[37,15],[42,34],[35,40]]
    K3 = [[17,6],[34,50],[33,38],[46,4],[31,31]]
    t3, obj3 = object_placement_distance_minimize(L3, K3, 8)
    print(f"\n--- ZADANIE 3 ---")
    print(f"  Czas: {t3*1000:.2f} ms, Cel: {obj3:.4f}")