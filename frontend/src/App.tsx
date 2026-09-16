import React, { useEffect } from 'react';
import { Navbar } from './components/layout/Navbar';
import { Sidebar } from './components/layout/Sidebar';
import { ChatWindow } from './components/chat/ChatWindow';
import { CitationDrawer } from './components/chat/CitationDrawer';
import { PlanReviewView } from './components/academic/PlanReviewView';
import { CalculatorView } from './components/engineering/CalculatorView';
import { ArchitectureView } from './components/diagrams/ArchitectureView';
import { MemoryManagerView } from './components/memory/MemoryManagerView';
import { useAppStore } from './stores/useAppStore';
import { api } from './services/api';

export const App: React.FC = () => {
  const { activeTab, setConversations } = useAppStore();

  useEffect(() => {
    const loadConversations = async () => {
      try {
        const convs = await api.getConversations();
        setConversations(convs);
      } catch (err) {
        console.warn('Backend not yet reachable or empty conversations:', err);
      }
    };
    loadConversations();
  }, [setConversations]);

  return (
    <div className="min-h-screen bg-surface text-slate-100 flex flex-col font-sans selection:bg-brand-500 selection:text-white antialiased">
      {/* Platform Navigation Header */}
      <Navbar />

      {/* Main Workspace Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Navigation & Agent Persona Sidebar */}
        <Sidebar />

        {/* Central Workspace Area */}
        <main className="flex-1 flex flex-col overflow-hidden bg-surface relative">
          {activeTab === 'chat' && <ChatWindow />}
          {activeTab === 'plan_reviewer' && <PlanReviewView />}
          {activeTab === 'calculator' && <CalculatorView />}
          {activeTab === 'architecture' && <ArchitectureView />}
          {activeTab === 'memory' && <MemoryManagerView />}
        </main>

        {/* Slide-in Grounding / Citations Evidence Drawer */}
        <CitationDrawer />
      </div>
    </div>
  );
};

export default App;
