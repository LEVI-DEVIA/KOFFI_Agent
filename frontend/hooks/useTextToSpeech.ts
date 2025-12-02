import { useState, useCallback, useRef } from 'react';

export const useTextToSpeech = () => {
    const [isSpeaking, setIsSpeaking] = useState(false);
    const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

    const speak = useCallback((text: string, lang: string = 'fr-FR') => {
        // Arrêter toute lecture en cours
        if (window.speechSynthesis.speaking) {
            window.speechSynthesis.cancel();
        }

        // Créer une nouvelle utterance
        const utterance = new SpeechSynthesisUtterance(text);
        utteranceRef.current = utterance;

        // Configuration
        utterance.lang = lang;
        utterance.rate = 1.0; // Vitesse normale
        utterance.pitch = 1.0; // Ton normal
        utterance.volume = 1.0; // Volume max

        // Essayer de trouver une voix française
        const voices = window.speechSynthesis.getVoices();
        const frenchVoice = voices.find(voice => voice.lang.startsWith('fr'));
        if (frenchVoice) {
            utterance.voice = frenchVoice;
        }

        // Événements
        utterance.onstart = () => {
            setIsSpeaking(true);
        };

        utterance.onend = () => {
            setIsSpeaking(false);
            utteranceRef.current = null;
        };

        utterance.onerror = (event) => {
            console.error('Erreur TTS:', event);
            setIsSpeaking(false);
            utteranceRef.current = null;
        };

        // Lancer la lecture
        window.speechSynthesis.speak(utterance);
    }, []);

    const stop = useCallback(() => {
        if (window.speechSynthesis.speaking) {
            window.speechSynthesis.cancel();
            setIsSpeaking(false);
            utteranceRef.current = null;
        }
    }, []);

    const pause = useCallback(() => {
        if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
            window.speechSynthesis.pause();
        }
    }, []);

    const resume = useCallback(() => {
        if (window.speechSynthesis.paused) {
            window.speechSynthesis.resume();
        }
    }, []);

    return {
        speak,
        stop,
        pause,
        resume,
        isSpeaking,
    };
};
