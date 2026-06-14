import { useEffect, useState, useMemo } from "react";
import { deleteEvent, getCurrentUser, getUsers, updateEvent } from "../api";
import { SecurityEvent, EventUpdatePayload, User } from "../types";

const STATUS_OPTIONS = ["Open", "In Progress", "Resolved"] as const;
const SEVERITY_OPTIONS = ["HIGH", "MEDIUM", "LOW"] as const;

interface EventViewModalProps {
  event: SecurityEvent;
  userRole: string;
  onClose: () => void;
  onSaved: () => void;
  onDeleted: () => void;
}

function severityClass(severity: string) {
  if (severity === "HIGH") return "event-modal-control--severity-high";
  if (severity === "MEDIUM") return "event-modal-control--severity-medium";
  return "event-modal-control--severity-low";
}

interface FormRowProps {
  label: string;
  fullWidth?: boolean;
  children: React.ReactNode;
}

function FormRow({ label, fullWidth, children }: FormRowProps) {
  return (
    <div className={`event-modal-row${fullWidth ? " event-modal-row--full" : ""}`}>
      <div className="event-modal-label">{label}</div>
      <div className="event-modal-control-wrap">{children}</div>
    </div>
  );
}

export default function EventViewModal({
  event,
  userRole,
  onClose,
  onSaved,
  onDeleted,
}: EventViewModalProps) {
  const isViewer = userRole === "viewer";
  const isAnalyst = userRole === "analyst";
  const isAdmin = userRole === "admin";

  const [severity, setSeverity] = useState(event.severity);
  const [title, setTitle] = useState(event.title);
  const [asset, setAsset] = useState(event.asset);
  const [sourceIp, setSourceIp] = useState(event.source_ip);
  const [userId, setUserId] = useState(event.user_id);
  const [status, setStatus] = useState(event.status || "Open");
  const [comments, setComments] = useState(event.comments || "");
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [usersLoading, setUsersLoading] = useState(false);

  useEffect(() => {
    getCurrentUser()
      .then(setCurrentUser)
      .catch(() => setCurrentUser(null));
  }, []);

  useEffect(() => {
    if (!isAdmin) return;
    setUsersLoading(true);
    getUsers()
      .then(setUsers)
      .catch(() => setUsers([]))
      .finally(() => setUsersLoading(false));
  }, [isAdmin]);

  const activeUsers = useMemo(
    () => users.filter((u) => u.status === "active"),
    [users]
  );

  const assigneeOptions = useMemo(() => {
    const options = activeUsers.map((u) => ({ value: u.id, label: u.email }));
    if (userId && !options.some((o) => o.value === userId)) {
      const assigned = users.find((u) => u.id === userId);
      const label =
        assigned?.email ??
        (currentUser?.id === userId ? currentUser.email : "Unknown user");
      options.unshift({ value: userId, label });
    }
    return options;
  }, [activeUsers, users, userId, currentUser]);

  const resolveUserEmail = (id: string): string => {
    const match = users.find((u) => u.id === id);
    if (match) return match.email;
    if (currentUser?.id === id) return currentUser.email;
    return id;
  };

  useEffect(() => {
    setSeverity(event.severity);
    setTitle(event.title);
    setAsset(event.asset);
    setSourceIp(event.source_ip);
    setUserId(event.user_id);
    setStatus(event.status || "Open");
    setComments(event.comments || "");
    setError(null);
  }, [event]);

  const disabled = saving || deleting;

  const handleSave = async () => {
    setError(null);
    setSaving(true);

    try {
      let payload: EventUpdatePayload = {};

      if (isAdmin) {
        payload = {
          severity,
          title,
          asset,
          source_ip: sourceIp,
          user_id: userId,
          status,
          comments,
        };
      } else if (isAnalyst) {
        payload = { status, comments };
      }

      await updateEvent(event.id, payload);
      onSaved();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save changes");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm(`Permanently delete event "${event.title}"?`)) return;

    setError(null);
    setDeleting(true);

    try {
      await deleteEvent(event.id);
      onDeleted();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete event");
    } finally {
      setDeleting(false);
    }
  };

  const rawEventData = {
    id: event.id,
    severity: isAdmin ? severity : event.severity,
    title: isAdmin ? title : event.title,
    description: event.description,
    asset: isAdmin ? asset : event.asset,
    source_ip: isAdmin ? sourceIp : event.source_ip,
    user_id: isAdmin ? userId : event.user_id,
    status,
    comments,
    timestamp: event.timestamp,
    tags: event.tags || [],
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal event-modal" onClick={(e) => e.stopPropagation()}>
        <button
          className="modal-close"
          type="button"
          onClick={onClose}
          disabled={disabled}
          aria-label="Close"
        >
          ✕
        </button>

        <header className="event-modal-header">
          <h2>{event.title}</h2>
          <div className="event-modal-meta">
            <span>
              Event ID: <code>{event.id}</code>
            </span>
            <span className="event-modal-role">
              {userRole}
              {isViewer && " · read-only"}
            </span>
          </div>
          
          {event.tags && event.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-2" style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginTop: "8px" }}>
              {event.tags.map((tag, index) => (
                <span 
                  key={index} 
                  className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-zinc-800 text-zinc-200 border border-zinc-700"
                  style={{
                    backgroundColor: "#27272a",
                    color: "#e4e4e7",
                    border: "1px solid #3f3f46",
                    borderRadius: "4px",
                    padding: "2px 8px",
                    fontSize: "12px",
                    fontWeight: 500,
                    display: "inline-flex",
                    alignItems: "center"
                  }}
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </header>

        {error && <div className="event-modal-error">{error}</div>}

        <div className="event-modal-body">
          <div className="event-modal-form">
            {/* Severity */}
            <FormRow label="Severity">
              {isAdmin ? (
                <select
                  className="event-modal-control"
                  value={severity}
                  onChange={(e) =>
                    setSeverity(e.target.value as SecurityEvent["severity"])
                  }
                  disabled={disabled}
                >
                  {SEVERITY_OPTIONS.map((opt) => (
                    <option key={opt} value={opt}>
                      {opt}
                    </option>
                  ))}
                </select>
              ) : (
                <div
                  className={`event-modal-control event-modal-readonly ${severityClass(severity)}`}
                >
                  {severity}
                </div>
              )}
            </FormRow>

            {/* Title */}
            <FormRow label="Title">
              {isAdmin ? (
                <input
                  type="text"
                  className="event-modal-control"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  disabled={disabled}
                />
              ) : (
                <div className="event-modal-control event-modal-readonly">
                  {title}
                </div>
              )}
            </FormRow>

            {/* Asset */}
            <FormRow label="Asset">
              {isAdmin ? (
                <input
                  type="text"
                  className="event-modal-control event-modal-readonly--mono"
                  value={asset}
                  onChange={(e) => setAsset(e.target.value)}
                  disabled={disabled}
                />
              ) : (
                <div className="event-modal-control event-modal-readonly event-modal-readonly--mono">
                  {asset || "—"}
                </div>
              )}
            </FormRow>

            {/* Source IP */}
            <FormRow label="Source IP">
              {isAdmin ? (
                <input
                  type="text"
                  className="event-modal-control event-modal-readonly--mono"
                  value={sourceIp}
                  onChange={(e) => setSourceIp(e.target.value)}
                  disabled={disabled}
                />
              ) : (
                <div className="event-modal-control event-modal-readonly event-modal-readonly--mono">
                  {sourceIp || "—"}
                </div>
              )}
            </FormRow>

            {/* Assigned User */}
            <FormRow label="Assigned User">
              {isAdmin ? (
                <select
                  className="event-modal-control"
                  value={userId}
                  onChange={(e) => setUserId(e.target.value)}
                  disabled={disabled || usersLoading}
                >
                  {usersLoading && assigneeOptions.length === 0 ? (
                    <option value={userId}>Loading users…</option>
                  ) : (
                    assigneeOptions.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))
                  )}
                </select>
              ) : (
                <div className="event-modal-control event-modal-readonly">
                  {resolveUserEmail(userId)}
                </div>
              )}
            </FormRow>

            {/* Description — full width */}
            <FormRow label="Description" fullWidth>
              <div className="event-modal-control event-modal-readonly event-modal-readonly--textarea">
                {event.description || "—"}
              </div>
            </FormRow>

            {/* Timestamp */}
            <FormRow label="Timestamp">
              <div className="event-modal-control event-modal-readonly">
                {new Date(event.timestamp).toLocaleString()}
              </div>
            </FormRow>

            {/* Status */}
            <FormRow label="Status">
              {isAnalyst || isAdmin ? (
                <select
                  className="event-modal-control"
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                  disabled={disabled}
                >
                  {STATUS_OPTIONS.map((opt) => (
                    <option key={opt} value={opt}>
                      {opt}
                    </option>
                  ))}
                </select>
              ) : (
                <div className="event-modal-control event-modal-readonly">
                  {status}
                </div>
              )}
            </FormRow>

            {/* Notes / Comments — full width */}
            <FormRow label="Notes / Comments" fullWidth>
              {isAnalyst || isAdmin ? (
                <textarea
                  className="event-modal-control event-modal-control--textarea"
                  value={comments}
                  onChange={(e) => setComments(e.target.value)}
                  disabled={disabled}
                  rows={4}
                />
              ) : (
                <div className="event-modal-control event-modal-readonly event-modal-readonly--textarea">
                  {comments || "—"}
                </div>
              )}
            </FormRow>
          </div>
        </div>

        {(isAnalyst || isAdmin) && (
          <div className="event-modal-actions">
            <button
              type="button"
              className="btn-primary"
              onClick={handleSave}
              disabled={disabled}
            >
              {saving ? "Saving…" : "Save Changes"}
            </button>
            {isAdmin && (
              <button
                type="button"
                className="event-modal-btn-delete"
                onClick={handleDelete}
                disabled={disabled}
              >
                {deleting ? "Deleting…" : "Delete Event"}
              </button>
            )}
          </div>
        )}

        <div className="event-modal-raw">
          <h3>Raw Event Data</h3>
          <pre>{JSON.stringify(rawEventData, null, 2)}</pre>
        </div>
      </div>
    </div>
  );
}