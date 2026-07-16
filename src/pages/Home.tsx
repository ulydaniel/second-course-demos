import { Link } from "react-router-dom";

const apple = `${import.meta.env.BASE_URL}images/SC_apple_transp.png`;

const CARDS = [
  {
    to: "/portal",
    title: "University Dashboard",
    blurb:
      "Live-style analytics for campus partners — posts, claims, demand heatmaps, staff utilization, and grant-ready impact metrics. Staff sign in with an email approved by Second Course.",
    accent: "bg-scGreen/25",
  },
  {
    to: "/mobile",
    title: "Mobile App",
    blurb:
      "The student app in a phone frame, including two new tabs — Resources and Offers — plus live chat on individual posts.",
    accent: "bg-scPink/25",
  },
  {
    to: "/web",
    title: "Web App",
    blurb:
      "A responsive, browser-based version of the mobile app with the same feature set, including the new Resources and Offers experiences.",
    accent: "bg-scOrange/25",
  },
  {
    to: "/training",
    title: "Training",
    blurb:
      "Click-through courses for new organizers (mobile + web posting) and for university staff using the dashboard — finish to earn a personalized certificate.",
    accent: "bg-scYellow/35",
  },
] as const;

export default function Home() {
  return (
    <div className="px-4 py-10">
      <div className="relative mx-auto max-w-5xl">
        <div className="pointer-events-none absolute -top-4 right-0 floating-character hidden md:block">
          <img
            src={apple}
            alt=""
            className="h-28 w-auto drop-shadow-[8px_8px_0_rgba(0,0,0,0.35)]"
          />
        </div>

        <header className="mb-8 max-w-2xl space-y-3">
          <h1 className="font-display text-4xl text-black md:text-5xl">Second Course Demos</h1>
          <p className="font-sans text-black/80">
            A collection of interactive product demos for Second Course. Pick one below or use the
            links at the top to switch between them anytime.
          </p>
          <div className="callout-warning max-w-xl">
            <strong className="block mb-1">Demo preview</strong>
            Sample content for design review only — not connected to live data or accounts.
          </div>
        </header>

        <div className="grid gap-5 sm:grid-cols-2">
          {CARDS.map((card) => (
            <Link
              key={card.to}
              to={card.to}
              className={`card block p-6 transition-transform hover:-translate-y-1 ${card.accent}`}
            >
              <h2 className="font-display text-2xl text-black">{card.title}</h2>
              <p className="mt-2 font-sans text-sm text-black/80">{card.blurb}</p>
              <span className="mt-4 inline-block font-sans text-sm font-semibold underline">
                Open demo →
              </span>
            </Link>
          ))}
        </div>

        <footer className="mt-12 flex flex-col items-center gap-2 text-sm text-black/70 font-sans">
          <a href="https://www.instagram.com/haveasecondcourse/" className="underline hover:text-black">
            @haveasecondcourse
          </a>
          <a href="mailto:support@secondcourse.co" className="underline hover:text-black">
            support@secondcourse.co
          </a>
        </footer>
      </div>
    </div>
  );
}
