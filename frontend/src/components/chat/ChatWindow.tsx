import React, { useState, useRef, useEffect } from 'react';
import { useAppStore } from '../../stores/useAppStore';
import { MessageBubble } from './MessageBubble';
import { api } from '../../services/api';
import { Send, Sparkles, AlertCircle, RefreshCw } from 'lucide-react';
import { AgentId } from '../../types';

export const ChatWindow: React.FC = () => {
  const {
    activeAgent,
    currentConversationId,
    setCurrentConversationId,
    messages,
    setMessages,
    addMessage,
    updateLastMessageDelta,
    isStreaming,
    setIsStreaming,
    setActiveCitations,
  } = useAppStore();

  const [input, setInput] = useState('');
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestedPrompts: Record<AgentId, string[]> = {
    academic: [
      'What are the official rules for attendance condonation?',
      'Can you review my 6th semester plan for credit overload?',
      'What are the prerequisites for Machine Learning Systems (CS308)?',
    ],
    engineering: [
      'Design a modular monolith system architecture and render a Mermaid flowchart',
      'Calculate QPS and 3-year storage capacity for 100K DAU with 50 writes/day',
      'Generate a Mermaid ER diagram for a high-concurrency order processing engine',
    ],
    commerce: [
      'Explain unit economics formulas for CAC, LTV, and Payback Period',
      'How do I model gross margins and operating leverage for SaaS?',
    ],
    management: [
      'How do I structure Stream-aligned vs Platform teams using Team Topologies?',
      'How to resolve sprint spillover and improve velocity in Scrum?',
    ],
    law: [
      'What is the practical difference between MIT and AGPL v3 software licenses?',
      'What are the mandatory elements of an NDA confidentiality clause?',
    ],
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming]);

  const handleSend = async (contentToSend?: string) => {
    const text = (contentToSend || input).trim();
    if (!text || isStreaming) return;

    setError(null);
    setInput('');

    // 1. Ensure conversation exists
    let convId = currentConversationId;
    if (!convId) {
      try {
        const newConv = await api.createConversation(activeAgent, text.substring(0, 30));
        convId = newConv.id;
        setCurrentConversationId(convId);
      } catch (err: any) {
        setError(`Failed to initiate conversation: ${err.message}`);
        return;
      }
    }

    // 2. Append User Message
    const userMsg = {
      id: `user-${Date.now()}`,
      role: 'user' as const,
      content: text,
      created_at: new Date().toISOString(),
    };
    addMessage(userMsg);

    // 3. Append Initial Assistant Streaming Placeholder
    const assistantMsg = {
      id: `assistant-${Date.now()}`,
      role: 'assistant' as const,
      content: '',
      isStreaming: true,
      created_at: new Date().toISOString(),
    };
    addMessage(assistantMsg);
    setIsStreaming(true);

    // 4. Stream response from backend SSE
    await api.streamMessage(
      convId,
      text,
      (delta) => {
        updateLastMessageDelta(delta);
      },
      () => {
        setIsStreaming(false);
      },
      (err) => {
        setError(err.message || 'Error occurred during generation.');
        setIsStreaming(false);
      }
    );
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex-1 h-[calc(100vh-4rem)] flex flex-col justify-between overflow-hidden relative radial-glow">
      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center max-w-xl mx-auto space-y-6">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-600/30 to-indigo-500/30 border border-brand-500/30 flex items-center justify-center shadow-glow">
              <Sparkles className="w-8 h-8 text-brand-400" />
            </div>
            <div className="space-y-2">
              <h2 className="text-2xl font-bold tracking-tight text-white">
                How can MANABI assist you today?
              </h2>
              <p className="text-sm text-slate-400">
                Engage with authoritative multi-domain agents backed by LangGraph workflows, deterministic math calculators, and pgvector RAG.
              </p>
            </div>

            {/* Suggested Prompts Grid */}
            <div className="w-full space-y-2 pt-2">
              <span className="text-xs uppercase font-semibold tracking-wider text-slate-500 block">
                Suggested questions for {activeAgent.toUpperCase()}:
              </span>
              <div className="grid gap-2">
                {suggestedPrompts[activeAgent]?.map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(prompt)}
                    className="w-full text-left p-3 rounded-xl border border-white/5 bg-surface-raised/50 hover:bg-white/10 hover:border-brand-500/40 transition text-xs text-slate-300 hover:text-white flex items-center justify-between"
                  >
                    <span>{prompt}</span>
                    <Sparkles className="w-3.5 h-3.5 text-brand-400 shrink-0 ml-2" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.map((m) => (
              <MessageBubble key={m.id} message={m} />
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Box Area */}
      <div className="p-4 border-t border-border/80 bg-surface/80 backdrop-blur-xl">
        <div className="max-w-4xl mx-auto space-y-2">
          {error && (
            <div className="flex items-center gap-2 p-2.5 rounded-lg bg-red-950/50 border border-red-800/50 text-red-300 text-xs">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="relative rounded-2xl glass-input flex items-end p-2 gap-2 shadow-lg">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={`Message ${activeAgent} advisor... (Press Enter to send)`}
              rows={1}
              className="flex-1 bg-transparent resize-none text-sm text-white placeholder-slate-500 px-3 py-2 focus:outline-none max-h-32 min-h-[2.5rem]"
            />
            <button
              onClick={() => handleSend()}
              disabled={!input.trim() || isStreaming}
              className="p-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 disabled:opacity-40 disabled:hover:bg-brand-600 text-white transition active:scale-95 shadow-glow shrink-0"
            >
              {isStreaming ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </div>
          <div className="flex items-center justify-between px-2 text-[11px] text-slate-500">
            <span>Powered by Model Gateway (Gemini / OpenAI / Ollama)</span>
            <span>Deterministic arithmetic & pgvector RAG enabled</span>
          </div>
        </div>
      </div>
    </div>
  );
};
