import { create } from 'zustand';
import { AgentId, Conversation, Message, Citation } from '../types';

interface AppState {
  activeAgent: AgentId;
  activeTab: 'chat' | 'plan_reviewer' | 'calculator' | 'memory' | 'architecture';
  currentConversationId: string | null;
  conversations: Conversation[];
  messages: Message[];
  isStreaming: boolean;
  activeCitations: Citation[];
  isCitationDrawerOpen: boolean;

  setActiveAgent: (agent: AgentId) => void;
  setActiveTab: (tab: 'chat' | 'plan_reviewer' | 'calculator' | 'memory' | 'architecture') => void;
  setCurrentConversationId: (id: string | null) => void;
  setConversations: (conversations: Conversation[]) => void;
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  updateLastMessageDelta: (delta: string) => void;
  setIsStreaming: (streaming: boolean) => void;
  setActiveCitations: (citations: Citation[]) => void;
  toggleCitationDrawer: (open?: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeAgent: 'academic',
  activeTab: 'chat',
  currentConversationId: null,
  conversations: [],
  messages: [],
  isStreaming: false,
  activeCitations: [],
  isCitationDrawerOpen: false,

  setActiveAgent: (agent) => set({ activeAgent: agent }),
  setActiveTab: (tab) => set({ activeTab: tab }),
  setCurrentConversationId: (id) => set({ currentConversationId: id }),
  setConversations: (conversations) => set({ conversations }),
  setMessages: (messages) => set({ messages }),
  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),
  updateLastMessageDelta: (delta) =>
    set((state) => {
      const msgs = [...state.messages];
      if (msgs.length > 0) {
        const last = msgs[msgs.length - 1];
        if (last.role === 'assistant') {
          msgs[msgs.length - 1] = {
            ...last,
            content: last.content + delta,
            isStreaming: true,
          };
        }
      }
      return { messages: msgs };
    }),
  setIsStreaming: (isStreaming) =>
    set((state) => {
      const msgs = [...state.messages];
      if (!isStreaming && msgs.length > 0) {
        const last = msgs[msgs.length - 1];
        if (last.role === 'assistant') {
          msgs[msgs.length - 1] = { ...last, isStreaming: false };
        }
      }
      return { isStreaming, messages: msgs };
    }),
  setActiveCitations: (citations) => set({ activeCitations: citations }),
  toggleCitationDrawer: (open) =>
    set((state) => ({
      isCitationDrawerOpen: open !== undefined ? open : !state.isCitationDrawerOpen,
    })),
}));
