# Fliptych

A swipe-style art discovery game that doubles as a storefront for canvas
prints. Two artworks face off, the player taps a favourite, the winner
stays king-of-the-hill for ~20 rounds, and a results screen reveals their
"champion" piece plus a taste-matched Top 5 — all sellable as canvas
prints by named artists.

## Run it

```bash
npm install
npm run dev
```

## How it works

- **`src/types.ts`** — the `Artwork` schema. Each piece carries hidden
  tags (colour palette, subject, mood, medium) used only by the taste
  engine, never shown in the UI.
- **`src/data/artworks.ts`** — the mock catalogue (~40 pieces). This is
  the one file you'd replace with a real catalogue/JSON feed; nothing
  else needs to change as long as the `Artwork` shape is preserved.
- **`src/lib/tasteEngine.ts`** — builds a running taste profile from
  win/loss tag deltas, picks tag-diverse pairs early (fast exploration)
  and taste-weighted pairs later (convergence), and scores/ranks pieces
  for the results screen.
- **`src/lib/placeholder.ts`** — generates an abstract gradient
  placeholder from a piece's tags when it has no real `imageUrl`.
- **`src/components/`** — `SetupScreen` (skippable size/price prefs),
  `PlayScreen` (the two-up tap loop, animated with framer-motion),
  `ResultsScreen` (champion, taste summary, Top 5, refine, email
  capture), `ArtistSheet` (tappable artist provenance card).
