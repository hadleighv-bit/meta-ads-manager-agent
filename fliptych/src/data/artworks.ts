import type { Artwork, ColorPalette, Medium, Mood, Orientation, PriceTier, Subject } from '../types';

/**
 * Mock catalogue of ~40 placeholder artworks.
 *
 * This is the ONLY file you need to replace to go live with a real
 * catalogue of hundreds of pieces — keep the Artwork shape (see
 * src/types.ts) and everything downstream (taste engine, pairing,
 * results) works unchanged. Swap `imageUrl: null` for a real photo URL
 * once you have one; until then the app renders an abstract gradient
 * placeholder derived from the piece's tags.
 */

function priceFor(tier: PriceTier): number {
  switch (tier) {
    case '$':
      return 95 + Math.round(Math.random() * 55);
    case '$$':
      return 180 + Math.round(Math.random() * 140);
    case '$$$':
      return 380 + Math.round(Math.random() * 420);
  }
}

interface Seed {
  title: string;
  artistName: string;
  artistBio: string;
  orientation: Orientation;
  priceTier: PriceTier;
  palette: ColorPalette;
  subject: Subject;
  mood: Mood;
  medium: Medium;
}

const SEEDS: Seed[] = [
  { title: 'Low Tide, Amber Hour', artistName: 'Mireille Auclair', artistBio: 'Coastal painter working out of a converted boathouse in Brittany.', orientation: 'landscape', priceTier: '$$', palette: 'warm', subject: 'landscape', mood: 'calm', medium: 'oil' },
  { title: 'Quiet Pines', artistName: 'Soren Thale', artistBio: 'Norwegian landscape painter known for restrained, foggy palettes.', orientation: 'portrait', priceTier: '$', palette: 'cool', subject: 'landscape', mood: 'calm', medium: 'watercolor' },
  { title: 'Marigold Field, Noon', artistName: 'Priya Nandakumar', artistBio: 'Self-taught painter documenting the farmland of rural Karnataka.', orientation: 'landscape', priceTier: '$$', palette: 'warm', subject: 'landscape', mood: 'energetic', medium: 'acrylic' },
  { title: 'Glacier Light', artistName: 'Edda Magnusdottir', artistBio: 'Reykjavik-based artist painting Iceland\'s shifting ice fields.', orientation: 'landscape', priceTier: '$$$', palette: 'cool', subject: 'landscape', mood: 'calm', medium: 'oil' },
  { title: 'Dust Road, August', artistName: 'Walt Inniss', artistBio: 'Texas-born plein air painter chasing dry heat and long shadows.', orientation: 'landscape', priceTier: '$', palette: 'warm', subject: 'landscape', mood: 'calm', medium: 'oil' },
  { title: 'Canyon Static', artistName: 'Rosa Beltran', artistBio: 'Mixed-media artist layering pigment and sand from the Sonoran desert.', orientation: 'square', priceTier: '$$', palette: 'bold', subject: 'landscape', mood: 'energetic', medium: 'mixed-media' },

  { title: 'Portrait in Half Light', artistName: 'Janek Wos', artistBio: 'Krakow painter trained in classical chiaroscuro technique.', orientation: 'portrait', priceTier: '$$$', palette: 'neutral', subject: 'portrait', mood: 'calm', medium: 'oil' },
  { title: 'Sister, Looking Back', artistName: 'Adaeze Obi', artistBio: 'Lagos-based portraitist focused on intimate family studies.', orientation: 'portrait', priceTier: '$$', palette: 'warm', subject: 'portrait', mood: 'calm', medium: 'acrylic' },
  { title: 'Carnival Mask', artistName: 'Tomas Reyes', artistBio: 'Oaxacan muralist who brings street-festival colour into the studio.', orientation: 'portrait', priceTier: '$$', palette: 'bold', subject: 'portrait', mood: 'energetic', medium: 'acrylic' },
  { title: 'Self Portrait, Blue Room', artistName: 'Helene Druot', artistBio: 'Paris-trained painter exploring solitude through cool interiors.', orientation: 'portrait', priceTier: '$$$', palette: 'cool', subject: 'portrait', mood: 'calm', medium: 'oil' },
  { title: 'Untitled (Boxer)', artistName: 'Marcus Penny', artistBio: 'Detroit photographer documenting amateur boxing gyms since 2009.', orientation: 'square', priceTier: '$', palette: 'neutral', subject: 'portrait', mood: 'energetic', medium: 'photography' },
  { title: 'Bride, Unfinished', artistName: 'Yuki Hasegawa', artistBio: 'Kyoto ink painter reinterpreting traditional portraiture.', orientation: 'portrait', priceTier: '$$', palette: 'neutral', subject: 'portrait', mood: 'calm', medium: 'ink' },

  { title: 'Fracture No. 7', artistName: 'Bram Voskuijlen', artistBio: 'Rotterdam abstractionist working in hard-edged geometric forms.', orientation: 'square', priceTier: '$$', palette: 'bold', subject: 'abstract', mood: 'energetic', medium: 'acrylic' },
  { title: 'Sediment Study III', artistName: 'Nina Carrasco', artistBio: 'Santiago painter building texture from pumice and raw pigment.', orientation: 'square', priceTier: '$$$', palette: 'neutral', subject: 'abstract', mood: 'calm', medium: 'mixed-media' },
  { title: 'Held Breath', artistName: 'Iris Okonkwo', artistBio: 'Abstract painter exploring stillness through layered washes.', orientation: 'portrait', priceTier: '$$', palette: 'cool', subject: 'abstract', mood: 'calm', medium: 'watercolor' },
  { title: 'Static Bloom', artistName: 'Devon Marsh', artistBio: 'Chicago digital artist generating form from audio waveforms.', orientation: 'square', priceTier: '$', palette: 'bold', subject: 'abstract', mood: 'energetic', medium: 'digital' },
  { title: 'Ash and Ember', artistName: 'Faye Lindqvist', artistBio: 'Swedish painter working from controlled studio fires.', orientation: 'landscape', priceTier: '$$', palette: 'warm', subject: 'abstract', mood: 'energetic', medium: 'oil' },
  { title: 'Quiet Geometry', artistName: 'Sami Al-Rashid', artistBio: 'Amman-based artist drawing on Islamic geometric tradition.', orientation: 'square', priceTier: '$$$', palette: 'neutral', subject: 'abstract', mood: 'calm', medium: 'acrylic' },
  { title: 'Fault Line', artistName: 'Greta Holm', artistBio: 'Berlin artist mapping tectonic imagery onto canvas.', orientation: 'landscape', priceTier: '$', palette: 'bold', subject: 'abstract', mood: 'energetic', medium: 'mixed-media' },

  { title: 'Concrete Bloom', artistName: 'Theo Marchetti', artistBio: 'Milanese street photographer of plants reclaiming architecture.', orientation: 'portrait', priceTier: '$', palette: 'neutral', subject: 'photography', mood: 'calm', medium: 'photography' },
  { title: 'Night Bus, Seoul', artistName: 'Hana Cho', artistBio: 'Seoul photographer documenting the city after midnight.', orientation: 'landscape', priceTier: '$$', palette: 'cool', subject: 'photography', mood: 'energetic', medium: 'photography' },
  { title: 'Harbour Fog', artistName: 'Liam Doheny', artistBio: 'Cork-based maritime photographer shooting at first light.', orientation: 'landscape', priceTier: '$$', palette: 'cool', subject: 'photography', mood: 'calm', medium: 'photography' },
  { title: 'Neon Crosswalk', artistName: 'Carmen Iglesias', artistBio: 'Madrid street photographer obsessed with reflective surfaces.', orientation: 'portrait', priceTier: '$', palette: 'bold', subject: 'photography', mood: 'energetic', medium: 'photography' },
  { title: 'Dunes at Dusk', artistName: 'Khalid Mansour', artistBio: 'Dubai-based fine art photographer of the Empty Quarter.', orientation: 'landscape', priceTier: '$$$', palette: 'warm', subject: 'photography', mood: 'calm', medium: 'photography' },
  { title: 'Market Stall, Marrakech', artistName: 'Yasmine Idrissi', artistBio: 'Documentary photographer focused on North African markets.', orientation: 'square', priceTier: '$', palette: 'warm', subject: 'photography', mood: 'energetic', medium: 'photography' },

  { title: 'Lemons and Linen', artistName: 'Odile Fournier', artistBio: 'Provence-based still life painter trained in the Dutch masters.', orientation: 'square', priceTier: '$', palette: 'warm', subject: 'still-life', mood: 'calm', medium: 'oil' },
  { title: 'Glassware, Morning', artistName: 'Petra Vance', artistBio: 'London painter known for luminous studies of glass and light.', orientation: 'square', priceTier: '$$', palette: 'cool', subject: 'still-life', mood: 'calm', medium: 'watercolor' },
  { title: 'Spilled Ink Bottles', artistName: 'Renzo Calabria', artistBio: 'Florentine painter modernizing classical still life subjects.', orientation: 'square', priceTier: '$$', palette: 'bold', subject: 'still-life', mood: 'energetic', medium: 'acrylic' },
  { title: 'Dried Flowers, Late Fall', artistName: 'Margit Esser', artistBio: 'Vienna painter cataloguing the decay of cut flowers.', orientation: 'portrait', priceTier: '$$$', palette: 'neutral', subject: 'still-life', mood: 'calm', medium: 'oil' },
  { title: 'Kitchen Table, Sunday', artistName: 'Noah Fielding', artistBio: 'Vermont painter of domestic ritual and quiet mornings.', orientation: 'landscape', priceTier: '$', palette: 'warm', subject: 'still-life', mood: 'calm', medium: 'acrylic' },
  { title: 'Knife and Citrus', artistName: 'Beatriz Mota', artistBio: 'Sao Paulo painter bringing bold color to kitchen still lifes.', orientation: 'square', priceTier: '$$', palette: 'bold', subject: 'still-life', mood: 'energetic', medium: 'oil' },

  { title: 'Terraced Hills, Spring', artistName: 'Mei Lin Tan', artistBio: 'Guangxi-born painter of rice terraces and river valleys.', orientation: 'landscape', priceTier: '$$', palette: 'cool', subject: 'landscape', mood: 'calm', medium: 'watercolor' },
  { title: 'Wildfire Smoke, Ridgeline', artistName: 'Caleb Strand', artistBio: 'Montana painter capturing the changed light of fire season.', orientation: 'landscape', priceTier: '$$$', palette: 'bold', subject: 'landscape', mood: 'energetic', medium: 'oil' },
  { title: 'Subway Stranger', artistName: 'Renata Souza', artistBio: 'Rio-based painter of fleeting public moments.', orientation: 'portrait', priceTier: '$', palette: 'neutral', subject: 'portrait', mood: 'energetic', medium: 'digital' },
  { title: 'Old Friend, New Light', artistName: 'Daniel Achterberg', artistBio: 'Amsterdam painter revisiting old family photographs in oil.', orientation: 'portrait', priceTier: '$$', palette: 'warm', subject: 'portrait', mood: 'calm', medium: 'oil' },
  { title: 'Drift Pattern', artistName: 'Aino Salonen', artistBio: 'Helsinki textile-trained artist translating fabric patterns to canvas.', orientation: 'square', priceTier: '$$', palette: 'cool', subject: 'abstract', mood: 'energetic', medium: 'digital' },
  { title: 'Pressure Study', artistName: 'Quinn Albrecht', artistBio: 'Brooklyn artist working with industrial pigment and resin.', orientation: 'square', priceTier: '$$$', palette: 'bold', subject: 'abstract', mood: 'energetic', medium: 'mixed-media' },
  { title: 'Rooftops, Grey Morning', artistName: 'Pavel Sokolov', artistBio: 'Moscow photographer of pre-dawn city rooftops.', orientation: 'landscape', priceTier: '$', palette: 'neutral', subject: 'photography', mood: 'calm', medium: 'photography' },
  { title: 'Lanterns, Closing Time', artistName: 'Anh Nguyen', artistBio: 'Hanoi photographer documenting night markets.', orientation: 'portrait', priceTier: '$$', palette: 'warm', subject: 'photography', mood: 'energetic', medium: 'photography' },
  { title: 'Pear and Pewter', artistName: 'Ingrid Falk', artistBio: 'Stockholm painter of minimalist Nordic still lifes.', orientation: 'square', priceTier: '$$', palette: 'neutral', subject: 'still-life', mood: 'calm', medium: 'oil' },
  { title: 'Tide Pool Geometry', artistName: 'Owen Brandt', artistBio: 'Pacific Northwest painter studying coastal micro-patterns.', orientation: 'landscape', priceTier: '$$$', palette: 'cool', subject: 'abstract', mood: 'calm', medium: 'acrylic' },
];

function slugify(title: string): string {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

export const ARTWORKS: Artwork[] = SEEDS.map((seed, index) => ({
  id: `${slugify(seed.title)}-${index}`,
  title: seed.title,
  artistName: seed.artistName,
  artistBio: seed.artistBio,
  imageUrl: null,
  price: priceFor(seed.priceTier),
  priceTier: seed.priceTier,
  orientation: seed.orientation,
  tags: {
    palette: seed.palette,
    subject: seed.subject,
    mood: seed.mood,
    medium: seed.medium,
  },
}));
