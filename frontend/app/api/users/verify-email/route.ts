//frontend/app/api/users/verify-email/route.ts

import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  try {
    const backend = process.env.NEXT_PUBLIC_API_URL;

    if (!backend) {
      return NextResponse.json(
        { error: "API_URL is not configured" },
        { status: 500 }
      );
    }

    const { searchParams } = new URL(request.url);
    const token = searchParams.get("token");

    if (!token) {
      return NextResponse.json(
        { detail: "Missing verification token." },
        { status: 400 }
      );
    }

    const backendUrl =
      `${backend.replace(/\/$/, "")}` +
      `/api/users/verify-email?token=${encodeURIComponent(token)}`;

    const res = await fetch(backendUrl, {
      method: "GET",
      cache: "no-store",
      headers: {
        Accept: "application/json",
      },
    });

    const contentType = res.headers.get("content-type") || "";
    const text = await res.text();

    let data: unknown;

    try {
      data = text ? JSON.parse(text) : {};
    } catch {
      return NextResponse.json(
        {
          detail: "Backend did not return valid JSON.",
          received: text.substring(0, 500),
        },
        { status: 502 }
      );
    }

    if (!contentType.includes("application/json")) {
      return NextResponse.json(
        {
          detail: "Backend did not return JSON.",
          received: text.substring(0, 500),
        },
        { status: 502 }
      );
    }

    return NextResponse.json(data, {
      status: res.status,
      headers: {
        "Cache-Control": "no-store",
      },
    });
  } catch (error) {
    console.error("Email verification proxy error:", error);

    return NextResponse.json(
      { detail: "Failed to verify email." },
      { status: 500 }
    );
  }
}
