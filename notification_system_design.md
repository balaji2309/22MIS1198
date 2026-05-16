Campus Notification System Design

---

Stage 1

 Overview

REST API design for a campus notification platform supporting real-time
updates for Placements, Events, and Results. Authentication is pre-authorised
(no login/registration required from this service).

---

Core Actions

| Action | Method | Endpoint |
|---|---|---|
| Fetch all notifications | GET | `/api/v1/notifications` |
| Fetch single notification | GET | `/api/v1/notifications/{id}` |
| Create notification | POST | `/api/v1/notifications` |
| Mark notification as read | PATCH | `/api/v1/notifications/{id}/read` |
| Mark all as read | PATCH | `/api/v1/notifications/read-all` |
| Delete a notification | DELETE | `/api/v1/notifications/{id}` |
| Get unread count | GET | `/api/v1/notifications/unread-count` |
| Get priority inbox (top n) | GET | `/api/v1/notifications/priority?n=10` |

---

 Endpoint Contracts
 GET `/api/v1/notifications`

Fetches paginated notifications for a student. Student identity comes from
a pre-authorised request header.

**Request Headers**