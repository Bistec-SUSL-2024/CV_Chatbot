import React from 'react';

interface ChatMessageProps {
  text: string;
  isUser: boolean;
}

export function ChatMessage({ text, isUser }: ChatMessageProps) {
  return (
    <div className={`rounded-lg p-3 mb-3 ${
      isUser 
        ? 'bg-amber-100 text-left' 
        : 'bg-amber-50 text-right'
    }`}>
      <span className="font-bold">
        {isUser ? '❓ You: ' : '🤖 Bot: '}
      </span>
      {text}
    </div>
  );
}

