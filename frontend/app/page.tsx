//frontend/app/page.tsx

"use client";

import { useState, useEffect, type ChangeEvent } from "react";

import Navbar from "./components/Navbar";
import FilterForm from "./components/FilterForm";
import JobCard from "./components/JobCard";
import SearchBar from "./components/SearchBar";
import Loading from "./components/Loading";
import EmptyState from "./components/EmptyState";


interface Job {
  id: number | string;
  title: string;
  company: string;
  city: string;
  salary: string;
  salary_min?: number;
  salary_max?: number;
  date?: string;
  url: string;
  source: string;
  employment_type?: string;
}


interface Filter {
  country: string;
  city: string;
  language: string;
  keywords: string;
  jobCategory: string;
  employmentType: string;
  source?: string;
  minSalary: number;
  maxSalary: number;
}


interface AlertResponse {
  success?: boolean;
  verification_sent?: boolean;
  verified_email?: boolean;
  consent_given?: boolean;
  alerts_enabled?: boolean;
  message?: string;
  detail?: string;
  error?: string;
}


const EMPLOYMENT_LABELS: Record<string, string> = {
  all: "Alle",
  parttime: "Teilzeit",
  fulltime: "Vollzeit",
  mini: "Minijob",
};


export default function Home() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);

  const [filters, setFilters] = useState<Filter>({
    country: "Germany",
    city: "",
    language: "de",
    keywords: "",
    jobCategory: "all",
    employmentType: "all",
    minSalary: 0,
    maxSalary: 0,
  });


  // ─────────────────────────────────────────────────────────────────────
  // Email alerts
  // ─────────────────────────────────────────────────────────────────────

  const [email, setEmail] = useState("");
  const [emailConsent, setEmailConsent] = useState(false);

  const [emailStatus, setEmailStatus] = useState<string | null>(null);

  const [emailSaving, setEmailSaving] = useState(false);

  const [emailState, setEmailState] = useState<
    "idle" | "pending_verification" | "active" | "error"
  >("idle");


  // ─────────────────────────────────────────────────────────────────────
  // Telegram
  // ─────────────────────────────────────────────────────────────────────

  const [telegramId, setTelegramId] = useState("");
  const [showTelegramSetup, setShowTelegramSetup] = useState(false);


  // ─────────────────────────────────────────────────────────────────────
  // Jobs
  // ─────────────────────────────────────────────────────────────────────

  const fetchJobs = async (overrideFilters?: Filter) => {
    const f = overrideFilters ?? filters;

    setLoading(true);

    try {
      const params = new URLSearchParams({
        country: f.country,
        city: f.city,
        language: f.language,
        keywords: f.keywords,
        job_category: f.jobCategory,
        employment_type: f.employmentType,
        min_salary: String(f.minSalary),
        max_salary: String(f.maxSalary),
      });

      const response = await fetch(
        `/api/jobs?${params.toString()}`,
        {
          cache: "no-store",
        }
      );

      const contentType =
        response.headers.get("content-type") || "";

      if (!response.ok) {
        console.error(
          "API Error:",
          response.status,
          await response.text()
        );

        setJobs([]);
        return;
      }

      if (!contentType.includes("application/json")) {
        console.error(
          "Expected JSON but received non-JSON response"
        );

        setJobs([]);
        return;
      }

      const data = await response.json();

      const normalizedJobs: Job[] = Array.isArray(data)
        ? data.map((job: any, index: number) => ({
            ...job,

            id:
              job.id ??
              `${job.source ?? "job"}-${index}`,

            date:
              job.date ??
              job.created_at ??
              job.created ??
              job.posted_at ??
              "",

            salary:
              job.salary ??
              (
                job.salary_min != null &&
                job.salary_max != null
                  ? `€${job.salary_min} – €${job.salary_max}`
                  : "Nicht angegeben"
              ),
          }))
        : [];

      setJobs(normalizedJobs);
    } catch (error) {
      console.error(error);
      setJobs([]);
    } finally {
      setLoading(false);
    }
  };


  const saveFilter = async (newFilter: Filter) => {
    setFilters(newFilter);
    await fetchJobs(newFilter);
  };


  // ─────────────────────────────────────────────────────────────────────
  // Save email subscription
  // ─────────────────────────────────────────────────────────────────────

  const saveEmailAlerts = async () => {
    if (emailSaving) {
      return;
    }

    if (!emailConsent) {
      setEmailStatus(
        "Bitte stimme der E-Mail-Benachrichtigung zu."
      );
      setEmailState("error");
      return;
    }

    if (
      !email ||
      !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)
    ) {
      setEmailStatus(
        "Bitte gib eine gültige E-Mail-Adresse ein."
      );
      setEmailState("error");
      return;
    }

    setEmailSaving(true);
    setEmailStatus(null);
    setEmailState("idle");

    try {
      const response = await fetch(
        "/api/users/alerts",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email,

            // User explicitly requests alerts.
            alerts_enabled: true,

            // Explicit consent.
            consent: true,

            interval: "6h",

            keywords: filters.keywords,
            city: filters.city,
            country: filters.country,
            language: filters.language,

            employment_type:
              filters.employmentType,

            job_category:
              filters.jobCategory,

            min_salary:
              filters.minSalary > 0
                ? filters.minSalary
                : null,

            max_salary:
              filters.maxSalary > 0
                ? filters.maxSalary
                : null,
          }),
        }
      );

      const data: AlertResponse =
        await response.json();

      if (!response.ok) {
        setEmailState("error");

        setEmailStatus(
          data.detail ||
            data.error ||
            "Beim Speichern ist ein Fehler aufgetreten."
        );

        return;
      }

      // Already verified.
      if (
        data.verified_email &&
        data.alerts_enabled
      ) {
        setEmailState("active");

        setEmailStatus(
          "E-Mail-Benachrichtigungen sind aktiv."
        );

        return;
      }

      // Verification email was sent.
      if (data.verification_sent) {
        setEmailState("pending_verification");

        setEmailStatus(
          "Bestätigungs-E-Mail gesendet. Bitte klicke auf den Link in der E-Mail. Erst danach werden die Benachrichtigungen aktiviert."
        );

        return;
      }

      // Consent exists but verification is pending.
      if (
        data.consent_given &&
        !data.verified_email
      ) {
        setEmailState("pending_verification");

        setEmailStatus(
          "Deine Einstellungen wurden gespeichert. Bitte bestätige deine E-Mail-Adresse über den Bestätigungs-Link."
        );

        return;
      }

      setEmailStatus(
        data.message ||
          "Einstellungen wurden gespeichert."
      );

    } catch (error) {
      console.error(
        "Error saving email alerts:",
        error
      );

      setEmailState("error");

      setEmailStatus(
        "Beim Speichern ist ein Fehler aufgetreten."
      );
    } finally {
      setEmailSaving(false);
    }
  };


  // ─────────────────────────────────────────────────────────────────────
  // Telegram
  // ─────────────────────────────────────────────────────────────────────

  const setupTelegram = () => {
    const botUsername = "YourJobRadarBot";

    if (!telegramId.trim()) {
      return;
    }

    localStorage.setItem(
      "telegramId",
      telegramId.trim()
    );

    window.open(
      `https://t.me/${botUsername}?start=${encodeURIComponent(
        telegramId.trim()
      )}`,
      "_blank",
      "noopener,noreferrer"
    );

    setShowTelegramSetup(false);
  };


  useEffect(() => {
    const savedId =
      localStorage.getItem("telegramId");

    if (savedId) {
      setTelegramId(savedId);
    }
  }, []);


  // ─────────────────────────────────────────────────────────────────────
  // Active filter summary
  // ─────────────────────────────────────────────────────────────────────

  const activeFilterTags: string[] = [];

  if (filters.city) {
    activeFilterTags.push(
      `${filters.city}, ${filters.country}`
    );
  }

  if (
    filters.employmentType &&
    filters.employmentType !== "all"
  ) {
    activeFilterTags.push(
      EMPLOYMENT_LABELS[
        filters.employmentType
      ] ??
        filters.employmentType
    );
  }

  if (
    filters.minSalary > 0 ||
    filters.maxSalary > 0
  ) {
    activeFilterTags.push(
      `€${filters.minSalary || 0} – €${
        filters.maxSalary || "∞"
      } / Monat`
    );
  }

  if (filters.keywords) {
    activeFilterTags.push(
      filters.keywords
    );
  }


  return (
    <div className="min-h-screen bg-gray-50">

      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            JobRadar
          </h1>

          <p className="text-gray-600 mt-2">
            Teilzeit &amp; Vollzeit Jobs in Deutschland —
            gefiltert nach deinen Kriterien
          </p>
        </div>


        {/* ─────────────────────────────────────────────────────────────
            Telegram
        ───────────────────────────────────────────────────────────── */}

        {!telegramId && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">

            <h3 className="font-semibold text-blue-900">
              Telegram-Benachrichtigungen
            </h3>

            <p className="text-blue-700 text-sm mt-1">
              Erhalte neue Jobs direkt auf dein Handy.
            </p>

            <button
              onClick={() =>
                setShowTelegramSetup(true)
              }
              className="mt-3 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm"
            >
              Telegram einrichten
            </button>

          </div>
        )}


        {showTelegramSetup && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">

            <div className="bg-white rounded-lg p-6 max-w-md w-full">

              <h2 className="text-xl font-bold mb-4">
                Telegram einrichten
              </h2>

              <input
                type="text"
                placeholder="Deine Telegram-ID eingeben"
                value={telegramId}
                onChange={(
                  e: ChangeEvent<HTMLInputElement>
                ) =>
                  setTelegramId(e.target.value)
                }
                className="w-full border rounded-lg p-2 mb-4"
              />

              <div className="flex gap-2">

                <button
                  onClick={setupTelegram}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg flex-1"
                >
                  Verbinden
                </button>

                <button
                  onClick={() =>
                    setShowTelegramSetup(false)
                  }
                  className="border px-4 py-2 rounded-lg"
                >
                  Abbrechen
                </button>

              </div>
            </div>
          </div>
        )}


        {/* ─────────────────────────────────────────────────────────────
            Email alerts
        ───────────────────────────────────────────────────────────── */}

        <div className="bg-white rounded-lg shadow mb-8 p-6">

          <h2 className="text-lg font-semibold mb-1">
            E-Mail-Benachrichtigungen
          </h2>

          <p className="text-sm text-gray-500 mb-4">
            Wir schicken dir nur Jobs, die deinen
            Filterkriterien entsprechen.
          </p>


          {activeFilterTags.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-4">

              {activeFilterTags.map((tag) => (
                <span
                  key={tag}
                  className="bg-blue-50 text-blue-700 text-xs font-medium px-3 py-1 rounded-full border border-blue-100"
                >
                  {tag}
                </span>
              ))}

            </div>
          )}


          {activeFilterTags.length === 0 && (
            <p className="text-xs text-amber-600 bg-amber-50 border border-amber-100 rounded-lg px-3 py-2 mb-4">
              Noch keine Filter gesetzt. Du kannst
              trotzdem abonnieren; die aktuellen
              Filterwerte werden gespeichert.
            </p>
          )}


          <div className="grid gap-4 sm:grid-cols-2">

            <input
              type="email"
              placeholder="Deine E-Mail-Adresse"
              value={email}
              onChange={(
                e: ChangeEvent<HTMLInputElement>
              ) =>
                setEmail(e.target.value)
              }
              className="w-full border rounded-lg p-2"
            />


            <label className="flex items-start gap-3 text-sm text-gray-700">

              <input
                type="checkbox"
                checked={emailConsent}
                onChange={(
                  e: ChangeEvent<HTMLInputElement>
                ) =>
                  setEmailConsent(
                    e.target.checked
                  )
                }
                className="mt-1 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />

              <span>
                Ich möchte E-Mail-Benachrichtigungen
                erhalten und stimme der Verarbeitung
                meiner E-Mail-Adresse zu.
              </span>

            </label>

          </div>


          {emailStatus && (
            <div
              className={`mt-4 rounded-lg border px-3 py-2 text-sm ${
                emailState === "active"
                  ? "bg-green-50 border-green-200 text-green-800"
                  : emailState ===
                    "pending_verification"
                  ? "bg-amber-50 border-amber-200 text-amber-800"
                  : emailState === "error"
                  ? "bg-red-50 border-red-200 text-red-800"
                  : "bg-gray-50 border-gray-200 text-gray-800"
              }`}
            >
              {emailStatus}
            </div>
          )}


          <button
            onClick={saveEmailAlerts}
            disabled={
              emailSaving ||
              !emailConsent ||
              !email
            }
            className="mt-4 inline-flex items-center justify-center rounded-lg bg-blue-600 px-5 py-2 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {emailSaving
              ? "Speichern…"
              : "E-Mail-Benachrichtigungen aktivieren"}
          </button>

        </div>


        {/* ─────────────────────────────────────────────────────────────
            Search filters
        ───────────────────────────────────────────────────────────── */}

        <div className="bg-white rounded-lg shadow mb-8 p-6">

          <h2 className="text-lg font-semibold mb-4">
            Suchfilter
          </h2>

          <FilterForm
            onSave={saveFilter}
            initialFilters={filters}
          />

        </div>


        <div className="mb-6">
          <SearchBar
            onSearch={(term) =>
              console.log("Search:", term)
            }
          />
        </div>


        {/* ─────────────────────────────────────────────────────────────
            Results
        ───────────────────────────────────────────────────────────── */}

        <div>

          <h2 className="text-xl font-semibold mb-4">
            Passende Jobs ({jobs.length})
          </h2>

          {loading && <Loading />}

          {!loading &&
            jobs.length === 0 && (
              <EmptyState />
            )}

          {!loading &&
            jobs.map((job, index) => (
              <div
                key={
                  job.id ??
                  `${job.source ?? "job"}-${index}`
                }
                className="contents"
              >
                <JobCard job={job} />
              </div>
            ))}

        </div>

      </main>
    </div>
  );
}