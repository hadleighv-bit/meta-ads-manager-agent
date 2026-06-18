import { useState } from 'react';
import type { OrientationFilter, PriceTierFilter } from '../types';

interface Props {
  onStart: (orientation: OrientationFilter, priceTier: PriceTierFilter) => void;
}

const ORIENTATION_OPTIONS: { value: OrientationFilter; label: string }[] = [
  { value: 'portrait', label: 'Portrait' },
  { value: 'landscape', label: 'Landscape' },
  { value: 'square', label: 'Square' },
  { value: 'all', label: 'Show me everything' },
];

const PRICE_OPTIONS: { value: PriceTierFilter; label: string; hint: string }[] = [
  { value: '$', label: '$', hint: 'under $150' },
  { value: '$$', label: '$$', hint: '$150–$320' },
  { value: '$$$', label: '$$$', hint: '$320+' },
  { value: 'all', label: 'Any', hint: 'no limit' },
];

export default function SetupScreen({ onStart }: Props) {
  const [orientation, setOrientation] = useState<OrientationFilter>('all');
  const [priceTier, setPriceTier] = useState<PriceTierFilter>('all');

  return (
    <div className="flex min-h-svh flex-col items-center justify-center px-6 py-12">
      <div className="w-full max-w-sm">
        <p className="font-serif text-2xl tracking-tight text-ink/90 italic">Fliptych</p>
        <h1 className="mt-3 font-serif text-[2.1rem] leading-[1.1] font-medium tracking-tight text-ink">
          Find the art that's actually yours.
        </h1>
        <p className="mt-3 text-[0.95rem] leading-relaxed text-stone">
          Tap the piece you prefer, twenty times. We'll learn your taste and
          show you a match worth hanging.
        </p>

        <div className="mt-9">
          <p className="text-xs font-medium tracking-wide text-stone uppercase">For your space</p>
          <div className="mt-3 grid grid-cols-2 gap-2">
            {ORIENTATION_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                onClick={() => setOrientation(opt.value)}
                className={`rounded-lg border px-3 py-2.5 text-sm transition-colors ${
                  orientation === opt.value
                    ? 'border-ink bg-ink text-paper'
                    : 'border-stone-light text-ink hover:border-ink/40'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-7">
          <p className="text-xs font-medium tracking-wide text-stone uppercase">Price range</p>
          <div className="mt-3 grid grid-cols-4 gap-2">
            {PRICE_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                onClick={() => setPriceTier(opt.value)}
                className={`flex flex-col items-center rounded-lg border px-2 py-2.5 transition-colors ${
                  priceTier === opt.value
                    ? 'border-ink bg-ink text-paper'
                    : 'border-stone-light text-ink hover:border-ink/40'
                }`}
              >
                <span className="text-sm font-semibold">{opt.label}</span>
                <span
                  className={`mt-0.5 text-[10px] ${
                    priceTier === opt.value ? 'text-paper/70' : 'text-stone'
                  }`}
                >
                  {opt.hint}
                </span>
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={() => onStart(orientation, priceTier)}
          className="mt-10 w-full rounded-full bg-clay px-6 py-3.5 text-sm font-semibold text-paper transition-transform active:scale-[0.98]"
        >
          Start matching
        </button>
        <button
          onClick={() => onStart('all', 'all')}
          className="mt-3 w-full rounded-full px-6 py-3 text-sm text-stone transition-colors hover:text-ink"
        >
          Skip and just play
        </button>
      </div>
    </div>
  );
}
