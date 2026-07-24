"""In-memory store for campus Resources (pantries, events, bulletin).

Skeleton mirroring services/user_store.py: routes depend only on the
`ResourcesStore` protocol, so a SqlResourcesStore or FirebaseResourcesStore can
drop in later without any route changes. Data is process-local and resets on
restart. Seeded from the same content as the frontend mock in src/appData.ts so
the API and the offline fallback stay in sync.
"""

from typing import Protocol
from uuid import uuid4

from app.schemas.resources import (
    BulletinItemIn,
    BulletinItemOut,
    PantryIn,
    PantryOut,
    ResourcesSnapshot,
    SpecialEventIn,
    SpecialEventOut,
)


class ResourcesStore(Protocol):
    def snapshot(self) -> ResourcesSnapshot: ...
    def add_pantry(self, payload: PantryIn) -> PantryOut: ...
    def update_pantry(self, pantry_id: str, payload: PantryIn) -> PantryOut | None: ...
    def delete_pantry(self, pantry_id: str) -> bool: ...
    def add_event(self, payload: SpecialEventIn) -> SpecialEventOut: ...
    def update_event(self, event_id: str, payload: SpecialEventIn) -> SpecialEventOut | None: ...
    def delete_event(self, event_id: str) -> bool: ...
    def add_bulletin(self, payload: BulletinItemIn) -> BulletinItemOut: ...
    def update_bulletin(self, item_id: str, payload: BulletinItemIn) -> BulletinItemOut | None: ...
    def delete_bulletin(self, item_id: str) -> bool: ...


def _new_id() -> str:
    return uuid4().hex


class InMemoryResourcesStore:
    """Process-local store, seeded on construction. Data resets on restart."""

    def __init__(self) -> None:
        # Insertion order is preserved, which drives the display order in the UI.
        self._pantries: dict[str, PantryOut] = {}
        self._events: dict[str, SpecialEventOut] = {}
        self._bulletin: dict[str, BulletinItemOut] = {}
        self._seed()

    def _seed(self) -> None:
        for pantry in _SEED_PANTRIES:
            self.add_pantry(pantry)
        for event in _SEED_EVENTS:
            self.add_event(event)
        for item in _SEED_BULLETIN:
            self.add_bulletin(item)

    def snapshot(self) -> ResourcesSnapshot:
        events: dict[int, list[SpecialEventOut]] = {}
        for event in self._events.values():
            events.setdefault(event.day, []).append(event)
        return ResourcesSnapshot(
            pantries=list(self._pantries.values()),
            events=events,
            bulletin=list(self._bulletin.values()),
        )

    def add_pantry(self, payload: PantryIn) -> PantryOut:
        pantry = PantryOut(id=_new_id(), **payload.model_dump())
        self._pantries[pantry.id] = pantry
        return pantry

    def update_pantry(self, pantry_id: str, payload: PantryIn) -> PantryOut | None:
        if pantry_id not in self._pantries:
            return None
        pantry = PantryOut(id=pantry_id, **payload.model_dump())
        self._pantries[pantry_id] = pantry
        return pantry

    def delete_pantry(self, pantry_id: str) -> bool:
        return self._pantries.pop(pantry_id, None) is not None

    def add_event(self, payload: SpecialEventIn) -> SpecialEventOut:
        event = SpecialEventOut(id=_new_id(), **payload.model_dump())
        self._events[event.id] = event
        return event

    def update_event(self, event_id: str, payload: SpecialEventIn) -> SpecialEventOut | None:
        if event_id not in self._events:
            return None
        event = SpecialEventOut(id=event_id, **payload.model_dump())
        self._events[event_id] = event
        return event

    def delete_event(self, event_id: str) -> bool:
        return self._events.pop(event_id, None) is not None

    def add_bulletin(self, payload: BulletinItemIn) -> BulletinItemOut:
        item = BulletinItemOut(id=_new_id(), **payload.model_dump())
        self._bulletin[item.id] = item
        return item

    def update_bulletin(self, item_id: str, payload: BulletinItemIn) -> BulletinItemOut | None:
        if item_id not in self._bulletin:
            return None
        item = BulletinItemOut(id=item_id, **payload.model_dump())
        self._bulletin[item_id] = item
        return item

    def delete_bulletin(self, item_id: str) -> bool:
        return self._bulletin.pop(item_id, None) is not None


# --- Seed content (mirrors src/appData.ts PANTRIES / SPECIAL_EVENTS / BULLETIN) ---

_SEED_PANTRIES: list[PantryIn] = [
    PantryIn(
        name="A.S. Food Pantry",
        location="Aztec Student Union, 2nd Floor Landing",
        emoji="🥫",
        note="All SDSU students with a Red ID. No proof of need required.",
        hours=[
            {"day": "Mon", "weekday": 1, "time": "10:00a – 2:00p"},
            {"day": "Wed", "weekday": 3, "time": "12:00p – 4:00p"},
            {"day": "Thu", "weekday": 4, "time": "1:00p – 6:00p"},
        ],
    ),
    PantryIn(
        name="Wesley House Food Pantry",
        location="5710 Hardy Ave (by Calpulli Center)",
        emoji="🏠",
        note="Free food for all students. Bring proof of enrollment. (Summer hours.)",
        hours=[
            {"day": "Mon", "weekday": 1, "time": "9:30a – 11:30a"},
            {"day": "Wed", "weekday": 3, "time": "1:30p – 4:00p"},
            {"day": "Fri", "weekday": 5, "time": "1:30p – 4:00p"},
        ],
    ),
]

_SEED_EVENTS: list[SpecialEventIn] = [
    SpecialEventIn(day=23, time="12p–1p", title="Free lunch on Aztec Lawn", tag="food", note="While supplies last"),
    SpecialEventIn(day=24, time="5p–7p", title="Community dinner (free)", tag="event", note="Newman Center"),
    SpecialEventIn(day=25, time="10a–12p", title="Mobile farmers market", tag="resource", note="Produce by donation"),
    SpecialEventIn(day=26, time="1p–3p", title="Leftover catering drop", tag="food", note="Posted live in Feed"),
    SpecialEventIn(day=29, time="3p–5p", title="CalFresh / EBT sign-up help", tag="resource", note="Student Union, Rm 120"),
]

_SEED_BULLETIN: list[BulletinItemIn] = [
    BulletinItemIn(
        kind="Recipe",
        title="3 no-cook meals from pantry staples",
        blurb="Chickpea salad wraps, peanut-banana oats, and a 5-minute tuna bowl — all under $2/serving.",
        emoji="🥗",
        content=[
            "No stove? No problem. These three meals use only pantry and fridge staples.",
            "Chickpea salad wrap: Mash 1 can of drained chickpeas with a fork. Stir in a spoon of mayo or mustard, a squeeze of lemon, and salt. Wrap in a tortilla with any greens.",
            "Peanut-banana overnight oats: Combine ½ cup oats, ½ cup milk (any kind), a spoon of peanut butter, and a sliced banana in a jar. Refrigerate overnight. Eat cold.",
            "5-minute tuna bowl: Drain 1 can of tuna over instant rice or crackers. Add hot sauce, a little mayo, and whatever veggies you have. Done.",
        ],
    ),
    BulletinItemIn(
        kind="Tip",
        title="Stretch your CalFresh dollars",
        blurb="Frozen veggies, store-brand grains, and shopping the 'manager's special' rack go a long way.",
        emoji="💸",
        content=[
            "CalFresh (California's SNAP/EBT program) can give eligible students up to ~$290/month. Make every dollar count:",
            "Buy frozen vegetables and fruit — same nutrition, no spoilage, often cheaper per serving.",
            "Choose store-brand grains, beans, and pasta. They're usually identical to name brands.",
            "Hit the 'manager's special' or markdown rack for meat and produce near its sell-by date, then freeze it.",
            "Plan meals around what's on sale, not the other way around.",
        ],
    ),
    BulletinItemIn(
        kind="Article",
        title="You're not alone: campus food insecurity",
        blurb="1 in 3 students experience it. Here are resources on campus you can use today — judgment-free.",
        emoji="📰",
        content=[
            "Roughly 1 in 3 college students experiences food insecurity at some point. It has nothing to do with effort or worth — costs are high and budgets are tight.",
            "On-campus resources you can use today, no questions asked:",
            "• A.S. Food Pantry — free groceries with your Red ID.",
            "• Wesley House Food Pantry — free food with proof of enrollment.",
            "• Second Course — claim free surplus food posted around campus in real time.",
            "• Basic Needs Center — CalFresh enrollment help, emergency grants, and more.",
            "Using these is normal and encouraged. They exist precisely so you can focus on school.",
        ],
    ),
    BulletinItemIn(
        kind="Recipe",
        title="Dorm-friendly microwave mug meals",
        blurb="Mac & cheese, veggie fried rice, and a brownie — one mug, one microwave, five minutes.",
        emoji="🍲",
        content=[
            "All you need is a microwave-safe mug and a few minutes.",
            "Mug mac & cheese: Combine ⅓ cup pasta and ½ cup water. Microwave 2–3 min (watch it). Stir in a splash of milk and a handful of shredded cheese.",
            "Veggie fried rice: Microwave leftover or instant rice with frozen mixed veggies and a beaten egg, stirring every 30 sec until the egg is set. Finish with soy sauce.",
            "Mug brownie: Mix 2 tbsp flour, 2 tbsp sugar, 1 tbsp cocoa, 2 tbsp oil, 2 tbsp water. Microwave ~60 sec. Treat yourself.",
        ],
    ),
]


resources_store: ResourcesStore = InMemoryResourcesStore()
