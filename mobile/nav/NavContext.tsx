import React, { createContext, useCallback, useContext, useState } from 'react';

export type ScreenId = string;

type NavCtx = {
  screen: ScreenId;
  nav: (s: ScreenId) => void;
  back: () => void;
  setScreen: (s: ScreenId) => void;
  askOpen: boolean;
  setAskOpen: (v: boolean) => void;
  precision: 'exact' | 'approximate' | 'unknown';
  setPrecision: (p: 'exact' | 'approximate' | 'unknown') => void;
};

const Ctx = createContext<NavCtx | null>(null);

export const NavProvider = ({ start = 'today', children }: { start?: ScreenId; children: React.ReactNode }) => {
  const [screen, setScreen] = useState<ScreenId>(start);
  const [history, setHistory] = useState<ScreenId[]>([]);
  const [askOpen, setAskOpen] = useState(false);
  const [precision, setPrecision] = useState<'exact' | 'approximate' | 'unknown'>('exact');

  const nav = (s: ScreenId) => { setHistory(h => [...h, screen]); setScreen(s); };
  const back = () => {
    setHistory(h => {
      if (!h.length) return h;
      setScreen(h[h.length - 1]);
      return h.slice(0, -1);
    });
  };

  return (
    <Ctx.Provider value={{ screen, nav, back, setScreen, askOpen, setAskOpen, precision, setPrecision }}>
      {children}
    </Ctx.Provider>
  );
};

export const useNav = () => {
  const v = useContext(Ctx);
  if (!v) throw new Error('useNav must be used inside NavProvider');
  return v;
};
