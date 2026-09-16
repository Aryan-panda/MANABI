import React from 'react';
import { Message } from '../../types';
import { MermaidViewer } from '../diagrams/MermaidViewer';
import { Bot, User as UserIcon, BookOpen, Layers } from 'lucide-react';
import { useAppStore } from '../../stores/useAppStore';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const { toggleCitationDrawer, setActiveCitations } = useAppStore();

  // Parse out Mermaid blocks from content
  const renderMessageContent = (content: string) => {
    const parts: React.ReactNode[] = [];
    const mermaidRegex = /```mermaid\n([\s\S]*?)\n```/g;
    let lastIndex = 0;
    let match;

    while ((match = mermaidRegex.exec(content)) !== null) {
      if (match.index > lastIndex) {
        parts.push(
          <div
            key={`text-${lastIndex}`}
            className="whitespace-pre-wrap leading-relaxed"
          >
            {content.substring(lastIndex, match.index)}
          </div>
        );
      }
      const chartCode = match[1];
      parts.push(
        <MermaidViewer
          key={`mermaid-${match.index}`}
          chart={chartCode}
        />
      );
      lastIndex = mermaidRegex.lastIndex;
    }

    if (lastIndex < content.length) {
      parts.push(
        <div
          key={`text-${lastIndex}`}
          className="whitespace-pre-wrap leading-relaxed"
        >
          {content.substring(lastIndex)}
        </div>
      );
    }
    return parts;
  };

  return (
    <div className={`flex gap-3.5 my-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar Icon */}
      <div
        className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 shadow-md ${
          isUser
            ? 'bg-gradient-to-tr from-brand-600 to-indigo-500 text-white'
            : 'bg-surface-raised border border-white/10 text-brand-400'
        }`}
      >
        {isUser ? <UserIcon className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>

      {/* Bubble Box */}
      <div className={`max-w-3xl space-y-2 ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`p-4 rounded-2xl border text-sm markdown-body transition ${
            isUser
              ? 'bg-brand-600 text-white border-brand-500/50 shadow-glow rounded-tr-none'
              : 'glass-panel text-slate-200 border-white/10 rounded-tl-none'
          }`}
        >
          {renderMessageContent(message.content)}

          {message.isStreaming && (
            <span className="inline-block w-2 h-4 ml-1 bg-brand-400 animate-pulse align-middle" />
          )}
        </div>

        {/* Message Meta & Citations */}
        {!isUser && (
          <div className="flex items-center gap-2 px-1 text-[11px] text-slate-400 font-mono">
            {message.model && (
              <span className="px-1.5 py-0.5 rounded bg-white/5 border border-white/10">
                {message.model}
              </span>
            )}
            {message.citations && message.citations.length > 0 && (
              <button
                onClick={() => {
                  setActiveCitations(message.citations || []);
                  toggleCitationDrawer(true);
                }}
                className="flex items-center gap-1 text-indigo-400 hover:text-indigo-300 transition underline underline-offset-2 cursor-pointer"
              >
                <BookOpen className="w-3 h-3" />
                <span>{message.citations.length} Verified Sources</span>
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
