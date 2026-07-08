//frontend/app/page.tsx
"use client";

import { useState, useEffect } from "react";
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
  city: string;
  minSalary: number;
  maxSalary: number;
  keywords: string;
}

export default function Home() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<Filter>({
    city: "Munich",
    minSalary: 150,
    maxSalary: 550,
    keywords: "",
  });
  const [telegramId, setTelegramId] = useState("");
  const [showTelegramSetup, setShowTelegramSetup] = useState(false);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `/api/jobs?city=${filters.city}&min_salary=${filters.minSalary}&max_salary=${filters.maxSalary}`
      );

      const data = await response.json();

      // normalization layer: API contract safety
      const normalizedJobs = Array.isArray(data)
        ? data.map((job, index) => ({
            ...job,
            date:
              job.date ?? job.created_at ?? job.created ?? job.posted_at,
            salary:
              job.salary_min && job.salary_max
                ? `€${job.salary_min} - €${job.salary_max}`
                : "Not specified",
            id: job.id ?? `${job.source ?? "job"}-${index}`,
          }))
        : [];

      setJobs(normalizedJobs);
    } catch (error) {
      console.error("Error fetching jobs:", error);
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

    await fetchJobs();
  };

  const setupTelegram = () => {
    const botUsername = "YourJobRadarBot";
    const telegramUrl = `https://t.me/${botUsername}?start=${telegramId}`;
    window.open(telegramUrl, "_blank");
    setShowTelegramSetup(false);
  };

  useEffect(() => {
    fetchJobs();

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
            Find Teilzeit jobs in Munich & Augsburg (150-550€/month)
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
                onChange={(e) => setTelegramId(e.target.value)}
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
              <JobCard
                key={job.id ?? `${job.source ?? "job"}-${index}`}
                job={job}
              />
            ))}
        </div>
      </main>
    </div>
  );
}