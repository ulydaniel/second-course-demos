import { useCallback, useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { PortalShell } from "../components/PortalShell";
import { getApiErrorMessage } from "../api";
import {
  approveUser,
  createUser,
  listUniversities,
  listUsers,
  type DashboardRole,
  type DashboardUser,
  type JobTitle,
  type University,
  type UserStatus,
} from "../api/auth";

const STATUS_FILTERS: { value: UserStatus | "all"; label: string }[] = [
  { value: "pending", label: "Pending" },
  { value: "approved", label: "Approved" },
  { value: "rejected", label: "Rejected" },
  { value: "all", label: "All" },
];

const DASHBOARD_ROLES: DashboardRole[] = ["administrator", "editor", "viewer"];

const JOB_TITLES: JobTitle[] = ["faculty", "representative", "dean", "admin", "staff", "other"];

function statusPill(status: UserStatus): string {
  if (status === "approved") return "pill bg-scGreen/40";
  if (status === "rejected") return "pill bg-scOrange/40";
  return "pill bg-scYellow/60";
}

function UserRow({
  user,
  universities,
  onChanged,
  onError,
}: {
  user: DashboardUser;
  universities: University[];
  onChanged: () => void;
  onError: (message: string) => void;
}) {
  const [role, setRole] = useState<DashboardRole>(user.dashboardRole);
  const [universityId, setUniversityId] = useState(user.university?.id ?? universities[0]?.id ?? "");
  const [busy, setBusy] = useState(false);

  async function apply(status: UserStatus) {
    setBusy(true);
    onError("");
    try {
      await approveUser(user.id, { status, dashboardRole: role, universityId });
      onChanged();
    } catch (error) {
      onError(getApiErrorMessage(error));
    } finally {
      setBusy(false);
    }
  }

  return (
    <tr>
      <td>
        <div className="font-sans text-sm font-semibold">{user.fullName || "—"}</div>
        <div className="font-sans text-xs text-black/60">{user.email}</div>
        <div className="font-sans text-xs text-black/50 capitalize">{user.jobTitle}</div>
      </td>
      <td>
        <span className={statusPill(user.status)}>{user.status}</span>
      </td>
      <td>
        <select
          value={universityId}
          onChange={(event) => setUniversityId(event.target.value)}
          className="rounded-lg border-2 border-black bg-white px-2 py-1 font-sans text-xs"
        >
          {universities.map((university) => (
            <option key={university.id} value={university.id}>
              {university.name}
            </option>
          ))}
        </select>
      </td>
      <td>
        <select
          value={role}
          onChange={(event) => setRole(event.target.value as DashboardRole)}
          className="rounded-lg border-2 border-black bg-white px-2 py-1 font-sans text-xs capitalize"
        >
          {DASHBOARD_ROLES.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </td>
      <td>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            className="btn-primary text-xs"
            disabled={busy}
            onClick={() => apply("approved")}
          >
            {user.status === "approved" ? "Update" : "Approve"}
          </button>
          {user.status !== "rejected" ? (
            <button
              type="button"
              className="btn-secondary text-xs"
              disabled={busy}
              onClick={() => apply("rejected")}
            >
              Reject
            </button>
          ) : null}
        </div>
      </td>
    </tr>
  );
}

export default function AdminApprovals() {
  const [filter, setFilter] = useState<UserStatus | "all">("pending");
  const [users, setUsers] = useState<DashboardUser[]>([]);
  const [universities, setUniversities] = useState<University[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [newEmail, setNewEmail] = useState("");
  const [newName, setNewName] = useState("");
  const [newRole, setNewRole] = useState<DashboardRole>("viewer");
  const [newJob, setNewJob] = useState<JobTitle>("staff");
  const [newUniversity, setNewUniversity] = useState("");
  const [creating, setCreating] = useState(false);
  const [createMessage, setCreateMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const status = filter === "all" ? undefined : filter;
      const list = await listUsers(status);
      setUsers(list);
    } catch (loadError) {
      setError(getApiErrorMessage(loadError));
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    listUniversities()
      .then((list) => {
        setUniversities(list);
        setNewUniversity((current) => current || list[0]?.id || "");
      })
      .catch(() => undefined);
  }, []);

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    setCreating(true);
    setCreateMessage(null);
    setError(null);
    try {
      await createUser({
        email: newEmail,
        fullName: newName,
        jobTitle: newJob,
        dashboardRole: newRole,
        universityId: newUniversity,
      });
      setCreateMessage(`Approved ${newEmail}.`);
      setNewEmail("");
      setNewName("");
      await load();
    } catch (createError) {
      setError(getApiErrorMessage(createError));
    } finally {
      setCreating(false);
    }
  }

  return (
    <PortalShell
      title="Access Approvals"
      subtitle="Approve campus emails and assign each user a dashboard role and university."
    >
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap gap-2" role="tablist" aria-label="Filter users by status">
          {STATUS_FILTERS.map((option) => (
            <button
              key={option.value}
              type="button"
              className={`pill ${filter === option.value ? "pill-active" : "bg-white"}`}
              onClick={() => setFilter(option.value)}
            >
              {option.label}
            </button>
          ))}
        </div>
        <Link to="/dashboard" className="pill bg-white">
          Open dashboard →
        </Link>
      </div>

      {error ? (
        <div className="callout-warning mb-4">{error}</div>
      ) : null}

      <div className="card mb-6 overflow-x-auto p-4">
        {loading ? (
          <p className="font-sans text-sm text-black/70">Loading users…</p>
        ) : users.length === 0 ? (
          <p className="font-sans text-sm text-black/70">No users in this view yet.</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Status</th>
                <th>University</th>
                <th>Dashboard role</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <UserRow
                  key={user.id}
                  user={user}
                  universities={universities}
                  onChanged={load}
                  onError={(message) => setError(message || null)}
                />
              ))}
            </tbody>
          </table>
        )}
      </div>

      <form className="card space-y-4 p-6 bg-scGreen/15" onSubmit={handleCreate}>
        <h2 className="font-display text-xl">Pre-approve an email</h2>
        <p className="font-sans text-sm text-black/70">
          Add a campus email directly to the allowlist so the user is approved before they register.
        </p>
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="block space-y-1">
            <span className="font-sans text-sm font-semibold">Email</span>
            <input
              type="email"
              required
              value={newEmail}
              onChange={(event) => setNewEmail(event.target.value)}
              placeholder="dean@university.edu"
              className="w-full rounded-lg border-2 border-black bg-white px-3 py-2 font-sans text-sm"
            />
          </label>
          <label className="block space-y-1">
            <span className="font-sans text-sm font-semibold">Full name</span>
            <input
              type="text"
              value={newName}
              onChange={(event) => setNewName(event.target.value)}
              placeholder="Optional"
              className="w-full rounded-lg border-2 border-black bg-white px-3 py-2 font-sans text-sm"
            />
          </label>
          <label className="block space-y-1">
            <span className="font-sans text-sm font-semibold">University</span>
            <select
              value={newUniversity}
              onChange={(event) => setNewUniversity(event.target.value)}
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
            <span className="font-sans text-sm font-semibold">Dashboard role</span>
            <select
              value={newRole}
              onChange={(event) => setNewRole(event.target.value as DashboardRole)}
              className="w-full rounded-lg border-2 border-black bg-white px-3 py-2 font-sans text-sm capitalize"
            >
              {DASHBOARD_ROLES.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
          <label className="block space-y-1">
            <span className="font-sans text-sm font-semibold">Role on campus</span>
            <select
              value={newJob}
              onChange={(event) => setNewJob(event.target.value as JobTitle)}
              className="w-full rounded-lg border-2 border-black bg-white px-3 py-2 font-sans text-sm capitalize"
            >
              {JOB_TITLES.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button type="submit" className="btn-primary" disabled={creating}>
            {creating ? "Adding…" : "Add to allowlist"}
          </button>
          {createMessage ? (
            <span className="font-sans text-sm text-black/70">{createMessage}</span>
          ) : null}
        </div>
      </form>
    </PortalShell>
  );
}
