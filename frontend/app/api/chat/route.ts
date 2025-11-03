import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
    try {
        const contentType = req.headers.get("content-type");

        // Gestion des requêtes audio
        if (contentType?.includes("multipart/form-data")) {
            const formData = await req.formData();
            const audioFile = formData.get("audio") as File;
            const userQuery = formData.get("message") as string;

            if (!audioFile && !userQuery) {
                return NextResponse.json(
                    { error: "Audio file or message is required" },
                    { status: 400 }
                );
            }

            // Préparer les données pour l'ADK
            const adkFormData = new FormData();

            if (audioFile) {
                adkFormData.append("audio", audioFile);
            }

            // Générer ou récupérer un ID de session unique pour l'audio
            const sessionId = req.headers.get("x-session-id") || `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            const userId = sessionId;
            const threadId = `memory_thread_${userId}`;

            // Structure ADK pour l'audio
            const adkPayload = {
                threadId: threadId,
                runId: `run_${Date.now()}`,
                state: {},
                messages: userQuery ? [
                    {
                        id: `msg_${Date.now()}`,
                        role: "user",
                        content: userQuery,
                    }
                ] : [],
                tools: [],
                context: [],
                forwardedProps: {}
            };

            adkFormData.append("data", JSON.stringify(adkPayload));

            // Appel au backend ADK avec audio
            const backendResponse = await fetch("http://localhost:8000/", {
                method: "POST",
                body: adkFormData,
            });

            if (!backendResponse.ok) {
                const errorText = await backendResponse.text();
                throw new Error(`Backend responded with status: ${backendResponse.status}, body: ${errorText}`);
            }

            // Vérifier si la réponse est de l'audio
            const responseContentType = backendResponse.headers.get("content-type");

            if (responseContentType?.includes("audio/")) {
                // Retourner l'audio directement
                const audioBuffer = await backendResponse.arrayBuffer();
                return new NextResponse(audioBuffer, {
                    headers: {
                        "Content-Type": responseContentType,
                        "Content-Length": audioBuffer.byteLength.toString(),
                    },
                });
            } else {
                // Traiter comme une réponse texte streamée
                const responseText = await backendResponse.text();
                const lines = responseText.split('\n').filter(line => line.startsWith('data: '));
                let assistantResponse = "";

                for (const line of lines) {
                    try {
                        const jsonStr = line.replace('data: ', '');
                        const data = JSON.parse(jsonStr);

                        if (data.type === "TEXT_MESSAGE_CONTENT" && data.delta) {
                            assistantResponse += data.delta;
                        }
                    } catch (e) {
                        continue;
                    }
                }

                return NextResponse.json({
                    result: assistantResponse || "Désolé, je n'ai pas pu traiter votre demande.",
                    type: "text"
                });
            }
        }

        // Gestion des requêtes texte (code existant)
        const body = await req.json();
        const { messages } = body;

        if (!messages || !Array.isArray(messages) || messages.length === 0) {
            return NextResponse.json(
                { error: "Messages array is required" },
                { status: 400 }
            );
        }

        const lastMessage = messages[messages.length - 1];
        const userQuery = lastMessage.content;

        // Générer ou récupérer un ID de session unique
        const sessionId = req.headers.get("x-session-id") || `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const userId = sessionId; // Utiliser l'ID de session comme user ID
        const threadId = `memory_thread_${userId}`;

        // Structure ADK complète
        const adkPayload = {
            threadId: threadId, // ThreadId fixe pour la mémoire
            runId: `run_${Date.now()}`,
            state: {},
            messages: [
                {
                    id: `msg_${Date.now()}`,
                    role: "user",
                    content: userQuery,
                }
            ],
            tools: [],
            context: [],
            forwardedProps: {}
        };

        // Ajouter un petit délai pour éviter les erreurs de quota
        await new Promise(resolve => setTimeout(resolve, 500));

        // Appel direct au backend ADK avec timeout plus long
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 secondes

        const backendResponse = await fetch("http://localhost:8000/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(adkPayload),
            signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!backendResponse.ok) {
            const errorText = await backendResponse.text();
            throw new Error(`Backend responded with status: ${backendResponse.status}, body: ${errorText}`);
        }

        // Traiter le stream correctement
        const reader = backendResponse.body?.getReader();
        const decoder = new TextDecoder();
        let assistantResponse = "";

        if (reader) {
            try {
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    const chunk = decoder.decode(value, { stream: true });
                    const lines = chunk.split('\n').filter(line => line.startsWith('data: '));

                    for (const line of lines) {
                        try {
                            const jsonStr = line.replace('data: ', '');
                            const data = JSON.parse(jsonStr);

                            if (data.type === "TEXT_MESSAGE_CONTENT" && data.delta) {
                                assistantResponse += data.delta;
                            }
                        } catch (e) {
                            // Ignorer les lignes malformées
                            continue;
                        }
                    }
                }
            } finally {
                reader.releaseLock();
            }
        }

        if (!assistantResponse) {
            assistantResponse = "Désolé, je n'ai pas pu traiter votre demande.";
        }

        return NextResponse.json({
            result: assistantResponse,
            type: "text"
        });

    } catch (error) {
        console.error("API Error:", error);
        return NextResponse.json(
            {
                error: "Erreur de communication avec le backend",
                details: error instanceof Error ? error.message : "Unknown error"
            },
            { status: 500 }
        );
    }
}