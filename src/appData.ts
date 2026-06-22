// Mock content shared by the Mobile App and Web App demos.

export type ChatMessage = {
  from: "poster" | "claimer";
  name: string;
  text: string;
};

export type FeedPost = {
  id: string;
  title: string;
  org: string;
  poster: string;
  location: string;
  distance: string;
  posted: string;
  window: string;
  servings: number;
  claimed: number;
  allergens: string[];
  emoji: string;
  description: string;
  seedChat: ChatMessage[];
};

export const FEED_POSTS: FeedPost[] = [
  {
    id: "p1",
    title: "Catered sandwiches & salads",
    org: "Alumni Center",
    poster: "Maria G.",
    location: "Alumni Center, Lobby",
    distance: "0.2 mi",
    posted: "5 min ago",
    window: "Until 2:30 PM",
    servings: 30,
    claimed: 12,
    allergens: ["Gluten", "Dairy"],
    emoji: "🥪",
    description:
      "Leftover boxed lunches from a donor breakfast. Turkey, veggie, and caprese sandwiches plus garden salads. Come to the front lobby and ask for Maria.",
    seedChat: [
      { from: "claimer", name: "Jordan", text: "Are the veggie ones vegan or just vegetarian?" },
      { from: "poster", name: "Maria G.", text: "Vegetarian — they have cheese. The garden salads are vegan though!" },
    ],
  },
  {
    id: "p2",
    title: "Pizza from club meeting",
    org: "Engineering Society",
    poster: "James T.",
    location: "Engineering Bldg, Room 204",
    distance: "0.4 mi",
    posted: "18 min ago",
    window: "Until 6:00 PM",
    servings: 24,
    claimed: 19,
    allergens: ["Gluten", "Dairy"],
    emoji: "🍕",
    description:
      "About 4 boxes left from our weekly meeting — cheese and pepperoni. Room 204, second floor. Door is propped open.",
    seedChat: [
      { from: "claimer", name: "Priya", text: "Any cheese-only boxes left?" },
      { from: "poster", name: "James T.", text: "Yep, 2 full cheese boxes still here." },
    ],
  },
  {
    id: "p3",
    title: "Bagels & cream cheese",
    org: "Library Front Desk",
    poster: "Dana W.",
    location: "Love Library, Entrance",
    distance: "0.1 mi",
    posted: "32 min ago",
    window: "Until 11:00 AM",
    servings: 40,
    claimed: 33,
    allergens: ["Gluten", "Dairy"],
    emoji: "🥯",
    description:
      "Assorted bagels from a morning event. Plain, everything, and blueberry, with tubs of cream cheese. Grab-and-go at the library entrance.",
    seedChat: [],
  },
];

// Guaranteed weekly food pantries near campus. `days` uses JS weekday numbers
// (0 = Sun … 6 = Sat) so the calendar can mark recurring pantry days automatically.
export type Pantry = {
  name: string;
  location: string;
  emoji: string;
  note: string;
  hours: { day: string; weekday: number; time: string }[];
};

export const PANTRIES: Pantry[] = [
  {
    name: "A.S. Food Pantry",
    location: "Aztec Student Union, 2nd Floor Landing",
    emoji: "🥫",
    note: "All SDSU students with a Red ID. No proof of need required.",
    hours: [
      { day: "Mon", weekday: 1, time: "10:00a – 2:00p" },
      { day: "Wed", weekday: 3, time: "12:00p – 4:00p" },
      { day: "Thu", weekday: 4, time: "1:00p – 6:00p" },
    ],
  },
  {
    name: "Wesley House Food Pantry",
    location: "5710 Hardy Ave (by Calpulli Center)",
    emoji: "🏠",
    note: "Free food for all students. Bring proof of enrollment. (Summer hours.)",
    hours: [
      { day: "Mon", weekday: 1, time: "9:30a – 11:30a" },
      { day: "Wed", weekday: 3, time: "1:30p – 4:00p" },
      { day: "Fri", weekday: 5, time: "1:30p – 4:00p" },
    ],
  },
];

// One-off events keyed by day-of-month for the current demo month (June 2026).
export type SpecialEvent = {
  time: string;
  title: string;
  tag: "food" | "resource" | "event";
  note?: string;
};

export const SPECIAL_EVENTS: Record<number, SpecialEvent[]> = {
  23: [{ time: "12p–1p", title: "Free lunch on Aztec Lawn", tag: "food", note: "While supplies last" }],
  24: [{ time: "5p–7p", title: "Community dinner (free)", tag: "event", note: "Newman Center" }],
  25: [{ time: "10a–12p", title: "Mobile farmers market", tag: "resource", note: "Produce by donation" }],
  26: [{ time: "1p–3p", title: "Leftover catering drop", tag: "food", note: "Posted live in Feed" }],
  29: [{ time: "3p–5p", title: "CalFresh / EBT sign-up help", tag: "resource", note: "Student Union, Rm 120" }],
};

export type BulletinItem = {
  kind: "Article" | "Recipe" | "Tip";
  title: string;
  blurb: string;
  emoji: string;
  content: string[];
};

export const BULLETIN: BulletinItem[] = [
  {
    kind: "Recipe",
    title: "3 no-cook meals from pantry staples",
    blurb: "Chickpea salad wraps, peanut-banana oats, and a 5-minute tuna bowl — all under $2/serving.",
    emoji: "🥗",
    content: [
      "No stove? No problem. These three meals use only pantry and fridge staples.",
      "Chickpea salad wrap: Mash 1 can of drained chickpeas with a fork. Stir in a spoon of mayo or mustard, a squeeze of lemon, and salt. Wrap in a tortilla with any greens.",
      "Peanut-banana overnight oats: Combine ½ cup oats, ½ cup milk (any kind), a spoon of peanut butter, and a sliced banana in a jar. Refrigerate overnight. Eat cold.",
      "5-minute tuna bowl: Drain 1 can of tuna over instant rice or crackers. Add hot sauce, a little mayo, and whatever veggies you have. Done.",
    ],
  },
  {
    kind: "Tip",
    title: "Stretch your CalFresh dollars",
    blurb: "Frozen veggies, store-brand grains, and shopping the 'manager's special' rack go a long way.",
    emoji: "💸",
    content: [
      "CalFresh (California's SNAP/EBT program) can give eligible students up to ~$290/month. Make every dollar count:",
      "Buy frozen vegetables and fruit — same nutrition, no spoilage, often cheaper per serving.",
      "Choose store-brand grains, beans, and pasta. They're usually identical to name brands.",
      "Hit the 'manager's special' or markdown rack for meat and produce near its sell-by date, then freeze it.",
      "Plan meals around what's on sale, not the other way around.",
    ],
  },
  {
    kind: "Article",
    title: "You're not alone: campus food insecurity",
    blurb: "1 in 3 students experience it. Here are resources on campus you can use today — judgment-free.",
    emoji: "📰",
    content: [
      "Roughly 1 in 3 college students experiences food insecurity at some point. It has nothing to do with effort or worth — costs are high and budgets are tight.",
      "On-campus resources you can use today, no questions asked:",
      "• A.S. Food Pantry — free groceries with your Red ID.",
      "• Wesley House Food Pantry — free food with proof of enrollment.",
      "• Second Course — claim free surplus food posted around campus in real time.",
      "• Basic Needs Center — CalFresh enrollment help, emergency grants, and more.",
      "Using these is normal and encouraged. They exist precisely so you can focus on school.",
    ],
  },
  {
    kind: "Recipe",
    title: "Dorm-friendly microwave mug meals",
    blurb: "Mac & cheese, veggie fried rice, and a brownie — one mug, one microwave, five minutes.",
    emoji: "🍲",
    content: [
      "All you need is a microwave-safe mug and a few minutes.",
      "Mug mac & cheese: Combine ⅓ cup pasta and ½ cup water. Microwave 2–3 min (watch it). Stir in a splash of milk and a handful of shredded cheese.",
      "Veggie fried rice: Microwave leftover or instant rice with frozen mixed veggies and a beaten egg, stirring every 30 sec until the egg is set. Finish with soy sauce.",
      "Mug brownie: Mix 2 tbsp flour, 2 tbsp sugar, 1 tbsp cocoa, 2 tbsp oil, 2 tbsp water. Microwave ~60 sec. Treat yourself.",
    ],
  },
];

export type Offer = {
  id: string;
  business: string;
  deal: string;
  detail: string;
  distance: string;
  emoji: string;
  code: string;
  expires: string;
};

export const OFFERS: Offer[] = [
  {
    id: "o1",
    business: "Lolita's Taco Shop",
    deal: "Free drink with any burrito",
    detail: "Show this screen at the College Ave location. One per student per day.",
    distance: "0.3 mi",
    emoji: "🌮",
    code: "SC-LOLITA",
    expires: "Jun 30",
  },
  {
    id: "o2",
    business: "Oggi's Pizza",
    deal: "20% off your order",
    detail: "Dine-in or takeout. Not combinable with other offers.",
    distance: "0.6 mi",
    emoji: "🍕",
    code: "SC-OGGI20",
    expires: "Jul 15",
  },
  {
    id: "o3",
    business: "Pekoe Tea & Coffee",
    deal: "$1 off any boba",
    detail: "Valid all day, every day during finals season.",
    distance: "0.2 mi",
    emoji: "🧋",
    code: "SC-PEKOE1",
    expires: "Jul 1",
  },
  {
    id: "o4",
    business: "The Habit",
    deal: "Free fries with Charburger",
    detail: "College Area location only. Mention Second Course.",
    distance: "0.8 mi",
    emoji: "🍟",
    code: "SC-HABIT",
    expires: "Jun 28",
  },
];
