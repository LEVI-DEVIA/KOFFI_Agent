from google.adk.agents.llm_agent import Agent

natacha_agent = Agent(
    model='gemini-2.5-flash-native-audio-preview-09-2025',
    name='natacha',
    description='Specialized in the eat',
    instruction='Answer user questions to the best of your knowledge',
)
