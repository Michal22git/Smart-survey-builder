import os
from functools import lru_cache

from openai import OpenAI

from .exceptions import APIKeyError


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    """
    Get or create an OpenAI client instance.

    Returns:
        An initialized OpenAI client

    Raises:
        APIKeyError: If the OpenAI API key is missing
    """
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise APIKeyError(
            "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
        )

    return OpenAI(api_key=api_key)


def get_default_model() -> str:
    """
    Get the default OpenAI model to use.

    Returns:
        The model name as a string
    """
    return os.environ.get("OPENAI_DEFAULT_MODEL", "gpt-4-turbo")
