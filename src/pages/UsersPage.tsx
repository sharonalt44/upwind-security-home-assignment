import { useState, useEffect, useCallback } from "react";
import { User, UserRole, UserStatus } from "../types";
import { getUsers, createUser, deleteUser, updateUser, getCurrentUser } from "../api";

const ROLES: UserRole[] = ["admin", "analyst", "viewer"];
const STATUSES: UserStatus[] = ["active", "disabled"];

function statusSelectClass(status: UserStatus): string {
  return status === "active"
    ? "user-status-select user-status-select--active"
    : "user-status-select user-status-select--disabled";
}

function formatErrorMessage(rawError: string | null): string | null {
  if (!rawError) return null;
  if (rawError.includes("Not authenticated") || rawError.includes("token missing")) {
    return "Session has expired. Please log in again.";
  }
  return rawError;
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [showForm, setShowForm] = useState(false);
  const [newEmail, setNewEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newRole, setNewRole] = useState<UserRole>("analyst");
  const [newStatus, setNewStatus] = useState<UserStatus>("active");

  const [currentUserId, setCurrentUserId] = useState<string | null>(null);
  const [updatingStatusId, setUpdatingStatusId] = useState<string | null>(null);
  const [updatingRoleId, setUpdatingRoleId] = useState<string | null>(null);

  const loadUsers = useCallback(() => {
    setLoading(true);
    setError(null);
    getUsers()
      .then((data: User[]) => {
        setUsers(data);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || "Failed to load system users.");
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    loadUsers();
    getCurrentUser()
      .then((user: User) => setCurrentUserId(user.id))
      .catch(() => setCurrentUserId(null));
  }, [loadUsers]);

  const isSelf = (userId: string): boolean => userId === currentUserId;

  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEmail || !newPassword) return;
    setError(null);

    try {
      await createUser({
        email: newEmail,
        password: newPassword,
        role: newRole,
        status: newStatus,
      });

      setNewEmail("");
      setNewPassword("");
      setNewRole("analyst");
      setNewStatus("active");
      setShowForm(false);
      loadUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to provision new user profile");
    }
  };

  const handleStatusChange = async (user: User, nextStatus: UserStatus) => {
    if (nextStatus === user.status || isSelf(user.id)) return;

    setError(null);
    setUpdatingStatusId(user.id);

    const previousStatus = user.status;
    setUsers((prev) =>
      prev.map((u) => (u.id === user.id ? { ...u, status: nextStatus } : u))
    );

    try {
      await updateUser(user.id, { status: nextStatus });
      loadUsers();
    } catch (err) {
      setUsers((prev) =>
        prev.map((u) => (u.id === user.id ? { ...u, status: previousStatus } : u))
      );
      setError(err instanceof Error ? err.message : "Failed to update user status");
    } finally {
      setUpdatingStatusId(null);
    }
  };

  const handleRoleChange = async (user: User, nextRole: UserRole) => {
    if (nextRole === user.role || isSelf(user.id)) return;

    setError(null);
    setUpdatingRoleId(user.id);

    const previousRole = user.role;
    setUsers((prev) =>
      prev.map((u) => (u.id === user.id ? { ...u, role: nextRole } : u))
    );

    try {
      await updateUser(user.id, { role: nextRole });
      loadUsers();
    } catch (err) {
      setUsers((prev) =>
        prev.map((u) => (u.id === user.id ? { ...u, role: previousRole } : u))
      );
      setError(err instanceof Error ? err.message : "Failed to update user role");
    } finally {
      setUpdatingRoleId(null);
    }
  };

  const handleDelete = async (id: string) => {
    if (isSelf(id)) return;
    if (!window.confirm("Are you sure you want to permanently delete this user account?")) return;
    setError(null);

    try {
      await deleteUser(id);
      loadUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to execute account purge");
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <p>Loading system registry streams...</p>
      </div>
    );
  }

  if (error && users.length === 0) {
    return (
      <div className="page-container">
        <h1>User Management</h1>
        <p style={{ color: "red", backgroundColor: "#fee2e2", padding: 12, borderRadius: 6 }}>
          <strong>Access Denied:</strong> {formatErrorMessage(error)}
        </p>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 16,
        }}
      >
        <h1>User Management</h1>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancel" : "Add User"}
        </button>
      </div>

      {error && (
        <div
          style={{
            color: "red",
            backgroundColor: "#fee2e2",
            padding: 12,
            borderRadius: 6,
            marginBottom: 16,
            fontSize: 14,
          }}
        >
          <strong>Operational Exception:</strong> {formatErrorMessage(error)}
        </div>
      )}

      {showForm && (
        <div
          style={{
            border: "1px solid #ddd",
            padding: 16,
            marginBottom: 20,
            background: "#fafafa",
          }}
        >
          <h3 style={{ marginBottom: 12 }}>New User</h3>
          <form onSubmit={handleAddUser}>
            <div style={{ marginBottom: 8 }}>
              <label htmlFor="new-user-email">Email</label>
              <input
                id="new-user-email"
                type="email"
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                placeholder="user@penguwave.io"
                required
              />
            </div>
            <div style={{ marginBottom: 8 }}>
              <label htmlFor="new-user-password">Password</label>
              <input
                id="new-user-password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Minimum 8 characters"
                minLength={8}
                required
              />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label htmlFor="new-user-role">Role</label>
              <select
                id="new-user-role"
                value={newRole}
                onChange={(e) => setNewRole(e.target.value as UserRole)}
              >
                {ROLES.map((role) => (
                  <option key={role} value={role}>
                    {role.charAt(0).toUpperCase() + role.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            <div style={{ marginBottom: 12 }}>
              <label htmlFor="new-user-status">Status</label>
              <select
                id="new-user-status"
                value={newStatus}
                onChange={(e) => setNewStatus(e.target.value as UserStatus)}
              >
                {STATUSES.map((status) => (
                  <option key={status} value={status}>
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            <button type="submit" className="btn-primary">
              Create User
            </button>
          </form>
        </div>
      )}

      <table className="users-table">
        <thead>
          <tr>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.email}</td>

              {/* Role column: editable dropdown for other users; locked for self */}
              <td>
                {isSelf(user.id) ? (
                  <span
                    className="user-field-locked"
                    title="You cannot change your own role"
                  >
                    {user.role}
                  </span>
                ) : (
                  <select
                    className="user-role-select"
                    value={user.role}
                    disabled={updatingRoleId === user.id}
                    onChange={(e) =>
                      handleRoleChange(user, e.target.value as UserRole)
                    }
                    aria-label={`Role for ${user.email}`}
                  >
                    {ROLES.map((role) => (
                      <option key={role} value={role}>
                        {role}
                      </option>
                    ))}
                  </select>
                )}
              </td>

              {/* Status column: editable dropdown for other users; locked for self */}
              <td>
                {isSelf(user.id) ? (
                  <span
                    className={
                      user.status === "active"
                        ? "user-status-locked"
                        : "user-status-locked user-status-locked--disabled"
                    }
                    title="You cannot disable your own account"
                  >
                    {user.status}
                  </span>
                ) : (
                  <select
                    className={statusSelectClass(user.status)}
                    value={user.status}
                    disabled={updatingStatusId === user.id}
                    onChange={(e) =>
                      handleStatusChange(user, e.target.value as UserStatus)
                    }
                    aria-label={`Status for ${user.email}`}
                  >
                    {STATUSES.map((status) => (
                      <option
                        key={status}
                        value={status}
                        className={
                          status === "active"
                            ? "user-status-option--active"
                            : "user-status-option--disabled"
                        }
                      >
                        {status}
                      </option>
                    ))}
                  </select>
                )}
              </td>

              {/* Actions column: delete blocked for self */}
              <td>
                {!isSelf(user.id) ? (
                  <a
                    href="#"
                    className="user-delete-link"
                    onClick={(e) => {
                      e.preventDefault();
                      handleDelete(user.id);
                    }}
                  >
                    Delete
                  </a>
                ) : (
                  <span
                    className="user-actions-muted"
                    title="You cannot delete your own account"
                  >
                    —
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {users.length === 0 && (
        <p style={{ color: "#999" }}>No registered profiles detected in database.</p>
      )}
    </div>
  );
}
