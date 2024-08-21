import os
import dotenv
from googleapiclient.discovery import build
from py_expression_eval import Parser
from groq import Groq
from wolframalpha import Client
import re
import wolframalpha
import asyncio
from simpletest import scrape_google


class Groq_Agent:
    def __init__(self):
        dotenv.load_dotenv()
        print(os.getenv("GOOGLE_CSE_ID"))
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")
        self.google_cse_api_key = os.getenv("GOOGLE_CSE_API_KEY")
        self.wolfram_app_id = os.getenv("WOLFRAM_APP_ID")
        self.model = "llama-3.1-70b-versatile"
        self.System_prompt = """
        Answer the following questions and obey the following commands as best you can.

        You have access to the following tools:

        Search: Search: useful for when you need to answer questions about current events. You should ask targeted questions.
        Calculator: Useful for when you need to answer questions about math. Use python code, eg: 2 + 2
        WolframAlpha: Useful for Scientific questions, questions about weather or dates, you might also want to use it to narrow down the information from search results. Use simple but queries.
        Response To Human: When you need to respond to the human you are talking to.

        You will receive a message from the human, then you should start a loop and do one of two things run multiple thought loops and searches before answering to the human if necessary

        Option 1: You use a tool to answer the question.
        For this, you should use the following format:
        Thought: you should always think about what to do your thoughts should be verbose and contain previous gathered information if there is any
        Action: the action to take, should be one of [Search, Calculator, WolframAlpha]
        Action Input: "the input to the action, to be sent to the tool"

        After this, the human will respond with an observation, and you will continue.

        Option 2: You respond to the human.
        For this, you should use the following format:
        Action: Response To Human
        Action Input: "your response to the human, summarizing what you did and what you learned"

        Begin!
        """

        self.wolfram_client = wolframalpha.Client(self.wolfram_app_id)
        self.client = Groq(api_key=self.groq_api_key)
        self.parser = Parser()

    async def wolfram_alpha(self, prompt):
        res = await self.wolfram_client.aquery(prompt)
        print(res)
        return res

    # Google search engine
    async def search(self, search_term):
        search_result = ""
        service = build("customsearch", "v1", developerKey=self.google_cse_api_key)
        res = service.cse().list(q=search_term, cx=self.google_cse_id, num=10).execute()
        for result in res["items"]:
            search_result_snippets = search_result + result["snippet"]
        scrapes = scrape_google(search_term)
        return scrapes

    # Calculator
    async def calculator(self, str):
        return self.parser.parse(str).evaluate({})

    async def stream_agent(self, prompt):
        return_message = []
        messages = [
            {"role": "system", "content": self.System_prompt},
            {"role": "user", "content": prompt},
        ]

        def extract_action_and_input(text):
            action_pattern = r"Action: (.+?)\n"
            input_pattern = r"Action Input: \"(.+?)\""
            action = re.findall(action_pattern, text)
            action_input = re.findall(input_pattern, text)
            return action, action_input

        while True:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5,
                max_tokens=8000,
                top_p=1,
            )
            response_text = response.choices[0].message.content
            return_message.append(response_text)
            action, action_input = extract_action_and_input(response_text)

            if action[-1] == "Search":
                tool = self.search
            elif action[-1] == "Calculator":
                tool = self.calculator
            elif action[-1] == "WolframAlpha":
                tool = self.wolfram_alpha
            elif action[-1] == "Response To Human":
                response_to_human = f"\nResponse to Human:\n{action_input[-1]}"
                return_message.append(response_to_human)
                return return_message

            observation = await tool(action_input[-1])
            observation = str(observation)
            messages.extend([
                {"role": "assistant", "content": response_text},
                {"role": "user", "content": observation},
            ])


async def main():
    agent = Groq_Agent()
    result = await agent.stream_agent(prompt="tell me about yesterday's biggest news")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
