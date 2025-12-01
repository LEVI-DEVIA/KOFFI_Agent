"use client";

import { useState, useRef, useCallback } from 'react';

export const useVoiceRecording = () => {
    const [isRecording, setIsRecording] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const recognitionRef = useRef<any>(null);

    const startRecording = useCallback(async () => {
        try {
            // Vérifier si on est dans un navigateur
            if (typeof window === 'undefined') {
                throw new Error('Non disponible côté serveur');
            }

            // Essayer d'obtenir l'API SpeechRecognition
            const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

            if (!SpeechRecognition) {
                throw new Error(
                    'La reconnaissance vocale n\'est pas supportée par ce navigateur.\n\n' +
                    'Navigateurs supportés:\n' +
                    '- Chrome/Edge (recommandé)\n' +
                    '- Safari sur iOS/macOS\n\n' +
                    'Note: Firefox ne supporte pas cette fonctionnalité.'
                );
            }

            // Vérifier les permissions du microphone
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                stream.getTracks().forEach(track => track.stop()); // Arrêter immédiatement
            } catch (permError) {
                throw new Error(
                    'Accès au microphone refusé.\n\n' +
                    'Veuillez autoriser l\'accès au microphone dans les paramètres de votre navigateur.'
                );
            }

            const recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'fr-FR';
            recognition.maxAlternatives = 1;

            recognitionRef.current = recognition;
            setIsRecording(true);

            recognition.start();
            console.log('🎤 Reconnaissance vocale démarrée');

        } catch (error) {
            console.error('Error starting recording:', error);
            setIsRecording(false);
            throw error;
        }
    }, []);

    const stopRecording = useCallback((): Promise<string> => {
        return new Promise((resolve, reject) => {
            const recognition = recognitionRef.current;

            if (!recognition) {
                setIsRecording(false);
                reject(new Error('Aucune reconnaissance active'));
                return;
            }

            let finalTranscript = '';
            let hasResult = false;

            recognition.onresult = (event: any) => {
                hasResult = true;
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript + ' ';
                    }
                }
                console.log('📝 Transcription:', finalTranscript);
            };

            recognition.onend = () => {
                setIsRecording(false);
                recognitionRef.current = null;

                if (!hasResult || !finalTranscript.trim()) {
                    reject(new Error('Aucun texte reconnu. Veuillez réessayer en parlant plus clairement.'));
                } else {
                    console.log('✅ Reconnaissance terminée:', finalTranscript.trim());
                    resolve(finalTranscript.trim());
                }
            };

            recognition.onerror = (event: any) => {
                setIsRecording(false);
                recognitionRef.current = null;

                let errorMessage = 'Erreur de reconnaissance vocale';
                switch (event.error) {
                    case 'no-speech':
                        errorMessage = 'Aucune parole détectée. Veuillez réessayer.';
                        break;
                    case 'audio-capture':
                        errorMessage = 'Microphone non disponible.';
                        break;
                    case 'not-allowed':
                        errorMessage = 'Permission microphone refusée.';
                        break;
                    case 'network':
                        errorMessage = 'Erreur réseau. Vérifiez votre connexion.';
                        break;
                    default:
                        errorMessage = `Erreur: ${event.error}`;
                }

                console.error('❌ Erreur reconnaissance:', event.error);
                reject(new Error(errorMessage));
            };

            try {
                recognition.stop();
            } catch (error) {
                setIsRecording(false);
                recognitionRef.current = null;
                reject(new Error('Erreur lors de l\'arrêt de la reconnaissance'));
            }
        });
    }, []);

    const sendTextMessage = useCallback(async (text: string): Promise<{ result: string; type: string; audioUrl?: string }> => {
        setIsProcessing(true);

        try {
            // Récupérer l'ID de session depuis localStorage
            const sessionId = localStorage.getItem("koffi-session-id") || `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-session-id': sessionId, // Inclure l'ID de session
                },
                body: JSON.stringify({
                    messages: [
                        {
                            role: 'user',
                            content: text
                        }
                    ]
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Utiliser l'API Text-to-Speech pour convertir la réponse en audio
            const audioUrl = await textToSpeech(data.result);

            return {
                result: data.result || "Pas de réponse",
                type: "audio",
                audioUrl
            };

        } catch (error) {
            console.error('Error sending message:', error);
            throw new Error('Erreur lors de l\'envoi du message');
        } finally {
            setIsProcessing(false);
        }
    }, []);

    const textToSpeech = useCallback(async (text: string): Promise<string> => {
        return new Promise((resolve, reject) => {
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'fr-FR';
                utterance.rate = 0.9;
                utterance.pitch = 1;

                // Trouver une voix française si disponible
                const voices = speechSynthesis.getVoices();
                const frenchVoice = voices.find(voice => voice.lang.startsWith('fr'));
                if (frenchVoice) {
                    utterance.voice = frenchVoice;
                }

                speechSynthesis.speak(utterance);

                utterance.onend = () => {
                    resolve('tts-played');
                };

                utterance.onerror = () => {
                    reject(new Error('Erreur de synthèse vocale'));
                };
            } else {
                reject(new Error('Synthèse vocale non supportée'));
            }
        });
    }, []);

    const playAudio = useCallback((audioUrl: string) => {
        if (audioUrl === 'tts-played') {
            // Le TTS a déjà été joué
            return;
        }
        const audio = new Audio(audioUrl);
        audio.play().catch(error => {
            console.error('Error playing audio:', error);
        });
    }, []);

    return {
        isRecording,
        isProcessing,
        startRecording,
        stopRecording,
        sendTextMessage,
        playAudio,
        textToSpeech,
    };
};