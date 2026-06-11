"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight, LoaderCircle, Mic, ShieldCheck } from "lucide-react";
import { getStoredAuthToken, login, register, setStoredAuthToken } from "@/lib/api";

export function AuthScreen({ mode }: { mode: "login" | "register" }) {
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    if (getStoredAuthToken()) {
      router.replace("/dashboard");
    }
  }, [router]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const formData = new FormData(event.currentTarget);
      const payload = {
        name: String(formData.get("name") ?? ""),
        storeName: String(formData.get("storeName") ?? ""),
        email: String(formData.get("email") ?? ""),
        password: String(formData.get("password") ?? ""),
      };
      const response = mode === "login" ? await login(payload) : await register(payload);
      setStoredAuthToken(response.token);
      router.replace("/dashboard");
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-gradient-to-br from-slate-50 to-slate-100 px-6 py-10">
      <div className="w-full max-w-5xl overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-md lg:grid lg:grid-cols-[0.92fr_1.08fr]">
        <section className="flex flex-col justify-between border-b border-slate-200 bg-gradient-to-br from-slate-900 to-slate-800 p-8 lg:border-b-0 lg:border-r lg:p-10">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-slate-700 bg-slate-800 px-4 py-2 text-sm text-sky-200">
              <Mic className="h-4 w-4" />
              Voice-first retail access
            </div>
            <h1 className="mt-8 max-w-md font-[family-name:var(--font-display)] text-4xl font-bold tracking-tight text-slate-50 lg:text-5xl">
              {mode === "login" ? "Welcome back to your store" : "Create your merchant workspace"}
            </h1>
            <p className="mt-4 max-w-lg text-base leading-7 text-slate-200">
              Use one login for inventory, voice commands, and audit trails. The backend is JWT-based and ready for MongoDB-backed production deployment.
            </p>
          </div>

          <div className="mt-10 rounded-[1.5rem] border border-slate-700 bg-slate-900 p-5 text-sm leading-7 text-slate-300">
            <div className="flex items-center gap-2 text-white">
              <ShieldCheck className="h-4 w-4 text-emerald-400" />
              What this app is built for
            </div>
            <p className="mt-3">
              Voice order capture, stock mutation, merchant-friendly inventory naming, and a frontend that can expand into checkout, receipts, and analytics.
            </p>
          </div>
        </section>

        <section className="p-8 lg:p-10 bg-white">
          <div className="max-w-xl">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm uppercase tracking-[0.3em] text-slate-500">{mode === "login" ? "Sign in" : "Get started"}</p>
                <h2 className="mt-2 text-3xl font-semibold text-slate-900">{mode === "login" ? "Enter dashboard" : "Merchant registration"}</h2>
              </div>
              <Link className="rounded-full border border-slate-200 px-4 py-2 text-sm text-slate-600 hover:bg-slate-100" href={mode === "login" ? "/register" : "/login"}>
                {mode === "login" ? "Register" : "Login"}
              </Link>
            </div>

            <form onSubmit={handleSubmit} className="mt-8 space-y-4">
              {mode === "register" ? (
                <>
                  <AuthField name="name" label="Your name" placeholder="Aman" />
                  <AuthField name="storeName" label="Store name" placeholder="Aman General Store" />
                </>
              ) : null}
              <AuthField name="email" label="Email" type="email" placeholder="owner@store.com" />
              <AuthField name="password" label="Password" type="password" placeholder="••••••••" />
              <button
                type="submit"
                disabled={loading}
                className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-sky-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-sky-600 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <ArrowRight className="h-4 w-4" />}
                {loading ? "Working..." : mode === "login" ? "Sign in" : "Create account"}
              </button>
            </form>

            {error ? <p className="mt-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p> : null}
          </div>
        </section>
      </div>
    </main>
  );
}

function AuthField({ label, name, type = "text", placeholder }: { label: string; name: string; type?: string; placeholder: string }) {
  return (
    <label className="block space-y-2">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <input
        name={name}
        type={type}
        placeholder={placeholder}
        className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-sky-400 focus:ring-2 focus:ring-sky-100"
      />
    </label>
  );
}
