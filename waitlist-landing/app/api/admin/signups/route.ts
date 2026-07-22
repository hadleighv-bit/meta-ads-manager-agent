import { NextResponse } from "next/server";
import { getKlaviyoListProfiles, klaviyoConfigured } from "@/lib/klaviyo";
import { readSignups, Signup } from "@/lib/store";

export const dynamic = "force-dynamic";

function authorized(request: Request): boolean {
  const configured = process.env.ADMIN_PASSWORD;
  if (!configured) return false; // admin disabled until a password is set
  const provided = request.headers.get("x-admin-password");
  return provided === configured;
}

async function loadSignups(): Promise<Signup[]> {
  if (klaviyoConfigured()) {
    try {
      const profiles = await getKlaviyoListProfiles();
      if (profiles.length > 0) {
        return profiles.map((p) => ({ email: p.email, joinedAt: p.joinedAt }));
      }
    } catch (err) {
      console.error("Klaviyo profile fetch failed, using local store:", err);
    }
  }
  const local = await readSignups();
  return [...local].reverse(); // newest first
}

export async function GET(request: Request) {
  if (!authorized(request)) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const signups = await loadSignups();
  const { searchParams } = new URL(request.url);

  if (searchParams.get("format") === "csv") {
    const rows = [
      "email,joined_at",
      ...signups.map(
        (s) => `${JSON.stringify(s.email)},${JSON.stringify(s.joinedAt)}`
      ),
    ];
    return new NextResponse(rows.join("\n"), {
      headers: {
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Disposition": 'attachment; filename="signups.csv"',
      },
    });
  }

  return NextResponse.json({
    signups,
    source: klaviyoConfigured() ? "klaviyo" : "local",
  });
}
