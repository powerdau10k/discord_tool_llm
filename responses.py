import os
import dotenv
from groq import Groq
from tooling import Groq_Agent
from dotenv import load_dotenv

dotenv.load_dotenv()
TOKEN = os.getenv("GROQ_API_KEY")

client = Groq(api_key=TOKEN)
message_history = []


def get_tool(prompt):
    agent = Groq_Agent()
    return agent.stream_agent(prompt=prompt)


def get_answer(message):
    message_history.append({"role": "user", "content": message})
    chat_completion = client.chat.completions.create(
        #
        # Required parameters
        #
        messages=message_history,
        # The language model which will generate the completion.
        model="llama-3.1-70b-versatile",
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        # A stop sequence is a predefined or user-specified text string that
        # signals an AI to stop generating content, ensuring its responses
        # remain focused and concise. Examples include punctuation marks and
        # markers like "[end]".
        stop=None,
        # If set, partial message deltas will be sent.
        stream=False,
    )
    message_history.append({
        "role": "assistant",
        "content": chat_completion.choices[0].message.content,
    })
    return chat_completion.choices[0].message.content
