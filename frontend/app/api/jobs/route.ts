// frontend/app/api/jobs/route.ts

import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const { searchParams } = req.nextUrl;

  const backend = process.env.API_URL;
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
    const res = await fetch(url.toString(), {
      cache: "no-store",
    });

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