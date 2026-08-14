"""Campus Resources store (pantries, events, bulletin).

When Firestore is configured, reads and writes go to the mobile app's
`resources` / `bulletins` / `resourceEvents` collections so the university
dashboard and Second Course app stay in sync. Otherwise a process-local
in-memory seed is used so the demo still boots offline.
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
    def snapshot(self, university_id: str) -> ResourcesSnapshot: ...
    def add_pantry(self, university_id: str, payload: PantryIn) -> PantryOut: ...
    def update_pantry(
        self, university_id: str, pantry_id: str, payload: PantryIn
    ) -> PantryOut | None: ...
    def delete_pantry(self, university_id: str, pantry_id: str) -> bool: ...
    def add_event(self, university_id: str, payload: SpecialEventIn) -> SpecialEventOut: ...
    def update_event(
        self, university_id: str, event_id: str, payload: SpecialEventIn
    ) -> SpecialEventOut | None: ...
    def delete_event(self, university_id: str, event_id: str) -> bool: ...
    def add_bulletin(self, university_id: str, payload: BulletinItemIn) -> BulletinItemOut: ...
    def update_bulletin(
        self, university_id: str, item_id: str, payload: BulletinItemIn
    ) -> BulletinItemOut | None: ...
    def delete_bulletin(self, university_id: str, item_id: str) -> bool: ...


def _new_id() -> str:
    return uuid4().hex


class InMemoryResourcesStore:
    """Process-local store partitioned by university, seeded on construction."""

    def __init__(self) -> None:
        # {university_id: {record_id: record}} — insertion order drives display.
        self._pantries: dict[str, dict[str, PantryOut]] = {}
        self._events: dict[str, dict[str, SpecialEventOut]] = {}
        self._bulletin: dict[str, dict[str, BulletinItemOut]] = {}
        self._seed()

    def _ensure(self, university_id: str) -> None:
        self._pantries.setdefault(university_id, {})
        self._events.setdefault(university_id, {})
        self._bulletin.setdefault(university_id, {})

    def _seed(self) -> None:
        for university_id, seed in _SEED_BY_UNIVERSITY.items():
            self._ensure(university_id)
            for pantry in seed["pantries"]:
                self.add_pantry(university_id, pantry)
            for event in seed["events"]:
                self.add_event(university_id, event)
            for item in seed["bulletin"]:
                self.add_bulletin(university_id, item)

    def snapshot(self, university_id: str) -> ResourcesSnapshot:
        self._ensure(university_id)
        events: dict[int, list[SpecialEventOut]] = {}
        for event in self._events[university_id].values():
            events.setdefault(event.day, []).append(event)
        return ResourcesSnapshot(
            pantries=list(self._pantries[university_id].values()),
            events=events,
            bulletin=list(self._bulletin[university_id].values()),
        )

    def add_pantry(self, university_id: str, payload: PantryIn) -> PantryOut:
        self._ensure(university_id)
        pantry = PantryOut(id=_new_id(), **payload.model_dump())
        self._pantries[university_id][pantry.id] = pantry
        return pantry

    def update_pantry(
        self, university_id: str, pantry_id: str, payload: PantryIn
    ) -> PantryOut | None:
        self._ensure(university_id)
        if pantry_id not in self._pantries[university_id]:
            return None
        pantry = PantryOut(id=pantry_id, **payload.model_dump())
        self._pantries[university_id][pantry_id] = pantry
        return pantry

    def delete_pantry(self, university_id: str, pantry_id: str) -> bool:
        self._ensure(university_id)
        return self._pantries[university_id].pop(pantry_id, None) is not None

    def add_event(self, university_id: str, payload: SpecialEventIn) -> SpecialEventOut:
        self._ensure(university_id)
        event = SpecialEventOut(id=_new_id(), **payload.model_dump())
        self._events[university_id][event.id] = event
        return event

    def update_event(
        self, university_id: str, event_id: str, payload: SpecialEventIn
    ) -> SpecialEventOut | None:
        self._ensure(university_id)
        if event_id not in self._events[university_id]:
            return None
        event = SpecialEventOut(id=event_id, **payload.model_dump())
        self._events[university_id][event_id] = event
        return event

    def delete_event(self, university_id: str, event_id: str) -> bool:
        self._ensure(university_id)
        return self._events[university_id].pop(event_id, None) is not None

    def add_bulletin(self, university_id: str, payload: BulletinItemIn) -> BulletinItemOut:
        self._ensure(university_id)
        item = BulletinItemOut(id=_new_id(), **payload.model_dump())
        self._bulletin[university_id][item.id] = item
        return item

    def update_bulletin(
        self, university_id: str, item_id: str, payload: BulletinItemIn
    ) -> BulletinItemOut | None:
        self._ensure(university_id)
        if item_id not in self._bulletin[university_id]:
            return None
        item = BulletinItemOut(id=item_id, **payload.model_dump())
        self._bulletin[university_id][item_id] = item
        return item

    def delete_bulletin(self, university_id: str, item_id: str) -> bool:
        self._ensure(university_id)
        return self._bulletin[university_id].pop(item_id, None) is not None


# --- Seed content -----------------------------------------------------------
# SDSU mirrors src/appData.ts; other campuses get campus-specific pantries and
# events so each tenant renders as its own deployment. Bulletin tips are generic
# and shared across campuses.

_SDSU_PANTRIES: list[PantryIn] = [
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

_SDSU_EVENTS: list[SpecialEventIn] = [
    SpecialEventIn(day=23, time="12p–1p", title="Free lunch on Aztec Lawn", tag="food", note="While supplies last"),
    SpecialEventIn(day=24, time="5p–7p", title="Community dinner (free)", tag="event", note="Newman Center"),
    SpecialEventIn(day=25, time="10a–12p", title="Mobile farmers market", tag="resource", note="Produce by donation"),
    SpecialEventIn(day=26, time="1p–3p", title="Leftover catering drop", tag="food", note="Posted live in Feed"),
    SpecialEventIn(day=29, time="3p–5p", title="CalFresh / EBT sign-up help", tag="resource", note="Student Union, Rm 120"),
]

_UCSD_PANTRIES: list[PantryIn] = [
    PantryIn(
        name="The Hub Triton Food Pantry",
        location="Original Student Center, Ground Floor",
        emoji="🔱",
        note="Free groceries for all UC San Diego students. Swipe your ID.",
        hours=[
            {"day": "Mon", "weekday": 1, "time": "11:00a – 6:00p"},
            {"day": "Wed", "weekday": 3, "time": "11:00a – 6:00p"},
            {"day": "Fri", "weekday": 5, "time": "10:00a – 3:00p"},
        ],
    ),
    PantryIn(
        name="Basic Needs Hub",
        location="Price Center East, Level 3",
        emoji="🥑",
        note="CalFresh help, produce pop-ups, and emergency food support.",
        hours=[
            {"day": "Tue", "weekday": 2, "time": "10:00a – 4:00p"},
            {"day": "Thu", "weekday": 4, "time": "10:00a – 4:00p"},
        ],
    ),
]

_UCSD_EVENTS: list[SpecialEventIn] = [
    SpecialEventIn(day=22, time="12p–2p", title="Triton Farmers Market", tag="resource", note="Town Square"),
    SpecialEventIn(day=24, time="5p–7p", title="Free community dinner", tag="food", note="The Village"),
    SpecialEventIn(day=27, time="1p–3p", title="Surplus catering drop", tag="food", note="Posted live in Feed"),
    SpecialEventIn(day=30, time="3p–5p", title="CalFresh sign-up help", tag="resource", note="Price Center East L3"),
]

_CSULB_PANTRIES: list[PantryIn] = [
    PantryIn(
        name="ASI Beach Pantry",
        location="University Student Union, Room 229",
        emoji="🏖️",
        note="Free food for all CSULB students. Bring your BeachID.",
        hours=[
            {"day": "Mon", "weekday": 1, "time": "10:00a – 4:00p"},
            {"day": "Wed", "weekday": 3, "time": "10:00a – 4:00p"},
            {"day": "Thu", "weekday": 4, "time": "12:00p – 6:00p"},
        ],
    ),
]

_CSULB_EVENTS: list[SpecialEventIn] = [
    SpecialEventIn(day=23, time="12p–1p", title="Free lunch on Friendship Walk", tag="food", note="While supplies last"),
    SpecialEventIn(day=26, time="10a–12p", title="Mobile farmers market", tag="resource", note="Central Quad"),
    SpecialEventIn(day=28, time="3p–5p", title="CalFresh / EBT sign-up help", tag="resource", note="USU Room 229"),
]

_SWC_PANTRIES: list[PantryIn] = [
    PantryIn(
        name="Jaguar Food Pantry",
        location="Cesar Chavez Building, Room 101",
        emoji="🐆",
        note="Free groceries for all Southwestern College students. No ID needed.",
        hours=[
            {"day": "Tue", "weekday": 2, "time": "9:00a – 1:00p"},
            {"day": "Thu", "weekday": 4, "time": "1:00p – 5:00p"},
        ],
    ),
]

_SWC_EVENTS: list[SpecialEventIn] = [
    SpecialEventIn(day=25, time="11a–1p", title="Free lunch at Mayan Hall", tag="food", note="While supplies last"),
    SpecialEventIn(day=29, time="2p–4p", title="CalFresh sign-up help", tag="resource", note="LRC Library"),
]

_SHARED_BULLETIN: list[BulletinItemIn] = [
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
            "Check your campus pantry and Basic Needs Center for free groceries, CalFresh enrollment help, and emergency grants.",
            "Second Course — claim free surplus food posted around campus in real time.",
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

_SEED_BY_UNIVERSITY: dict[str, dict[str, list]] = {
    "sdsu": {"pantries": _SDSU_PANTRIES, "events": _SDSU_EVENTS, "bulletin": _SHARED_BULLETIN},
    "ucsd": {"pantries": _UCSD_PANTRIES, "events": _UCSD_EVENTS, "bulletin": _SHARED_BULLETIN},
    "csulb": {"pantries": _CSULB_PANTRIES, "events": _CSULB_EVENTS, "bulletin": _SHARED_BULLETIN},
    "southwestern": {"pantries": _SWC_PANTRIES, "events": _SWC_EVENTS, "bulletin": _SHARED_BULLETIN},
}


class _FirestoreBackedResourcesStore:
    """Prefer Firestore; fall back to the in-memory seed when it is unavailable."""

    def __init__(self) -> None:
        self._memory = InMemoryResourcesStore()

    def _live(self):
        from app.services.firestore_client import firestore_enabled, get_client
        from app.services.firestore_resources import FirestoreResourcesStore

        if not firestore_enabled() or get_client() is None:
            return None
        return FirestoreResourcesStore()

    def snapshot(self, university_id: str) -> ResourcesSnapshot:
        live = self._live()
        if live is None:
            return self._memory.snapshot(university_id)
        try:
            return live.snapshot(university_id)
        except Exception as exc:
            import logging

            logging.getLogger(__name__).warning(
                "Firestore resources snapshot failed, using in-memory seed: %s", exc
            )
            return self._memory.snapshot(university_id)

    def add_pantry(self, university_id: str, payload: PantryIn) -> PantryOut:
        live = self._live()
        if live is None:
            return self._memory.add_pantry(university_id, payload)
        return live.add_pantry(university_id, payload)

    def update_pantry(
        self, university_id: str, pantry_id: str, payload: PantryIn
    ) -> PantryOut | None:
        live = self._live()
        if live is None:
            return self._memory.update_pantry(university_id, pantry_id, payload)
        return live.update_pantry(university_id, pantry_id, payload)

    def delete_pantry(self, university_id: str, pantry_id: str) -> bool:
        live = self._live()
        if live is None:
            return self._memory.delete_pantry(university_id, pantry_id)
        return live.delete_pantry(university_id, pantry_id)

    def add_event(self, university_id: str, payload: SpecialEventIn) -> SpecialEventOut:
        live = self._live()
        if live is None:
            return self._memory.add_event(university_id, payload)
        return live.add_event(university_id, payload)

    def update_event(
        self, university_id: str, event_id: str, payload: SpecialEventIn
    ) -> SpecialEventOut | None:
        live = self._live()
        if live is None:
            return self._memory.update_event(university_id, event_id, payload)
        return live.update_event(university_id, event_id, payload)

    def delete_event(self, university_id: str, event_id: str) -> bool:
        live = self._live()
        if live is None:
            return self._memory.delete_event(university_id, event_id)
        return live.delete_event(university_id, event_id)

    def add_bulletin(self, university_id: str, payload: BulletinItemIn) -> BulletinItemOut:
        live = self._live()
        if live is None:
            return self._memory.add_bulletin(university_id, payload)
        return live.add_bulletin(university_id, payload)

    def update_bulletin(
        self, university_id: str, item_id: str, payload: BulletinItemIn
    ) -> BulletinItemOut | None:
        live = self._live()
        if live is None:
            return self._memory.update_bulletin(university_id, item_id, payload)
        return live.update_bulletin(university_id, item_id, payload)

    def delete_bulletin(self, university_id: str, item_id: str) -> bool:
        live = self._live()
        if live is None:
            return self._memory.delete_bulletin(university_id, item_id)
        return live.delete_bulletin(university_id, item_id)


resources_store: ResourcesStore = _FirestoreBackedResourcesStore()
