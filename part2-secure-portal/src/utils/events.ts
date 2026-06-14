import { SecurityEvent } from "../types";

/** Normalize API / legacy camelCase event payloads into a consistent shape. */
export function normalizeEvent(raw: Record<string, unknown>): SecurityEvent {
  const asset = String(raw.asset ?? raw.assetHostname ?? "");
  const sourceIp = String(raw.source_ip ?? raw.sourceIp ?? "");
  const userId = String(raw.user_id ?? raw.userId ?? "");

  return {
    id: String(raw.id ?? ""),
    timestamp: String(raw.timestamp ?? ""),
    severity: (raw.severity as SecurityEvent["severity"]) ?? "LOW",
    title: String(raw.title ?? ""),
    description: String(raw.description ?? ""),
    asset,
    source_ip: sourceIp,
    user_id: userId,
    status: String(raw.status ?? "Open"),
    comments: String(raw.comments ?? ""),
    tags: Array.isArray(raw.tags) ? (raw.tags as string[]) : [],
    assetHostname: asset,
    sourceIp,
    userId,
  };
}
