//frontend/app/api/jobs/route.ts

import { NextResponse } from "next/server";

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);

  const backend =
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000";

  const backendUrl =
    `${backend}/api/jobs?city=${encodeURIComponent(searchParams.get("city") ?? "")}`;

  console.log("BACKEND =", backend);
  console.log("URL =", backendUrl);

  try {
    const res = await fetch(backendUrl);

    console.log("STATUS =", res.status);

    const text = await res.text();

    console.log(text.substring(0,500));

    return new Response(text, {
      status: res.status,
      headers: {
        "Content-Type":"application/json"
      }
    });

  } catch (e) {
    console.error(e);

    return NextResponse.json({
      error:String(e)
    });
  }
}