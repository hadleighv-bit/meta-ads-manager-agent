import { motion } from 'framer-motion';
import type { Artwork } from '../types';

export default function ArtistSheet({
  artwork,
  worksByArtist,
  onClose,
}: {
  artwork: Artwork;
  worksByArtist: Artwork[];
  onClose: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40" onClick={onClose}>
      <motion.div
        initial={{ y: '100%' }}
        animate={{ y: 0 }}
        exit={{ y: '100%' }}
        transition={{ type: 'spring', stiffness: 320, damping: 32 }}
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-md rounded-t-2xl bg-paper p-6 pb-9"
      >
        <div className="mx-auto mb-5 h-1 w-10 rounded-full bg-stone-light" />
        <p className="text-xs font-medium tracking-wide text-stone uppercase">Artist</p>
        <h3 className="mt-1 font-serif text-2xl font-medium text-ink">{artwork.artistName}</h3>
        <p className="mt-3 text-sm leading-relaxed text-stone">{artwork.artistBio}</p>
        <p className="mt-4 text-xs text-stone">
          {worksByArtist.length} piece{worksByArtist.length === 1 ? '' : 's'} in this collection
        </p>
        <button
          onClick={onClose}
          className="mt-6 w-full rounded-full border border-stone-light px-6 py-3 text-sm font-medium text-ink"
        >
          Close
        </button>
      </motion.div>
    </div>
  );
}
