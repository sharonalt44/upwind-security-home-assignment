export interface SecurityEvent {
  id: string;
  timestamp: string;
  severity: "HIGH" | "MEDIUM" | "LOW";
  title: string;
  description: string;
  asset: string;
  source_ip: string;
  user_id: string;
  status: string;
  comments: string;
  tags?: string[];
  assetHostname?: string;
  assetIp?: string;
  sourceIp?: string;
  userId?: string;
}

/** Mirrors backend AllowedRole literal — admin | analyst | viewer */
export type UserRole = "admin" | "analyst" | "viewer";

/** Mirrors backend AllowedStatus literal — active | disabled */
export type UserStatus = "active" | "disabled";

export interface User {
  id: string;
  email: string;
  role: UserRole;
  status: UserStatus;
}

/** Payload for POST /users — mirrors backend UserCreate schema. */
export type UserCreatePayload = {
  email: string;
  password: string;
  role?: UserRole;
  status?: UserStatus;
};

/** Payload for PATCH /users/{id} — mirrors backend UserUpdate schema. */
export type UserUpdatePayload = {
  status?: UserStatus;
  role?: UserRole;
};

export type EventUpdatePayload = {
  severity?: string;
  title?: string;
  asset?: string;
  source_ip?: string;
  user_id?: string;
  status?: string;
  comments?: string;
};
