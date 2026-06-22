import { useState } from "react";
import { MODULES, type TrainingModule } from "../trainingData";

const apple = `${import.meta.env.BASE_URL}images/SC_apple_transp.png`;
const logo = `${import.meta.env.BASE_URL}images/second-course-logo.png`;

type Stage = "slides" | "name" | "certificate";

export default function Training() {
  const [module, setModule] = useState<TrainingModule | null>(null);
  const [index, setIndex] = useState(0);
  const [stage, setStage] = useState<Stage>("slides");
  const [name, setName] = useState("");

  function start(m: TrainingModule) {
    setModule(m);
    setIndex(0);
    setStage("slides");
    setName("");
  }

  function reset() {
    setModule(null);
    setIndex(0);
    setStage("slides");
    setName("");
  }

  /* ----------------------------- Module picker ---------------------------- */
  if (!module) {
    return (
      <div className="px-4 py-10">
        <div className="relative mx-auto max-w-4xl">
          <div className="pointer-events-none absolute -top-4 right-0 floating-character hidden md:block">
            <img src={apple} alt="" className="h-24 w-auto drop-shadow-[8px_8px_0_rgba(0,0,0,0.35)]" />
          </div>
          <header className="mb-8 max-w-2xl space-y-2">
            <h1 className="font-display text-3xl text-black md:text-4xl">Training</h1>
            <p className="font-sans text-black/80">
              Short, click-through courses. Finish one to earn a personalized certificate.
            </p>
          </header>
          <div className="grid gap-5 sm:grid-cols-2">
            {MODULES.map((m) => (
              <button
                key={m.id}
                type="button"
                onClick={() => start(m)}
                className={`card block p-6 text-left transition-transform hover:-translate-y-1 ${m.accent}`}
              >
                <span className="pill bg-white text-xs">{m.audience}</span>
                <h2 className="mt-3 font-display text-2xl text-black">{m.title}</h2>
                <p className="mt-2 font-sans text-sm text-black/80">{m.blurb}</p>
                <span className="mt-4 inline-block text-sm font-semibold underline">
                  {m.slides.length} lessons · Start →
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  /* ------------------------------ Certificate ----------------------------- */
  if (stage === "certificate") {
    const today = new Date().toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
    return (
      <div className="px-4 py-10">
        <div className="mx-auto max-w-3xl">
          <div id="certificate" className="relative rounded-2xl border-4 border-black bg-white p-8 text-center md:p-12"
            style={{ boxShadow: "10px 10px 0 rgba(0,0,0,0.3)" }}>
            <div className="pointer-events-none absolute inset-3 rounded-xl border-2 border-dashed border-black/40" />
            <img src={logo} alt="Second Course" className="mx-auto h-12 w-auto" />
            <p className="mt-6 font-sans text-sm uppercase tracking-[0.2em] text-black/60">
              Certificate of Completion
            </p>
            <p className="mt-6 font-sans text-black/70">This certifies that</p>
            <h2 className="mt-2 font-display text-4xl text-black md:text-5xl">{name}</h2>
            <p className="mt-4 font-sans text-black/70">has successfully completed</p>
            <h3 className="mt-1 font-display text-2xl text-brandGreen">{module.title}</h3>
            <p className="mx-auto mt-3 max-w-md font-sans text-sm text-black/70">{module.blurb}</p>
            <div className="mt-8 flex items-end justify-between gap-4">
              <div className="text-left">
                <div className="font-display text-lg">Second Course</div>
                <div className="text-xs text-black/60">haveasecondcourse</div>
              </div>
              <div className="text-right">
                <div className="border-b-2 border-black px-6 font-display text-lg">{today}</div>
                <div className="text-xs text-black/60">Date completed</div>
              </div>
            </div>
          </div>

          <div className="mt-6 flex flex-wrap justify-center gap-3 print:hidden">
            <button type="button" className="btn-primary" onClick={() => window.print()}>
              Print / Save as PDF
            </button>
            <button type="button" className="btn-secondary" onClick={reset}>
              Back to courses
            </button>
          </div>
        </div>
      </div>
    );
  }

  /* -------------------------------- Name form ----------------------------- */
  if (stage === "name") {
    return (
      <div className="px-4 py-12">
        <div className="mx-auto max-w-md">
          <div className="card p-6 text-center">
            <div className="text-5xl">🎓</div>
            <h2 className="mt-3 font-display text-2xl">Almost done!</h2>
            <p className="mt-1 font-sans text-sm text-black/75">
              Enter your name as you'd like it to appear on your certificate.
            </p>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && name.trim() && setStage("certificate")}
              placeholder="Your full name"
              className="mt-5 w-full rounded-xl border-2 border-black px-4 py-3 text-center font-display text-xl outline-none"
              autoFocus
            />
            <button
              type="button"
              disabled={!name.trim()}
              onClick={() => setStage("certificate")}
              className="btn-primary mt-4 w-full disabled:opacity-50"
            >
              Get my certificate
            </button>
            <button
              type="button"
              onClick={() => setStage("slides")}
              className="mt-2 text-sm underline"
            >
              ← Back to lessons
            </button>
          </div>
        </div>
      </div>
    );
  }

  /* --------------------------------- Slides ------------------------------- */
  const slide = module.slides[index];
  const isLast = index === module.slides.length - 1;
  const progress = Math.round(((index + 1) / module.slides.length) * 100);

  return (
    <div className="px-4 py-10">
      <div className="mx-auto max-w-2xl">
        <div className="mb-4 flex items-center justify-between text-sm">
          <button type="button" onClick={reset} className="font-semibold underline">
            ← All courses
          </button>
          <span className="text-black/60">
            {module.title} · {index + 1}/{module.slides.length}
          </span>
        </div>

        <div className="mb-4 h-2.5 w-full overflow-hidden rounded-full border-2 border-black bg-white">
          <div className="h-full bg-scGreen transition-all" style={{ width: `${progress}%` }} />
        </div>

        <div className="card min-h-[360px] p-8">
          <div className="text-6xl">{slide.emoji}</div>
          <h2 className="mt-4 font-display text-3xl">{slide.title}</h2>
          <p className="mt-3 font-sans text-black/80">{slide.body}</p>
          {slide.points ? (
            <ul className="mt-4 space-y-2">
              {slide.points.map((p) => (
                <li key={p} className="flex items-start gap-2 font-sans text-black/80">
                  <span className="mt-1 text-brandGreen">✓</span>
                  <span>{p}</span>
                </li>
              ))}
            </ul>
          ) : null}
        </div>

        <div className="mt-5 flex items-center justify-between">
          <button
            type="button"
            className="btn-secondary disabled:opacity-40"
            disabled={index === 0}
            onClick={() => setIndex((i) => i - 1)}
          >
            Back
          </button>
          {isLast ? (
            <button type="button" className="btn-primary" onClick={() => setStage("name")}>
              Finish & get certificate →
            </button>
          ) : (
            <button type="button" className="btn-primary" onClick={() => setIndex((i) => i + 1)}>
              Next →
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
