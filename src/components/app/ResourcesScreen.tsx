import { useState, type FormEvent, type ReactNode } from "react";
import {
  BULLETIN,
  PANTRIES,
  SPECIAL_EVENTS,
  type BulletinItem,
  type Pantry,
  type SpecialEvent,
} from "../../appData";
import { useAuth } from "../../context/AuthContext";

const MONTH_LABEL = "June 2026";
const MONTH_YEAR = 2026;
const MONTH_INDEX = 5; // June (0-based)
const WEEKDAY_LABELS = ["S", "M", "T", "W", "T", "F", "S"];
const WEEKDAY_OPTIONS = [
  { day: "Sun", weekday: 0 },
  { day: "Mon", weekday: 1 },
  { day: "Tue", weekday: 2 },
  { day: "Wed", weekday: 3 },
  { day: "Thu", weekday: 4 },
  { day: "Fri", weekday: 5 },
  { day: "Sat", weekday: 6 },
];
const PANTRY_EMOJIS = [
  { value: "🏠", label: "House" },
  { value: "🥫", label: "Food can" },
  { value: "🥬", label: "Veggies" },
];
const BULLETIN_KINDS: BulletinItem["kind"][] = ["Article", "Recipe", "Tip"];
const EVENT_TAGS: SpecialEvent["tag"][] = ["food", "resource", "event"];

const fieldClass =
  "w-full rounded-lg border-2 border-black bg-white px-2.5 py-1.5 text-sm";
const labelClass = "block space-y-1 text-xs font-semibold";

function tagStyle(tag: SpecialEvent["tag"]) {
  if (tag === "food") return "bg-scGreen/30";
  if (tag === "event") return "bg-scPink/30";
  return "bg-scYellow/40";
}

function pantriesOpenOn(pantries: Pantry[], weekday: number) {
  return pantries
    .map((p) => ({
      pantry: p,
      slot: p.hours.find((h) => h.weekday === weekday),
    }))
    .filter((x) => x.slot);
}

function EditChip({
  label,
  onClick,
}: {
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="shrink-0 rounded-full border-2 border-black bg-white px-2.5 py-0.5 text-[11px] font-semibold hover:bg-cream"
    >
      {label}
    </button>
  );
}

function OverlaySheet({
  title,
  onClose,
  children,
}: {
  title: string;
  onClose: () => void;
  children: ReactNode;
}) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      onClick={onClose}
    >
      <div
        className="max-h-[min(90vh,40rem)] w-full max-w-md overflow-y-auto rounded-2xl border-4 border-black bg-white p-5"
        style={{ boxShadow: "6px 6px 0 rgba(0,0,0,0.3)" }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-3 flex items-start justify-between gap-3">
          <h3 className="font-display text-xl leading-tight">{title}</h3>
          <button
            type="button"
            onClick={onClose}
            className="grid h-8 w-8 shrink-0 place-items-center rounded-full border-2 border-black bg-white text-lg leading-none"
          >
            ×
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

function BulletinModal({ item, onClose }: { item: BulletinItem; onClose: () => void }) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      onClick={onClose}
    >
      <div
        className="max-h-[min(90vh,40rem)] w-full max-w-md overflow-y-auto rounded-2xl border-4 border-black bg-white p-5"
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

type HourDraft = { day: string; weekday: number; time: string };

function emptyPantry(): Pantry {
  return {
    name: "",
    location: "",
    emoji: "🥫",
    note: "",
    hours: [{ day: "Mon", weekday: 1, time: "10:00a – 2:00p" }],
  };
}

function emptyEvent(): SpecialEvent {
  return { time: "", title: "", tag: "food", note: "" };
}

function emptyBulletin(): BulletinItem {
  return {
    kind: "Tip",
    title: "",
    blurb: "",
    emoji: "💡",
    content: [""],
  };
}

function PantryEditor({
  initial,
  onSave,
  onDelete,
  onClose,
}: {
  initial: Pantry | null;
  onSave: (pantry: Pantry) => void;
  onDelete?: () => void;
  onClose: () => void;
}) {
  const [draft, setDraft] = useState<Pantry>(initial ?? emptyPantry());
  const isNew = !initial;

  function setHour(index: number, patch: Partial<HourDraft>) {
    setDraft((prev) => ({
      ...prev,
      hours: prev.hours.map((h, i) => {
        if (i !== index) return h;
        const next = { ...h, ...patch };
        if (patch.weekday !== undefined) {
          const opt = WEEKDAY_OPTIONS.find((o) => o.weekday === patch.weekday);
          if (opt) next.day = opt.day;
        }
        return next;
      }),
    }));
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!draft.name.trim() || !draft.location.trim()) return;
    onSave({
      ...draft,
      name: draft.name.trim(),
      location: draft.location.trim(),
      note: draft.note.trim(),
      hours: draft.hours.filter((h) => h.time.trim()),
    });
    onClose();
  }

  return (
    <OverlaySheet title={isNew ? "Add pantry" : "Edit pantry"} onClose={onClose}>
      <form className="space-y-3" onSubmit={handleSubmit}>
        <label className={labelClass}>
          Name
          <input
            required
            className={fieldClass}
            value={draft.name}
            onChange={(e) => setDraft({ ...draft, name: e.target.value })}
          />
        </label>
        <label className={labelClass}>
          Address / location
          <input
            required
            className={fieldClass}
            value={draft.location}
            onChange={(e) => setDraft({ ...draft, location: e.target.value })}
          />
        </label>
        <label className={labelClass}>
          Emoji
          <select
            className={fieldClass}
            value={draft.emoji}
            onChange={(e) => setDraft({ ...draft, emoji: e.target.value })}
          >
            {PANTRY_EMOJIS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.value} {opt.label}
              </option>
            ))}
          </select>
        </label>
        <label className={labelClass}>
          Note
          <input
            className={fieldClass}
            value={draft.note}
            onChange={(e) => setDraft({ ...draft, note: e.target.value })}
            placeholder="Who can visit, what to bring…"
          />
        </label>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold">Hours</span>
            <button
              type="button"
              className="text-[11px] font-semibold underline"
              onClick={() =>
                setDraft({
                  ...draft,
                  hours: [...draft.hours, { day: "Mon", weekday: 1, time: "" }],
                })
              }
            >
              + Add time block
            </button>
          </div>
          {draft.hours.map((h, i) => (
            <div key={i} className="flex gap-2">
              <select
                className={fieldClass}
                value={h.weekday}
                onChange={(e) => setHour(i, { weekday: Number(e.target.value) })}
              >
                {WEEKDAY_OPTIONS.map((opt) => (
                  <option key={opt.weekday} value={opt.weekday}>
                    {opt.day}
                  </option>
                ))}
              </select>
              <input
                className={fieldClass}
                value={h.time}
                onChange={(e) => setHour(i, { time: e.target.value })}
                placeholder="10:00a – 2:00p"
                required
              />
              {draft.hours.length > 1 ? (
                <button
                  type="button"
                  className="shrink-0 text-xs font-semibold text-black/50"
                  onClick={() =>
                    setDraft({
                      ...draft,
                      hours: draft.hours.filter((_, j) => j !== i),
                    })
                  }
                >
                  ✕
                </button>
              ) : null}
            </div>
          ))}
        </div>
        <div className="flex flex-wrap gap-2 pt-1">
          <button type="submit" className="btn-primary text-sm">
            {isNew ? "Add pantry" : "Save"}
          </button>
          {!isNew && onDelete ? (
            <button
              type="button"
              className="btn-secondary text-sm"
              onClick={() => {
                onDelete();
                onClose();
              }}
            >
              Delete
            </button>
          ) : null}
        </div>
      </form>
    </OverlaySheet>
  );
}

function EventEditor({
  dayLabel,
  initial,
  onSave,
  onDelete,
  onClose,
}: {
  dayLabel: string;
  initial: SpecialEvent | null;
  onSave: (event: SpecialEvent) => void;
  onDelete?: () => void;
  onClose: () => void;
}) {
  const [draft, setDraft] = useState<SpecialEvent>(initial ?? emptyEvent());
  const isNew = !initial;

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!draft.title.trim() || !draft.time.trim()) return;
    onSave({
      ...draft,
      title: draft.title.trim(),
      time: draft.time.trim(),
      note: draft.note?.trim() || undefined,
    });
    onClose();
  }

  return (
    <OverlaySheet
      title={isNew ? `Add event · ${dayLabel}` : `Edit event · ${dayLabel}`}
      onClose={onClose}
    >
      <form className="space-y-3" onSubmit={handleSubmit}>
        <label className={labelClass}>
          Time
          <input
            className={fieldClass}
            value={draft.time}
            onChange={(e) => setDraft({ ...draft, time: e.target.value })}
            placeholder="12p–1p"
            required
          />
        </label>
        <label className={labelClass}>
          Title
          <input
            className={fieldClass}
            value={draft.title}
            onChange={(e) => setDraft({ ...draft, title: e.target.value })}
            placeholder="Event name"
            required
          />
        </label>
        <label className={labelClass}>
          Tag
          <select
            className={fieldClass}
            value={draft.tag}
            onChange={(e) =>
              setDraft({ ...draft, tag: e.target.value as SpecialEvent["tag"] })
            }
          >
            {EVENT_TAGS.map((tag) => (
              <option key={tag} value={tag}>
                {tag}
              </option>
            ))}
          </select>
        </label>
        <label className={labelClass}>
          Note
          <input
            className={fieldClass}
            value={draft.note ?? ""}
            onChange={(e) => setDraft({ ...draft, note: e.target.value })}
            placeholder="Optional details"
          />
        </label>
        <div className="flex flex-wrap gap-2 pt-1">
          <button type="submit" className="btn-primary text-sm">
            {isNew ? "Add event" : "Save"}
          </button>
          {!isNew && onDelete ? (
            <button
              type="button"
              className="btn-secondary text-sm"
              onClick={() => {
                onDelete();
                onClose();
              }}
            >
              Delete
            </button>
          ) : null}
        </div>
      </form>
    </OverlaySheet>
  );
}

function BulletinEditor({
  initial,
  onSave,
  onDelete,
  onClose,
}: {
  initial: BulletinItem | null;
  onSave: (item: BulletinItem) => void;
  onDelete?: () => void;
  onClose: () => void;
}) {
  const [draft, setDraft] = useState<BulletinItem>(initial ?? emptyBulletin());
  const isNew = !initial;
  const contentText = draft.content.join("\n\n");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!draft.title.trim()) return;
    const paragraphs = contentText
      .split(/\n\s*\n/)
      .map((p) => p.trim())
      .filter(Boolean);
    onSave({
      ...draft,
      title: draft.title.trim(),
      blurb: draft.blurb.trim(),
      content: paragraphs.length ? paragraphs : [draft.blurb.trim() || draft.title.trim()],
    });
    onClose();
  }

  return (
    <OverlaySheet title={isNew ? "Add bulletin item" : "Edit bulletin item"} onClose={onClose}>
      <form className="space-y-3" onSubmit={handleSubmit}>
        <label className={labelClass}>
          Type
          <select
            className={fieldClass}
            value={draft.kind}
            onChange={(e) =>
              setDraft({ ...draft, kind: e.target.value as BulletinItem["kind"] })
            }
          >
            {BULLETIN_KINDS.map((kind) => (
              <option key={kind} value={kind}>
                {kind}
              </option>
            ))}
          </select>
        </label>
        <label className={labelClass}>
          Emoji
          <input
            className={fieldClass}
            value={draft.emoji}
            onChange={(e) => setDraft({ ...draft, emoji: e.target.value })}
            maxLength={4}
          />
        </label>
        <label className={labelClass}>
          Title
          <input
            required
            className={fieldClass}
            value={draft.title}
            onChange={(e) => setDraft({ ...draft, title: e.target.value })}
          />
        </label>
        <label className={labelClass}>
          Blurb
          <input
            className={fieldClass}
            value={draft.blurb}
            onChange={(e) => setDraft({ ...draft, blurb: e.target.value })}
          />
        </label>
        <label className={labelClass}>
          Body (separate paragraphs with a blank line)
          <textarea
            className={`${fieldClass} min-h-28`}
            value={contentText}
            onChange={(e) =>
              setDraft({
                ...draft,
                content: e.target.value.split(/\n\s*\n/).map((p) => p.trim()),
              })
            }
          />
        </label>
        <div className="flex flex-wrap gap-2 pt-1">
          <button type="submit" className="btn-primary text-sm">
            {isNew ? "Add item" : "Save"}
          </button>
          {!isNew && onDelete ? (
            <button
              type="button"
              className="btn-secondary text-sm"
              onClick={() => {
                onDelete();
                onClose();
              }}
            >
              Delete
            </button>
          ) : null}
        </div>
      </form>
    </OverlaySheet>
  );
}

export function ResourcesScreen() {
  const { canEditResources } = useAuth();
  const firstWeekday = new Date(MONTH_YEAR, MONTH_INDEX, 1).getDay();
  const daysInMonth = new Date(MONTH_YEAR, MONTH_INDEX + 1, 0).getDate();

  const [pantries, setPantries] = useState<Pantry[]>(() => PANTRIES.map((p) => ({ ...p, hours: [...p.hours] })));
  const [events, setEvents] = useState<Record<number, SpecialEvent[]>>(() =>
    Object.fromEntries(
      Object.entries(SPECIAL_EVENTS).map(([day, list]) => [
        Number(day),
        list.map((e) => ({ ...e })),
      ]),
    ),
  );
  const [bulletin, setBulletin] = useState<BulletinItem[]>(() =>
    BULLETIN.map((item) => ({ ...item, content: [...item.content] })),
  );

  const [selected, setSelected] = useState(22);
  const [openItem, setOpenItem] = useState<BulletinItem | null>(null);
  const [editingPantryIndex, setEditingPantryIndex] = useState<number | "new" | null>(null);
  const [eventEditor, setEventEditor] = useState<"new" | number | null>(null);
  const [editingBulletinIndex, setEditingBulletinIndex] = useState<number | "new" | null>(null);

  const cells: (number | null)[] = [
    ...Array(firstWeekday).fill(null),
    ...Array.from({ length: daysInMonth }, (_, i) => i + 1),
  ];

  const selectedWeekday = new Date(MONTH_YEAR, MONTH_INDEX, selected).getDay();
  const selectedPantries = pantriesOpenOn(pantries, selectedWeekday);
  const selectedSpecial = events[selected] ?? [];
  const selectedDayLabel = new Date(MONTH_YEAR, MONTH_INDEX, selected).toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
  });

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
        <div className="mb-2 flex items-center justify-between gap-2">
          <h3 className="font-display text-xl">Weekly food pantries</h3>
          {canEditResources ? (
            <EditChip label="+" onClick={() => setEditingPantryIndex("new")} />
          ) : null}
        </div>
        <div className="space-y-3">
          {pantries.map((p, index) => (
            <div key={`${p.name}-${index}`} className="card p-3">
              <div className="flex gap-3">
                <div className="grid h-11 w-11 shrink-0 place-items-center rounded-xl border-2 border-black bg-cream text-2xl">
                  {p.emoji}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h4 className="font-display text-base leading-tight">{p.name}</h4>
                      <p className="text-xs text-black/60">{p.location}</p>
                    </div>
                    {canEditResources ? (
                      <EditChip label="Edit" onClick={() => setEditingPantryIndex(index)} />
                    ) : null}
                  </div>
                </div>
              </div>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {p.hours.map((h) => (
                  <span
                    key={`${h.day}-${h.time}`}
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
              const hasPantry = pantriesOpenOn(pantries, weekday).length > 0;
              const hasEvent = Boolean(events[day]?.length);
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

        <div className="mt-3 card p-3">
          <div className="mb-2 flex items-start justify-between gap-2">
            <h4 className="font-display text-lg">{selectedDayLabel}</h4>
            {canEditResources ? (
              <EditChip label="+" onClick={() => setEventEditor("new")} />
            ) : null}
          </div>
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
                <div key={`${item.title}-${i}`} className="flex items-start gap-2">
                  <span className="shrink-0 rounded-md border-2 border-black bg-white px-1.5 py-0.5 text-[11px] font-semibold">
                    {item.time}
                  </span>
                  <div className="group min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className="text-sm font-semibold">{item.title}</span>
                      <span
                        className={`rounded-full border border-black px-1.5 text-[10px] capitalize ${tagStyle(item.tag)}`}
                      >
                        {item.tag}
                      </span>
                      {canEditResources ? (
                        <span className="opacity-0 transition-opacity group-hover:opacity-100 group-focus-within:opacity-100">
                          <EditChip label="Edit" onClick={() => setEventEditor(i)} />
                        </span>
                      ) : null}
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
        <div className="flex items-center justify-between gap-2">
          <h3 className="font-display text-xl">Bulletin board</h3>
          {canEditResources ? (
            <EditChip label="+" onClick={() => setEditingBulletinIndex("new")} />
          ) : null}
        </div>
        <p className="mb-3 text-sm text-black/70">
          Tap to read — articles, recipes, and money-saving tips for hungry students, faculty & staff.
        </p>
        <div className="space-y-3">
          {bulletin.map((item, index) => (
            <div key={`${item.title}-${index}`} className="relative">
              <button
                type="button"
                onClick={() => setOpenItem(item)}
                className="card flex w-full gap-3 p-3 text-left transition-transform hover:-translate-y-0.5"
              >
                <div className="grid h-12 w-12 shrink-0 place-items-center rounded-xl border-2 border-black bg-cream text-2xl">
                  {item.emoji}
                </div>
                <div className="min-w-0 flex-1 pr-14">
                  <span className="rounded-full border-2 border-black bg-scYellow/40 px-2 py-0.5 text-[10px] font-semibold uppercase">
                    {item.kind}
                  </span>
                  <h4 className="mt-1 font-display text-base leading-tight">{item.title}</h4>
                  <p className="text-xs text-black/70">{item.blurb}</p>
                </div>
              </button>
              {canEditResources ? (
                <div className="absolute right-3 top-3">
                  <EditChip
                    label="Edit"
                    onClick={() => setEditingBulletinIndex(index)}
                  />
                </div>
              ) : null}
            </div>
          ))}
        </div>
      </div>

      {openItem ? <BulletinModal item={openItem} onClose={() => setOpenItem(null)} /> : null}

      {editingPantryIndex !== null ? (
        <PantryEditor
          initial={editingPantryIndex === "new" ? null : pantries[editingPantryIndex]}
          onClose={() => setEditingPantryIndex(null)}
          onSave={(pantry) => {
            setPantries((prev) => {
              if (editingPantryIndex === "new") return [...prev, pantry];
              return prev.map((item, i) => (i === editingPantryIndex ? pantry : item));
            });
          }}
          onDelete={
            editingPantryIndex === "new"
              ? undefined
              : () =>
                  setPantries((prev) => prev.filter((_, i) => i !== editingPantryIndex))
          }
        />
      ) : null}

      {eventEditor !== null ? (
        <EventEditor
          dayLabel={selectedDayLabel}
          initial={eventEditor === "new" ? null : selectedSpecial[eventEditor]}
          onClose={() => setEventEditor(null)}
          onSave={(event) => {
            setEvents((prev) => {
              const existing = [...(prev[selected] ?? [])];
              if (eventEditor === "new") {
                existing.push(event);
              } else {
                existing[eventEditor] = event;
              }
              return { ...prev, [selected]: existing };
            });
          }}
          onDelete={
            eventEditor === "new"
              ? undefined
              : () => {
                  setEvents((prev) => {
                    const existing = (prev[selected] ?? []).filter((_, i) => i !== eventEditor);
                    const copy = { ...prev };
                    if (existing.length === 0) delete copy[selected];
                    else copy[selected] = existing;
                    return copy;
                  });
                }
          }
        />
      ) : null}

      {editingBulletinIndex !== null ? (
        <BulletinEditor
          initial={editingBulletinIndex === "new" ? null : bulletin[editingBulletinIndex]}
          onClose={() => setEditingBulletinIndex(null)}
          onSave={(item) => {
            setBulletin((prev) => {
              if (editingBulletinIndex === "new") return [...prev, item];
              return prev.map((entry, i) => (i === editingBulletinIndex ? item : entry));
            });
          }}
          onDelete={
            editingBulletinIndex === "new"
              ? undefined
              : () =>
                  setBulletin((prev) => prev.filter((_, i) => i !== editingBulletinIndex))
          }
        />
      ) : null}
    </div>
  );
}
