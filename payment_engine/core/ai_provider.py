"""
AI Provider Abstraction
"""

import os

try:
    from groq import Groq
except Exception:
    Groq = None


class AIProvider:

    def __init__(self):

        api_key = os.getenv("GROQ_API_KEY")

        if Groq is not None and api_key:
            self.client = Groq(api_key=api_key)
        else:
            self.client = None

        self.default_model = "llama-3.3-70b-versatile"

    def available(self):
        return self.client is not None

    def generate(self, prompt):

        if self.client is None:
            return (
                "[AI Offline] "
                "Groq SDK or dependencies are unavailable."
            )

        response = self.client.chat.completions.create(
            model=self.default_model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content
