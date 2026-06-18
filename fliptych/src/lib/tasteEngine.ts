import type {
  Artwork,
  ColorPalette,
  Medium,
  Mood,
  OrientationFilter,
  PriceTierFilter,
  Subject,
} from '../types';

/**
 * Running taste profile built from tap history. Each dimension tracks a
 * score per possible tag value; picking a piece nudges its tags up,
 * rejecting one nudges them down. Pure addition/subtraction — no need for
 * anything fancier at this scale.
 */
export interface TasteProfile {
  palette: Record<ColorPalette, number>;
  subject: Record<Subject, number>;
  mood: Record<Mood, number>;
  medium: Record<Medium, number>;
}

const PALETTES: ColorPalette[] = ['warm', 'cool', 'neutral', 'bold'];
const SUBJECTS: Subject[] = ['landscape', 'portrait', 'abstract', 'photography', 'still-life'];
const MOODS: Mood[] = ['calm', 'energetic'];
const MEDIUMS: Medium[] = ['oil', 'acrylic', 'watercolor', 'photography', 'digital', 'mixed-media', 'ink'];

function zeroRecord<K extends string>(keys: K[]): Record<K, number> {
  return Object.fromEntries(keys.map((k) => [k, 0])) as Record<K, number>;
}

export function createTasteProfile(): TasteProfile {
  return {
    palette: zeroRecord(PALETTES),
    subject: zeroRecord(SUBJECTS),
    mood: zeroRecord(MOODS),
    medium: zeroRecord(MEDIUMS),
  };
}

const WIN_WEIGHT = 1;
const LOSE_WEIGHT = 0.5;

/** Updates the profile in place from one tap decision (immutable copy returned). */
export function updateTasteProfile(
  profile: TasteProfile,
  winner: Artwork,
  loser: Artwork,
): TasteProfile {
  const next: TasteProfile = {
    palette: { ...profile.palette },
    subject: { ...profile.subject },
    mood: { ...profile.mood },
    medium: { ...profile.medium },
  };

  // Only count a dimension as a signal when the two pieces disagree on it —
  // if both share a tag, the tap doesn't tell us anything about that tag.
  if (winner.tags.palette !== loser.tags.palette) {
    next.palette[winner.tags.palette] += WIN_WEIGHT;
    next.palette[loser.tags.palette] -= LOSE_WEIGHT;
  }
  if (winner.tags.subject !== loser.tags.subject) {
    next.subject[winner.tags.subject] += WIN_WEIGHT;
    next.subject[loser.tags.subject] -= LOSE_WEIGHT;
  }
  if (winner.tags.mood !== loser.tags.mood) {
    next.mood[winner.tags.mood] += WIN_WEIGHT;
    next.mood[loser.tags.mood] -= LOSE_WEIGHT;
  }
  if (winner.tags.medium !== loser.tags.medium) {
    next.medium[winner.tags.medium] += WIN_WEIGHT;
    next.medium[loser.tags.medium] -= LOSE_WEIGHT;
  }

  return next;
}

export interface RefineBias {
  /** -1 = push cooler, 0 = neutral, 1 = push warmer */
  temperature?: -1 | 0 | 1;
  subjectOnly?: Subject | null;
  maxPrice?: number | null;
}

/** Scores how well an artwork matches a taste profile. Higher is better. */
export function scoreArtwork(artwork: Artwork, profile: TasteProfile, bias?: RefineBias): number {
  let score =
    profile.palette[artwork.tags.palette] +
    profile.subject[artwork.tags.subject] +
    profile.mood[artwork.tags.mood] +
    profile.medium[artwork.tags.medium] * 0.5;

  if (bias?.temperature === -1 && artwork.tags.palette === 'cool') score += 3;
  if (bias?.temperature === -1 && artwork.tags.palette === 'warm') score -= 3;
  if (bias?.temperature === 1 && artwork.tags.palette === 'warm') score += 3;
  if (bias?.temperature === 1 && artwork.tags.palette === 'cool') score -= 3;

  return score;
}

function tagDistance(a: Artwork, b: Artwork): number {
  let d = 0;
  if (a.tags.palette !== b.tags.palette) d += 1;
  if (a.tags.subject !== b.tags.subject) d += 1;
  if (a.tags.mood !== b.tags.mood) d += 1;
  if (a.tags.medium !== b.tags.medium) d += 1;
  if (a.orientation !== b.orientation) d += 1;
  return d;
}

export function matchesFilters(
  artwork: Artwork,
  orientation: OrientationFilter,
  priceTier: PriceTierFilter,
): boolean {
  if (orientation !== 'all' && artwork.orientation !== orientation) return false;
  if (priceTier !== 'all' && artwork.priceTier !== priceTier) return false;
  return true;
}

function weightedPick(candidates: Artwork[], profile: TasteProfile, exclude: Set<string>): Artwork {
  const pool = candidates.filter((a) => !exclude.has(a.id));
  const usable = pool.length > 0 ? pool : candidates;

  // Softmax-ish weighted sample biased toward higher taste scores, with a
  // floor so low-scoring pieces still have a shot (keeps results varied).
  const scores = usable.map((a) => Math.exp(scoreArtwork(a, profile) * 0.6));
  const total = scores.reduce((s, v) => s + v, 0);
  let r = Math.random() * total;
  for (let i = 0; i < usable.length; i++) {
    r -= scores[i];
    if (r <= 0) return usable[i];
  }
  return usable[usable.length - 1];
}

export interface PairingState {
  shown: Set<string>;
}

const EARLY_ROUNDS = 6;

/**
 * Picks the next challenger to slot in opposite the reigning champion.
 * Early rounds favor pieces tag-different from the champion (fast
 * exploration); later rounds bias toward the emerging taste profile
 * (convergence) using a weighted random pick so it doesn't feel robotic.
 */
export function pickChallenger(
  pool: Artwork[],
  champion: Artwork,
  round: number,
  profile: TasteProfile,
  state: PairingState,
): Artwork {
  const candidates = pool.filter((a) => a.id !== champion.id);
  if (candidates.length === 0) return champion;

  if (round <= EARLY_ROUNDS) {
    const unseen = candidates.filter((a) => !state.shown.has(a.id));
    const fromPool = unseen.length > 0 ? unseen : candidates;
    let best = fromPool[0];
    let bestDist = -1;
    for (const c of fromPool) {
      const d = tagDistance(c, champion) + Math.random() * 0.5;
      if (d > bestDist) {
        bestDist = d;
        best = c;
      }
    }
    state.shown.add(best.id);
    return best;
  }

  const picked = weightedPick(candidates, profile, state.shown);
  state.shown.add(picked.id);
  return picked;
}

/** Picks two starting pieces that are tag-different from each other. */
export function pickOpeningPair(pool: Artwork[]): [Artwork, Artwork] {
  const a = pool[Math.floor(Math.random() * pool.length)];
  let best = pool[0];
  let bestDist = -1;
  for (const c of pool) {
    if (c.id === a.id) continue;
    const d = tagDistance(a, c) + Math.random() * 0.5;
    if (d > bestDist) {
      bestDist = d;
      best = c;
    }
  }
  return [a, best];
}

const SUBJECT_LABEL: Record<Subject, string> = {
  landscape: 'landscapes',
  portrait: 'portraits',
  abstract: 'abstract pieces',
  photography: 'photography',
  'still-life': 'still lifes',
};

const PALETTE_LABEL: Record<ColorPalette, string> = {
  warm: 'warm-toned',
  cool: 'cool-toned',
  neutral: 'neutral-toned',
  bold: 'boldly coloured',
};

const MOOD_LABEL: Record<Mood, string> = {
  calm: 'calm',
  energetic: 'energetic',
};

function topKey<K extends string>(record: Record<K, number>): K {
  return (Object.entries(record) as [K, number][]).sort((a, b) => b[1] - a[1])[0][0];
}

/** Produces the human-readable taste summary shown on the results screen. */
export function summarizeTaste(profile: TasteProfile): string {
  const palette = topKey(profile.palette);
  const subject = topKey(profile.subject);
  const mood = topKey(profile.mood);
  return `You lean toward ${PALETTE_LABEL[palette]} ${SUBJECT_LABEL[subject]} with a ${MOOD_LABEL[mood]} mood.`;
}
