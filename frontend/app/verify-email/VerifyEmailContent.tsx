//frontend/app/verify-email.VerifyEmailContent.tsx

"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";


type VerificationState =
  | "loading"
  | "success"
  | "expired"
  | "invalid"
  | "error";


interface VerificationResponse {
  success?: boolean;
  message?: string;
  verified_email?: boolean;
  consent_given?: boolean;
  alerts_enabled?: boolean;
  detail?: string;
  error?: string;
}


export default function VerifyEmailContent() {
  const searchParams = useSearchParams();

  const token = searchParams.get("token");

  const [state, setState] =
    useState<VerificationState>("loading");

  const [message, setMessage] =
    useState("E-Mail-Adresse wird bestätigt...");


  useEffect(() => {
    let cancelled = false;


    async function verify() {
      if (!token) {
        if (!cancelled) {
          setState("invalid");
          setMessage(
            "Der Bestätigungs-Link ist ungültig."
          );
        }

        return;
      }


      try {
        const response = await fetch(
          `/api/users/verify-email?token=${encodeURIComponent(
            token
          )}`,
          {
            method: "GET",
            cache: "no-store",
          }
        );


        const data: VerificationResponse =
          await response.json();


        if (cancelled) {
          return;
        }


        if (response.ok && data.success) {
          setState("success");

          if (data.alerts_enabled) {
            setMessage(
              "Deine E-Mail-Adresse wurde bestätigt. Die E-Mail-Benachrichtigungen sind jetzt aktiv."
            );
          } else {
            setMessage(
              "Deine E-Mail-Adresse wurde erfolgreich bestätigt."
            );
          }

          return;
        }


        if (response.status === 410) {
          setState("expired");

          setMessage(
            "Dieser Bestätigungs-Link ist abgelaufen."
          );

          return;
        }


        if (response.status === 404) {
          setState("invalid");

          setMessage(
            "Dieser Bestätigungs-Link ist ungültig oder wurde bereits verwendet."
          );

          return;
        }


        setState("error");

        setMessage(
          data.detail ||
            data.error ||
            "Die E-Mail-Adresse konnte nicht bestätigt werden."
        );

      } catch (error) {
        console.error(
          "Email verification error:",
          error
        );

        if (!cancelled) {
          setState("error");

          setMessage(
            "Die E-Mail-Bestätigung konnte nicht durchgeführt werden."
          );
        }
      }
    }


    verify();


    return () => {
      cancelled = true;
    };
  }, [token]);


  const isSuccess = state === "success";


  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-50 px-4">

      <div className="w-full max-w-md bg-white rounded-xl shadow p-8 text-center">

        {state === "loading" && (
          <>
            <div className="mx-auto mb-5 h-10 w-10 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600" />

            <h1 className="text-xl font-semibold text-gray-900">
              E-Mail-Adresse wird bestätigt
            </h1>

            <p className="mt-2 text-sm text-gray-600">
              Bitte warten...
            </p>
          </>
        )}


        {isSuccess && (
          <>
            <div className="mx-auto mb-5 flex h-12 w-12 items-center justify-center rounded-full bg-green-100 text-green-700">
              ✓
            </div>

            <h1 className="text-xl font-semibold text-gray-900">
              E-Mail bestätigt
            </h1>

            <p className="mt-3 text-sm text-gray-600">
              {message}
            </p>

            <a
              href="/"
              className="mt-6 inline-flex rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
            >
              Zurück zu JobRadar
            </a>
          </>
        )}


        {state === "expired" && (
          <>
            <div className="mx-auto mb-5 flex h-12 w-12 items-center justify-center rounded-full bg-amber-100 text-amber-700">
              !
            </div>

            <h1 className="text-xl font-semibold text-gray-900">
              Link abgelaufen
            </h1>

            <p className="mt-3 text-sm text-gray-600">
              {message}
            </p>

            <a
              href="/"
              className="mt-6 inline-flex rounded-lg border border-gray-300 px-5 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-50"
            >
              Zurück zu JobRadar
            </a>
          </>
        )}


        {state === "invalid" && (
          <>
            <div className="mx-auto mb-5 flex h-12 w-12 items-center justify-center rounded-full bg-red-100 text-red-700">
              ×
            </div>

            <h1 className="text-xl font-semibold text-gray-900">
              Ungültiger Bestätigungs-Link
            </h1>

            <p className="mt-3 text-sm text-gray-600">
              {message}
            </p>

            <a
              href="/"
              className="mt-6 inline-flex rounded-lg border border-gray-300 px-5 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-50"
            >
              Zurück zu JobRadar
            </a>
          </>
        )}


        {state === "error" && (
          <>
            <div className="mx-auto mb-5 flex h-12 w-12 items-center justify-center rounded-full bg-red-100 text-red-700">
              ×
            </div>

            <h1 className="text-xl font-semibold text-gray-900">
              Bestätigung fehlgeschlagen
            </h1>

            <p className="mt-3 text-sm text-gray-600">
              {message}
            </p>

            <a
              href="/"
              className="mt-6 inline-flex rounded-lg border border-gray-300 px-5 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-50"
            >
              Zurück zu JobRadar
            </a>
          </>
        )}

      </div>
    </main>
  );
}