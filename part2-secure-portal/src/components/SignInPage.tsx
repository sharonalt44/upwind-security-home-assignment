import { useState } from "react";
import { login } from "../api";
import { User } from "../types";

interface SignInPageProps {
  onSuccess: (user: User) => void;
}

export default function SignInPage({ onSuccess }: SignInPageProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const user = await login(email, password);
      onSuccess(user);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="sign-in-page">
      <div className="sign-in-layout">
        <header className="sign-in-welcome">
          <div className="sign-in-penguin" aria-hidden="true">
            🐧
          </div>
          <h1 className="sign-in-welcome-title">Welcome to PenguWave</h1>
          <p className="sign-in-welcome-subtitle">
            Please log in to your account to access the platform.
          </p>
        </header>

        <div className="sign-in-card">
          <h2 className="sign-in-card-title">Sign In</h2>
          <p className="sign-in-subtitle">
            Enter your credentials to access the Security Operations Portal
          </p>

          <form onSubmit={handleSubmit}>
            {error && <div className="sign-in-error">{error}</div>}

            <div className="sign-in-field">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                required
                disabled={loading}
                autoComplete="email"
              />
            </div>

            <div className="sign-in-field">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                disabled={loading}
                autoComplete="current-password"
              />
            </div>

            <button type="submit" className="btn-primary sign-in-submit" disabled={loading}>
              {loading ? "Signing In…" : "Sign In"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
