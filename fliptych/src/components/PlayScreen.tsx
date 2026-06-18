import { AnimatePresence, motion } from 'framer-motion';
import ArtworkVisual from './ArtworkVisual';
import type { Artwork } from '../types';

interface Props {
  left: Artwork;
  right: Artwork;
  round: number;
  total: number;
  onPick: (side: 'left' | 'right') => void;
}

const slotVariants = (side: 'left' | 'right') => ({
  initial: { opacity: 0, x: side === 'left' ? -60 : 60, scale: 0.96 },
  animate: { opacity: 1, x: 0, scale: 1 },
  exit: { opacity: 0, x: side === 'left' ? -90 : 90, scale: 0.94, transition: { duration: 0.22 } },
});

function Slot({
  artwork,
  side,
  onPick,
}: {
  artwork: Artwork;
  side: 'left' | 'right';
  onPick: () => void;
}) {
  return (
    <div className="relative h-1/2 w-full overflow-hidden md:h-full md:w-1/2">
      <AnimatePresence initial={false}>
        <motion.button
          key={artwork.id}
          onClick={onPick}
          variants={slotVariants(side)}
          initial="initial"
          animate="animate"
          exit="exit"
          transition={{ type: 'spring', stiffness: 280, damping: 28 }}
          className="absolute inset-0 h-full w-full cursor-pointer"
        >
          <ArtworkVisual artwork={artwork} />
          <div className="absolute inset-0 bg-gradient-to-t from-black/35 via-transparent to-transparent transition-opacity active:from-black/10" />
        </motion.button>
      </AnimatePresence>
    </div>
  );
}

export default function PlayScreen({ left, right, round, total, onPick }: Props) {
  return (
    <div className="relative flex h-svh w-full flex-col md:flex-row">
      <Slot artwork={left} side="left" onPick={() => onPick('left')} />
      <Slot artwork={right} side="right" onPick={() => onPick('right')} />

      <div className="pointer-events-none absolute top-0 left-1/2 z-10 flex -translate-x-1/2 flex-col items-center pt-4">
        <div className="rounded-full bg-paper/90 px-3.5 py-1 font-sans text-xs font-semibold tracking-wide text-ink shadow-sm backdrop-blur">
          {round} / {total}
        </div>
      </div>

      <div className="pointer-events-none absolute top-1/2 left-1/2 z-10 hidden h-10 w-px -translate-x-1/2 -translate-y-1/2 bg-paper/40 md:block" />
    </div>
  );
}
