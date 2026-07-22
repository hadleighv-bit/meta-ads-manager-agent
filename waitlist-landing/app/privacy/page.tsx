import type { Metadata } from "next";
import Link from "next/link";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: `Privacy policy — ${site.brandName}`,
};

export default function PrivacyPage() {
  return (
    <main className="container-narrow py-16 sm:py-24">
      <p className="eyebrow">{site.brandName}</p>
      <h1 className="mt-4 font-display text-3xl leading-tight sm:text-4xl">
        Privacy policy
      </h1>

      <div className="mt-10 space-y-8 text-sm leading-relaxed text-ink/80">
        <section>
          <h2 className="font-display text-xl text-ink">What we collect</h2>
          <p className="mt-3">
            When you join our founding list we collect your email address and
            the time you signed up. That&apos;s it — no names, no tracking
            profiles, no purchase history (there&apos;s nothing to purchase
            yet).
          </p>
        </section>

        <section>
          <h2 className="font-display text-xl text-ink">How we use it</h2>
          <p className="mt-3">
            We use your email address to send you launch news and your
            founding-member offer. We won&apos;t sell, rent, or share your
            email address with third parties for their own marketing.
          </p>
        </section>

        <section>
          <h2 className="font-display text-xl text-ink">Where it&apos;s stored</h2>
          <p className="mt-3">
            Signups are stored with our email service provider (Klaviyo), which
            processes data on our behalf. Basic, privacy-respecting analytics
            may be used to understand how people find this page.
          </p>
        </section>

        <section>
          <h2 className="font-display text-xl text-ink">Your choices</h2>
          <p className="mt-3">
            Every email we send includes an unsubscribe link. You can also ask
            us at any time to access, correct, or delete the information we
            hold about you, in line with the New Zealand Privacy Act 2020.
            Reach us via{" "}
            <a
              href={site.instagramUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="underline underline-offset-4"
            >
              Instagram
            </a>{" "}
            or reply to any of our emails.
          </p>
        </section>
      </div>

      <p className="mt-12">
        <Link
          href="/"
          className="text-sm text-accent-deep underline-offset-4 hover:underline"
        >
          ← Back to {site.brandName}
        </Link>
      </p>
    </main>
  );
}
