from docplex.mp.model import Model
import math
import time

print("=" * 60)
print("  SOLVER: docplex (Python API dla IBM CPLEX)")
print("=" * 60)

"""======================DANE DO ZADAŃ============================"""
# Zadanie 1
Z_vals = [2, 4, -2, 1, 4, -4]
P = [10, 5]
m = [2, 1]

# Zadanie 2
L2 = [[24, 46], [15, 40], [2, 29], [47, 17], [26, 29], [2, 30]]
K2 = [[17, 6], [34, 50], [33, 38]]
p2 = 2
c2 = [20, 34, 5, 64, 21, 43]
V2 = 100

# Zadanie 3
L3 = [[24, 46], [15, 40], [2, 29], [47, 17], [26, 29], [2, 30], [43, 25], [25, 36],
      [47, 9], [0, 43], [4, 18], [6, 3], [21, 10], [47, 25], [50, 33], [2, 29], [16, 44], [37, 15], [42, 34], [35, 40]]
K3 = [[17, 6], [34, 50], [33, 38], [46, 4], [31, 31]]
P3 = 8


# ============================================================
# ZADANIE 1: Problem plecakowy z mnożnikami
# ============================================================

def backpack_problem(Z_vals, Pojemnosc_plecakow, mnozniki_liczb):
    # Z = zbiór liczb które wsadzamy do plecaka
    # m = mnożniki liczb, czyli jak trafiają do plecaka to przez to je mnożymy
    # P = pojemność plecaków

    if len(Pojemnosc_plecakow) != len(mnozniki_liczb):
        return 'Złe wymiary plecaków i mnożników = Mają być takie same'

    print("\n--- ZADANIE 1: Problem plecakowy z mnożnikami ---")

    z = len(Z_vals)
    n_knap = len(Pojemnosc_plecakow)
    P = Pojemnosc_plecakow
    m = mnozniki_liczb

    t_start = time.time()
    mdl1 = Model(name="Plecak_z_mnoznikami", log_output=False)

    # Zmienne binarne x[i][j]: czy liczba j trafia do plecaka i
    x1 = {(i, j): mdl1.binary_var(name=f"x_{i}_{j}") for i in range(n_knap) for j in range(z)}

    # Cel
    cel1 = sum(Z_vals) - mdl1.sum(x1[i, j] * Z_vals[j] for i in range(n_knap) for j in range(z))

    mdl1.minimize(cel1)

    # Każda liczba do co najwyżej jednego plecaka
    for j in range(z):
        mdl1.add_constraint(mdl1.sum(x1[i, j] for i in range(n_knap)) <= 1,f"jeden_plecak_{j}")

    # Pojemność plecaków
    for i in range(n_knap):
        mdl1.add_constraint(mdl1.sum(x1[i, j] * abs(Z_vals[j] * m[i]) for j in range(z)) <= P[i],
                            f"pojemnosc_{i}")
    sol1 = mdl1.solve()
    t1 = time.time() - t_start

    print(f"  Status: {mdl1.solve_details.status}")
    print(f"  Wartość funkcji celu: {sol1.objective_value:.4f}")
    print(f"  Czas: {t1*1000:.2f} ms")

    for i in range(n_knap):
        w_plecaku = [Z_vals[j] for j in range(z) if x1[i, j].solution_value > 0.5]
        print(f"  Plecak {i+1} (poj={P[i]}, mnożnik={m[i]}): {w_plecaku}")

    nie_trafilo = [Z_vals[j] for j in range(z)
                   if all(x1[i, j].solution_value < 0.5 for i in range(n_knap))]

    print(f"  Liczby poza plecakami: {nie_trafilo}, suma = {sum(nie_trafilo)}")

    return t1, sol1.objective_value


# ============================================================
# ZADANIE 2: Rozmieszczenie p obiektów (z budżetem V)
# Wybieramy taką lokalizację p razy, żeby odległość od najbliższego punktu
# referencyjnego była jak najmniejsza prz uwzględnieniu kosztów.
# ============================================================

def object_placement(Lokalizacje, p_referencyjne, n, koszty_lokalizacji, max_koszt):
    print("\n--- ZADANIE 2: Rozmieszczenie obiektów (min. odl. do najbliższego ref.) ---")
    if len(Lokalizacje) != len(koszty_lokalizacji) and len(Lokalizacje):
        return "Lokalizacje i koszty lokalizacji się nie zgadzają!"
    L2 = Lokalizacje
    K2 = p_referencyjne
    n2, k2 = len(L2), len(K2)
    p2 = n
    c2 = koszty_lokalizacji
    V2 = max_koszt

    def min_dist(loc, refs):
        return min(math.sqrt((loc[0]-r[0])**2 + (loc[1]-r[1])**2) for r in refs)

    dist2 = [min_dist(L2[i], K2) for i in range(n2)]

    t_start = time.time()
    mdl2 = Model(name="Rozmieszczenie_budzet", log_output=False)
    x2 = [mdl2.binary_var(name=f"x_{i}") for i in range(n2)]

    mdl2.minimize(mdl2.sum(x2[i] * dist2[i] for i in range(n2)))
    mdl2.add_constraint(mdl2.sum(x2[i] for i in range(n2)) == p2, "liczba_punktow")
    mdl2.add_constraint(mdl2.sum(x2[i] * c2[i] for i in range(n2)) <= V2, "budzet")

    sol2 = mdl2.solve()
    t2 = time.time() - t_start

    print(f"  Status: {mdl2.solve_details.status}")
    print(f"  Wartość funkcji celu: {sol2.objective_value:.4f}")
    print(f"  Czas: {t2*1000:.2f} ms")

    wybrane2 = [i for i in range(n2) if x2[i].solution_value > 0.5]
    for i in wybrane2:
        print(f"  Lokalizacja {i+1}: {L2[i]}, koszt={c2[i]}, min_dist={dist2[i]:.2f}")
    print(f"  Łączny koszt: {sum(c2[i] for i in wybrane2)}")

    return t2, sol2.objective_value


# ============================================================
# ZADANIE 3: Rozmieszczenie P obiektów (suma odleglosci do WSZYSTKICH)
# ============================================================

def object_placement_distance_minimize(Lokalizacje, p_referencyjne, n):
    print("\n--- ZADANIE 3: Rozmieszczenie obiektów (suma odl. do wszystkich ref.) ---")

    L3 = Lokalizacje
    K3 = p_referencyjne
    l3, k3 = len(L3), len(K3)
    P3 = n

    def sum_dist(loc, refs):
        return sum(math.sqrt((loc[0]-r[0])**2 + (loc[1]-r[1])**2) for r in refs)

    dist3 = [sum_dist(L3[i], K3) for i in range(l3)]

    t_start = time.time()
    mdl3 = Model(name="Rozmieszczenie_suma", log_output=False)
    x3 = [mdl3.binary_var(name=f"x_{i}") for i in range(l3)]

    mdl3.minimize(mdl3.sum(x3[i] * dist3[i] for i in range(l3)))
    mdl3.add_constraint(mdl3.sum(x3[i] for i in range(l3)) == P3, "liczba_punktow")

    sol3 = mdl3.solve()
    t3 = time.time() - t_start

    print(f"  Status: {mdl3.solve_details.status}")
    print(f"  Wartość funkcji celu: {sol3.objective_value:.4f}")
    print(f"  Czas: {t3*1000:.2f} ms")

    wybrane3 = [i for i in range(l3) if x3[i].solution_value > 0.5]
    print(f"  Wybrane lokalizacje (indeksy): {[i+1 for i in wybrane3]}")
    for i in wybrane3:
        print(f"    L[{i+1}]={L3[i]}, suma_dist={dist3[i]:.2f}")

    return t3, sol3.objective_value

t1, cel1 = backpack_problem(Z_vals, P, m)
t2, cel2 = object_placement(L2, K2, p2, c2, V2)
t3, cel3 = object_placement_distance_minimize(L3, K3, P3)

print("=" * 60)
print(f"  PODSUMOWANIE CZASÓW (docplex/CPLEX):")
print(f"  Zadanie 1: {t1*1000:.2f} ms")
print(f"  Zadanie 2: {t2*1000:.2f} ms")
print(f"  Zadanie 3: {t3*1000:.2f} ms")
print("=" * 60)
