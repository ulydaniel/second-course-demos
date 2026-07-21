import { useEffect, useMemo, useState, type FormEvent } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { PortalShell } from "../components/PortalShell";
import { useAuth } from "../context/AuthContext";
import { getApiErrorMessage } from "../api";
import { listUniversities, type JobTitle, type University, type UserStatus } from "../api/auth";

const JOB_TITLES: { value: JobTitle; label: string }[] = [
  { value: "faculty", label: "Faculty" },
  { value: "representative", label: "Representative" },
  { value: "dean", label: "Dean" },
  { value: "admin", label: "Administrator" },
  { value: "staff", label: "Staff" },
  { value: "other", label: "Other" },
];

type Mode = "signin" | "request";

function StatusCallout({ status }: { status: UserStatus }) {
  if (status === "approved") {
    return (
      <div className="callout-info">
        <strong className="block mb-1">Access approved</strong>
        Taking you to your university dashboard…
      </div>
    );
  }
  if (status === "rejected") {
    return (
      <div className="callout-warning">
        <strong className="block mb-1">Access not granted</strong>
        Your request was not approved. Contact{" "}
        <a className="underline" href="mailto:support@secondcourse.co">
          support@secondcourse.co
        </a>{" "}
        if you believe this is a mistake.
      </div>
    );
  }
  return (
    <div className="callout-neutral">
      <strong className="block mb-1">Request received</strong>
      Your access request is awaiting approval from Second Course. You'll be able to sign in once a
      developer approves your email for your campus.
    </div>
  );
}

function validatePasswordPair(password: string, confirmPassword: string): string | null {
  if (password.length < 8) {
    return "Password must be at least 8 characters.";
  }
  if (password !== confirmPassword) {
    return "Passwords do not match. Check for typos and try again.";
  }
  const hasLetter = /[A-Za-z]/.test(password);
  const hasDigit = /\d/.test(password);
  if (!hasLetter || !hasDigit) {
    return "Password must include at least one letter and one number.";
  }
  return null;
}

export default function Portal() {
  const { user, loading, isApproved, login, register } = useAuth();
  const navigate = useNavigate();

  const [mode, setMode] = useState<Mode>("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [jobTitle, setJobTitle] = useState<JobTitle>("faculty");
  const [universityId, setUniversityId] = useState("");
  const [universities, setUniversities] = useState<University[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<UserStatus | null>(null);

  const passwordHint = useMemo(() => {
    if (mode !== "request" || !password) return null;
    if (confirmPassword && password !== confirmPassword) {
      return "Passwords do not match yet.";
    }
    if (password.length > 0 && password.length < 8) {
      return "Use at least 8 characters.";
    }
    return null;
  }, [mode, password, confirmPassword]);

  useEffect(() => {
    let cancelled = false;
    listUniversities()
      .then((list) => {
        if (!cancelled) {
          setUniversities(list);
          setUniversityId((current) => current || list[0]?.id || "");
        }
      })
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, []);

  if (!loading && isApproved) {
    return <Navigate to="/dashboard" replace />;
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    setStatus(null);
    try {
      if (mode === "signin") {
        const result = await login({ email, password });
        setStatus(result.status);
        if (result.status === "approved") {
          navigate("/dashboard", { replace: true });
        }
      } else {
        const localError = validatePasswordPair(password, confirmPassword);
        if (localError) {
          setError(localError);
          return;
        }
        const result = await register({
          email,
          fullName,
          jobTitle,
          universityId,
          password,
          confirmPassword,
        });
        setStatus(result.status);
        if (result.status === "approved") {
          navigate("/dashboard", { replace: true });
        }
      }
    } catch (submitError) {
      setError(getApiErrorMessage(submitError));
    } finally {
      setSubmitting(false);
    }
  }

  const signedInPending = user && user.status !== "approved";

  return (
    <PortalShell
      title="University Portal"
      subtitle="Sign in with the campus email approved by Second Course to reach your university dashboard."
    >
      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_360px]">
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className={`pill ${mode === "signin" ? "pill-active" : "bg-white"}`}
              onClick={() => {
                setMode("signin");
                setError(null);
                setStatus(null);
                setPassword("");
                setConfirmPassword("");
              }}
            >
              Sign in
            </button>
            <button
              type="button"
              className={`pill ${mode === "request" ? "pill-active" : "bg-white"}`}
              onClick={() => {
                setMode("request");
                setError(null);
                setStatus(null);
                setPassword("");
                setConfirmPassword("");
              }}
            >
              Request access
            </button>
          </div>

          <form className="card space-y-4 p-6" onSubmit={handleSubmit}>
            <label className="block space-y-1">
              <span className="font-sans text-sm font-semibold">Campus email</span>
              <input
                type="email"
                required
                autoComplete="username"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@university.edu"
                className="w-full rounded-lg border-2 border-black bg-white px-3 py-2 font-sans text-sm"
              />
            </label>

            <label className="block space-y-1">
              <span className="font-sans text-sm font-semibold">
                {mode === "request" ? "Create password" : "Password"}
              </span>
              <input
                type="password"
                required
                minLength={mode === "request" ? 8 : 1}
                autoComplete={mode === "request" ? "new-password" : "current-password"}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder={mode === "request" ? "At least 8 characters" : "Your password"}
                className="w-full rounded-lg border-2 border-black bg-white px-3 py-2 font-sans text-sm"
              />
            </label>

            {mode === "request" ? (
              <>
                <label className="block space-y-1">
                  <span className="font-sans text-sm font-semibold">Confirm password</span>
                  <input
                    type="password"
                    required
                    minLength={8}
                    autoComplete="new-password"
                    value={confirmPassword}
                    onChange={(event) => setConfirmPassword(event.target.value)}
                    placeholder="Re-enter password"
                    className="w-full rounded-lg border-2 border-black bg-white px-3 py-2 font-sans text-sm"
                  />
                  {passwordHint ? (
                    <span className="font-sans text-xs text-scOrange">{passwordHint}</span>
                  ) : confirmPassword && password === confirmPassword ? (
                    <span className="font-sans text-xs text-brandGreen">Passwords match</span>
                  ) : (
                    <span className="font-sans text-xs text-black/60">
                      Must match exactly — catches typos before we create your account.
                    </span>
                  )}
                </label>

                <label className="block space-y-1">
                  <span className="font-sans text-sm font-semibold">Full name</span>
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(event) => setFullName(event.target.value)}
                    placeholder="Jordan Rivera"
                    className="w-full rounded-lg border-2 border-black bg-white px-3 py-2 font-sans text-sm"
                  />
                </label>

                <label className="block space-y-1">
                  <span className="font-sans text-sm font-semibold">University</span>
                  <select
                    value={universityId}
                    onChange={(event) => setUniversityId(event.target.value)}
                    className="w-full rounded-lg border-2 border-black bg-white px-3 py-2 font-sans text-sm"
                  >
                    {universities.map((university) => (
                      <option key={university.id} value={university.id}>
                        {university.name}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="block space-y-1">
                  <span className="font-sans text-sm font-semibold">Role on campus</span>
                  <select
                    value={jobTitle}
                    onChange={(event) => setJobTitle(event.target.value as JobTitle)}
                    className="w-full rounded-lg border-2 border-black bg-white px-3 py-2 font-sans text-sm"
                  >
                    {JOB_TITLES.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>
              </>
            ) : null}

            <button type="submit" className="btn-primary w-full" disabled={submitting}>
              {submitting
                ? "Please wait…"
                : mode === "signin"
                  ? "Sign in"
                  : "Request access"}
            </button>

            {error ? (
              <div className="callout-warning">
                <p>{error}</p>
                {mode === "signin" ? (
                  <button
                    type="button"
                    className="mt-2 underline font-sans text-sm"
                    onClick={() => {
                      setMode("request");
                      setError(null);
                      setPassword("");
                      setConfirmPassword("");
                    }}
                  >
                    Request access instead →
                  </button>
                ) : null}
              </div>
            ) : null}

            {status ? <StatusCallout status={status} /> : null}
          </form>
        </div>

        <aside className="space-y-4">
          {signedInPending ? (
            <div className="card p-6 space-y-2 bg-scYellow/25">
              <h2 className="font-display text-xl">Signed in as</h2>
              <p className="font-sans text-sm text-black/80">{user?.email}</p>
              <StatusCallout status={user!.status} />
            </div>
          ) : null}

          <div className="card p-6 space-y-3 bg-scGreen/20">
            <h2 className="font-display text-xl">How access works</h2>
            <ol className="list-decimal space-y-2 pl-5 font-sans text-sm text-black/80">
              <li>Request access with your campus email and create a password.</li>
              <li>A Second Course developer approves your email and assigns your campus and role.</li>
              <li>Sign in with email + password to open your university's live dashboard.</li>
            </ol>
          </div>

          <div className="callout-neutral">
            Need help? Email{" "}
            <a className="underline" href="mailto:support@secondcourse.co">
              support@secondcourse.co
            </a>
          </div>
        </aside>
      </div>
    </PortalShell>
  );
}
