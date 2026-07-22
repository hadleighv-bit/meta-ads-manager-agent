/**
 * Central site configuration.
 * The brand name is a placeholder — set NEXT_PUBLIC_BRAND_NAME in your env
 * (or edit the fallback here) when the name is decided. Every component,
 * meta tag and copy block reads from this file.
 */
export const site = {
  brandName: process.env.NEXT_PUBLIC_BRAND_NAME || "LaLa Labs",
  url: process.env.NEXT_PUBLIC_SITE_URL || "https://example.com",
  instagramUrl:
    process.env.NEXT_PUBLIC_INSTAGRAM_URL || "https://instagram.com/yourbrand",
  tagline: "NZ's batch-tested NMN dietary supplement",
  description:
    "Batch-tested NMN dietary supplement, independently tested in New Zealand labs for purity and heavy metals. Join the founding list for 30% off at launch.",
  // Displayed count never drops below this floor.
  waitlistFloor: 50,
};
