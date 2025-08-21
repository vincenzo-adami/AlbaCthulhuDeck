export interface GameState {
  gm: string | null;
  decks: Map<string, string[]>;
  discards: Map<string, string[]>;
}

export const state: GameState = {
  gm: null,
  decks: new Map(),
  discards: new Map()
};
