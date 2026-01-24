class WebtopError(Exception):
    """Base exception for pywebtop."""


class WebtopLoginError(WebtopError):
    """Raised when login fails or token is missing."""


class WebtopRequestError(WebtopError):
    """Raised when an API request fails."""
