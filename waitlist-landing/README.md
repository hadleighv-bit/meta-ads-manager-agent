# NMN Waitlist Landing Page

Premium waitlist landing page for a New Zealand longevity supplement brand,
launching with batch-tested NMN. Next.js 14 (App Router) + Tailwind CSS,
built mobile-first for Instagram traffic and deployable to Vercel.

## Features

- **Hero email capture** → posts to a Klaviyo list via `/api/subscribe`, with
  a local JSON fallback (`data/signups.json`) when Klaviyo isn't configured
- **Waitlist counter** reading the real signup count (display floor of 50)
- **Compliance-safe copy** — written for NZ dietary supplement rules: no
  therapeutic claims, "supports / healthy ageing / cellular energy" language
  only, "dietary supplement" labelling, and the standard disclaimer in both
  the education section and footer
- **Transparency section** with Certificate of Analysis placeholder and
  batch-search promise
- **FAQ accordion**, founder section, privacy policy page
- **`/admin`** — password-protected signups table with CSV export
- **OG/meta tags** + a generated Open Graph image (`app/opengraph-image.tsx`)
  for Instagram link sharing
- **Plausible and/or GA4** analytics, enabled purely by env vars

## Brand

The site is branded **LaLa Labs**: sign-orange accent (`#EFA33C`) on deep
café-teal ink (`#17383B`), with Shantell Sans as the hand-lettered display
face. The name can be overridden with `NEXT_PUBLIC_BRAND_NAME` — every
component, meta tag, and copy block reads it from [`lib/site.ts`](lib/site.ts);
colours live in [`tailwind.config.ts`](tailwind.config.ts).

## Local development

```bash
cd waitlist-landing
cp .env.example .env.local   # fill in what you have; everything is optional locally
npm install
npm run dev
```

Open http://localhost:3000. Without Klaviyo keys, signups are written to
`data/signups.json` so the whole flow (form → counter → admin → CSV) works
out of the box.

## Deploy to Vercel

1. Push this repository to GitHub.
2. In [Vercel](https://vercel.com/new), click **Add New → Project** and import
   the repo.
3. Set **Root Directory** to `waitlist-landing` (Framework Preset: Next.js —
   auto-detected; default build settings are fine).
4. Under **Environment Variables**, add the variables from
   [`.env.example`](.env.example):

   | Variable | Required | Purpose |
   |---|---|---|
   | `NEXT_PUBLIC_BRAND_NAME` | recommended | Brand name shown site-wide |
   | `NEXT_PUBLIC_SITE_URL` | recommended | Canonical URL for OG/meta tags |
   | `NEXT_PUBLIC_INSTAGRAM_URL` | recommended | Footer Instagram link |
   | `KLAVIYO_API_KEY` | for production | Klaviyo private key (`pk_...`) |
   | `KLAVIYO_LIST_ID` | for production | Klaviyo list to subscribe to |
   | `ADMIN_PASSWORD` | for `/admin` | Password for the signups dashboard |
   | `NEXT_PUBLIC_PLAUSIBLE_DOMAIN` | optional | Enables Plausible |
   | `NEXT_PUBLIC_GA_MEASUREMENT_ID` | optional | Enables GA4 |

5. Click **Deploy**. Add your custom domain under **Settings → Domains**, then
   update `NEXT_PUBLIC_SITE_URL` to match and redeploy.

> **Important:** the local JSON fallback is ephemeral on Vercel (serverless
> filesystems don't persist). It exists so you can ship and test before
> Klaviyo is ready — set `KLAVIYO_API_KEY` + `KLAVIYO_LIST_ID` before driving
> real Instagram traffic.

## Klaviyo setup

1. Klaviyo → **Lists & Segments** → create a list (e.g. "Founding waitlist").
   The list ID is in the URL (e.g. `XyZ123`).
2. **Settings → Account → API keys** → create a private key with read/write
   scopes for Profiles, Lists, and Subscriptions.
3. Set `KLAVIYO_API_KEY` and `KLAVIYO_LIST_ID` in Vercel and redeploy.

Signups are subscribed with explicit email-marketing consent
(`custom_source: "Waitlist landing page"`), so they're immediately usable in
Klaviyo flows (e.g. a welcome email carrying the founding-member offer).

## Admin dashboard

Visit `/admin`, enter `ADMIN_PASSWORD`. Shows all signups (from Klaviyo when
configured, otherwise the local store) with an **Export CSV** button. If
`ADMIN_PASSWORD` is unset the route is disabled entirely.

## Compliance notes (NZ dietary supplements)

Copy on this page deliberately:

- never claims to treat, cure, prevent, or diagnose anything, and never
  mentions diseases or life extension;
- uses only "supports", "healthy ageing", "cellular energy" style language,
  framed as **ingredient education**, not product claims;
- labels the product a **dietary supplement** wherever it's named;
- includes "This product is not intended to diagnose, treat, cure or prevent
  any disease" in the education section and footer, plus "always read the
  label and use only as directed".

If you edit copy, keep to this standard — review against the Dietary
Supplements Regulations 1985 and Medicines Act 1981 (a therapeutic claim can
legally turn a supplement into a medicine).

## Project structure

```
waitlist-landing/
├── app/
│   ├── page.tsx                  # landing page (all sections)
│   ├── layout.tsx                # fonts, metadata, analytics
│   ├── opengraph-image.tsx       # generated OG image
│   ├── privacy/page.tsx          # privacy policy
│   ├── admin/page.tsx            # signups dashboard
│   └── api/
│       ├── subscribe/route.ts    # POST email → Klaviyo (or local JSON)
│       ├── waitlist-count/route.ts
│       └── admin/signups/route.ts  # JSON + CSV, password-protected
├── components/                   # EmailForm, Faq, WaitlistCounter, Analytics
├── lib/                          # site config, Klaviyo client, local store
└── data/                         # local fallback store (gitignored)
```
