import { getPlaceholderStyle } from '../lib/placeholder';
import type { Artwork } from '../types';

export default function ArtworkVisual({
  artwork,
  className = '',
}: {
  artwork: Artwork;
  className?: string;
}) {
  if (artwork.imageUrl) {
    return (
      <img
        src={artwork.imageUrl}
        alt={artwork.title}
        className={`h-full w-full object-cover ${className}`}
        draggable={false}
      />
    );
  }
  return (
    <div
      className={`h-full w-full ${className}`}
      style={getPlaceholderStyle(artwork)}
      aria-label={artwork.title}
      role="img"
    />
  );
}
