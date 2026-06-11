import Link from "next/link";
import { ArrowRight, AudioLines, BadgeCheck, Box, Mic, ShieldCheck, Sparkles, Workflow } from "lucide-react";

const highlights = [
  {
    icon: Mic,
    title: "Voice-native commands",
    description: "Say things like 'add 2.5 kg rice' or 'remove three packets of milk' and the backend parses the intent.",
  },
  {
    icon: Sparkles,
    title: "Free-form item understanding",
    description: "Supports grams, kilograms, packets, bottles, boxes, and merchant phrasing with an optional LLM layer.",
  },
  {
    icon: Workflow,
    title: "Inventory workflow",
    description: "Track stock, reorder thresholds, and voice logs from one dashboard with future POS expansion in mind.",
  },
];

const stats = [
  { label: "Voice accuracy", value: "LLM-assisted" },
  { label: "Database", value: "MongoDB" },
  { label: "Frontend", value: "Next.js" },
  { label: "Backend", value: "Flask API" },
];

export function MarketingShell() {
  return (
    <main className="mx-auto flex min-h-screen max-w-7xl flex-col px-6 pb-16 pt-6 lg:px-8">
      <header className="flex items-center justify-between rounded-full border border-slate-200 bg-white px-5 py-3 shadow-sm">
        <div>
          <p className="text-xs uppercase tracking-[0.4em] text-slate-500">Merchant Voice POS</p>
          <p className="font-[family-name:var(--font-display)] text-lg font-bold text-slate-900">Voice-first retail ops</p>
        </div>

        <div className="hidden items-center gap-3 md:flex">
          <Link className="rounded-full border border-slate-200 px-4 py-2 text-sm text-slate-700 transition hover:bg-slate-100" href="/login">
            Login
          </Link>
          <Link className="inline-flex items-center gap-2 rounded-full bg-sky-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-600" href="/dashboard">
            Open dashboard <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </header>

      <section className="grid flex-1 items-center gap-12 py-12 lg:grid-cols-[1.15fr_0.85fr] lg:py-20">
        <div className="space-y-8">
          <div className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-100 px-4 py-2 text-sm text-slate-700">
            <AudioLines className="h-4 w-4" />
            Merchant workflow tuned for speech, units, and messy real-world item names
          </div>

          <div className="space-y-5">
            <h1 className="max-w-3xl font-[family-name:var(--font-display)] text-5xl font-bold leading-[0.95] tracking-tight text-slate-900 sm:text-6xl lg:text-7xl">
              A modern POS that understands how merchants actually speak.
            </h1>
            <p className="max-w-2xl text-lg leading-8 text-slate-700 sm:text-xl">
              Built for kiosks, kiranas, and fast-moving retail teams. Capture voice commands, normalize quantities in kg, grams, liters, packets, and more, then sync to a production-ready backend.
            </p>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row">
            <Link className="inline-flex items-center justify-center gap-2 rounded-full bg-white px-6 py-3 text-sm font-semibold text-slate-900 transition hover:-translate-y-0.5 hover:bg-slate-50" href="/register">
              Start free <ArrowRight className="h-4 w-4" />
            </Link>
            <Link className="inline-flex items-center justify-center gap-2 rounded-full border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50" href="/login">
              View login flow <ShieldCheck className="h-4 w-4" />
            </Link>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {stats.map((stat) => (
              <div key={stat.label} className="rounded-3xl border border-slate-200 bg-white px-4 py-4">
                <p className="text-xs uppercase tracking-[0.25em] text-slate-500">{stat.label}</p>
                <p className="mt-2 text-lg font-semibold text-slate-900">{stat.value}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="relative">
          <div className="absolute -inset-8 rounded-[2rem] bg-sky-100/60 blur-3xl" />
          <div className="relative overflow-hidden rounded-[2rem] border border-slate-200 bg-white p-6 shadow-md flex flex-col lg:flex-row gap-6">
            <div className="lg:w-1/2">
              <img src="/hero.svg" alt="Hero" className="w-full h-56 object-cover rounded-lg" />
            </div>

            <div className="lg:w-1/2">
              <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                <div>
                  <p className="text-sm text-slate-500">Live inventory command</p>
                  <p className="text-2xl font-semibold text-slate-900">Ready for voice</p>
                </div>
                <div className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700">Connected</div>
              </div>

              <div className="mt-6 space-y-4">
                <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                  <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Spoken input</p>
                  <p className="mt-2 text-xl text-slate-900">Add 2.5 kg rice and remove 3 packets of milk</p>
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="rounded-3xl border border-slate-200 bg-sky-50 p-4">
                    <Box className="h-6 w-6 text-sky-600" />
                    <p className="mt-4 text-sm text-slate-500">Detected item</p>
                    <p className="mt-1 text-lg font-semibold text-slate-900">Rice</p>
                  </div>

                  <div className="rounded-3xl border border-slate-200 bg-amber-50 p-4">
                    <BadgeCheck className="h-6 w-6 text-amber-600" />
                    <p className="mt-4 text-sm text-slate-500">Confidence</p>
                    <p className="mt-1 text-lg font-semibold text-slate-900">High</p>
                  </div>
                </div>

                <div className="rounded-3xl border border-emerald-100 bg-emerald-50 p-4 text-sm leading-7 text-emerald-800">
                  Voice output, inventory mutation, and audit trail all stay aligned in the backend.
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-5 md:grid-cols-3">
        {highlights.map((item) => {
          const Icon = item.icon;
          return (
            <article key={item.title} className="rounded-[1.75rem] border border-slate-200 bg-white p-6 shadow-sm">
              <Icon className="h-6 w-6 text-sky-600" />
              <h2 className="mt-5 text-xl font-semibold text-slate-900">{item.title}</h2>
              <p className="mt-3 leading-7 text-slate-700">{item.description}</p>
            </article>
          );
        })}
      </section>
    </main>
  );
}

export default MarketingShell;
