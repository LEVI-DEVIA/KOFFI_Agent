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
            const backendUrl = (process.env.BACKEND_URL || "http://localhost:8000") + "/chat";
            const backendResponse = await fetch(backendUrl, {
                method: "POST",
                body: adkFormData,
            });

            if (!backendResponse.ok) {
                const errorText = await backendResponse.text();
                throw new Error(`Backend responded with status: ${backendResponse.status}, body: ${errorText}`);
            }

            // Handle the JSON response from FastAPI
            const responseData = await backendResponse.json();

            if (!responseData.message || !responseData.message.content) {
                throw new Error('Invalid response format from backend');
            }

            return NextResponse.json({
                result: responseData.message.content,
                type: "text"
            });
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
        const backendUrl = (process.env.BACKEND_URL || "http://localhost:8000") + "/chat";

        const backendResponse = await fetch(backendUrl, {
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

        // Handle the JSON response from FastAPI
        const responseData = await backendResponse.json();

        if (!responseData.message || !responseData.message.content) {
            throw new Error('Invalid response format from backend');
        }

        return NextResponse.json({
            result: responseData.message.content,
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