import { useState, useEffect, useCallback } from "react";
import { getEvents, getCurrentUser } from "../api";
import { SecurityEvent } from "../types";
import { normalizeEvent } from "../utils/events";
import EventViewModal from "../components/EventViewModal";

export default function EventsPage() {
  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [selectedEvent, setSelectedEvent] = useState<SecurityEvent | null>(null);
  const [userRole, setUserRole] = useState<string>("viewer");

  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const loadEvents = useCallback(async () => {
    const data = await getEvents();
    setEvents(data.map((e: Record<string, unknown>) => normalizeEvent(e)));
  }, []);

  useEffect(() => {
    Promise.all([getEvents(), getCurrentUser().catch(() => null)])
      .then(([data, user]) => {
        setEvents(data.map((e: Record<string, unknown>) => normalizeEvent(e)));
        if (user?.role) setUserRole(user.role);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to load real-time telemetry");
        setLoading(false);
      });
  }, []);

  const showSuccess = (message: string) => {
    setSuccessMessage(message);
    setTimeout(() => setSuccessMessage(null), 3500);
  };

  const handleSaved = async () => {
    await loadEvents();
    showSuccess("Event updated successfully.");
  };

  const handleDeleted = async () => {
    await loadEvents();
    showSuccess("Event deleted successfully.");
  };

  const filtered = events.filter((e) => {
    const title = e.title || "";
    const description = e.description || "";
    const hostname = e.asset || "";

    const matchesSearch =
      title.toLowerCase().includes(search.toLowerCase()) ||
      description.toLowerCase().includes(search.toLowerCase()) ||
      hostname.toLowerCase().includes(search.toLowerCase());
    const matchesSeverity = severityFilter === "ALL" || e.severity === severityFilter;
    return matchesSearch && matchesSeverity;
  });

  const severityColor = (s: string) => {
    if (s === "HIGH") return "red";
    if (s === "MEDIUM") return "orange";
    return "green";
  };

  if (loading) {
    return <div className="page-container"><p>Fetching secure telemetry streams...</p></div>;
  }

  if (error) {
    return (
      <div className="page-container">
        <h1>Security Events</h1>
        <p style={{ color: "red", backgroundColor: "#fee2e2", padding: 12, borderRadius: 6 }}>
          <strong>Access Denied / Connection Error:</strong> {error}
        </p>
      </div>
    );
  }

  return (
    <div className="page-container">
      <h1>Security Events</h1>

      {successMessage && (
        <p
          style={{
            color: "#166534",
            backgroundColor: "#dcfce7",
            padding: "10px 14px",
            borderRadius: 6,
            marginBottom: 16,
            fontSize: 14,
          }}
        >
          {successMessage}
        </p>
      )}

      <div style={{ marginBottom: 16, display: "flex", gap: 12, alignItems: "center" }}>
        <input
          type="text"
          placeholder="Search events..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ width: "100%", maxWidth: 400 }}
        />
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          style={{ width: 140 }}
        >
          <option value="ALL">All Severities</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>
      </div>

      {search && (
        <p>
          <span
            dangerouslySetInnerHTML={{
              __html: "Showing results for: <strong>" + search + "</strong>",
            }}
          />
          {" "}({filtered.length} events)
        </p>
      )}

      <table>
        <thead>
          <tr>
            <th>Severity</th>
            <th>Title</th>
            <th>Asset</th>
            <th>Source IP</th>
            <th>Status</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map((event) => (
            <tr
              key={event.id}
              onClick={() => setSelectedEvent(event)}
              style={{ cursor: "pointer" }}
            >
              <td style={{ color: severityColor(event.severity), fontWeight: 600 }}>
                {event.severity}
              </td>
              <td>{event.title}</td>
              <td style={{ fontFamily: "monospace", fontSize: 13 }}>
                {event.asset}
              </td>
              <td style={{ fontFamily: "monospace", fontSize: 13 }}>
                {event.source_ip}
              </td>
              <td style={{ fontSize: 13 }}>{event.status || "Open"}</td>
              <td style={{ fontSize: 13 }}>
                {new Date(event.timestamp).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {filtered.length === 0 && <p style={{ color: "#999" }}>No events found.</p>}

      <div style={{ marginTop: 12 }}>
        <button
          onClick={() => {
            const blob = new Blob([JSON.stringify(filtered, null, 2)], { type: "application/json" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "penguwave_events_export.json";
            a.click();
            URL.revokeObjectURL(url);
          }}
          style={{ fontSize: 13 }}
        >
          Export Events (JSON)
        </button>
      </div>

      {selectedEvent && (
        <EventViewModal
          event={selectedEvent}
          userRole={userRole}
          onClose={() => setSelectedEvent(null)}
          onSaved={handleSaved}
          onDeleted={handleDeleted}
        />
      )}
    </div>
  );
}
