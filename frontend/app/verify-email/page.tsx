"use client";

import {
  Suspense,
  useEffect,
  useRef,
  useState,
} from "react";
import { useSearchParams } from "next/navigation";

type VerificationState =
  | "loading"
  | "success"
  | "error";

function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token") || "";

  const [state, setState] =
    useState<VerificationState>("loading");

  const [status, setStatus] =
    useState("Verifiziere E-Mail...");

  // Prevent duplicate verification requests from this mounted page instance.
  const verificationStarted = useRef(false);

  useEffect(() => {
    if (verificationStarted.current) {
      return;
    }

    verificationStarted.current = true;

    if (!token) {
      setState("error");
      setStatus("Ungültiger Verifizierungslink.");
      return;
    }

    const verify = async () => {
      try {
        const response = await fetch(
          `/api/users/verify-email?token=${encodeURIComponent(token)}`,
          {
            method: "GET",
            cache: "no-store",
          }
        );

        const contentType =
          response.headers.get("content-type") || "";

        let data: any = {};

        if (contentType.includes("application/json")) {
          data = await response.json();
        } else {
          const text = await response.text();

          setState("error");
          setStatus(
            "Der Verifizierungsserver hat eine ungültige Antwort zurückgegeben."
          );

          console.error(
            "Verification returned non-JSON:",
            text
          );

          return;
        }

        if (!response.ok) {
          setState("error");

          setStatus(
            data?.detail ||
            data?.error ||
            data?.body ||
            "Die Verifizierung ist fehlgeschlagen."
          );

          return;
        }

        setState("success");

        setStatus(
          data?.message ||
          "Deine E-Mail-Adresse wurde erfolgreich bestätigt. " +
          "E-Mail-Benachrichtigungen sind jetzt aktiviert."
        );

      } catch (error) {
        console.error(
          "Email verification error:",
          error
        );

        setState("error");

        setStatus(
          "Die Verifizierung ist fehlgeschlagen. " +
          "Bitte versuche es später erneut."
        );
      }
    };

    verify();
  }, [token]);

  const title =
    state === "success"
      ? "E-Mail erfolgreich bestätigt"
      : state === "error"
        ? "E-Mail-Verifizierung fehlgeschlagen"
        : "E-Mail-Verifizierung";

  const stateClass =
    state === "success"
      ? "border-green-200 bg-green-50 text-green-800"
      : state === "error"
        ? "border-red-200 bg-red-50 text-red-800"
        : "border-slate-200 bg-white text-slate-700";

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-12">
      <div className="max-w-lg w-full rounded-3xl border border-slate-200 bg-white p-8 shadow-lg">
        <h1 className="text-2xl font-semibold text-slate-900">
          {title}
        </h1>

        <div
          className={`mt-5 rounded-xl border p-4 text-sm ${stateClass}`}
        >
          {status}
        </div>

        {state === "loading" && (
          <p className="mt-4 text-sm text-slate-500">
            Bitte einen Moment warten...
          </p>
        )}

        {state === "success" && (
          <p className="mt-4 text-sm text-slate-600">
            Zukünftige Job-Benachrichtigungen werden anhand deiner gespeicherten Filter gesendet.
          </p>
        )}

        {state === "error" && (
          <p className="mt-4 text-sm text-slate-500">
            Wenn der Link abgelaufen ist, speichere die E-Mail-Benachrichtigungen erneut, um einen neuen Bestätigungslink zu erhalten.
          </p>
        )}
      </div>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-12">
          <p className="text-sm text-slate-500">
            Lade Verifizierung...
          </p>
        </div>
      }
    >
      <VerifyEmailContent />
    </Suspense>
  );
}

