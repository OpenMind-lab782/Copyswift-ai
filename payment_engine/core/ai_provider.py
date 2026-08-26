"""
Swift Payment Engine — Native HTTP AI Provider.

Uses the Groq OpenAI-compatible HTTP API directly.

This implementation intentionally does NOT depend on the Groq Python SDK
or Pydantic, making it compatible with constrained environments such as
Termux/Android ARMv7.
"""

import json
import os
from typing import Any

import requests
from dotenv import load_dotenv


class AIProvider:
    """
    Groq-backed AI provider using direct HTTPS requests.

    Public compatibility:
        available()
        generate(prompt)
        generate_json(prompt)
    """

    DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"
    DEFAULT_MODEL = "llama-3.3-70b-versatile"
    DEFAULT_TIMEOUT = 30

    def __init__(
        self,
        api_key=None,
        model=None,
        base_url=None,
        timeout=None,
        session=None,
    ):
        # Load local development secrets without overriding
        # explicitly supplied environment variables.
        load_dotenv()

        self.api_key = (
            api_key
            if api_key is not None
            else os.getenv("GROQ_API_KEY", "")
        ).strip()

        self.default_model = (
            model
            or os.getenv("GROQ_MODEL")
            or self.DEFAULT_MODEL
        )

        self.base_url = (
            base_url
            or os.getenv("GROQ_BASE_URL")
            or self.DEFAULT_BASE_URL
        ).rstrip("/")

        configured_timeout = (
            timeout
            if timeout is not None
            else os.getenv("GROQ_TIMEOUT")
        )

        if configured_timeout is None:
            self.timeout = self.DEFAULT_TIMEOUT
        else:
            try:
                self.timeout = float(configured_timeout)
            except (TypeError, ValueError):
                self.timeout = self.DEFAULT_TIMEOUT

        self.session = session or requests.Session()

    def available(self):
        """
        Return whether the provider has the credentials required to operate.
        """
        return bool(self.api_key)

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _chat_completion(
        self,
        messages,
        model=None,
        temperature=0.2,
        max_tokens=1000,
    ):
        if not self.available():
            raise RuntimeError(
                "GROQ_API_KEY is not configured."
            )

        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Groq API connectivity error: {type(exc).__name__}"
            ) from exc

        if not response.ok:
            raise RuntimeError(
                f"Groq API request failed with HTTP {response.status_code}."
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                "Groq API returned invalid JSON."
            ) from exc

        choices = data.get("choices") or []

        if not choices:
            raise RuntimeError(
                "Groq API returned no completion choices."
            )

        message = choices[0].get("message") or {}
        content = message.get("content")

        if not isinstance(content, str):
            raise RuntimeError(
                "Groq API returned an invalid completion payload."
            )

        return content.strip()

    def generate(
        self,
        prompt,
        model=None,
        system=None,
        temperature=0.2,
        max_tokens=1000,
    ):
        """
        Generate plain-text AI output.
        """
        messages = []

        if system:
            messages.append({
                "role": "system",
                "content": system,
            })

        messages.append({
            "role": "user",
            "content": prompt,
        })

        return self._chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def generate_json(
        self,
        prompt,
        model=None,
        system=None,
        temperature=0.2,
        max_tokens=1200,
    ) -> Any:
        """
        Generate and parse a JSON response.

        Handles both raw JSON and accidental Markdown code fences.
        """
        content = self.generate(
            prompt=prompt,
            model=model,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        cleaned = content.strip()

        if cleaned.startswith("```"):
            lines = cleaned.splitlines()

            if lines and lines[0].strip().startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            cleaned = "\n".join(lines).strip()

            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].lstrip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Groq returned non-JSON content where JSON was required."
            ) from exc
