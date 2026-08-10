// frontend/app/api/users/alerts/route.ts

import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const backend = process.env.NEXT_PUBLIC_API_URL;
    if (!backend) {
      return NextResponse.json({ error: "API_URL is not configured" }, { status: 500 });
    }

    console.log("Sending request to backend");

    const res = await fetch(`${backend}/api/users/alerts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
    });

    console.log(res.status);

    const contentType = res.headers.get("content-type") || "";
    const text = await res.text();

    if (!res.ok) {
      return NextResponse.json(
        { error: "Backend returned an error", status: res.status, body: text },
        { status: res.status }
      );
    }

    if (!contentType.includes("application/json")) {
      return NextResponse.json(
        { error: "Backend did not return JSON", received: text.substring(0, 500) },
        { status: 502 }
      );
    }

    return new NextResponse(text, {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: "Failed to save email alert preferences" }, { status: 500 });
  }
}
