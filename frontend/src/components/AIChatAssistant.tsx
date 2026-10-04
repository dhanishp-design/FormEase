import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Sparkles,
  Bot,
  User,
  Loader2
} from 'lucide-react';
import type { ChatMessage, Language } from '../types';
import { sendChatMessage } from '../services/api';

interface AIChatAssistantProps {
  formTitle: string;
  selectedFieldId: string | null;
  language: Language;
}

export const AIChatAssistant: React.FC<AIChatAssistantProps> = ({
  formTitle,
  selectedFieldId,
  language,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'init-msg',
      role: 'assistant',
      content:
        language === 'mr'
          ? 'नमस्कार! मी FormEase AI सहाय्यक आहे. या अर्जातील नियमांविषयी किंवा रकान्यांविषयी काहीही विचारा.'
          : language === 'hi'
          ? 'नमस्ते! मैं FormEase AI सहायक हूँ। इस फॉर्म या किसी भी फ़ील्ड के बारे में बेझिझक पूछें।'
          : "Hello! I am your FormEase assistant. Ask me anything about this application form, terminology, or requirements.",
      timestamp: 'Just now',
    },
  ]);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const suggestedQuestions = {
    en: [
      'What does Domicile mean?',
      'What is an IFSC code?',
      'Which fields are mandatory?',
      'Permanent vs current address?',
    ],
    hi: [
      'अधिवास (Domicile) का क्या मतलब है?',
      'IFSC कोड क्या होता है?',
      'कौन से फ़ील्ड अनिवार्य हैं?',
      'स्थायी और वर्तमान पते में क्या अंतर है?',
    ],
    mr: [
      'अधिवास (Domicile) म्हणजे काय?',
      'IFSC कोड काय असतो?',
      'कोणते रकाने अनिवार्य आहेत?',
      'कायमचा आणि चालू पत्त्यात काय फरक आहे?',
    ],
  }[language];

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: 'smooth',
    });
  }, [messages, isTyping]);

  const handleSend = async (textToSend?: string) => {
    const text = textToSend || inputMessage;
    if (!text.trim() || isTyping) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text.trim(),
      timestamp: 'Just now',
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setIsTyping(true);

    try {
      const historyPayload = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const response = await sendChatMessage(
        text.trim(),
        formTitle,
        selectedFieldId || undefined,
        language,
        historyPayload
      );

      const aiMsg: ChatMessage = {
        id: `ai-${Date.now()}`,
        role: 'assistant',
        content: response.reply,
        timestamp: 'Just now',
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      console.error('Chat error:', err);
      const errorMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        role: 'assistant',
        content: "I couldn't fetch an answer right now. Please verify with the official form instructions.",
        timestamp: 'Just now',
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-xs">
      
      {/* Header */}
      <div className="p-3.5 border-b border-slate-100 bg-slate-50/60 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-blue-600 text-white flex items-center justify-center shadow-xs">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-bold text-slate-800">FormEase AI Assistant</div>
            <div className="text-[10px] text-slate-400">Grounded in uploaded document context</div>
          </div>
        </div>

        <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
          Live Assistant
        </span>
      </div>

      {/* Messages Scroll Area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3.5 text-xs">
        {messages.map((msg) => {
          const isUser = msg.role === 'user';

          return (
            <div
              key={msg.id}
              className={`flex items-start gap-2.5 ${isUser ? 'flex-row-reverse' : ''}`}
            >
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 ${
                  isUser
                    ? 'bg-slate-800 text-white text-[10px] font-bold'
                    : 'bg-blue-600 text-white'
                }`}
              >
                {isUser ? <User className="w-3.5 h-3.5" /> : <Sparkles className="w-3.5 h-3.5" />}
              </div>

              <div
                className={`max-w-[85%] p-3 rounded-2xl leading-relaxed ${
                  isUser
                    ? 'bg-blue-600 text-white rounded-tr-none'
                    : 'bg-slate-100 text-slate-800 rounded-tl-none border border-slate-200/60'
                }`}
              >
                {msg.content}
              </div>
            </div>
          );
        })}

        {isTyping && (
          <div className="flex items-center gap-2 text-slate-400 text-xs italic py-1">
            <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-600" />
            <span>FormEase is thinking...</span>
          </div>
        )}
      </div>

      {/* Suggested Prompt Chips */}
      <div className="px-3 py-2 bg-slate-50/70 border-t border-slate-100 flex items-center gap-1.5 overflow-x-auto text-[11px] no-scrollbar">
        <span className="text-[10px] font-semibold text-slate-400 shrink-0">Ask:</span>
        {suggestedQuestions.map((q) => (
          <button
            key={q}
            onClick={() => handleSend(q)}
            className="px-2.5 py-1 rounded-full bg-white hover:bg-blue-50 border border-slate-200 hover:border-blue-300 text-slate-700 hover:text-blue-700 whitespace-nowrap transition-all shadow-2xs shrink-0 cursor-pointer"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Chat Input Bar */}
      <div className="p-3 border-t border-slate-200 bg-white">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            placeholder={
              language === 'mr'
                ? 'या अर्जाबद्दल काहीही विचारा...'
                : language === 'hi'
                ? 'इस फॉर्म के बारे में कुछ भी पूछें...'
                : 'Ask anything about this form...'
            }
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            className="flex-1 px-3.5 py-2 rounded-xl border border-slate-200 bg-slate-50 text-xs text-slate-800 placeholder:text-slate-400 focus:bg-white focus:outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || isTyping}
            className="p-2 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white transition-all cursor-pointer"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>

    </div>
  );
};
