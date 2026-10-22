import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "@tanstack/react-router";
import { useAuth } from "@/lib/auth";

export function AuthForm({ kind }: { kind: "login" | "signup" }) {
  const { logIn, signUp } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      if (kind === "login") await logIn(email, password);
      else await signUp(username, email, password);
      navigate({ to: "/" });
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <form onSubmit={submit} className="panel mx-auto flex w-full max-w-sm flex-col gap-4">
      <h1 className="font-display text-xl text-primary glow">
        {kind === "login" ? "LOG IN" : "SIGN UP"}
      </h1>
      {kind === "signup" && (
        <label className="field">
          Username
          <input value={username} onChange={(e) => setUsername(e.target.value)} required />
        </label>
      )}
      <label className="field">
        Email
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
      </label>
      <label className="field">
        Password
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
      </label>
      {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
      <button className="btn-primary" disabled={busy} type="submit">
        {busy ? "…" : kind === "login" ? "Log in" : "Create account"}
      </button>
      <p className="text-xs text-muted-foreground">
        {kind === "login" ? (
          <>No account? <Link to="/signup" className="underline">Sign up</Link> · Demo: demo@snake.dev / demo123</>
        ) : (
          <>Have an account? <Link to="/login" className="underline">Log in</Link></>
        )}
      </p>
    </form>
  );
}
