import os
import sys
import requests

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

try:
    from logging_middleware.logger import get_logger
    log = get_logger("vehicle_scheduler")
except ImportError:

    print("WARNING: Could not find 'logging_middleware.logger'. Check file location.")
    import logging
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger("vehicle_scheduler")

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJiYWxhamkuazIwMjJiQHZpdHN0dWRlbnQuYWMuaW4iLCJleHAiOjE3Nzg5MzI3OTEsImlhdCI6MTc3ODkzMTg5MSwiaXNzIjoiQWZmb3JkIE1lZGljYWwgVGVjaG5vbG9naWVzIFByaXZhdGUgTGltaXRlZCIsImp0aSI6ImY0YmIxOGQ0LWNjYmMtNDlhMC04NTk4LTczZjMwMWU3NDhjNSIsImxvY2FsZSI6ImVuLUlOIiwibmFtZSI6ImJhbGFqaSBrIiwic3ViIjoiYTlhYmQyMWYtZTliMi00OGI4LWJjNTYtM2Y2MTIwOGMxZDhmIn0sImVtYWlsIjoiYmFsYWppLmsyMDIyYkB2aXRzdHVkZW50LmFjLmluIiwibmFtZSI6ImJhbGFqaSBrIiwicm9sbE5vIjoiMjJtaXMxMTk4IiwiYWNjZXNzQ29kZSI6IlNmRnVXZyIsImNsaWVudElEIjoiYTlhYmQyMWYtZTliMi00OGI4LWJjNTYtM2Y2MTIwOGMxZDhmIiwiY2xpZW50U2VjcmV0IjoiZ3R4dEZua1RCTnl6VHNVeiJ9.JXcLjyIkxxc7Xt3SZM6Yd3bW2F5fgqRR8H8YjD557U0"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}
BASE_URL = "http://4.224.186.213/evaluation-service"
DP_THRESHOLD = 50_000_000

def fetch_depots():
    log.info("Fetching depots from Affordmed evaluation service...")
    try:
        resp = requests.get(f"{BASE_URL}/depots", headers=HEADERS, timeout=10)
        resp.raise_for_status()
        depots = resp.json().get("depots", [])
        log.info(f"Successfully retrieved {len(depots)} operational depots.")
        return depots
    except requests.exceptions.RequestException as e:
        log.error(f"Failed to fetch depots: {e}")
        raise


def fetch_vehicles():
    log.info("Fetching vehicle profiles from Affordmed evaluation service...")
    try:
        resp = requests.get(f"{BASE_URL}/vehicles", headers=HEADERS, timeout=10)
        resp.raise_for_status()
        vehicles = resp.json().get("vehicles", [])
        log.info(f"Successfully retrieved {len(vehicles)} available task profiles.")
        return vehicles
    except requests.exceptions.RequestException as e:
        log.error(f"Failed to fetch vehicle profiles: {e}")
        raise


def knapsack_dp(vehicles: list, capacity: int) -> tuple[int, list]:
    log.info(f"Initiating DP matrix compute. Tasks: {len(vehicles)}, Budget capacity: {capacity}h")
    n = len(vehicles)
    dp = [0] * (capacity + 1)

    for task in vehicles:
        d = task["Duration"]
        imp = task["Impact"]
        for w in range(capacity, d - 1, -1):
            dp[w] = max(dp[w], dp[w - d] + imp)

    selected = []
    w = capacity
    for i in range(n - 1, -1, -1):
        d = vehicles[i]["Duration"]
        imp = vehicles[i]["Impact"]
        if w >= d and dp[w] == dp[w - d] + imp:
            selected.append(vehicles[i]["TaskID"])
            w -= d

    log.info(f"DP computation optimization complete. Peak score: {dp[capacity]}")
    return dp[capacity], selected


def knapsack_greedy(vehicles: list, capacity: int) -> tuple[int, list]:
    log.info("Running greedy approximation sort fallback...")
    sorted_tasks = sorted(vehicles, key=lambda t: t["Impact"] / t["Duration"], reverse=True)
    total_impact, total_duration = 0, 0
    selected = []
    
    for task in sorted_tasks:
        if total_duration + task["Duration"] <= capacity:
            selected.append(task["TaskID"])
            total_impact += task["Impact"]
            total_duration += task["Duration"]
    return total_impact, selected


def optimise_schedule(vehicles: list, capacity: int) -> dict:
    n = len(vehicles)
    if n == 0 or capacity == 0:
        return {"max_impact": 0, "selected_tasks": [], "total_duration": 0, "algorithm": "none"}

    complexity = n * capacity
    if complexity <= DP_THRESHOLD:
        max_impact, selected_ids = knapsack_dp(vehicles, capacity)
        algo = "dp_exact"
    else:
        log.warning(f"Complexity limit threshold passed ({complexity}). Switching to greedy fallback.")
        max_impact, selected_ids = knapsack_greedy(vehicles, capacity)
        algo = "greedy_approx"

    id_set = set(selected_ids)
    selected_details = [v for v in vehicles if v["TaskID"] in id_set]
    total_duration = sum(v["Duration"] for v in selected_details)

    return {
        "max_impact": max_impact,
        "selected_tasks": selected_details,
        "total_duration": total_duration,
        "budget": capacity,
        "algorithm": algo,
    }

def run():
    log.info("=== Starting Vehicle Maintenance Scheduler Hub ===")
    try:
        depots = fetch_depots()
        vehicles = fetch_vehicles()
    except Exception:
        log.critical("Halting pipeline due to upstream credential/network exceptions.")
        return

    all_results = []
    for depot in depots:
        depot_id = depot["ID"]
        budget = depot["MechanicHours"]
        
        log.info(f"Processing Optimization Set for Depot ID: {depot_id}")
        result = optimise_schedule(vehicles, budget)
        result["depot_id"] = depot_id
        all_results.append(result)

        # Print layout to console window for required evaluator screenshot
        print(f"\n{'='*65}")
        print(f"  DEPOT STATION {depot_id} | Global Allocation Budget: {budget} Hours")
        print(f"{'='*65}")
        print(f"  Execution Logic Matrix : {result['algorithm']}")
        print(f"  Total Operational Score: {result['max_impact']}")
        print(f"  Capacity Allocation    : {result['total_duration']}h consumed / {budget}h max")
        print(f"  Target Tasks Scheduled : {len(result['selected_tasks'])} units")
        print(f"\n  Scheduled Breakdown Trace:")
        print(f"  {'Task Unique Identifier (UUID)':<42} {'Duration':>10} {'Impact':>8}")
        print(f"  {'-'*62}")
        for task in result["selected_tasks"]:
            print(f"  {task['TaskID']:<42} {task['Duration']:>9}h {task['Impact']:>8}")
        print(f"{'='*65}\n")

    log.info("=== Process Finished. All depots updated and mapped. ===")
    return all_results


if __name__ == "__main__":
    run()