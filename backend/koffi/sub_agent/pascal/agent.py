from google.adk.agents.llm_agent import Agent

pascal_agent = Agent(
    model="gemini-2.5-flash-native-audio-preview-09-2025",
    name="pascal",
    description="Specialized in the course.",
    instruction="Answer user questions to the best of your knowledge",
)
