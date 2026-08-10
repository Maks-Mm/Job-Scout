// frontend/app/api/users/verify-email/route.ts

import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  try {
    const backend = process.env.NEXT_PUBLIC_API_URL;
    if (!backend) {
      return NextResponse.json({ error: "API_URL is not configured" }, { status: 500 });
    }

    const url = new URL(request.url);
    const token = url.searchParams.get("token") || "";

    const res = await fetch(`${backend}/api/users/verify-email?token=${encodeURIComponent(token)}`, {
      method: "GET",
      cache: "no-store",
    });

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
    return NextResponse.json({ error: "Failed to verify email" }, { status: 500 });
  }
}
