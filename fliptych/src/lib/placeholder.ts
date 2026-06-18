import type { CSSProperties } from 'react';
import type { Artwork, ColorPalette, Mood } from '../types';

/**
 * Generates an abstract gradient/colour-block placeholder for artworks that
 * don't have a real imageUrl yet. Picks deterministically from a curated
 * set of stops per palette so pieces in the same palette still look
 * distinct, and varies the composition (radial vs. linear vs. blocky) by
 * mood so "energetic" pieces read busier than "calm" ones.
 */

const STOPS: Record<ColorPalette, string[][]> = {
  warm: [
    ['#F4A261', '#E76F51', '#C9402F'],
    ['#F2C57C', '#E08E45', '#A4462F'],
    ['#FFD6A5', '#FB8B24', '#D6411D'],
    ['#F6BD60', '#F28482', '#9B2915'],
  ],
  cool: [
    ['#A8DADC', '#457B9D', '#1D3557'],
    ['#90E0EF', '#0096C7', '#023E8A'],
    ['#CAF0F8', '#48CAE4', '#03045E'],
    ['#B8E0D2', '#4A7C6F', '#1B3A33'],
  ],
  neutral: [
    ['#E8E2D9', '#C9BFB1', '#8C8275'],
    ['#EDEAE4', '#BFB8AC', '#6F675C'],
    ['#DDD8CE', '#A9A097', '#5C564D'],
    ['#F1EDE6', '#D6CFC2', '#94897A'],
  ],
  bold: [
    ['#FF3366', '#3A0CA3', '#0B0014'],
    ['#FFBE0B', '#FB5607', '#8338EC'],
    ['#06D6A0', '#118AB2', '#073B4C'],
    ['#EF476F', '#FFD166', '#073B4C'],
  ],
};

function hash(id: string): number {
  let h = 0;
  for (let i = 0; i < id.length; i++) {
    h = (h * 31 + id.charCodeAt(i)) >>> 0;
  }
  return h;
}

function composition(mood: Mood, variantIndex: number): string {
  const angle = 35 + (variantIndex % 4) * 40;
  if (mood === 'energetic') {
    return `linear-gradient(${angle}deg, var(--c1) 0%, var(--c2) 45%, var(--c3) 100%)`;
  }
  return `radial-gradient(circle at ${30 + (variantIndex % 3) * 20}% ${
    25 + (variantIndex % 4) * 15
  }%, var(--c1) 0%, var(--c2) 55%, var(--c3) 100%)`;
}

export function getPlaceholderStyle(artwork: Artwork): CSSProperties {
  const palette = STOPS[artwork.tags.palette];
  const h = hash(artwork.id);
  const variant = palette[h % palette.length];
  const [c1, c2, c3] = variant;
  return {
    backgroundImage: composition(artwork.tags.mood, h),
    // @ts-expect-error custom properties
    '--c1': c1,
    '--c2': c2,
    '--c3': c3,
  };
}
