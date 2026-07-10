"""Demo data ported from src/data.ts.

Serves as the data source until SQL models are populated from the live
Second Course app (student users, food posters, posts, claims).
"""

from app.config import settings

UNIVERSITY = settings.university_name
DATE_RANGE = "Aug 2025 – Jun 2026"

MONTHS = ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun"]
POSTS_BY_MONTH = [42, 68, 91, 78, 55, 72, 88, 95, 102, 86, 70]
CLAIMS_BY_MONTH = [198, 312, 410, 356, 248, 334, 401, 438, 472, 398, 364]

HOURS = ["6a", "8a", "10a", "12p", "2p", "4p", "6p", "8p"]
CLAIMS_BY_HOUR = [12, 48, 92, 156, 134, 98, 64, 28]

LOCATIONS = [
    {"name": "Alumni Center", "posts": 312, "claim_rate": 76},
    {"name": "Student Union", "posts": 248, "claim_rate": 71},
    {"name": "Aztec Recreation", "posts": 186, "claim_rate": 52},
    {"name": "Engineering Quad", "posts": 142, "claim_rate": 64},
    {"name": "Campus Events", "posts": 98, "claim_rate": 58},
]

DEMAND_GRID = [
    [2, 4, 8, 12, 10, 6, 3, 1],
    [3, 6, 14, 18, 15, 9, 4, 2],
    [1, 3, 9, 11, 8, 5, 2, 1],
    [4, 8, 16, 20, 17, 11, 5, 2],
    [2, 5, 11, 14, 12, 7, 3, 1],
]

DEMAND_LOCATIONS = ["Alumni Ctr", "Student Union", "Aztec Rec", "Eng. Quad", "Events"]
DEMAND_TIMES = ["7–9a", "9–11a", "11a–1p", "1–3p", "3–5p", "5–7p", "7–9p", "9–11p"]

STAFF = [
    {
        "name": "Maria G.",
        "role": "Dining Hall Mgr",
        "posts": 142,
        "last_post": "Today, 11:40a",
        "avg_claim_min": 9.2,
        "utilization": "high",
    },
    {
        "name": "James T.",
        "role": "Events Catering",
        "posts": 118,
        "last_post": "Yesterday, 4:15p",
        "avg_claim_min": 11.8,
        "utilization": "high",
    },
    {
        "name": "Priya S.",
        "role": "Student Union",
        "posts": 96,
        "last_post": "3 days ago",
        "avg_claim_min": 14.1,
        "utilization": "medium",
    },
    {
        "name": "Alex R.",
        "role": "Aztec Recreation",
        "posts": 34,
        "last_post": "12 days ago",
        "avg_claim_min": 22.4,
        "utilization": "low",
    },
    {
        "name": "Chris L.",
        "role": "Campus Events",
        "posts": 18,
        "last_post": "21 days ago",
        "avg_claim_min": 31.6,
        "utilization": "low",
    },
]

POSTS = [
    {
        "id": "P-1042",
        "title": "Catered lunch surplus — sandwiches & fruit",
        "staff": "Maria G.",
        "location": "Alumni Center",
        "posted": "Jun 12, 11:35a",
        "posted_at": "2026-06-12T11:35",
        "claims": 28,
        "views": 41,
        "claim_rate": 68,
        "first_claim_min": 4.2,
        "allergens": "Gluten, dairy",
        "description": "Assorted wraps, fruit cups, and cookies from a 120-person conference.",
        "lbs_diverted": 42,
    },
    {
        "id": "P-1038",
        "title": "Pizza & salad bar leftovers",
        "staff": "James T.",
        "location": "Student Union",
        "posted": "Jun 11, 1:10p",
        "posted_at": "2026-06-11T13:10",
        "claims": 44,
        "views": 52,
        "claim_rate": 85,
        "first_claim_min": 3.1,
        "allergens": "Gluten, dairy, tree nuts",
        "description": "Whole pizzas and mixed greens from a student org mixer.",
        "lbs_diverted": 58,
    },
    {
        "id": "P-1031",
        "title": "Breakfast pastries & coffee service",
        "staff": "Priya S.",
        "location": "Engineering Quad",
        "posted": "Jun 10, 8:50a",
        "posted_at": "2026-06-10T08:50",
        "claims": 19,
        "views": 36,
        "claim_rate": 53,
        "first_claim_min": 18.7,
        "allergens": "Gluten, eggs, dairy",
        "description": "Croissants, muffins, and fruit from a morning department meeting.",
        "lbs_diverted": 24,
    },
    {
        "id": "P-1024",
        "title": "Post-game catering trays",
        "staff": "Alex R.",
        "location": "Aztec Recreation",
        "posted": "May 28, 6:20p",
        "posted_at": "2026-05-28T18:20",
        "claims": 8,
        "views": 22,
        "claim_rate": 36,
        "first_claim_min": 42.0,
        "allergens": "None listed",
        "description": "Chicken tenders, veggie trays, and bottled water from intramural finals.",
        "lbs_diverted": 16,
    },
]

WASTE_MONTHS = ["Aug", "Oct", "Dec", "Feb", "Apr", "Jun"]
WASTE_LBS = [180, 310, 420, 520, 680, 820]
CLIMATE_MONTHS = ["Aug", "Oct", "Dec", "Feb", "Apr", "Jun"]
CLIMATE_TCO2 = [0.08, 0.14, 0.19, 0.23, 0.3, 0.36]

SUMMARY = {
    "total_posts": 847,
    "total_claims": 4231,
    "claim_rate": 68,
    "avg_first_claim_min": 12.4,
    "lbs_diverted": 3420,
    "tco2e": 1.2,
    "hauling_savings": 4280,
}
