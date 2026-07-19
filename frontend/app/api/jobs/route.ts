//frontend/app/api/jobs/route.ts

import { NextResponse } from "next/server";

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);

  const backend =
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000";

  const backendUrl =
    `${backend}/api/jobs?city=${encodeURIComponent(searchParams.get("city") ?? "")}` +
    `&keywords=${encodeURIComponent(searchParams.get("keywords") ?? "")}` +
    `&employment_type=${encodeURIComponent(searchParams.get("employment_type") ?? "")}` +
    `&min_salary=${encodeURIComponent(searchParams.get("min_salary") ?? "")}` +
    `&max_salary=${encodeURIComponent(searchParams.get("max_salary") ?? "")}`;

  try {
    const res = await fetch(backendUrl);

    if (!res.ok) {
      return NextResponse.json([]);
    }

    return NextResponse.json(await res.json());

  } catch {
    return NextResponse.json([]);
  }
}