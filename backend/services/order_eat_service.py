from langchain_core.tools import tool
import asyncio
import os
from browser_use import Agent, Browser, ChatGoogle


@tool
def order_eat(query: str) -> str:
    """Order food from a restaurant using Browser Use automation.

    This tool processes food orders by first authenticating the user,
    then navigating restaurant websites, selecting items, and completing the order.

    Args:
        query (str): Food order details including restaurant, items, quantity, delivery address
    """

    async def process_order():
        try:
            # Initialize browser with stealth mode
            browser = Browser()
            llm = ChatGoogle(model="gemini-2.5-flash")

            # Create agent with authentication and food ordering task
            agent = Agent(
                task=f"""Process this food order step by step: {query}
                
                IMPORTANT AUTHENTICATION REQUIREMENT:
                Before proceeding with the order, you MUST first authenticate:
                1. Look for a "Se connecter" or "Connexion" button
                2. Click it and wait for the login form to appear
                3. The system will prompt the user to enter their credentials
                4. Wait for the authentication to complete before proceeding
                
                Only after successful authentication, continue with:
                1. Navigate to the restaurant website
                2. Add items to cart with correct quantities
                3. Proceed to checkout
                4. Fill delivery information
                5. Complete order and get confirmation
                
                If authentication fails or is not possible, immediately return:
                "Erreur: Authentification requise. Veuillez vous connecter avant de passer commande."
                
                Be thorough and make sure to complete the entire process.""",
                llm=llm,
                browser=browser,
            )

            result = await agent.run()
            await browser.close()
            return str(result)

        except Exception as e:
            return f"Error processing food order: {str(e)}"

    return asyncio.run(process_order())
