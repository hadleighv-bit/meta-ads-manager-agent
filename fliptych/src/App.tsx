import { useRef, useState } from 'react';
import SetupScreen from './components/SetupScreen';
import PlayScreen from './components/PlayScreen';
import ResultsScreen from './components/ResultsScreen';
import { ARTWORKS } from './data/artworks';
import {
  createTasteProfile,
  matchesFilters,
  pickChallenger,
  pickOpeningPair,
  updateTasteProfile,
  type PairingState,
  type TasteProfile,
} from './lib/tasteEngine';
import type { Artwork, OrientationFilter, PriceTierFilter } from './types';

const TOTAL_ROUNDS = 20;

type Screen = 'setup' | 'play' | 'results';

interface PlayState {
  left: Artwork;
  right: Artwork;
  round: number;
  profile: TasteProfile;
  pool: Artwork[];
}

function buildPool(orientation: OrientationFilter, priceTier: PriceTierFilter): Artwork[] {
  const filtered = ARTWORKS.filter((a) => matchesFilters(a, orientation, priceTier));
  return filtered.length >= 8 ? filtered : ARTWORKS;
}

export default function App() {
  const [screen, setScreen] = useState<Screen>('setup');
  const [play, setPlay] = useState<PlayState | null>(null);
  const [champion, setChampion] = useState<Artwork | null>(null);
  const [resultProfile, setResultProfile] = useState<TasteProfile>(createTasteProfile());
  const pairingState = useRef<PairingState>({ shown: new Set() });

  const handleStart = (orientation: OrientationFilter, priceTier: PriceTierFilter) => {
    const pool = buildPool(orientation, priceTier);
    const [left, right] = pickOpeningPair(pool);
    pairingState.current = { shown: new Set([left.id, right.id]) };
    setPlay({ left, right, round: 1, profile: createTasteProfile(), pool });
    setChampion(null);
    setScreen('play');
  };

  const handlePick = (side: 'left' | 'right') => {
    if (!play) return;
    const winner = side === 'left' ? play.left : play.right;
    const loser = side === 'left' ? play.right : play.left;
    const nextProfile = updateTasteProfile(play.profile, winner, loser);

    if (play.round >= TOTAL_ROUNDS) {
      setChampion(winner);
      setResultProfile(nextProfile);
      setScreen('results');
      return;
    }

    const nextRound = play.round + 1;
    const challenger = pickChallenger(play.pool, winner, nextRound, nextProfile, pairingState.current);

    setPlay({
      left: side === 'left' ? winner : challenger,
      right: side === 'left' ? challenger : winner,
      round: nextRound,
      profile: nextProfile,
      pool: play.pool,
    });
  };

  const handlePlayAgain = () => {
    setScreen('setup');
    setPlay(null);
    setChampion(null);
  };

  if (screen === 'setup') {
    return <SetupScreen onStart={handleStart} />;
  }

  if (screen === 'play' && play) {
    return (
      <PlayScreen
        left={play.left}
        right={play.right}
        round={play.round}
        total={TOTAL_ROUNDS}
        onPick={handlePick}
      />
    );
  }

  if (screen === 'results' && champion) {
    return (
      <ResultsScreen
        champion={champion}
        catalog={ARTWORKS}
        profile={resultProfile}
        onPlayAgain={handlePlayAgain}
      />
    );
  }

  return null;
}
