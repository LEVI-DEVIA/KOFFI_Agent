"use client";

import { useState, useRef, useEffect } from "react";
import { useVoiceRecording } from "../hooks/useVoiceRecording";

interface Message {
  id: number;
  text: string;
  isBot: boolean;
  timestamp: Date;
  type?: "text" | "audio";
  audioUrl?: string;
}

export default function HomePage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Salut moi c'est Koffi, on fait quoi aujourd'hui ?",
      isBot: true,
      timestamp: new Date(),
      type: "text"
    }
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Générer un ID de session unique au chargement
  useEffect(() => {
    const storedSessionId = localStorage.getItem("koffi-session-id");
    if (storedSessionId) {
      setSessionId(storedSessionId);
    } else {
      const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      setSessionId(newSessionId);
      localStorage.setItem("koffi-session-id", newSessionId);
    }
  }, []);

  const {
    isRecording,
    isProcessing,
    startRecording,
    stopRecording,
    sendTextMessage,
    playAudio,
    textToSpeech,
  } = useVoiceRecording();

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
            "x-session-id": sessionId, // Envoyer l'ID de session
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
          type: "text"
        };

        setMessages(prev => [...prev, botMessage]);

      } catch (error) {
        console.error("Erreur:", error);
        const errorMessage: Message = {
          id: Date.now() + 1,
          text: "Désolé, une erreur s'est produite. Vérifiez que votre serveur ADK est démarré sur localhost:8000",
          isBot: true,
          timestamp: new Date(),
          type: "text"
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

  const handleVoiceRecording = async () => {
    if (isRecording) {
      try {
        const transcribedText = await stopRecording();

        // Ajouter le message vocal de l'utilisateur avec le texte transcrit
        const userMessage: Message = {
          id: Date.now(),
          text: `🎤 "${transcribedText}"`,
          isBot: false,
          timestamp: new Date(),
          type: "audio"
        };

        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);

        // Envoyer le texte transcrit au backend
        const response = await sendTextMessage(transcribedText);

        const botMessage: Message = {
          id: Date.now() + 1,
          text: response.result,
          isBot: true,
          timestamp: new Date(),
          type: response.type as "text" | "audio",
          audioUrl: response.audioUrl
        };

        setMessages(prev => [...prev, botMessage]);

        // La réponse audio est automatiquement jouée par le TTS

      } catch (error) {
        console.error("Erreur vocal:", error);
        const errorMessage: Message = {
          id: Date.now() + 1,
          text: `Erreur lors du traitement vocal: ${error instanceof Error ? error.message : 'Erreur inconnue'}`,
          isBot: true,
          timestamp: new Date(),
          type: "text"
        };
        setMessages(prev => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    } else {
      try {
        await startRecording();
      } catch (error) {
        console.error("Erreur microphone:", error);
        alert(`Erreur: ${error instanceof Error ? error.message : 'Impossible de démarrer la reconnaissance vocale'}`);
      }
    }
  };

  const clearChat = () => {
    // Générer un nouvel ID de session
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);
    localStorage.setItem("koffi-session-id", newSessionId);

    // Réinitialiser les messages
    setMessages([
      {
        id: 1,
        text: "Salut moi c'est Koffi, on fait quoi aujourd'hui ?",
        isBot: true,
        timestamp: new Date(),
        type: "text"
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
            <p className="text-gray-400 text-sm">Ton partenaire de la life 😎 </p>
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

                  {/* Bouton de lecture pour les messages audio */}
                  {message.type === "audio" && message.audioUrl && (
                    <button
                      onClick={() => playAudio(message.audioUrl!)}
                      className="mt-2 flex items-center space-x-2 text-sm opacity-80 hover:opacity-100 transition-opacity"
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M8 5v14l11-7z" />
                      </svg>
                      <span>Écouter la réponse</span>
                    </button>
                  )}

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
              className="w-full px-6 py-4 bg-gray-800/80 border border-gray-700 rounded-full text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-32 disabled:opacity-50 backdrop-blur-sm shadow-lg"
            />
            {/* Bouton microphone */}
            <button
              onClick={handleVoiceRecording}
              disabled={isLoading || isProcessing}
              className={`absolute right-16 top-1/2 transform -translate-y-1/2 p-3 rounded-full transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg ${isRecording
                ? "bg-red-500 hover:bg-red-600 animate-pulse"
                : "bg-gray-700 hover:bg-gray-600"
                } text-white`}
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
                  d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                />
              </svg>
            </button>

            {/* Bouton envoyer */}
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

          {/* Indicateur d'enregistrement */}
          {isRecording && (
            <div className="text-center mt-4">
              <div className="inline-flex items-center space-x-2 text-red-500">
                <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium">Enregistrement en cours... Cliquez à nouveau pour arrêter</span>
              </div>
            </div>
          )}

          {/* Indicateur de traitement */}
          {isProcessing && (
            <div className="text-center mt-4">
              <div className="inline-flex items-center space-x-2 text-blue-500">
                <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce"></div>
                <span className="text-sm font-medium">Traitement du message vocal...</span>
              </div>
            </div>
          )}

          {/* Tips */}
          {!isRecording && !isProcessing && (
            <div className="text-center mt-4">
              <p className="text-gray-500 text-sm">
                Tapez votre message ou utilisez le microphone pour parler à Koffi
              </p>
              <p className="text-gray-600 text-xs mt-1">
                Exemple : "Commande moi une pizza sur glovo." ou "Qui a gagné la dernière coupe du monde ?"
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center pb-4 border-t border-gray-800 pt-4">
          <p className="text-gray-500 text-sm">Powered by ASSALE YAO - AI ENGINEER</p>
        </div>
      </div>
    </main>
  );
}