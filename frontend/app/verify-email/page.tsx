"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token") || "";
  const [status, setStatus] = useState("Verifiziere E-Mail...");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      setStatus("Ungültiger Verifizierungslink.");
      setLoading(false);
      return;
    }

    const verify = async () => {
      try {
        const response = await fetch(`/api/users/verify-email?token=${encodeURIComponent(token)}`);
        const data = await response.json();

        if (!response.ok) {
          setStatus(data?.detail || data?.error || "Die Verifizierung ist fehlgeschlagen.");
        } else {
          setStatus("Deine E-Mail-Adresse wurde erfolgreich bestätigt.");
        }
      } catch (error) {
        console.error(error);
        setStatus("Die Verifizierung ist fehlgeschlagen. Bitte versuche es später erneut.");
      } finally {
        setLoading(false);
      }
    };

    verify();
  }, [token]);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-12">
      <div className="max-w-lg w-full bg-white rounded-3xl border border-slate-200 p-8 shadow-lg">
        <h1 className="text-2xl font-semibold text-slate-900">E-Mail-Verifizierung</h1>
        <p className="mt-4 text-sm text-slate-600">{status}</p>
        {loading && <p className="mt-4 text-sm text-slate-500">Bitte einen Moment warten...</p>}
      </div>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-12"><p className="text-sm text-slate-500">Lade Verifizierung...</p></div>}>
      <VerifyEmailContent />
    </Suspense>
  );
}
