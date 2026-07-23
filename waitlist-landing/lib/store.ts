import { promises as fs } from "fs";
import path from "path";

/**
 * Local JSON fallback store, used when Klaviyo env vars are not set.
 *
 * NOTE: on Vercel the filesystem is ephemeral — signups written here survive
 * only within a single deployment instance. This fallback exists so the page
 * works end-to-end before Klaviyo is configured; configure Klaviyo before
 * driving real traffic.
 */
const DATA_FILE = path.join(process.cwd(), "data", "signups.json");

export interface Signup {
  email: string;
  joinedAt: string;
}

export async function readSignups(): Promise<Signup[]> {
  try {
    const raw = await fs.readFile(DATA_FILE, "utf8");
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export async function addSignup(email: string): Promise<void> {
  const signups = await readSignups();
  if (signups.some((s) => s.email.toLowerCase() === email.toLowerCase())) {
    return; // already on the list — treat as success
  }
  signups.push({ email, joinedAt: new Date().toISOString() });
  await fs.mkdir(path.dirname(DATA_FILE), { recursive: true });
  await fs.writeFile(DATA_FILE, JSON.stringify(signups, null, 2), "utf8");
}

export async function countSignups(): Promise<number> {
  return (await readSignups()).length;
}
