import Link from "next/link";
import { site } from "@/lib/site";
import EmailForm from "@/components/EmailForm";
import WaitlistCounter from "@/components/WaitlistCounter";
import Faq from "@/components/Faq";

const trustPoints = [
  "99%+ purity",
  "NZ lab tested",
  "Ships from NZ",
  "Every batch verified",
];

const educationCards = [
  {
    title: "NAD+ declines with age",
    body: "NAD+ is a coenzyme found in every living cell, involved in hundreds of cellular processes. Research shows NAD+ levels naturally decline as we get older.",
  },
  {
    title: "NMN and cellular energy",
    body: "NMN (nicotinamide mononucleotide) is a direct precursor to NAD+. The body converts NMN into NAD+, which plays a role in normal cellular energy production.",
  },
  {
    title: "A part of healthy ageing",
    body: "Many people include NMN in their routine to support healthy ageing, alongside the fundamentals — sleep, movement, and a balanced diet.",
  },
];

const faqItems = [
  {
    question: "What is NMN?",
    answer:
      "NMN (nicotinamide mononucleotide) is a naturally occurring molecule related to vitamin B3 and a direct precursor to NAD+, a coenzyme found in every cell. Our NMN is offered as a dietary supplement.",
  },
  {
    question: "How much should I take?",
    answer:
      "Always read the label and use only as directed. Serving suggestions will be printed on the label, and each batch page will include full composition details. If you have a medical condition, are pregnant or breastfeeding, or take medication, talk to your health professional before use.",
  },
  {
    question: "Do you ship across New Zealand?",
    answer:
      "Yes — we ship nationwide from within New Zealand, so no customs, no surprise duties, and no long international transit. Australian shipping is on the roadmap.",
  },
  {
    question: "When do you launch?",
    answer:
      "We launch as soon as our first production batch clears independent laboratory testing. Founding list members hear first and receive 30% off their first order.",
  },
];

export default function Home() {
  return (
    <main>
      {/* Hero */}
      <section className="border-b border-ink/10">
        <div className="container-narrow flex min-h-[92svh] flex-col justify-center py-16">
          <p className="eyebrow">{site.brandName} · Dietary supplement</p>
          <h1 className="mt-6 font-display text-4xl leading-[1.08] sm:text-5xl">
            NZ&apos;s batch-tested NMN. Founding members get 30% off.
          </h1>
          <p className="mt-6 max-w-md text-base leading-relaxed text-ink/70">
            Every batch of our NMN dietary supplement is independently tested
            in New Zealand laboratories for purity and heavy metals — and the
            results are published.
          </p>
          <div className="mt-10">
            <EmailForm />
          </div>
          <div className="mt-8">
            <WaitlistCounter />
          </div>
        </div>
      </section>

      {/* Trust strip */}
      <section aria-label="Quality commitments" className="border-b border-ink/10 bg-white">
        <div className="container-wide">
          <ul className="grid grid-cols-2 divide-ink/10 sm:grid-cols-4 sm:divide-x">
            {trustPoints.map((point) => (
              <li
                key={point}
                className="px-4 py-6 text-center text-[11px] font-medium uppercase tracking-widest2 text-ink/80"
              >
                {point}
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* Why NMN — ingredient education */}
      <section className="border-b border-ink/10">
        <div className="container-wide py-20 sm:py-28">
          <p className="eyebrow">Ingredient education</p>
          <h2 className="mt-4 max-w-lg font-display text-3xl leading-tight sm:text-4xl">
            Why NMN
          </h2>
          <div className="mt-12 grid gap-px overflow-hidden border border-ink/10 bg-ink/10 sm:grid-cols-3">
            {educationCards.map((card, i) => (
              <article key={card.title} className="bg-paper p-8">
                <p className="font-display text-sm text-accent-deep">
                  0{i + 1}
                </p>
                <h3 className="mt-4 font-display text-xl">{card.title}</h3>
                <p className="mt-4 text-sm leading-relaxed text-ink/70">
                  {card.body}
                </p>
              </article>
            ))}
          </div>
          <p className="mt-8 max-w-2xl text-xs leading-relaxed text-stone-mid">
            This information is general ingredient education, not advice about
            our product. This product is not intended to diagnose, treat, cure
            or prevent any disease.
          </p>
        </div>
      </section>

      {/* Transparency */}
      <section className="border-b border-ink/10 bg-white">
        <div className="container-wide py-20 sm:py-28">
          <p className="eyebrow">Transparency</p>
          <h2 className="mt-4 max-w-lg font-display text-3xl leading-tight sm:text-4xl">
            Test results you can read yourself
          </h2>
          <div className="mt-12 grid gap-12 sm:grid-cols-2">
            <div>
              <h3 className="font-display text-xl">Certificate of Analysis</h3>
              <p className="mt-4 text-sm leading-relaxed text-ink/70">
                Every production batch is sent to an independent, accredited
                New Zealand laboratory and tested for NMN purity and heavy
                metals. The full Certificate of Analysis for our first batch
                will be published here before launch.
              </p>
              <p className="mt-6">
                <span
                  aria-disabled="true"
                  className="inline-block border border-ink/20 px-5 py-3 text-[11px] font-medium uppercase tracking-widest2 text-stone-mid"
                >
                  COA (PDF) — available at launch
                </span>
              </p>
            </div>
            <div>
              <h3 className="font-display text-xl">
                Every batch number, searchable
              </h3>
              <p className="mt-4 text-sm leading-relaxed text-ink/70">
                The batch number printed on your pouch will be searchable on
                this site, linking directly to that batch&apos;s laboratory
                results. If we wouldn&apos;t publish the numbers, we
                wouldn&apos;t ship the batch.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Founder */}
      <section className="border-b border-ink/10">
        <div className="container-wide py-20 sm:py-28">
          <div className="grid items-start gap-12 sm:grid-cols-[280px_1fr]">
            <div
              role="img"
              aria-label="Portrait of Justin, founder — photo coming soon"
              className="flex aspect-[4/5] w-full max-w-[280px] items-center justify-center border border-ink/10 bg-stone-light"
            >
              <span className="text-[11px] uppercase tracking-widest2 text-stone-mid">
                Photo coming soon
              </span>
            </div>
            <div>
              <p className="eyebrow">Founder</p>
              <h2 className="mt-4 font-display text-3xl leading-tight sm:text-4xl">
                From Justin
              </h2>
              <p className="mt-6 max-w-lg text-base leading-relaxed text-ink/70">
                &ldquo;I started {site.brandName} because I wanted an NMN
                dietary supplement I could actually verify — made for New
                Zealand, tested in New Zealand, with the lab results out in
                the open. No imported mystery powder, no marketing hype. Just
                a clean ingredient, an honest label, and the paperwork to
                prove it.&rdquo;
              </p>
              <p className="mt-6 text-sm text-stone-mid">
                Justin — Founder, {site.brandName}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="border-b border-ink/10 bg-white">
        <div className="container-narrow py-20 sm:py-28">
          <p className="eyebrow">FAQ</p>
          <h2 className="mt-4 font-display text-3xl leading-tight sm:text-4xl">
            Questions, answered
          </h2>
          <div className="mt-10">
            <Faq items={faqItems} />
          </div>
        </div>
      </section>

      {/* Closing CTA */}
      <section className="border-b border-ink/10">
        <div className="container-narrow py-20 sm:py-28">
          <h2 className="font-display text-3xl leading-tight sm:text-4xl">
            Be first in line.
          </h2>
          <p className="mt-4 text-base leading-relaxed text-ink/70">
            Join the founding list for 30% off your first order and first
            access when our inaugural batch clears testing.
          </p>
          <div className="mt-8">
            <EmailForm />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer>
        <div className="container-wide py-14">
          <div className="flex flex-col gap-8 sm:flex-row sm:items-start sm:justify-between">
            <p className="font-display text-lg">{site.brandName}</p>
            <nav aria-label="Footer" className="flex gap-8 text-sm">
              <Link
                href="/privacy"
                className="text-ink/70 underline-offset-4 hover:underline"
              >
                Privacy policy
              </Link>
              <a
                href={site.instagramUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-ink/70 underline-offset-4 hover:underline"
              >
                Instagram
              </a>
            </nav>
          </div>
          <div className="mt-10 max-w-3xl space-y-3 border-t border-ink/10 pt-8 text-xs leading-relaxed text-stone-mid">
            <p>
              {site.brandName} NMN is a dietary supplement. Dietary supplements
              are not a replacement for a balanced diet. Always read the label
              and use only as directed. If symptoms persist, see your health
              professional. This product is not intended to diagnose, treat,
              cure or prevent any disease.
            </p>
            <p>
              © {new Date().getFullYear()} {site.brandName}. Made and shipped
              from Aotearoa New Zealand.
            </p>
          </div>
        </div>
      </footer>
    </main>
  );
}
