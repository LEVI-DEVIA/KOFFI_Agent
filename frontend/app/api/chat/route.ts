import { NextRequest, NextResponse } from "next/server";
import { cookies } from 'next/headers';

export const runtime = 'edge';

// Fonction pour gérer les sessions
async function getOrCreateSessionId(request: NextRequest): Promise<string> {
    // Vérifier d'abord l'en-tête x-session-id
    const sessionIdFromHeader = request.headers.get('x-session-id');
    if (sessionIdFromHeader) {
        return sessionIdFromHeader;
    }

    // Sinon, vérifier les cookies
    const cookieStore = await cookies();
    const sessionIdFromCookie = cookieStore.get('sessionId')?.value;

    if (sessionIdFromCookie) {
        return sessionIdFromCookie;
    }

    // Créer un nouvel ID de session si aucun n'existe
    return `session_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
}

export async function POST(req: NextRequest) {
    try {
        const contentType = req.headers.get("content-type");
        const body = await req.json();
        const { messages, stream = false } = body;

        if (!messages || !Array.isArray(messages) || messages.length === 0) {
            return NextResponse.json(
                { error: "Messages array is required" },
                { status: 400 }
            );
        }

        const lastMessage = messages[messages.length - 1];
        const userQuery = lastMessage.content;

        // Récupérer ou créer un ID de session
        const sessionId = await getOrCreateSessionId(req);

        // Structure ADK complète
        const adkPayload = {
            threadId: `memory_thread_${sessionId}`,
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
            forwardedProps: {},
            stream: stream  // Ajouter le flag de streaming
        };

        // Appel direct au backend ADK
        const backendUrl = (process.env.BACKEND_URL || "http://localhost:8000") + "/chat";

        if (stream) {
            // Pour le streaming, nous devons créer un transform stream
            const { readable, writable } = new TransformStream();
            
            // Lancer la requête au backend en arrière-plan
            (async () => {
                const writer = writable.getWriter();
                const encoder = new TextEncoder();
                
                try {
                    const backendResponse = await fetch(backendUrl, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "x-session-id": sessionId,
                        },
                        body: JSON.stringify(adkPayload),
                    });

                    if (!backendResponse.ok) {
                        const errorText = await backendResponse.text();
                        throw new Error(`Backend responded with status: ${backendResponse.status}, body: ${errorText}`);
                    }

                    // Relayer le flux de réponse du backend
                    const reader = backendResponse.body?.getReader();
                    
                    if (!reader) {
                        throw new Error("Impossible de lire le flux de réponse du backend");
                    }

                    while (true) {
                        const { done, value } = await reader.read();
                        
                        if (done) break;
                        
                        await writer.write(value);
                    }
                } catch (error) {
                    console.error("Error in streaming:", error);
                    const errorMessage = `data: ${JSON.stringify({ type: 'error', error: error instanceof Error ? error.message : 'Unknown error' })}\n\n`;
                    await writer.write(encoder.encode(errorMessage));
                } finally {
                    await writer.close();
                }
            })();

            // Retourner le flux de réponse
            return new NextResponse(readable, {
                headers: {
                    'Content-Type': 'text/event-stream',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Set-Cookie': `sessionId=${sessionId}; Path=/; HttpOnly; SameSite=Lax; Max-Age=31536000`
                }
            });
        } else {
            // Mode non-streaming (code existant)
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 secondes pour les recherches web

            const backendResponse = await fetch(backendUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "x-session-id": sessionId,
                    "Cache-Control": "no-cache",
                    "Pragma": "no-cache"
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

            // Renvoyer la réponse avec le cookie de session
            const responseWithCookie = NextResponse.json({
                result: responseData.message.content,
                type: "text"
            });
            responseWithCookie.headers.set('Set-Cookie', `sessionId=${sessionId}; Path=/; HttpOnly; SameSite=Lax; Max-Age=31536000`);

            return responseWithCookie;
        }

    } catch (error) {
        console.error("API Error:", error);
        return NextResponse.json(
            {
                error: "Erreur de communication avec le backend",
                details: error instanceof Error ? error.message : "Unknown error"
            },
            {
                status: 500,
                headers: {
                    'Set-Cookie': `sessionId=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0`,
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, x-session-id'
                }
            }
        );
    }
}