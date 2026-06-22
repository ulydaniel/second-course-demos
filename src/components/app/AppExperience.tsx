import { useMemo, useRef, useState } from "react";
import {
  BULLETIN,
  FEED_POSTS,
  OFFERS,
  PANTRIES,
  SPECIAL_EVENTS,
  type BulletinItem,
  type ChatMessage,
  type FeedPost,
} from "../../appData";

const BASE = import.meta.env.BASE_URL;

type TabId = "feed" | "posts" | "resources" | "offers" | "profile";

const TABS: { id: TabId; label: string; icon: string; emoji: string; badge?: boolean }[] = [
  { id: "feed", label: "Feed", icon: `${BASE}images/sc-home-tab.png`, emoji: "🍎" },
  { id: "posts", label: "Posts", icon: `${BASE}images/sc-post-tab.png`, emoji: "➕" },
  { id: "resources", label: "Resources", icon: "", emoji: "📅", badge: true },
  { id: "offers", label: "Offers", icon: "", emoji: "🎟️", badge: true },
  { id: "profile", label: "Profile", icon: `${BASE}images/sc-profile-banana.png`, emoji: "🍌" },
];

/* ---------------------------------- Feed ---------------------------------- */

function AllergenPills({ allergens }: { allergens: string[] }) {
  return (
    <div className="flex flex-wrap gap-1">
      {allergens.map((a) => (
        <span
          key={a}
          className="rounded-full border-2 border-black bg-scOrange/20 px-2 py-0.5 text-[11px]"
        >
          {a}
        </span>
      ))}
    </div>
  );
}

function ProgressBar({ value, max }: { value: number; max: number }) {
  const pct = Math.min(100, Math.round((value / max) * 100));
  return (
    <div className="h-2.5 w-full overflow-hidden rounded-full border-2 border-black bg-white">
      <div className="h-full rounded-full bg-scGreen" style={{ width: `${pct}%` }} />
    </div>
  );
}

function FeedScreen({ onOpen }: { onOpen: (post: FeedPost) => void }) {
  return (
    <div className="space-y-4">
      <div className="flex items-baseline justify-between">
        <h2 className="font-display text-2xl">Free food near you</h2>
        <span className="text-xs text-black/60">SDSU</span>
      </div>
      {FEED_POSTS.map((post) => {
        const remaining = post.servings - post.claimed;
        return (
          <button
            key={post.id}
            type="button"
            onClick={() => onOpen(post)}
            className="card block w-full p-4 text-left transition-transform hover:-translate-y-0.5"
          >
            <div className="flex gap-3">
              <div className="grid h-14 w-14 shrink-0 place-items-center rounded-xl border-2 border-black bg-cream text-3xl">
                {post.emoji}
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="font-display text-lg leading-tight">{post.title}</h3>
                  <span className="shrink-0 text-xs text-black/60">{post.posted}</span>
                </div>
                <p className="text-sm text-black/70">
                  {post.org} · {post.distance}
                </p>
                <div className="mt-2 flex items-center justify-between gap-2">
                  <span className="text-xs font-semibold text-brandGreen">
                    {remaining} of {post.servings} left
                  </span>
                  <span className="text-xs text-black/60">{post.window}</span>
                </div>
                <div className="mt-1.5">
                  <ProgressBar value={post.claimed} max={post.servings} />
                </div>
                <div className="mt-2">
                  <AllergenPills allergens={post.allergens} />
                </div>
              </div>
            </div>
          </button>
        );
      })}
    </div>
  );
}

/* ------------------------------ Post + chat ------------------------------- */

function PostDetail({ post, onBack }: { post: FeedPost; onBack: () => void }) {
  const [claimed, setClaimed] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>(post.seedChat);
  const [draft, setDraft] = useState("");
  const scroller = useRef<HTMLDivElement>(null);

  function send() {
    const text = draft.trim();
    if (!text) return;
    const next: ChatMessage[] = [...messages, { from: "claimer", name: "You", text }];
    setMessages(next);
    setDraft("");
    // Simulate the poster replying.
    setTimeout(() => {
      setMessages((m) => [
        ...m,
        {
          from: "poster",
          name: post.poster,
          text: "Thanks for asking! Yep, still plenty here — come on by 🙂",
        },
      ]);
      scroller.current?.scrollTo({ top: scroller.current.scrollHeight, behavior: "smooth" });
    }, 900);
  }

  return (
    <div className="space-y-4">
      <button type="button" onClick={onBack} className="text-sm font-semibold underline">
        ← Back to feed
      </button>

      <div className="grid h-40 place-items-center rounded-2xl border-4 border-black bg-cream text-6xl">
        {post.emoji}
      </div>

      <div>
        <h2 className="font-display text-2xl leading-tight">{post.title}</h2>
        <p className="text-sm text-black/70">
          {post.org} · posted by {post.poster} · {post.posted}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-2 text-sm">
        <div className="rounded-xl border-2 border-black bg-white px-3 py-2">
          <div className="text-black/60 text-xs">Pickup window</div>
          <div className="font-semibold">{post.window}</div>
        </div>
        <div className="rounded-xl border-2 border-black bg-white px-3 py-2">
          <div className="text-black/60 text-xs">Location</div>
          <div className="font-semibold">{post.location}</div>
        </div>
      </div>

      <AllergenPills allergens={post.allergens} />
      <p className="text-sm text-black/80">{post.description}</p>

      <button
        type="button"
        onClick={() => setClaimed((c) => !c)}
        className={`w-full rounded-xl border-2 border-black px-4 py-3 font-semibold ${
          claimed ? "bg-scYellow" : "bg-scGreen"
        }`}
        style={{ boxShadow: "3px 3px 0 rgba(0,0,0,0.25)" }}
      >
        {claimed ? "✓ Claimed — show this at pickup" : "Claim a serving"}
      </button>

      {/* Live chat */}
      <div className="rounded-2xl border-4 border-black bg-white" style={{ boxShadow: "6px 6px 0 rgba(0,0,0,0.3)" }}>
        <div className="flex items-center justify-between border-b-2 border-black px-4 py-2">
          <h3 className="font-display text-lg">Ask the poster</h3>
          <span className="flex items-center gap-1 text-xs text-brandGreen">
            <span className="h-2 w-2 rounded-full bg-brandGreen" /> Live
          </span>
        </div>
        <div ref={scroller} className="max-h-56 space-y-2 overflow-y-auto px-4 py-3">
          {messages.length === 0 ? (
            <p className="py-4 text-center text-sm text-black/50">
              No questions yet. Ask about ingredients, directions, or how much is left.
            </p>
          ) : (
            messages.map((m, i) => (
              <div key={i} className={`flex ${m.from === "claimer" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[80%] rounded-2xl border-2 border-black px-3 py-1.5 text-sm ${
                    m.from === "claimer" ? "bg-scGreen/30" : "bg-cream"
                  }`}
                >
                  <div className="text-[10px] font-semibold text-black/60">{m.name}</div>
                  {m.text}
                </div>
              </div>
            ))
          )}
        </div>
        <div className="flex items-center gap-2 border-t-2 border-black px-3 py-2">
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="Type a question…"
            className="flex-1 rounded-full border-2 border-black px-3 py-1.5 text-sm outline-none"
          />
          <button
            type="button"
            onClick={send}
            className="rounded-full border-2 border-black bg-scGreen px-4 py-1.5 text-sm font-semibold"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

/* ------------------------------- Posts tab -------------------------------- */

function PostsScreen() {
  return (
    <div className="space-y-4">
      <h2 className="font-display text-2xl">Your posts</h2>
      <button
        type="button"
        className="w-full rounded-xl border-2 border-black bg-scGreen px-4 py-3 font-semibold"
        style={{ boxShadow: "3px 3px 0 rgba(0,0,0,0.25)" }}
      >
        + Post free food
      </button>
      {FEED_POSTS.slice(0, 2).map((post) => (
        <div key={post.id} className="card p-4">
          <div className="flex items-center justify-between">
            <h3 className="font-display text-lg">{post.title}</h3>
            <span className="rounded-full border-2 border-black bg-scGreen/30 px-2 py-0.5 text-xs">
              Active
            </span>
          </div>
          <p className="mt-1 text-sm text-black/70">
            {post.claimed} of {post.servings} claimed · {post.window}
          </p>
          <div className="mt-2">
            <ProgressBar value={post.claimed} max={post.servings} />
          </div>
        </div>
      ))}
    </div>
  );
}

/* ----------------------------- Resources tab ------------------------------ */

function tagStyle(tag: "food" | "resource" | "event") {
  if (tag === "food") return "bg-scGreen/30";
  if (tag === "event") return "bg-scPink/30";
  return "bg-scYellow/40";
}

const MONTH_LABEL = "June 2026";
const MONTH_YEAR = 2026;
const MONTH_INDEX = 5; // June (0-based)
const WEEKDAY_LABELS = ["S", "M", "T", "W", "T", "F", "S"];

function pantriesOpenOn(weekday: number) {
  return PANTRIES.map((p) => ({
    pantry: p,
    slot: p.hours.find((h) => h.weekday === weekday),
  })).filter((x) => x.slot);
}

function BulletinModal({ item, onClose }: { item: BulletinItem; onClose: () => void }) {
  return (
    <div
      className="absolute inset-0 z-30 flex items-end justify-center bg-black/40 p-3"
      onClick={onClose}
    >
      <div
        className="max-h-[88%] w-full overflow-y-auto rounded-2xl border-4 border-black bg-white p-5"
        style={{ boxShadow: "6px 6px 0 rgba(0,0,0,0.3)" }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-3 flex items-start justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="text-3xl">{item.emoji}</span>
            <span className="rounded-full border-2 border-black bg-scYellow/40 px-2 py-0.5 text-[10px] font-semibold uppercase">
              {item.kind}
            </span>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="grid h-8 w-8 shrink-0 place-items-center rounded-full border-2 border-black bg-white text-lg leading-none"
          >
            ×
          </button>
        </div>
        <h3 className="font-display text-2xl leading-tight">{item.title}</h3>
        <div className="mt-3 space-y-2">
          {item.content.map((para, i) => (
            <p key={i} className="text-sm text-black/80">
              {para}
            </p>
          ))}
        </div>
      </div>
    </div>
  );
}

function ResourcesScreen() {
  const firstWeekday = new Date(MONTH_YEAR, MONTH_INDEX, 1).getDay();
  const daysInMonth = new Date(MONTH_YEAR, MONTH_INDEX + 1, 0).getDate();
  const [selected, setSelected] = useState(22); // demo "today"
  const [openItem, setOpenItem] = useState<BulletinItem | null>(null);

  const cells: (number | null)[] = [
    ...Array(firstWeekday).fill(null),
    ...Array.from({ length: daysInMonth }, (_, i) => i + 1),
  ];

  const selectedWeekday = new Date(MONTH_YEAR, MONTH_INDEX, selected).getDay();
  const selectedPantries = pantriesOpenOn(selectedWeekday);
  const selectedSpecial = SPECIAL_EVENTS[selected] ?? [];

  return (
    <div className="space-y-5">
      <div>
        <h2 className="font-display text-2xl">Campus resources</h2>
        <p className="text-sm text-black/70">
          Weekly pantries, a what's-on calendar, and a bulletin board.
        </p>
      </div>

      {/* Weekly pantries */}
      <div>
        <h3 className="mb-2 font-display text-xl">Weekly food pantries</h3>
        <div className="space-y-3">
          {PANTRIES.map((p) => (
            <div key={p.name} className="card p-3">
              <div className="flex gap-3">
                <div className="grid h-11 w-11 shrink-0 place-items-center rounded-xl border-2 border-black bg-cream text-2xl">
                  {p.emoji}
                </div>
                <div className="min-w-0">
                  <h4 className="font-display text-base leading-tight">{p.name}</h4>
                  <p className="text-xs text-black/60">{p.location}</p>
                </div>
              </div>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {p.hours.map((h) => (
                  <span
                    key={h.day}
                    className="rounded-md border-2 border-black bg-scGreen/20 px-2 py-0.5 text-[11px] font-semibold"
                  >
                    {h.day} {h.time}
                  </span>
                ))}
              </div>
              <p className="mt-2 text-xs text-black/60">{p.note}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Calendar */}
      <div>
        <h3 className="mb-2 font-display text-xl">{MONTH_LABEL}</h3>
        <div className="card p-3">
          <div className="mb-1 grid grid-cols-7 gap-1 text-center text-[11px] font-semibold text-black/50">
            {WEEKDAY_LABELS.map((d, i) => (
              <div key={i}>{d}</div>
            ))}
          </div>
          <div className="grid grid-cols-7 gap-1">
            {cells.map((day, i) => {
              if (day === null) return <div key={`e${i}`} />;
              const weekday = new Date(MONTH_YEAR, MONTH_INDEX, day).getDay();
              const hasPantry = pantriesOpenOn(weekday).length > 0;
              const hasEvent = Boolean(SPECIAL_EVENTS[day]);
              const isSelected = day === selected;
              return (
                <button
                  key={day}
                  type="button"
                  onClick={() => setSelected(day)}
                  className={`flex aspect-square flex-col items-center justify-center rounded-lg border-2 text-sm ${
                    isSelected
                      ? "border-black bg-scYellow font-bold"
                      : "border-transparent hover:bg-cream/60"
                  }`}
                >
                  {day}
                  <span className="mt-0.5 flex h-1.5 gap-0.5">
                    {hasPantry ? <span className="h-1.5 w-1.5 rounded-full bg-scGreen" /> : null}
                    {hasEvent ? <span className="h-1.5 w-1.5 rounded-full bg-scPink" /> : null}
                  </span>
                </button>
              );
            })}
          </div>
          <div className="mt-2 flex gap-3 text-[10px] text-black/60">
            <span className="flex items-center gap-1">
              <span className="h-1.5 w-1.5 rounded-full bg-scGreen" /> Pantry day
            </span>
            <span className="flex items-center gap-1">
              <span className="h-1.5 w-1.5 rounded-full bg-scPink" /> Event
            </span>
          </div>
        </div>

        {/* Selected day detail */}
        <div className="mt-3 card p-3">
          <h4 className="mb-2 font-display text-lg">
            {new Date(MONTH_YEAR, MONTH_INDEX, selected).toLocaleDateString("en-US", {
              weekday: "long",
              month: "long",
              day: "numeric",
            })}
          </h4>
          {selectedPantries.length === 0 && selectedSpecial.length === 0 ? (
            <p className="text-sm text-black/50">Nothing scheduled. Check the Feed for live posts.</p>
          ) : (
            <div className="space-y-2">
              {selectedPantries.map(({ pantry, slot }) => (
                <div key={pantry.name} className="flex items-start gap-2">
                  <span className="shrink-0 rounded-md border-2 border-black bg-white px-1.5 py-0.5 text-[11px] font-semibold">
                    {slot!.time}
                  </span>
                  <div>
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className="text-sm font-semibold">{pantry.name}</span>
                      <span className="rounded-full border border-black bg-scYellow/40 px-1.5 text-[10px]">
                        pantry
                      </span>
                    </div>
                    <p className="text-xs text-black/60">{pantry.location}</p>
                  </div>
                </div>
              ))}
              {selectedSpecial.map((item, i) => (
                <div key={i} className="flex items-start gap-2">
                  <span className="shrink-0 rounded-md border-2 border-black bg-white px-1.5 py-0.5 text-[11px] font-semibold">
                    {item.time}
                  </span>
                  <div>
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className="text-sm font-semibold">{item.title}</span>
                      <span className={`rounded-full border border-black px-1.5 text-[10px] capitalize ${tagStyle(item.tag)}`}>
                        {item.tag}
                      </span>
                    </div>
                    {item.note ? <p className="text-xs text-black/60">{item.note}</p> : null}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Bulletin board */}
      <div>
        <h3 className="font-display text-xl">Bulletin board</h3>
        <p className="mb-3 text-sm text-black/70">
          Tap to read — articles, recipes, and money-saving tips for hungry students, faculty & staff.
        </p>
        <div className="space-y-3">
          {BULLETIN.map((item) => (
            <button
              key={item.title}
              type="button"
              onClick={() => setOpenItem(item)}
              className="card flex w-full gap-3 p-3 text-left transition-transform hover:-translate-y-0.5"
            >
              <div className="grid h-12 w-12 shrink-0 place-items-center rounded-xl border-2 border-black bg-cream text-2xl">
                {item.emoji}
              </div>
              <div>
                <span className="rounded-full border-2 border-black bg-scYellow/40 px-2 py-0.5 text-[10px] font-semibold uppercase">
                  {item.kind}
                </span>
                <h4 className="mt-1 font-display text-base leading-tight">{item.title}</h4>
                <p className="text-xs text-black/70">{item.blurb}</p>
              </div>
            </button>
          ))}
        </div>
      </div>

      {openItem ? <BulletinModal item={openItem} onClose={() => setOpenItem(null)} /> : null}
    </div>
  );
}

/* ------------------------------- Offers tab ------------------------------- */

function OffersScreen() {
  const [redeemed, setRedeemed] = useState<string | null>(null);
  return (
    <div className="space-y-4">
      <div>
        <h2 className="font-display text-2xl">Exclusive offers</h2>
        <p className="text-sm text-black/70">
          Redeemable student discounts at local restaurants near campus.
        </p>
      </div>
      {OFFERS.map((offer) => (
        <div key={offer.id} className="card overflow-hidden p-0">
          <div className="flex items-center gap-3 p-4">
            <div className="grid h-14 w-14 shrink-0 place-items-center rounded-xl border-2 border-black bg-cream text-3xl">
              {offer.emoji}
            </div>
            <div className="min-w-0 flex-1">
              <h3 className="font-display text-lg leading-tight">{offer.business}</h3>
              <p className="text-sm font-semibold text-brandGreen">{offer.deal}</p>
              <p className="text-xs text-black/60">
                {offer.distance} · expires {offer.expires}
              </p>
            </div>
          </div>
          <div className="border-t-2 border-dashed border-black px-4 py-3">
            <p className="mb-2 text-xs text-black/70">{offer.detail}</p>
            {redeemed === offer.id ? (
              <div className="rounded-lg border-2 border-black bg-scGreen/30 px-3 py-2 text-center text-sm font-semibold tracking-widest">
                {offer.code}
              </div>
            ) : (
              <button
                type="button"
                onClick={() => setRedeemed(offer.id)}
                className="w-full rounded-lg border-2 border-black bg-scYellow px-3 py-2 text-sm font-semibold"
              >
                Tap to reveal code
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

/* ------------------------------ Profile tab ------------------------------- */

function ProfileScreen() {
  return (
    <div className="space-y-4">
      <div className="card flex items-center gap-4 p-4">
        <div className="grid h-16 w-16 place-items-center rounded-full border-4 border-black bg-scPink/40 text-3xl">
          🎓
        </div>
        <div>
          <h2 className="font-display text-2xl leading-tight">Alex Rivera</h2>
          <p className="text-sm text-black/70">SDSU · Student</p>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        {[
          ["14", "Meals claimed"],
          ["8 lbs", "Food saved"],
          ["3", "Offers used"],
        ].map(([v, l]) => (
          <div key={l} className="card p-3">
            <div className="font-display text-2xl text-brandGreen">{v}</div>
            <div className="text-xs text-black/60">{l}</div>
          </div>
        ))}
      </div>
      <div className="card divide-y-2 divide-black/10 p-0">
        {["Claim history", "Notifications", "Dietary preferences", "Help & support", "Log out"].map(
          (row) => (
            <div key={row} className="flex items-center justify-between px-4 py-3 text-sm font-semibold">
              {row}
              <span className="text-black/40">›</span>
            </div>
          ),
        )}
      </div>
    </div>
  );
}

/* ---------------------------- Tab orchestration --------------------------- */

export function AppExperience({ variant }: { variant: "mobile" | "web" }) {
  const [tab, setTab] = useState<TabId>("feed");
  const [openPost, setOpenPost] = useState<FeedPost | null>(null);

  const screen = useMemo(() => {
    if (tab === "feed") {
      return openPost ? (
        <PostDetail post={openPost} onBack={() => setOpenPost(null)} />
      ) : (
        <FeedScreen onOpen={setOpenPost} />
      );
    }
    if (tab === "posts") return <PostsScreen />;
    if (tab === "resources") return <ResourcesScreen />;
    if (tab === "offers") return <OffersScreen />;
    return <ProfileScreen />;
  }, [tab, openPost]);

  function selectTab(id: TabId) {
    setOpenPost(null);
    setTab(id);
  }

  // Web variant: sidebar nav + wide content.
  if (variant === "web") {
    return (
      <div className="relative flex min-h-[640px]">
        <aside className="w-56 shrink-0 border-r-4 border-black bg-cream/60 p-3">
          <img src={`${BASE}images/sc-logo-text.png`} alt="Second Course" className="mb-4 h-9 w-auto" />
          <nav className="space-y-1">
            {TABS.map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => selectTab(t.id)}
                className={`flex w-full items-center gap-2 rounded-xl border-2 px-3 py-2 text-left text-sm font-semibold ${
                  tab === t.id ? "border-black bg-white" : "border-transparent hover:bg-white/60"
                }`}
              >
                <span className="text-lg">{t.emoji}</span>
                {t.label}
                {t.badge ? (
                  <span className="ml-auto rounded-full border border-black bg-scPink/40 px-1.5 text-[9px] font-bold uppercase">
                    New
                  </span>
                ) : null}
              </button>
            ))}
          </nav>
        </aside>
        <div className="flex-1 overflow-y-auto p-6">
          <div className="mx-auto max-w-2xl">{screen}</div>
        </div>
      </div>
    );
  }

  // Mobile variant: scrolling content + bottom tab bar.
  return (
    <div className="relative flex h-full flex-col bg-white">
      <div className="flex items-center justify-center border-b-2 border-black/10 py-2">
        <img src={`${BASE}images/sc-logo-text.png`} alt="Second Course" className="h-7 w-auto" />
      </div>
      <div className="flex-1 overflow-y-auto px-4 py-4">{screen}</div>
      <nav className="grid grid-cols-5 border-t-2 border-black bg-white">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => selectTab(t.id)}
            className={`relative flex flex-col items-center gap-0.5 py-2 text-[10px] font-semibold ${
              tab === t.id ? "text-brandGreen" : "text-black/55"
            }`}
          >
            {t.icon ? (
              <img src={t.icon} alt="" className="h-6 w-6 object-contain" />
            ) : (
              <span className="text-xl leading-none">{t.emoji}</span>
            )}
            {t.label}
            {t.badge ? (
              <span className="absolute right-2 top-1 h-2 w-2 rounded-full border border-black bg-scPink" />
            ) : null}
          </button>
        ))}
      </nav>
    </div>
  );
}
