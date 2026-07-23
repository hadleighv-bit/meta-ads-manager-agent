const KLAVIYO_BASE = "https://a.klaviyo.com/api";
const KLAVIYO_REVISION = "2024-10-15";

export function klaviyoConfigured(): boolean {
  return Boolean(process.env.KLAVIYO_API_KEY && process.env.KLAVIYO_LIST_ID);
}

function headers(): HeadersInit {
  return {
    Authorization: `Klaviyo-API-Key ${process.env.KLAVIYO_API_KEY}`,
    "Content-Type": "application/json",
    Accept: "application/vnd.api+json",
    revision: KLAVIYO_REVISION,
  };
}

/**
 * Subscribe an email to the configured Klaviyo list with explicit
 * email-marketing consent. Uses the bulk subscribe job endpoint, which is
 * the current recommended way to add + subscribe a profile in one call.
 */
export async function subscribeToKlaviyo(email: string): Promise<void> {
  const listId = process.env.KLAVIYO_LIST_ID;
  const res = await fetch(
    `${KLAVIYO_BASE}/profile-subscription-bulk-create-jobs`,
    {
      method: "POST",
      headers: headers(),
      body: JSON.stringify({
        data: {
          type: "profile-subscription-bulk-create-job",
          attributes: {
            custom_source: "Waitlist landing page",
            profiles: {
              data: [
                {
                  type: "profile",
                  attributes: {
                    email,
                    subscriptions: {
                      email: { marketing: { consent: "SUBSCRIBED" } },
                    },
                  },
                },
              ],
            },
          },
          relationships: {
            list: { data: { type: "list", id: listId } },
          },
        },
      }),
    }
  );

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Klaviyo subscribe failed (${res.status}): ${body}`);
  }
}

/** Profile count of the configured list, or null if unavailable. */
export async function getKlaviyoListCount(): Promise<number | null> {
  const listId = process.env.KLAVIYO_LIST_ID;
  const res = await fetch(
    `${KLAVIYO_BASE}/lists/${listId}?additional-fields[list]=profile_count`,
    { headers: headers(), next: { revalidate: 60 } }
  );
  if (!res.ok) return null;
  const json = await res.json();
  const count = json?.data?.attributes?.profile_count;
  return typeof count === "number" ? count : null;
}

export interface KlaviyoProfile {
  email: string;
  joinedAt: string;
}

/** First pages of profiles on the list, newest first (admin view). */
export async function getKlaviyoListProfiles(
  maxPages = 10
): Promise<KlaviyoProfile[]> {
  const listId = process.env.KLAVIYO_LIST_ID;
  const profiles: KlaviyoProfile[] = [];
  let url: string | null =
    `${KLAVIYO_BASE}/lists/${listId}/profiles?page[size]=100&fields[profile]=email,joined_group_at&sort=-joined_group_at`;

  for (let page = 0; url && page < maxPages; page++) {
    const res: Response = await fetch(url, {
      headers: headers(),
      cache: "no-store",
    });
    if (!res.ok) break;
    const json: any = await res.json();
    for (const item of json?.data ?? []) {
      profiles.push({
        email: item?.attributes?.email ?? "",
        joinedAt: item?.attributes?.joined_group_at ?? "",
      });
    }
    url = json?.links?.next ?? null;
  }
  return profiles;
}
