import { useMemo, useState } from 'react';
import ArtworkVisual from './ArtworkVisual';
import ArtistSheet from './ArtistSheet';
import { scoreArtwork, summarizeTaste, type RefineBias, type TasteProfile } from '../lib/tasteEngine';
import type { Artwork, Subject } from '../types';

interface Props {
  champion: Artwork;
  catalog: Artwork[];
  profile: TasteProfile;
  onPlayAgain: () => void;
}

const SUBJECT_OPTIONS: { value: Subject | null; label: string }[] = [
  { value: null, label: 'All subjects' },
  { value: 'landscape', label: 'Landscapes' },
  { value: 'portrait', label: 'Portraits' },
  { value: 'abstract', label: 'Abstract' },
  { value: 'photography', label: 'Photography' },
  { value: 'still-life', label: 'Still life' },
];

function BuyButton({ artwork }: { artwork: Artwork }) {
  const [added, setAdded] = useState(false);
  return (
    <button
      onClick={() => setAdded(true)}
      disabled={added}
      className={`flex-1 rounded-full px-4 py-2.5 text-xs font-semibold transition-colors ${
        added ? 'bg-stone-light text-stone' : 'bg-ink text-paper hover:bg-ink/90'
      }`}
    >
      {added ? 'Added ✓' : `Buy print · $${artwork.price}`}
    </button>
  );
}

function PieceCard({
  artwork,
  saved,
  onToggleSave,
  onShowArtist,
}: {
  artwork: Artwork;
  saved: boolean;
  onToggleSave: () => void;
  onShowArtist: () => void;
}) {
  return (
    <div className="w-44 flex-shrink-0 snap-start">
      <div className="relative aspect-[4/5] overflow-hidden rounded-lg bg-stone-light">
        <ArtworkVisual artwork={artwork} />
        <button
          onClick={onToggleSave}
          aria-label="Save"
          className="absolute top-2 right-2 flex h-8 w-8 items-center justify-center rounded-full bg-paper/90 text-base backdrop-blur"
        >
          {saved ? '♥' : '♡'}
        </button>
      </div>
      <button onClick={onShowArtist} className="mt-2 block text-left">
        <p className="truncate text-sm font-medium text-ink">{artwork.title}</p>
        <p className="truncate text-xs text-stone">{artwork.artistName}</p>
      </button>
      <div className="mt-2">
        <BuyButton artwork={artwork} />
      </div>
    </div>
  );
}

export default function ResultsScreen({ champion, catalog, profile, onPlayAgain }: Props) {
  const [saved, setSaved] = useState<Set<string>>(new Set());
  const [artistSheetFor, setArtistSheetFor] = useState<Artwork | null>(null);
  const [temperature, setTemperature] = useState<-1 | 0 | 1>(0);
  const [subjectOnly, setSubjectOnly] = useState<Subject | null>(null);
  const [maxPrice, setMaxPrice] = useState<number | null>(null);
  const [email, setEmail] = useState('');
  const [emailSaved, setEmailSaved] = useState(false);

  const topFive = useMemo(() => {
    const bias: RefineBias = { temperature, subjectOnly, maxPrice };
    const pool = catalog.filter((a) => {
      if (bias.subjectOnly && a.tags.subject !== bias.subjectOnly) return false;
      if (bias.maxPrice && a.price > bias.maxPrice) return false;
      return true;
    });
    return [...pool]
      .sort((a, b) => scoreArtwork(b, profile, bias) - scoreArtwork(a, profile, bias))
      .slice(0, 5);
  }, [catalog, profile, temperature, subjectOnly, maxPrice]);

  function toggleSave(id: string) {
    setSaved((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }

  return (
    <div className="min-h-svh px-5 pt-10 pb-16">
      <div className="mx-auto max-w-md">
        <p className="text-center text-xs font-medium tracking-widest text-stone uppercase">
          Your champion
        </p>

        <div className="mt-4 overflow-hidden rounded-xl bg-stone-light shadow-sm">
          <div className="aspect-[4/5]">
            <ArtworkVisual artwork={champion} />
          </div>
        </div>

        <button
          onClick={() => setArtistSheetFor(champion)}
          className="mt-4 block w-full text-center"
        >
          <p className="font-serif text-xl font-medium text-ink">
            You picked <span className="italic">{champion.title}</span> by {champion.artistName}.
          </p>
          <p className="mt-1 text-xs text-stone underline">View artist</p>
        </button>

        <p className="mx-auto mt-4 max-w-xs text-center text-sm leading-relaxed text-stone">
          {summarizeTaste(profile)}
        </p>

        <div className="mt-4 flex gap-2">
          <BuyButton artwork={champion} />
          <button
            onClick={() => toggleSave(champion.id)}
            className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full border border-stone-light text-base"
            aria-label="Save"
          >
            {saved.has(champion.id) ? '♥' : '♡'}
          </button>
        </div>

        <div className="mt-12">
          <p className="text-xs font-medium tracking-widest text-stone uppercase">Your top 5</p>
          <div className="mt-3 flex gap-3 overflow-x-auto pb-2 [-ms-overflow-style:none] [scrollbar-width:none] snap-x [&::-webkit-scrollbar]:hidden">
            {topFive.map((a) => (
              <PieceCard
                key={a.id}
                artwork={a}
                saved={saved.has(a.id)}
                onToggleSave={() => toggleSave(a.id)}
                onShowArtist={() => setArtistSheetFor(a)}
              />
            ))}
          </div>
        </div>

        <div className="mt-10 rounded-xl border border-stone-light p-4">
          <p className="text-xs font-medium tracking-widest text-stone uppercase">Refine</p>
          <p className="mt-1 text-xs text-stone">More like this, steered your way.</p>

          <div className="mt-3 flex gap-2">
            {([-1, 0, 1] as const).map((t) => (
              <button
                key={t}
                onClick={() => setTemperature(t)}
                className={`flex-1 rounded-full border px-2 py-2 text-xs font-medium ${
                  temperature === t
                    ? 'border-ink bg-ink text-paper'
                    : 'border-stone-light text-ink'
                }`}
              >
                {t === -1 ? 'Cooler' : t === 1 ? 'Warmer' : 'As is'}
              </button>
            ))}
          </div>

          <select
            value={subjectOnly ?? ''}
            onChange={(e) => setSubjectOnly((e.target.value || null) as Subject | null)}
            className="mt-2 w-full rounded-full border border-stone-light bg-paper px-3 py-2 text-xs text-ink"
          >
            {SUBJECT_OPTIONS.map((opt) => (
              <option key={opt.label} value={opt.value ?? ''}>
                {opt.label}
              </option>
            ))}
          </select>

          <div className="mt-2 flex items-center gap-2 text-xs text-stone">
            <span>Under $</span>
            <input
              type="number"
              placeholder="any"
              value={maxPrice ?? ''}
              onChange={(e) => setMaxPrice(e.target.value ? Number(e.target.value) : null)}
              className="w-20 rounded-full border border-stone-light bg-paper px-3 py-2 text-ink"
            />
          </div>
        </div>

        <div className="mt-10 rounded-xl bg-ink p-5 text-center">
          <p className="font-serif text-lg font-medium text-paper">Save your taste profile</p>
          <p className="mt-1 text-xs text-paper/70">Get your matches sent to your inbox.</p>
          {emailSaved ? (
            <p className="mt-3 text-sm text-paper">You're in. Check your inbox soon.</p>
          ) : (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (email.includes('@')) setEmailSaved(true);
              }}
              className="mt-3 flex gap-2"
            >
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@email.com"
                className="flex-1 rounded-full border border-paper/30 bg-transparent px-3.5 py-2.5 text-sm text-paper placeholder:text-paper/40"
              />
              <button
                type="submit"
                className="rounded-full bg-clay px-4 py-2.5 text-xs font-semibold text-paper"
              >
                Get matches
              </button>
            </form>
          )}
        </div>

        <button
          onClick={onPlayAgain}
          className="mt-8 w-full rounded-full border border-stone-light px-6 py-3.5 text-sm font-medium text-ink"
        >
          Play again
        </button>
      </div>

      {artistSheetFor && (
        <ArtistSheet
          artwork={artistSheetFor}
          worksByArtist={catalog.filter((a) => a.artistName === artistSheetFor.artistName)}
          onClose={() => setArtistSheetFor(null)}
        />
      )}
    </div>
  );
}
