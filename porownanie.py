import sys
import time
import math
import random
import matplotlib.pyplot as plt
import numpy as np

try:
    from gurobi_solver import backpack_problem as gurobi_backpack, \
                               object_placement as gurobi_placement, \
                               object_placement_distance_minimize as gurobi_summation
    GUROBI_AVAILABLE = True
except ImportError:
    GUROBI_AVAILABLE = False
    print("Nie ma Gurubi, pomijam.")

try:
    from cplex_solver import backpack_problem as cplex_backpack, \
                              object_placement as cplex_placement, \
                              object_placement_distance_minimize as cplex_summation
    CPLEX_AVAILABLE = True
except ImportError:
    CPLEX_AVAILABLE = False
    print("CPLEX nie jest posiadany, pomijam.")

try:
    from pulp_solver import backpack_problem as pulp_backpack, \
                            object_placement as pulp_placement, \
                            object_placement_distance_minimize as pulp_summation
    PULP_AVAILABLE = True
except ImportError:
    PULP_AVAILABLE = False
    print("Pulp nie jest dostępny, pomijam.")

try:
    from highs_solver import backpack_problem as highs_backpack, \
                             object_placement as highs_placement, \
                             object_placement_distance_minimize as highs_summation
    HIGHS_AVAILABLE = True
except ImportError:
    HIGHS_AVAILABLE = False
    print("HiGHS nie jest dostępny, pomijam.")


# Generatory danych
def generate_knapsack_data(num_items, num_knapsacks):
    """Dane dla problemu plecakowego."""
    Z_vals = [random.randint(-10, 20) for _ in range(num_items)]
    P = [random.randint(20, 100) for _ in range(num_knapsacks)]
    m = [random.randint(1, 3) for _ in range(num_knapsacks)]
    return Z_vals, P, m


def generate_placement_min_data(num_locations, num_refs):
    """Dane dla zadania 2 - min odległość, z budżetem"""
    # Lokalizacje i punkty referencyjne w kwadracie 0-100
    L = [[random.randint(0,100), random.randint(0,100)] for _ in range(num_locations)]
    K = [[random.randint(0,100), random.randint(0,100)] for _ in range(num_refs)]
    # Koszty losowe 1-100, budżet = 27% sumy wszystkich kosztów
    costs = [random.randint(1, 100) for _ in range(num_locations)]
    budget = int(0.27 * sum(costs))
    # Liczba punktów do wyboru = max(1, min(10, num_locations//3))
    p = max(1, min(9, num_locations // 3))
    return L, K, p, costs, budget

def generate_placement_sum_data(num_locations, num_refs):
    """Dane dla zadania 3 suma odległości do wszystkich referencji"""
    L = [[random.randint(0,100), random.randint(0,100)] for _ in range(num_locations)]
    K = [[random.randint(0,100), random.randint(0,100)] for _ in range(num_refs)]
    # Liczba punktów do wyboru = max(1, min(10, num_locations//4))
    p = max(1, min(9, num_locations // 4))
    return L, K, p


# ========== TESTY PORÓWNAWCZE ==========

def run_comparison():
    results = {
        "knapsack": {"sizes": [], "gurobi": [], "cplex": [], "pulp": [], "highs": []},
        "placement_min": {"sizes": [], "gurobi": [], "cplex": [], "pulp": [], "highs": []},
        "placement_sum": {"sizes": [], "gurobi": [], "cplex": [], "pulp": [], "highs": []}
    }

    # Skalowanie
    knapsack_sizes = [(20,2), (50,3), (100,4), (150,5), (175,6), (200,4)]
    placement_min_sizes = [(20,5), (40,10), (80,20), (160,40), (320,80), (640,160)]
    placement_sum_sizes = [(30,5), (60,10), (120,20), (240,40), (480,80), (500, 80), (550, 82)]

    # Funkcja pomocnicza do wykonania pojedynczego pomiaru
    def measure(solver_func, *args):
        if solver_func is None:
            return None
        try:
            t, obj = solver_func(*args)
            if obj is None:
                return None
            return t
        except Exception as e:
            print(f"  Błąd: {e}")
            return None

    # Zadanie 1: Plecakowy
    print("\n=== ZADANIE 1: Problem plecakowy ===")
    for (items, knaps) in knapsack_sizes:
        size_desc = f"{items} przedmiotów, {knaps} plecaków"
        print(f"\nRozmiar: {size_desc}")
        Z, P, m = generate_knapsack_data(items, knaps)
        results["knapsack"]["sizes"].append(size_desc)

        if GUROBI_AVAILABLE:
            t = measure(gurobi_backpack, Z, P, m)
            results["knapsack"]["gurobi"].append(t)
            print(f"  Gurobi: {t*1000:.2f} ms" if t else "  Gurobi: N/A")
        if CPLEX_AVAILABLE:
            t = measure(cplex_backpack, Z, P, m)
            results["knapsack"]["cplex"].append(t)
            print(f"  CPLEX:  {t*1000:.2f} ms" if t else "  CPLEX: N/A")
        if PULP_AVAILABLE:
            t = measure(pulp_backpack, Z, P, m)
            results["knapsack"]["pulp"].append(t)
            print(f"  PuLP:   {t*1000:.2f} ms" if t else "  PuLP: N/A")
        if HIGHS_AVAILABLE:
            t = measure(highs_backpack, Z, P, m)
            results["knapsack"]["highs"].append(t)
            print(f"  HiGHS:  {t*1000:.2f} ms" if t else "  HiGHS: N/A")

    # Zadanie 2: Min odległość + budżet
    print("\n=== ZADANIE 2: Min odległość z budżetem ===")
    for (locs, refs) in placement_min_sizes:
        size_desc = f"{locs} lokalizacji, {refs} punktów ref."
        print(f"\nRozmiar: {size_desc}")
        L, K, p, costs, budget = generate_placement_min_data(locs, refs)
        results["placement_min"]["sizes"].append(size_desc)

        if GUROBI_AVAILABLE:
            t = measure(gurobi_placement, L, K, p, costs, budget)
            results["placement_min"]["gurobi"].append(t)
            print(f"  Gurobi: {t*1000:.2f} ms" if t else "  Gurobi: N/A")
        if CPLEX_AVAILABLE:
            t = measure(cplex_placement, L, K, p, costs, budget)
            results["placement_min"]["cplex"].append(t)
            print(f"  CPLEX:  {t*1000:.2f} ms" if t else "  CPLEX: N/A")
        if PULP_AVAILABLE:
            t = measure(pulp_placement, L, K, p, costs, budget)
            results["placement_min"]["pulp"].append(t)
            print(f"  PuLP:   {t*1000:.2f} ms" if t else "  PuLP: N/A")
        if HIGHS_AVAILABLE:
            t = measure(highs_placement, L, K, p, costs, budget)
            results["placement_min"]["highs"].append(t)
            print(f"  HiGHS:  {t*1000:.2f} ms" if t else "  HiGHS: N/A")

    # Zadanie 3: Suma odległości do wszystkich referencji
    print("\n=== ZADANIE 3: Suma odległości do wszystkich ref. ===")
    for (locs, refs) in placement_sum_sizes:
        size_desc = f"{locs} lokalizacji, {refs} punktów ref."
        print(f"\nRozmiar: {size_desc}")
        L, K, p = generate_placement_sum_data(locs, refs)
        results["placement_sum"]["sizes"].append(size_desc)

        if GUROBI_AVAILABLE:
            t = measure(gurobi_summation, L, K, p)
            results["placement_sum"]["gurobi"].append(t)
            print(f"  Gurobi: {t*1000:.2f} ms" if t else "  Gurobi: N/A")
        if CPLEX_AVAILABLE:
            t = measure(cplex_summation, L, K, p)
            results["placement_sum"]["cplex"].append(t)
            print(f"  CPLEX:  {t*1000:.2f} ms" if t else "  CPLEX: N/A")
        if PULP_AVAILABLE:
            t = measure(pulp_summation, L, K, p)
            results["placement_sum"]["pulp"].append(t)
            print(f"  PuLP:   {t*1000:.2f} ms" if t else "  PuLP: N/A")
        if HIGHS_AVAILABLE:
            t = measure(highs_summation, L, K, p)
            results["placement_sum"]["highs"].append(t)
            print(f"  HiGHS:  {t*1000:.2f} ms" if t else "  HiGHS: N/A")

    return results


# RYSOWANIE WYKRESÓW
def plot_results(results):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    titles = ["Problem plecakowy", "Min. odległość (budżet)", "Suma odległości"]
    keys = ["knapsack", "placement_min", "placement_sum"]

    for ax, title, key in zip(axes, titles, keys):
        sizes = results[key]["sizes"]
        # Konwersja etykiet na indeksy numeryczne do osi X
        x = np.arange(len(sizes))

        for solver, label, color in [("gurobi", "GUROBI", "#4CAF50"),
                                      ("cplex",  "CPLEX",  "#FF5722"),
                                      ("pulp",   "PuLP+CBC","#2196F3"),
                                      ("highs",  "HiGHS",  "#9C27B0")]:
            times = results[key][solver]
            if times and any(t is not None for t in times):
                # Zamień None na NaN (nie rysuj)
                y = [t*1000 if t is not None else np.nan for t in times]
                ax.plot(x, y, marker='o', label=label, color=color)

        ax.set_title(title)
        ax.set_xlabel("Rozmiar problemu")
        ax.set_ylabel("Czas [ms]")
        # ax.set_yscale('log')
        ax.set_xticks(x)
        ax.set_xticklabels(sizes, rotation=45, ha='right', fontsize=8)
        ax.legend()
        ax.grid(True, which="both", ls="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig("comparison_plots.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    print("="*70)
    print("PORÓWNANIE SOLVERÓW: CPLEX, Gurobi, Pulp i Highs")
    print("="*70)

    if not (GUROBI_AVAILABLE or CPLEX_AVAILABLE or PULP_AVAILABLE or HIGHS_AVAILABLE):
        print("BŁĄD: Żaden solver nie jest dostępny. Zainstaluj przynajmniej jeden.")
        sys.exit(1)

    results = run_comparison()
    plot_results(results)
