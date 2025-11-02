"use client";

import { useState, useRef, useEffect } from "react";

interface Message {
  id: number;
  text: string;
  isBot: boolean;
  timestamp: Date;
}

export default function HomePage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Salut moi c'est Koffi, on fait quoi aujourd'hui ?",
      isBot: true,
      timestamp: new Date(),
    }
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll vers le dernier message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async () => {
    if (inputValue.trim() && !isLoading) {
      const userMessage: Message = {
        id: Date.now(),
        text: inputValue.trim(),
        isBot: false,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, userMessage]);
      setIsLoading(true);
      setInputValue("");

      try {
        // Appel à votre API Next.js qui communique avec l'ADK
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            messages: [
              {
                role: "user",
                content: inputValue.trim()
              }
            ]
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Adapter selon la structure de réponse de votre ADK
        const botResponse = data.result || data.response || data.answer ||
          "Désolé, je n'ai pas pu traiter votre demande.";

        const botMessage: Message = {
          id: Date.now() + 1,
          text: botResponse,
          isBot: true,
          timestamp: new Date(),
        };

        setMessages(prev => [...prev, botMessage]);

      } catch (error) {
        console.error("Erreur:", error);
        const errorMessage: Message = {
          id: Date.now() + 1,
          text: "Désolé, une erreur s'est produite. Vérifiez que votre serveur ADK est démarré sur localhost:8000",
          isBot: true,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: 1,
        text: "Salut moi c'est Koffi, on fait quoi aujourd'hui ?",
        isBot: true,
        timestamp: new Date(),
      }
    ]);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white flex flex-col">
      {/* Header amélioré */}
      <div className="p-6 border-b border-gray-800 bg-gray-900/80 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
              KOFFI
            </h1>
            <p className="text-gray-400 text-sm">Assistant spécialisé en recherche internet</p>
          </div>
          {messages.length > 1 && (
            <button
              onClick={clearChat}
              className="px-4 py-2 text-sm bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
            >
              Nouvelle discussion
            </button>
          )}
        </div>
      </div>

      {/* Chat Area améliorée */}
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full px-6">
        {/* Messages avec scroll */}
        <div className="flex-1 overflow-y-auto py-8">
          <div className="space-y-6 max-w-2xl mx-auto w-full">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.isBot ? "justify-start" : "justify-end"}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${message.isBot
                      ? "bg-gray-800/80 border border-gray-700 text-white"
                      : "bg-gradient-to-r from-blue-500 to-purple-600 text-white"
                    } shadow-lg backdrop-blur-sm`}
                >
                  <div className="whitespace-pre-wrap">{message.text}</div>
                  <div className={`text-xs mt-2 ${message.isBot ? "text-gray-400" : "text-blue-200"
                    }`}>
                    {message.timestamp.toLocaleTimeString("fr-FR", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-800/80 border border-gray-700 text-white px-4 py-3 rounded-2xl shadow-lg backdrop-blur-sm">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                    </div>
                    <span className="text-sm text-gray-400">Koffi réfléchit...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area améliorée */}
        <div className="pb-6 pt-4">
          <div className="relative max-w-2xl mx-auto">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Posez votre question à Koffi..."
              disabled={isLoading}
              className="w-full px-6 py-4 bg-gray-800/80 border border-gray-700 rounded-full text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-16 disabled:opacity-50 backdrop-blur-sm shadow-lg"
            />
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !inputValue.trim()}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 p-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-full hover:from-blue-600 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                />
              </svg>
            </button>
          </div>

          {/* Tips */}
          <div className="text-center mt-4">
            <p className="text-gray-500 text-sm">
              Exemple : "Quel est le prix de l'iPhone 15 ?" ou "Qui a gagné la dernière coupe du monde ?"
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center pb-4 border-t border-gray-800 pt-4">
          <p className="text-gray-500 text-sm">Powered by KOFFI ADK</p>
        </div>
      </div>
    </main>
  );
}