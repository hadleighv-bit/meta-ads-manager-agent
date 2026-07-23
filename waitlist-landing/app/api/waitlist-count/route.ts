import { NextResponse } from "next/server";
import { getKlaviyoListCount, klaviyoConfigured } from "@/lib/klaviyo";
import { countSignups } from "@/lib/store";
import { site } from "@/lib/site";

export const dynamic = "force-dynamic";

export async function GET() {
  let count = 0;
  try {
    if (klaviyoConfigured()) {
      count = (await getKlaviyoListCount()) ?? (await countSignups());
    } else {
      count = await countSignups();
    }
  } catch {
    count = 0;
  }
  return NextResponse.json({ count: Math.max(count, site.waitlistFloor) });
}
