"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AudioLines, Layers3, Mic, Package, PlusCircle, Sparkles, TrendingUp } from "lucide-react";
import { clearStoredAuthToken, commitVoice, getInventory, getMe, getStoredAuthToken, parseVoice } from "@/lib/api";

const metrics = [
  { label: "Today’s voice events", value: "48", icon: Mic },
  { label: "Fast-moving items", value: "12", icon: TrendingUp },
  { label: "Low stock alerts", value: "4", icon: Package },
  { label: "Automation score", value: "94%", icon: Sparkles },
];

export function DashboardShell() {
  const router = useRouter();
  const [token, setToken] = useState("");
  const [userName, setUserName] = useState("");
  const [storeName, setStoreName] = useState("");
  const [voiceText, setVoiceText] = useState("add 2.5 kg rice and remove 3 packets of milk");
  const [preview, setPreview] = useState<Record<string, unknown> | null>(null);
  const [inventory, setInventory] = useState<Array<Record<string, unknown>>>([]);
  const [message, setMessage] = useState<string>("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const storedToken = getStoredAuthToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }
    setToken(storedToken);
    getMe(storedToken)
      .then((response) => {
        setUserName(String(response.user.name ?? "Merchant"));
        setStoreName(String(response.user.storeName ?? "Your store"));
      })
      .catch(() => {
        clearStoredAuthToken();
        router.replace("/login");
      });
  }, [router]);

  useEffect(() => {
    if (!token) {
      return;
    }
    getInventory(token)
      .then((response) => setInventory(response.items))
      .catch(() => setMessage("Sign in to load inventory data."));
  }, [token]);

  async function runPreview() {
    if (!token) {
      setMessage("Store a JWT token in localStorage as merchant-pos-token to use the dashboard demo.");
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      const parsed = await parseVoice(token, voiceText);
      setPreview(parsed.result);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to parse voice command");
    } finally {
      setLoading(false);
    }
  }

  async function runCommit() {
    if (!token) {
      setMessage("Store a JWT token in localStorage as merchant-pos-token to commit voice commands.");
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      const response = await commitVoice(token, voiceText);
      setMessage(response.message);
      const refreshed = await getInventory(token);
      setInventory(refreshed.items);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to commit voice command");
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    clearStoredAuthToken();
    router.replace("/login");
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 px-4 py-6 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl space-y-6">
        <section className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm lg:p-8">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-100 px-4 py-2 text-sm text-slate-700">
                <Layers3 className="h-4 w-4" />
                Merchant command center
              </div>
              <h1 className="mt-5 font-[family-name:var(--font-display)] text-4xl font-bold text-slate-900 sm:text-5xl">Inventory, voice, and sales control in one panel.</h1>
              <p className="mt-3 max-w-3xl text-base leading-7 text-slate-700">
                This dashboard is designed for quick merchant actions: speak the order, preview the parser, commit stock changes, and keep a clean audit trail.
              </p>
              <p className="mt-3 text-sm text-slate-500">
                {storeName ? `${storeName}` : ""}{userName ? ` · ${userName}` : ""}
              </p>
            </div>
            <div className="flex flex-col gap-3 rounded-3xl border border-slate-200 bg-slate-50 px-5 py-4 text-sm text-slate-700">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Backend</p>
                <p className="mt-2 font-semibold text-slate-900">Flask + MongoDB + optional LLM parsing</p>
              </div>
              <button onClick={logout} className="inline-flex w-fit items-center justify-center rounded-full border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-100">
                Logout
              </button>
            </div>
          </div>
        </section>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {metrics.map((metric) => {
            const Icon = metric.icon;
            return (
              <article key={metric.label} className="rounded-[1.5rem] border border-slate-200 bg-white p-5 shadow-sm">
                <Icon className="h-6 w-6 text-sky-600" />
                <p className="mt-4 text-sm text-slate-500">{metric.label}</p>
                <p className="mt-2 text-3xl font-semibold text-slate-900">{metric.value}</p>
              </article>
            );
          })}
        </section>

        <section className="grid gap-6 lg:grid-cols-[1fr_0.95fr]">
          <article className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center gap-3">
              <AudioLines className="h-5 w-5 text-sky-600" />
              <h2 className="text-2xl font-semibold text-slate-900">Voice command workbench</h2>
            </div>
            <textarea
              value={voiceText}
              onChange={(event) => setVoiceText(event.target.value)}
              className="mt-5 min-h-36 w-full rounded-[1.5rem] border border-slate-200 bg-slate-50 p-4 text-slate-900 outline-none placeholder:text-slate-500 focus:border-sky-300 focus:ring-2 focus:ring-sky-100"
              placeholder="Say things like: add 1.5 kg rice, remove 3 packets milk, set 12 bottles water"
            />
            <div className="mt-4 flex flex-wrap gap-3">
              <button onClick={runPreview} disabled={loading} className="inline-flex items-center gap-2 rounded-full bg-sky-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-sky-600 disabled:opacity-50">
                <Mic className="h-4 w-4" />
                Preview parse
              </button>
              <button onClick={runCommit} disabled={loading} className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-50">
                <PlusCircle className="h-4 w-4" />
                Commit change
              </button>
            </div>
            {message ? <p className="mt-4 rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">{message}</p> : null}
            {preview ? (
              <pre className="mt-4 overflow-auto rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">{JSON.stringify(preview, null, 2)}</pre>
            ) : null}
          </article>

          <article className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-2xl font-semibold text-slate-900">Inventory snapshot</h2>
            <div className="mt-5 space-y-3">
              {inventory.length ? inventory.map((item) => (
                <div key={String(item._id ?? item.name)} className="flex items-center justify-between rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
                  <div>
                    <p className="font-medium text-slate-900">{String(item.displayName ?? item.name)}</p>
                    <p className="text-sm text-slate-500">Unit: {String(item.unit ?? "piece")}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-semibold text-slate-900">{String(item.stock ?? 0)}</p>
                    <p className="text-xs text-slate-600">Reorder {String(item.reorderLevel ?? 0)}</p>
                  </div>
                </div>
              )) : (
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
                  Connect a token to load inventory, or use the API to seed the initial merchant catalog.
                </div>
              )}
            </div>
          </article>
        </section>
      </div>
    </main>
  );
}
