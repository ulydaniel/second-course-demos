import type { ReactNode } from "react";

const apple = `${import.meta.env.BASE_URL}images/SC_apple_transp.png`;
const logo = `${import.meta.env.BASE_URL}images/second-course-logo.png`;

export function PortalShell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
}) {
  return (
    <div className="min-h-screen bg-cream px-4 py-10">
      <div className="relative mx-auto max-w-5xl">
        <div className="pointer-events-none absolute -top-4 right-0 floating-character hidden md:block">
          <img
            src={apple}
            alt=""
            className="h-28 w-auto drop-shadow-[8px_8px_0_rgba(0,0,0,0.35)]"
          />
        </div>

        <header className="mb-8 max-w-2xl space-y-3 pr-0 md:pr-36">
          <img src={logo} alt="Second Course" className="h-10 w-auto md:h-12" />
          <h1 className="font-display text-4xl text-black md:text-5xl">{title}</h1>
          {subtitle ? <p className="font-sans text-black/80">{subtitle}</p> : null}
        </header>

        {children}
      </div>
    </div>
  );
}
