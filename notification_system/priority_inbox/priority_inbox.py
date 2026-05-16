import os
import sys
import heapq
import requests
from datetime import datetime, timezone

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
if REPO_ROOT not in sys.path:
    sys.path.append(REPO_ROOT)

try:
    from logging_middleware.logger import get_logger
    log = get_logger("priority_inbox")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger("priority_inbox")

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJiYWxhamkuazIwMjJiQHZpdHN0dWRlbnQuYWMuaW4iLCJleHAiOjE3Nzg5MzI3OTEsImlhdCI6MTc3ODkzMTg5MSwiaXNzIjoiQWZmb3JkIE1lZGljYWwgVGVjaG5vbG9naWVzIFByaXZhdGUgTGltaXRlZCIsImp0aSI6ImY0YmIxOGQ0LWNjYmMtNDlhMC04NTk4LTczZjMwMWU3NDhjNSIsImxvY2FsZSI6ImVuLUlOIiwibmFtZSI6ImJhbGFqaSBrIiwic3ViIjoiYTlhYmQyMWYtZTliMi00OGI4LWJjNTYtM2Y2MTIwOGMxZDhmIn0sImVtYWlsIjoiYmFsYWppLmsyMDIyYkB2aXRzdHVkZW50LmFjLmluIiwibmFtZSI6ImJhbGFqaSBrIiwicm9sbE5vIjoiMjJtaXMxMTk4IiwiYWNjZXNzQ29kZSI6IlNmRnVXZyIsImNsaWVudElEIjoiYTlhYmQyMWYtZTliMi00OGI4LWJjNTYtM2Y2MTIwOGMxZDhmIiwiY2xpZW50U2VjcmV0IjoiZ3R4dEZua1RCTnl6VHNVeiJ9.JXcLjyIkxxc7Xt3SZM6Yd3bW2F5fgqRR8H8YjD557U0"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}
API_URL = "http://4.224.186.213/evaluation-service/notifications"
TOP_N = 10

TYPE_WEIGHT = {
    "Placement": 3,
    "Result":    2,
    "Event":     1,
}


def compute_priority(notification: dict) -> float:
    type_weight = TYPE_WEIGHT.get(notification.get("Type"), 0)
    ts_str = notification.get("Timestamp")
    
    try:
        ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        ts = datetime.now(timezone.utc)
        
    now = datetime.now(timezone.utc)
    hours_elapsed = max((now - ts).total_seconds() / 3600, 0)
    recency_score = 1 / (1 + hours_elapsed)
    
    score = (type_weight * 10) + (recency_score * 10)
    return round(score, 4)


class PriorityInbox:
    def __init__(self, n: int):
        self.n = n
        self._heap = []
        self._counter = 0
        log.info(f"PriorityInbox tracking initialized for top-{n} positions.")

    def push(self, notification: dict):
        score = compute_priority(notification)
        entry = (score, self._counter, notification)
        self._counter += 1

        if len(self._heap) < self.n:
            heapq.heappush(self._heap, entry)
            log.info(f"Queued into inbox -> ID: {notification.get('ID', '')[:8]} | Score: {score}")
        elif score > self._heap[0][0]:
            evicted = heapq.heapreplace(self._heap, entry)
            log.info(f"Evicted low priority node [{evicted[2].get('ID', '')[:8]}] for high rank entry [{notification.get('ID', '')[:8]}]")
        else:
            log.info(f"Skipped node [{notification.get('ID', '')[:8]}] due to insufficient priority weight.")

    def top_n(self) -> list:
        return [entry[2] for entry in sorted(self._heap, reverse=True)]

    def add_incoming(self, notification: dict):
        log.info(f"Processing real-time microservice broadcast entry -> ID: {notification.get('ID', '')[:8]}")
        self.push(notification)


def main():
    log.info("=== Starting Real-time Priority Inbox Diagnostics ===")
    
    try:
        log.info("Requesting latest system notifications feed...")
        resp = requests.get(API_URL, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        notifications = resp.json().get("notifications", [])
        log.info(f"Successfully processed {len(notifications)} upstream messages.")
    except Exception as e:
        log.critical(f"Aborting operations channel: Network handshake error: {e}")
        return

    inbox = PriorityInbox(n=TOP_N)
    for notif in notifications:
        inbox.push(notif)

    top = inbox.top_n()

    print(f"\n{'='*75}")
    print(f"  ACTIVE TOP {TOP_N} PRIORITY NOTIFICATION INBOX")
    print(f"{'='*75}")
    print(f"  {'Rank':<5} {'Type':<12} {'Composite Score':<18} {'Timestamp':<22} {'Message'}")
    print(f"  {'-'*71}")
    for rank, notif in enumerate(top, 1):
        score = compute_priority(notif)
        print(f"  {rank:<5} {notif.get('Type'):<12} {score:<18.4f} {notif.get('Timestamp'):<22} {notif.get('Message')}")
    print(f"{'='*75}\n")

    log.info("Injecting simulated real-time placement data streams...")
    new_notifications = [
        {"ID": "sim-uuid-001", "Type": "Placement", "Message": "Amazon Web Services SDE hiring", "Timestamp": "2026-05-16 17:15:00"},
        {"ID": "sim-uuid-002", "Type": "Event",     "Message": "Annual Sports Meet Registration", "Timestamp": "2026-05-16 16:30:00"},
        {"ID": "sim-uuid-003", "Type": "Result",    "Message": "Comprehensive Viva-Voce Results", "Timestamp": "2026-05-16 17:10:00"},
    ]
    for notif in new_notifications:
        inbox.add_incoming(notif)

    print(f"\n{'='*75}")
    print(f"  MUTATED HIGH-PRIORITY INBOX STATE AFTER STREAM INJECTION")
    print(f"{'='*75}")
    print(f"  {'Rank':<5} {'Type':<12} {'Composite Score':<18} {'Timestamp':<22} {'Message'}")
    print(f"  {'-'*71}")
    for rank, notif in enumerate(inbox.top_n(), 1):
        score = compute_priority(notif)
        print(f"  {rank:<5} {notif.get('Type'):<12} {score:<18.4f} {notif.get('Timestamp'):<22} {notif.get('Message')}")
    print(f"{'='*75}\n")
    log.info("=== Inbox execution run complete ===")


if __name__ == "__main__":
    main()