// frontend/app/api/jobs/route.ts

import { NextRequest, NextResponse } from "next/server";

async function fetchWithRetry(url: string, options: RequestInit = {}, retries = 2, delayMs = 3000) {
  let lastRes: Response | null = null;
  for (let i = 0; i <= retries; i++) {
    try {
      const res = await fetch(url, options);
      lastRes = res;
      // If success, return immediately
      if (res.ok) return res;
      // Only retry on 502 (gateway) which likely indicates cold-start proxy error
      if (res.status !== 502) return res;
    } catch (err) {
      lastRes = null;
    }

    if (i < retries) {
      await new Promise((r) => setTimeout(r, delayMs));
    }
  }

  if (lastRes) return lastRes;
  throw new Error("fetchWithRetry: no response returned");
}

export async function GET(req: NextRequest) {
  const { searchParams } = req.nextUrl;

  const backend = process.env.NEXT_PUBLIC_API_URL;
  console.log("Backend URL =", backend);

  if (!backend) {
    return NextResponse.json(
      { error: "API_URL is not configured" },
      { status: 500 }
    );
  }

  const url = new URL("/api/jobs", backend);

  searchParams.forEach((value, key) => {
    url.searchParams.set(key, value);
  });

  try {
    const res = await fetchWithRetry(url.toString(), { cache: "no-store" }, 2, 3000);

    const contentType = res.headers.get("content-type") || "";
    const body = await res.text();

    console.log("Backend:", url.toString());
    console.log("Status:", res.status);
    console.log("Content-Type:", contentType);

    if (!res.ok) {
      return NextResponse.json(
        {
          error: "Backend returned an error",
          status: res.status,
          body,
        },
        { status: res.status }
      );
    }

    if (!contentType.includes("application/json")) {
      return NextResponse.json(
        {
          error: "Backend did not return JSON",
          received: body.substring(0, 500),
        },
        { status: 502 }
      );
    }

    return new NextResponse(body, {
      status: 200,
      headers: {
        "Content-Type": "application/json",
      },
    });
  } catch (err) {
    console.error(err);

    return NextResponse.json(
      {
        error: err instanceof Error ? err.message : "Unknown error",
      },
      { status: 503 }
    );
  }
}