"use client";

import { useState } from "react";

interface FaqItem {
  question: string;
  answer: string;
}

export default function Faq({ items }: { items: FaqItem[] }) {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <div className="divide-y divide-ink/10 border-y border-ink/10">
      {items.map((item, i) => {
        const isOpen = open === i;
        return (
          <div key={item.question}>
            <button
              type="button"
              onClick={() => setOpen(isOpen ? null : i)}
              aria-expanded={isOpen}
              className="flex w-full items-baseline justify-between gap-4 py-5 text-left"
            >
              <span className="font-display text-lg">{item.question}</span>
              <span
                aria-hidden="true"
                className="text-xl leading-none text-accent"
              >
                {isOpen ? "−" : "+"}
              </span>
            </button>
            {isOpen && (
              <p className="pb-6 pr-8 text-sm leading-relaxed text-ink/70">
                {item.answer}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
}
