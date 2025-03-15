class OpenAIError(Exception):
    """Base exception for OpenAI-related errors."""
    pass

class GenerationError(OpenAIError):
    """Error during survey generation."""
    pass

class SchemaValidationError(OpenAIError):
    """Error validating the JSON schema."""
    pass

class APIKeyError(OpenAIError):
    """Error related to the API key."""
    pass 