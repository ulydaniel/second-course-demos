import { NavLink, Outlet, useLocation } from "react-router-dom";
import { useEffect } from "react";

export const DEMOS = [
  { to: "/dashboard", label: "University Dashboard" },
  { to: "/mobile", label: "Mobile App" },
  { to: "/web", label: "Web App" },
  { to: "/training", label: "Training" },
] as const;

const logo = `${import.meta.env.BASE_URL}images/second-course-logo.png`;

export function DemoLayout() {
  const { pathname } = useLocation();

  // Scroll to top whenever the demo changes.
  useEffect(() => {
    window.scrollTo({ top: 0 });
  }, [pathname]);

  return (
    <div className="min-h-screen bg-cream">
      <header className="sticky top-0 z-40 border-b-4 border-black bg-cream/95 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3">
          <NavLink to="/" className="flex items-center gap-2">
            <img src={logo} alt="Second Course" className="h-8 w-auto" />
            <span className="pill bg-scYellow text-[10px] uppercase tracking-wide">Demos</span>
          </NavLink>

          <nav className="flex flex-1 flex-wrap items-center justify-end gap-2">
            {DEMOS.map((demo) => (
              <NavLink
                key={demo.to}
                to={demo.to}
                className={({ isActive }) =>
                  `pill ${isActive ? "pill-active" : "bg-white"} text-xs`
                }
              >
                {demo.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main>
        <Outlet />
      </main>
    </div>
  );
}
