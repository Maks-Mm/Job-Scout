//frontend/app/api/jobs/route.ts

import { NextResponse } from "next/server";

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);

  const backend = process.env.NEXT_PUBLIC_API_URL!;

  const backendUrl =
    `${backend}/api/jobs?city=${encodeURIComponent(searchParams.get("city") ?? "")}` +
    `&keywords=${encodeURIComponent(searchParams.get("keywords") ?? "")}` +
    `&employment_type=${encodeURIComponent(searchParams.get("employment_type") ?? "")}` +
    `&min_salary=${encodeURIComponent(searchParams.get("min_salary") ?? "")}` +
    `&max_salary=${encodeURIComponent(searchParams.get("max_salary") ?? "")}`;

  console.log("Backend URL:", backendUrl);

  try {
    const res = await fetch(backendUrl);

    console.log("Backend status:", res.status);

    const text = await res.text();

    console.log("Backend response:");
    console.log(text);

    return new NextResponse(text, {
      status: res.status,
      headers: {
        "Content-Type": "application/json", // Oder res.headers.get("content-type") || "application/json"
      },
    });

  } catch (e) {
    console.error("Fetch error:", e);

    return NextResponse.json(
      {
        error: String(e),
      },
      {
        status: 503,
      }
    );
  }
}