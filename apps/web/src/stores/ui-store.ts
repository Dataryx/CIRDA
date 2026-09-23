import { create } from 'zustand';
import type { GraphLayer } from '@/api/generated/schema.d';

interface UiState {
  sidebarCollapsed: boolean;
  graphLayer: GraphLayer;
  toggleSidebar: () => void;
  setGraphLayer: (layer: GraphLayer) => void;
}

export const useUiStore = create<UiState>((set) => ({
  sidebarCollapsed: false,
  graphLayer: 'all',
  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
  setGraphLayer: (graphLayer) => set({ graphLayer }),
}));
