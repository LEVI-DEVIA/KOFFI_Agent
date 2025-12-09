"use client";

import { useState, useRef, useEffect } from "react";
import { useVoiceRecording } from "../hooks/useVoiceRecording";
import { useTextToSpeech } from "../hooks/useTextToSpeech";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github-dark.css";
import "katex/dist/katex.min.css";
import CookieConsent from "../components/CookieConsent";

interface Message {
  id: number;
  text: string;
  isBot: boolean;
  timestamp: Date;
  type?: "text" | "audio";
  audioUrl?: string;
  wasVoiceQuestion?: boolean; // Pour savoir si c'était une réponse à une question vocale
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
  const [streamingMessage, setStreamingMessage] = useState<string>("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [lastMessageWasVoice, setLastMessageWasVoice] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    isRecording,
    isProcessing,
    startRecording,
    stopRecording,
    playAudio,
  } = useVoiceRecording();

  const { speak, stop: stopSpeaking, isSpeaking, listAvailableVoices } = useTextToSpeech();

  // Lister les voix disponibles au chargement (pour debug)
  useEffect(() => {
    // Attendre que les voix soient chargées
    const loadVoices = () => {
      if (window.speechSynthesis.getVoices().length > 0) {
        listAvailableVoices();
      }
    };

    // Les voix peuvent être chargées de manière asynchrone
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    // Essayer de charger immédiatement aussi
    loadVoices();
  }, [listAvailableVoices]);

  // Fonction pour nettoyer le texte avant la lecture audio
  const cleanTextForSpeech = (text: string): string => {
    return text
      .replace(/\*\*/g, '')  // Enlever les ** (gras)
      .replace(/\*/g, '')    // Enlever les * (italique)
      .replace(/#{1,6}\s/g, '')  // Enlever les # (titres)
      .replace(/`{1,3}[^`]*`{1,3}/g, 'code')  // Remplacer le code par "code"
      .replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1')  // Garder juste le texte des liens
      .replace(/>\s/g, '')  // Enlever les > (citations)
      .replace(/[-*+]\s/g, '')  // Enlever les puces de liste
      .replace(/\d+\.\s/g, '')  // Enlever les numéros de liste
      .replace(/\n{3,}/g, '\n\n')  // Réduire les sauts de ligne multiples
      .trim();
  };

  useEffect(() => {
    const storedSessionId = localStorage.getItem("koffi-session-id");
    if (storedSessionId) {
      setSessionId(storedSessionId);
    } else {
      const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
      setSessionId(newSessionId);
      localStorage.setItem("koffi-session-id", newSessionId);
    }
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingMessage, isLoading]);

  const handleSendMessage = async () => {
    if (inputValue.trim() && !isLoading) {
      // Arrêter toute lecture audio en cours
      stopSpeaking();

      const userMessage: Message = {
        id: Date.now(),
        text: inputValue.trim(),
        isBot: false,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, userMessage]);
      setIsLoading(true);  // Affiche "Koffi réfléchit..."
      setInputValue("");
      setStreamingMessage("");
      setIsStreaming(false);  // Pas encore en streaming
      setLastMessageWasVoice(false);  // Message texte, pas de TTS

      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "x-session-id": sessionId,
          },
          body: JSON.stringify({
            messages: [
              {
                role: "user",
                content: userMessage.text
              }
            ],
            stream: true
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          throw new Error("Impossible de lire le flux de réponse");
        }

        let fullResponse = "";
        let firstChunkReceived = false;

        while (true) {
          const { done, value } = await reader.read();

          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));

                if (data.type === 'content' && data.content) {
                  // Dès le premier chunk, on cache "Koffi réfléchit" et on active le streaming
                  if (!firstChunkReceived) {
                    setIsLoading(false);  // Cache "Koffi réfléchit..."
                    setIsStreaming(true);  // Active le mode streaming
                    firstChunkReceived = true;
                  }

                  fullResponse += data.content;
                  setStreamingMessage(fullResponse);

                } else if (data.type === 'end') {
                  setIsStreaming(false);
                  setIsLoading(false);

                  const botMessage: Message = {
                    id: Date.now() + 1,
                    text: fullResponse,
                    isBot: true,
                    timestamp: new Date(),
                    type: "text"
                  };

                  setMessages(prev => [...prev, botMessage]);
                  setStreamingMessage("");

                } else if (data.type === 'error') {
                  throw new Error(data.error);
                }
              } catch (e) {
                console.error("Erreur lors du parsing des données:", e);
              }
            }
          }
        }

      } catch (error) {
        console.error("Erreur:", error);
        setIsStreaming(false);
        setStreamingMessage("");
        setIsLoading(false);

        const errorMessage: Message = {
          id: Date.now() + 1,
          text: "Désolé, une erreur s'est produite. Vérifiez que votre serveur ADK est démarré sur localhost:8000",
          isBot: true,
          timestamp: new Date(),
          type: "text"
        };
        setMessages(prev => [...prev, errorMessage]);
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

        const userMessage: Message = {
          id: Date.now(),
          text: `🎤 "${transcribedText}"`,
          isBot: false,
          timestamp: new Date(),
          type: "audio"
        };

        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);  // Affiche "Koffi réfléchit..."
        setStreamingMessage("");
        setIsStreaming(false);  // Pas encore en streaming
        setLastMessageWasVoice(true);  // Message vocal, activer le TTS pour la réponse

        const response = await fetch("/api/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "x-session-id": sessionId,
          },
          body: JSON.stringify({
            messages: [
              {
                role: "user",
                content: transcribedText
              }
            ],
            stream: true
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          throw new Error("Impossible de lire le flux de réponse");
        }

        let fullResponse = "";
        let firstChunkReceived = false;

        while (true) {
          const { done, value } = await reader.read();

          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));

                if (data.type === 'content' && data.content) {
                  // Dès le premier chunk, on cache "Koffi réfléchit" et on active le streaming
                  if (!firstChunkReceived) {
                    setIsLoading(false);  // Cache "Koffi réfléchit..."
                    setIsStreaming(true);  // Active le mode streaming
                    firstChunkReceived = true;
                  }

                  fullResponse += data.content;
                  setStreamingMessage(fullResponse);

                } else if (data.type === 'end') {
                  setIsStreaming(false);
                  setIsLoading(false);

                  const botMessage: Message = {
                    id: Date.now() + 1,
                    text: fullResponse,
                    isBot: true,
                    timestamp: new Date(),
                    type: "text",
                    wasVoiceQuestion: true  // Marquer que c'était une réponse à une question vocale
                  };

                  setMessages(prev => [...prev, botMessage]);
                  setStreamingMessage("");

                  // Lire la réponse en audio puisque la question était vocale
                  if (fullResponse) {
                    const cleanText = cleanTextForSpeech(fullResponse);
                    console.log('🔊 Lecture audio automatique:', cleanText.substring(0, 100) + '...');
                    speak(cleanText);
                  }

                } else if (data.type === 'error') {
                  throw new Error(data.error);
                }
              } catch (e) {
                console.error("Erreur lors du parsing des données:", e);
              }
            }
          }
        }

      } catch (error) {
        console.error("Erreur vocal:", error);
        setIsStreaming(false);
        setStreamingMessage("");
        setIsLoading(false);

        const errorMessage: Message = {
          id: Date.now() + 1,
          text: `Erreur lors du traitement vocal: ${error instanceof Error ? error.message : 'Erreur inconnue'}`,
          isBot: true,
          timestamp: new Date(),
          type: "text"
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } else {
      try {
        // Arrêter toute lecture audio en cours avant de commencer l'enregistrement
        stopSpeaking();
        await startRecording();
      } catch (error) {
        console.error("Erreur microphone:", error);

        // Afficher un message d'erreur plus détaillé
        const errorMsg = error instanceof Error ? error.message : 'Impossible de démarrer la reconnaissance vocale';

        const errorMessage: Message = {
          id: Date.now(),
          text: `❌ ${errorMsg}`,
          isBot: true,
          timestamp: new Date(),
          type: "text"
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    }
  };

  const clearChat = () => {
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
    setSessionId(newSessionId);
    localStorage.setItem("koffi-session-id", newSessionId);

    setMessages([
      {
        id: 1,
        text: "Salut moi c'est Koffi, on fait quoi aujourd'hui ?",
        isBot: true,
        timestamp: new Date(),
        type: "text"
      }
    ]);
    setStreamingMessage("");
    setIsStreaming(false);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white flex flex-col">
      <div className="sticky top-0 z-50 p-6 border-b border-gray-800 bg-gray-900/95 backdrop-blur-md shadow-lg">
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

      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full px-6">
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
                  <div className="prose prose-invert max-w-none prose-sm">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm, remarkMath]}
                      rehypePlugins={[rehypeKatex, rehypeHighlight]}
                      components={{
                        code({ node, className, children, ...props }: any) {
                          const match = /language-(\w+)/.exec(className || '');
                          const isCodeBlock = match;
                          return isCodeBlock ? (
                            <code className={`${className} block bg-gray-900 p-3 rounded text-xs overflow-x-auto my-2`} {...props}>
                              {children}
                            </code>
                          ) : (
                            <code className="bg-gray-700 px-1.5 py-0.5 rounded text-sm" {...props}>
                              {children}
                            </code>
                          )
                        },
                        p: ({ node, ...props }) => <p className="mb-2 last:mb-0 leading-relaxed" {...props} />,
                        ul: ({ node, ...props }) => <ul className="list-disc ml-4 mb-2 space-y-1" {...props} />,
                        ol: ({ node, ...props }) => <ol className="list-decimal ml-4 mb-2 space-y-1" {...props} />,
                        li: ({ node, ...props }) => <li className="mb-1 leading-relaxed" {...props} />,
                        h1: ({ node, ...props }) => <h1 className="text-xl font-bold mb-3 mt-2" {...props} />,
                        h2: ({ node, ...props }) => <h2 className="text-lg font-bold mb-2 mt-2" {...props} />,
                        h3: ({ node, ...props }) => <h3 className="text-base font-bold mb-2 mt-1" {...props} />,
                        strong: ({ node, ...props }) => <strong className="font-bold text-white" {...props} />,
                        a: ({ node, ...props }) => <a className="text-blue-400 hover:underline" {...props} />,
                        blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-gray-600 pl-3 italic my-2" {...props} />,
                      }}
                    >
                      {message.text}
                    </ReactMarkdown>
                  </div>

                  {/* Bouton play pour réécouter les réponses aux questions vocales */}
                  {message.isBot && message.wasVoiceQuestion && (
                    <button
                      onClick={() => {
                        const cleanText = cleanTextForSpeech(message.text);
                        speak(cleanText);
                      }}
                      className="mt-3 flex items-center space-x-2 text-sm text-green-400 hover:text-green-300 transition-colors"
                      title="Réécouter la réponse"
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M8 5v14l11-7z" />
                      </svg>
                      <span>Réécouter</span>
                    </button>
                  )}

                  <div className={`text-xs mt-2 flex items-center justify-between ${message.isBot ? "text-gray-400" : "text-blue-200"
                    }`}>
                    <span>
                      {message.timestamp.toLocaleTimeString("fr-FR", {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                    {message.isBot && message.wasVoiceQuestion && (
                      <span className="text-green-500 text-xs flex items-center space-x-1">
                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
                          <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
                        </svg>
                        <span>Audio</span>
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {/* Message "Koffi réfléchit..." - s'affiche AVANT le streaming */}
            {isLoading && !isStreaming && (
              <div className="flex justify-start">
                <div className="bg-gray-800/80 border border-gray-700 text-white px-4 py-3 rounded-2xl shadow-lg backdrop-blur-sm">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                    </div>
                    <span className="text-sm text-gray-400">Koffi réfléchit...</span>
                  </div>
                </div>
              </div>
            )}

            {/* Message en cours de streaming - s'affiche APRÈS "Koffi réfléchit..." */}
            {isStreaming && streamingMessage && (
              <div className="flex justify-start">
                <div className="bg-gray-800/80 border border-gray-700 text-white px-4 py-3 rounded-2xl shadow-lg backdrop-blur-sm max-w-xs lg:max-w-md">
                  <div className="prose prose-invert max-w-none prose-sm">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm, remarkMath]}
                      rehypePlugins={[rehypeKatex, rehypeHighlight]}
                      components={{
                        code({ node, className, children, ...props }: any) {
                          const match = /language-(\w+)/.exec(className || '');
                          const isCodeBlock = match;
                          return isCodeBlock ? (
                            <code className={`${className} block bg-gray-900 p-3 rounded text-xs overflow-x-auto my-2`} {...props}>
                              {children}
                            </code>
                          ) : (
                            <code className="bg-gray-700 px-1.5 py-0.5 rounded text-sm" {...props}>
                              {children}
                            </code>
                          )
                        },
                        p: ({ node, ...props }) => <p className="mb-2 last:mb-0" {...props} />,
                        ul: ({ node, ...props }) => <ul className="list-disc ml-4 mb-2" {...props} />,
                        ol: ({ node, ...props }) => <ol className="list-decimal ml-4 mb-2" {...props} />,
                        li: ({ node, ...props }) => <li className="mb-1" {...props} />,
                        h1: ({ node, ...props }) => <h1 className="text-xl font-bold mb-2" {...props} />,
                        h2: ({ node, ...props }) => <h2 className="text-lg font-bold mb-2" {...props} />,
                        h3: ({ node, ...props }) => <h3 className="text-base font-bold mb-1" {...props} />,
                        strong: ({ node, ...props }) => <strong className="font-bold text-white" {...props} />,
                        a: ({ node, ...props }) => <a className="text-blue-400 hover:underline" {...props} />,
                      }}
                    >
                      {streamingMessage}
                    </ReactMarkdown>
                  </div>
                  <div className="flex items-center space-x-2 mt-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                      <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" style={{ animationDelay: "0.1s" }}></div>
                      <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" style={{ animationDelay: "0.2s" }}></div>
                    </div>
                    <span className="text-xs text-gray-400">Koffi écrit...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

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

          {isSpeaking && (
            <div className="text-center mt-4">
              <div className="inline-flex items-center space-x-3">
                <div className="flex items-center space-x-2 text-green-500">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm font-medium">🔊 Koffi parle...</span>
                </div>
                <button
                  onClick={stopSpeaking}
                  className="px-3 py-1 text-xs bg-red-500 hover:bg-red-600 text-white rounded-full transition-colors"
                >
                  Arrêter
                </button>
              </div>
            </div>
          )}

          {isRecording && !isSpeaking && (
            <div className="text-center mt-4">
              <div className="inline-flex items-center space-x-2 text-red-500">
                <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium">Enregistrement en cours... Cliquez à nouveau pour arrêter</span>
              </div>
            </div>
          )}

          {isProcessing && !isSpeaking && (
            <div className="text-center mt-4">
              <div className="inline-flex items-center space-x-2 text-blue-500">
                <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce"></div>
                <span className="text-sm font-medium">Traitement du message vocal...</span>
              </div>
            </div>
          )}

          {!isRecording && !isProcessing && !isSpeaking && (
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

        <div className="text-center py-2 border-t border-gray-800 mt-2">
          <p className="text-gray-500 text-xs">Powered by ASSALE YAO - AI ENGINEER</p>
        </div>
      </div>
      <CookieConsent />
    </main>
  );
}