//frontend/app/api/jobs/route.ts

import { NextResponse } from "next/server";

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);

  const city = searchParams.get("city");
  const min_salary = searchParams.get("min_salary");
  const max_salary = searchParams.get("max_salary");

  const backendUrl = `http://localhost:8000/api/jobs?city=${city}&min_salary=${min_salary}&max_salary=${max_salary}`;

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 2000); // hard cutoff

    const res = await fetch(backendUrl, {
      signal: controller.signal,
    });

    clearTimeout(timeout);

    if (!res.ok) {
      return NextResponse.json([]); // degrade gracefully
    }

    const data = await res.json();

    return NextResponse.json(Array.isArray(data) ? data : []);
  } catch (err) {
    // backend sleeping/offline
    return NextResponse.json([]);
  }
}