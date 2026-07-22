import { NextResponse } from "next/server";
import { klaviyoConfigured, subscribeToKlaviyo } from "@/lib/klaviyo";
import { addSignup } from "@/lib/store";

export const dynamic = "force-dynamic";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

export async function POST(request: Request) {
  let email: unknown;
  try {
    ({ email } = await request.json());
  } catch {
    return NextResponse.json({ error: "Invalid request." }, { status: 400 });
  }

  if (typeof email !== "string" || !EMAIL_RE.test(email.trim())) {
    return NextResponse.json(
      { error: "Please enter a valid email address." },
      { status: 400 }
    );
  }
  const cleanEmail = email.trim().toLowerCase();

  try {
    if (klaviyoConfigured()) {
      await subscribeToKlaviyo(cleanEmail);
      // Mirror to the local store as well so the fallback counter keeps
      // working; ignore filesystem failures on read-only hosts.
      await addSignup(cleanEmail).catch(() => {});
    } else {
      await addSignup(cleanEmail);
    }
    return NextResponse.json({ ok: true });
  } catch (err) {
    console.error("Subscribe failed:", err);
    return NextResponse.json(
      { error: "Something went wrong — please try again." },
      { status: 500 }
    );
  }
}
