import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
    try {
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

        // Structure ADK complète
        const adkPayload = {
            threadId: `thread_${Date.now()}`,
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

        // Appel direct au backend ADK
        const backendResponse = await fetch("http://localhost:8000/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(adkPayload),
        });

        if (!backendResponse.ok) {
            const errorText = await backendResponse.text();
            throw new Error(`Backend responded with status: ${backendResponse.status}, body: ${errorText}`);
        }

        // Le backend retourne un stream, nous devons le traiter
        const responseText = await backendResponse.text();

        // Parser les lignes de données du stream
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
                // Ignorer les lignes qui ne sont pas du JSON valide
                continue;
            }
        }

        if (!assistantResponse) {
            assistantResponse = "Désolé, je n'ai pas pu traiter votre demande.";
        }

        return NextResponse.json({
            result: assistantResponse,
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