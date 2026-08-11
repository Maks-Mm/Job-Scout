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

export default function Home() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<Filter>({
    country: "",
    city: "",
    language: "de",
    keywords: "",
    jobCategory: "all",
    employmentType: "all",
    minSalary: 0,
    maxSalary: 0,
  });
  const [telegramId, setTelegramId] = useState("");
  const [showTelegramSetup, setShowTelegramSetup] = useState(false);
  const [email, setEmail] = useState("");
  const [emailConsent, setEmailConsent] = useState(false);
  const [emailStatus, setEmailStatus] = useState<string | null>(null);
  const [emailSaving, setEmailSaving] = useState(false);

  const fetchJobs = async (overrideFilters?: Filter) => {
    const activeFilters = overrideFilters ?? filters;

    setLoading(true);

    try {
      const response = await fetch(
        `/api/jobs?country=${encodeURIComponent(activeFilters.country)}` +
        `&city=${encodeURIComponent(activeFilters.city)}` +
        `&language=${encodeURIComponent(activeFilters.language)}` +
        `&keywords=${encodeURIComponent(activeFilters.keywords)}` +
        `&job_category=${encodeURIComponent(activeFilters.jobCategory)}` +
        `&employment_type=${encodeURIComponent(activeFilters.employmentType)}` +
        `&min_salary=${activeFilters.minSalary}` +
        `&max_salary=${activeFilters.maxSalary}`
      );

      const contentType = response.headers.get("content-type");

      if (!response.ok) {
        const errorText = await response.text();
        console.error("API Error:", response.status, errorText);

        setJobs([]);
        return;
      }

      if (!contentType?.includes("application/json")) {
        const text = await response.text();
        console.error("Expected JSON but received:", text);

        setJobs([]);
        return;
      }

      const data = await response.json();

      const normalizedJobs = Array.isArray(data)
        ? data.map((job: any, index: number) => ({
          ...job,
          id: job.id ?? `${job.source ?? "job"}-${index}`,
          date:
            job.date ??
            job.created_at ??
            job.created ??
            job.posted_at ??
            "",

          salary:
            job.salary ??
            (job.salary_min && job.salary_max
              ? `€${job.salary_min} - €${job.salary_max}`
              : "Not specified"),
        }))
        : [];

      setJobs(normalizedJobs);
    } catch (err) {
      console.error(err);
      setJobs([]);
    } finally {
      setLoading(false);
    }
  };

  const saveFilter = async (newFilter: Filter) => {
    setFilters(newFilter);

    if (telegramId) {
      try {
        await fetch("http://localhost:8000/api/filters", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            telegram_id: telegramId,
            ...newFilter,
          }),
        });
      } catch (error) {
        console.error("Error saving filter:", error);
      }
    }

    await fetchJobs(newFilter);
  };

  const setupTelegram = () => {
    const botUsername = "YourJobRadarBot";
    const telegramUrl = `https://t.me/${botUsername}?start=${telegramId}`;
    window.open(telegramUrl, "_blank");
    setShowTelegramSetup(false);
  };

  const saveEmailAlerts = async () => {
    if (!emailConsent) {
      setEmailStatus("Bitte stimme der E-Mail-Benachrichtigung zu.");
      return;
    }

    if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      setEmailStatus("Bitte gib eine gültige E-Mail-Adresse ein.");
      return;
    }

    setEmailSaving(true);
    setEmailStatus(null);

    try {
      const response = await fetch("/api/users/alerts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          alerts_enabled: true,
          keywords: filters.keywords,
          city: filters.city,
          country: filters.country,
          interval: "6h",
          consent: true,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setEmailStatus(
          data?.detail || data?.error || "Beim Speichern der E-Mail-Benachrichtigungen ist ein Fehler aufgetreten."
        );
        return;
      }

      setEmailStatus(
        data.verification_sent
          ? "Eine Verifizierungs-E-Mail wurde an dich gesendet. Bitte bestätige deine E-Mail-Adresse."
          : "E-Mail-Benachrichtigungen wurden gespeichert."
      );
    } catch (error) {
      console.error("Error saving email alerts:", error);
      setEmailStatus("Beim Speichern der E-Mail-Benachrichtigungen ist ein Fehler aufgetreten.");
    } finally {
      setEmailSaving(false);
    }
  };

  useEffect(() => {
   // fetchJobs();
    const savedId = localStorage.getItem("telegramId");
    if (savedId) setTelegramId(savedId);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">JobRadar</h1>
          <p className="text-gray-600 mt-2">
            Find Teilzeit/Vollzeit Jobs in ganz Deutschland (150-3500/month)
          </p>
        </div>

        {!telegramId && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-blue-900">
              Get Notifications on Telegram
            </h3>
            <p className="text-blue-700 text-sm mt-1">
              Receive new jobs directly to your phone
            </p>
            <button
              onClick={() => setShowTelegramSetup(true)}
              className="mt-3 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm"
            >
              Setup Telegram Notifications
            </button>
          </div>
        )}

        {showTelegramSetup && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full">
              <h2 className="text-xl font-bold mb-4">Setup Telegram</h2>

              <input
                type="text"
                placeholder="Enter your Telegram ID"
                value={telegramId}
                onChange={(e: ChangeEvent<HTMLInputElement>) => setTelegramId(e.target.value)}
                className="w-full border rounded-lg p-2 mb-4"
              />

              <div className="flex gap-2">
                <button
                  onClick={setupTelegram}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg flex-1"
                >
                  Connect Telegram
                </button>

                <button
                  onClick={() => setShowTelegramSetup(false)}
                  className="border px-4 py-2 rounded-lg"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg shadow mb-8 p-6">
          <h2 className="text-lg font-semibold mb-4">E-Mail-Benachrichtigungen</h2>
          <p className="text-sm text-gray-600 mb-4">
            Erhalte neue Jobangebote per E-Mail. Gib deine E-Mail-Adresse ein und bestätige sie anschließend über den Link, den wir dir zusenden.
          </p>

          <div className="grid gap-4 sm:grid-cols-2">
            <input
              type="email"
              placeholder="Deine E-Mail-Adresse"
              value={email}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
              className="w-full border rounded-lg p-2"
            />

            <label className="flex items-start gap-3 text-sm text-gray-700">
              <input
                type="checkbox"
                checked={emailConsent}
                onChange={(e: ChangeEvent<HTMLInputElement>) => setEmailConsent(e.target.checked)}
                className="mt-1 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span>
                Ich möchte E-Mail-Benachrichtigungen erhalten und stimme der Verarbeitung meiner E-Mail-Adresse zu.
              </span>
            </label>
          </div>

          {emailStatus && (
            <p className="mt-3 text-sm text-gray-800">{emailStatus}</p>
          )}

          <button
            onClick={saveEmailAlerts}
            disabled={emailSaving || !emailConsent || !email}
            className="mt-4 inline-flex items-center justify-center rounded-lg bg-blue-600 px-5 py-2 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {emailSaving ? "Speichern…" : "E-Mail-Benachrichtigung aktivieren"}
          </button>
        </div>

        <div className="bg-white rounded-lg shadow mb-8 p-6">
          <h2 className="text-lg font-semibold mb-4">Search Filters</h2>
          <FilterForm onSave={saveFilter} initialFilters={filters} />
        </div>

        <div className="mb-6">
          <SearchBar onSearch={(term) => console.log("Search:", term)} />
        </div>

        <div>
          <h2 className="text-xl font-semibold mb-4">
            Matching Jobs ({jobs.length})
          </h2>

          {loading && <Loading />}

          {!loading && jobs.length === 0 && <EmptyState />}

          {!loading &&
            jobs.map((job, index) => (
              <div
                key={job.id ?? `${job.source ?? "job"}-${index}`}
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