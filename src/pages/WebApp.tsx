import { AppExperience } from "../components/app/AppExperience";

export default function WebApp() {
  return (
    <div className="px-4 py-8">
      <div className="mx-auto max-w-5xl">
        <header className="mb-6 max-w-2xl space-y-2">
          <h1 className="font-display text-3xl text-black md:text-4xl">Web App</h1>
          <p className="font-sans text-black/80">
            A responsive, browser-based version of the Second Course app with the same feature set —
            including the new <strong>Resources</strong> and <strong>Offers</strong> tabs and{" "}
            <strong>live chat</strong> on posts. Use the sidebar to move between sections.
          </p>
        </header>

        {/* Browser frame */}
        <div
          className="overflow-hidden rounded-2xl border-4 border-black bg-white"
          style={{ boxShadow: "10px 10px 0 rgba(0,0,0,0.3)" }}
        >
          <div className="flex items-center gap-2 border-b-4 border-black bg-cream/70 px-4 py-2">
            <span className="h-3 w-3 rounded-full border-2 border-black bg-scRed" />
            <span className="h-3 w-3 rounded-full border-2 border-black bg-scYellow" />
            <span className="h-3 w-3 rounded-full border-2 border-black bg-scGreen" />
            <div className="ml-3 flex-1 rounded-full border-2 border-black bg-white px-3 py-1 text-xs text-black/60">
              app.secondcourse.co
            </div>
          </div>
          <AppExperience variant="web" />
        </div>
      </div>
    </div>
  );
}
