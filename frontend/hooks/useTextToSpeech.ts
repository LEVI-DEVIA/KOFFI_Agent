import { useState, useCallback, useRef } from 'react';

/**
 * Hook pour la synthèse vocale (Text-to-Speech)
 * KOFFI est un agent masculin - La voix masculine française est automatiquement sélectionnée
 */
export const useTextToSpeech = () => {
    const [isSpeaking, setIsSpeaking] = useState(false);
    const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

    // Fonction pour lister les voix disponibles (utile pour debug)
    const listAvailableVoices = useCallback(() => {
        const voices = window.speechSynthesis.getVoices();
        console.log('🎙️ Voix disponibles sur ce système:');
        voices.forEach((voice, index) => {
            const isFrench = voice.lang.startsWith('fr');
            const marker = isFrench ? '🇫🇷' : '  ';
            console.log(`${marker} ${index + 1}. ${voice.name} (${voice.lang}) ${voice.default ? '⭐' : ''}`);
        });
        return voices;
    }, []);

    const speak = useCallback((text: string, lang: string = 'fr-FR') => {
        // Arrêter toute lecture en cours
        if (window.speechSynthesis.speaking) {
            window.speechSynthesis.cancel();
        }

        // Découper le texte en phrases pour éviter les blocages
        // Limite de sécurité : 150 caractères par chunk
        const maxChunkLength = 150;
        const chunks: string[] = [];

        // Découper par phrases (points, points d'exclamation, points d'interrogation)
        const sentences = text.split(/([.!?]+\s+)/);
        let currentChunk = '';

        for (let i = 0; i < sentences.length; i++) {
            const sentence = sentences[i];

            // Si ajouter cette phrase dépasse la limite, sauvegarder le chunk actuel
            if (currentChunk.length + sentence.length > maxChunkLength && currentChunk.length > 0) {
                chunks.push(currentChunk.trim());
                currentChunk = sentence;
            } else {
                currentChunk += sentence;
            }
        }

        // Ajouter le dernier chunk
        if (currentChunk.trim().length > 0) {
            chunks.push(currentChunk.trim());
        }

        // Si pas de chunks (texte vide), ne rien faire
        if (chunks.length === 0) {
            return;
        }

        console.log(`🔊 Lecture de ${chunks.length} chunk(s) pour ${text.length} caractères`);

        // Fonction pour lire un chunk
        const speakChunk = (chunkIndex: number) => {
            if (chunkIndex >= chunks.length) {
                setIsSpeaking(false);
                utteranceRef.current = null;
                console.log('✅ Lecture terminée');
                return;
            }

            const chunk = chunks[chunkIndex];
            console.log(`📢 Chunk ${chunkIndex + 1}/${chunks.length}: "${chunk.substring(0, 50)}..."`);

            const utterance = new SpeechSynthesisUtterance(chunk);
            utteranceRef.current = utterance;

            // Configuration optimisée pour réactivité
            utterance.lang = lang;
            utterance.rate = 1.1; // Légèrement plus rapide pour réactivité
            utterance.pitch = 0.9; // Ton légèrement plus grave pour voix masculine
            utterance.volume = 1.0; // Volume max

            // KOFFI est un garçon - Imposer une voix masculine française
            const voices = window.speechSynthesis.getVoices();

            // Priorité 1 : Voix masculine française explicite (noms communs)
            let selectedVoice = voices.find(voice =>
                voice.lang.startsWith('fr') &&
                (voice.name.toLowerCase().includes('male') ||
                    voice.name.toLowerCase().includes('homme') ||
                    voice.name.toLowerCase().includes('man') ||
                    voice.name.toLowerCase().includes('thomas') ||
                    voice.name.toLowerCase().includes('daniel') ||
                    voice.name.toLowerCase().includes('nicolas') ||
                    voice.name.toLowerCase().includes('paul') ||
                    voice.name.toLowerCase().includes('pierre') ||
                    voice.name.toLowerCase().includes('laurent'))
            );

            // Priorité 2 : Voix française qui n'est PAS féminine (exclusion stricte)
            if (!selectedVoice) {
                selectedVoice = voices.find(voice =>
                    voice.lang.startsWith('fr') &&
                    !voice.name.toLowerCase().includes('female') &&
                    !voice.name.toLowerCase().includes('femme') &&
                    !voice.name.toLowerCase().includes('woman') &&
                    !voice.name.toLowerCase().includes('amelie') &&
                    !voice.name.toLowerCase().includes('marie') &&
                    !voice.name.toLowerCase().includes('claire') &&
                    !voice.name.toLowerCase().includes('julie') &&
                    !voice.name.toLowerCase().includes('sophie') &&
                    !voice.name.toLowerCase().includes('lea') &&
                    !voice.name.toLowerCase().includes('emma')
                );
            }

            // Priorité 3 : Première voix française disponible
            if (!selectedVoice) {
                selectedVoice = voices.find(voice => voice.lang.startsWith('fr'));
            }

            // Priorité 4 : Voix par défaut du système (dernier recours)
            if (!selectedVoice) {
                selectedVoice = voices.find(voice => voice.default);
            }

            if (selectedVoice) {
                utterance.voice = selectedVoice;
                if (chunkIndex === 0) {
                    console.log('🎙️ Voix de KOFFI (masculine):', selectedVoice.name, '(', selectedVoice.lang, ')');
                }
            }

            // Événements
            utterance.onstart = () => {
                if (chunkIndex === 0) {
                    setIsSpeaking(true);
                }
            };

            utterance.onend = () => {
                // Lire le chunk suivant
                speakChunk(chunkIndex + 1);
            };

            utterance.onerror = (event) => {
                console.error('❌ Erreur TTS chunk', chunkIndex + 1, ':', event);
                setIsSpeaking(false);
                utteranceRef.current = null;
            };

            // Lancer la lecture de ce chunk
            window.speechSynthesis.speak(utterance);
        };

        // Commencer la lecture du premier chunk
        speakChunk(0);
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
        listAvailableVoices,
    };
};
