/**
 * Core data schema for the Fliptych catalogue.
 *
 * The mock catalogue (src/data/artworks.ts) is a plain Artwork[] array.
 * To go live with a real catalogue, replace the contents of that file
 * (or point ARTWORKS at a fetched JSON payload of the same shape) —
 * nothing else in the app needs to change.
 */

export type Orientation = 'portrait' | 'landscape' | 'square';

/** Setup-screen size preference. 'all' = "show me everything". */
export type OrientationFilter = Orientation | 'all';

export type ColorPalette = 'warm' | 'cool' | 'neutral' | 'bold';

export type Subject =
  | 'landscape'
  | 'portrait'
  | 'abstract'
  | 'photography'
  | 'still-life';

export type Mood = 'calm' | 'energetic';

export type Medium =
  | 'oil'
  | 'acrylic'
  | 'watercolor'
  | 'photography'
  | 'digital'
  | 'mixed-media'
  | 'ink';

/** Setup-screen price preference. 'all' = no price filter. */
export type PriceTier = '$' | '$$' | '$$$';
export type PriceTierFilter = PriceTier | 'all';

/** Hidden tags used by the taste engine. Never shown to the player. */
export interface ArtworkTags {
  palette: ColorPalette;
  subject: Subject;
  mood: Mood;
  medium: Medium;
}

export interface Artwork {
  id: string;
  title: string;
  artistName: string;
  /** Short placeholder bio shown on the artist card. */
  artistBio: string;
  /**
   * Real catalogues should set a real photo URL here. Leave null to fall
   * back to a generated abstract gradient placeholder (see lib/placeholder.ts).
   */
  imageUrl: string | null;
  /** Price in whole USD. */
  price: number;
  priceTier: PriceTier;
  orientation: Orientation;
  tags: ArtworkTags;
}
