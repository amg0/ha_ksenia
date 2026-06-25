"""
API package for ksenia.

Architecture:
    Three-layer data flow: Entities → Coordinator → API Client.
    Only the coordinator should call the API client. Entities must never
    import or call the API client directly.

Exception hierarchy:
    KseniaLaresApiClientError (base)
    ├── KseniaLaresApiClientCommunicationError (network/timeout)
    └── KseniaLaresApiClientAuthenticationError (401/403)

Coordinator exception mapping:
    ApiClientAuthenticationError → ConfigEntryAuthFailed (triggers reauth)
    ApiClientCommunicationError → UpdateFailed (auto-retry)
    ApiClientError             → UpdateFailed (auto-retry)
"""

from .client import (
    KseniaLaresApiClient,
    KseniaLaresApiClientAuthenticationError,
    KseniaLaresApiClientCommunicationError,
    KseniaLaresApiClientError,
)

__all__ = [
    "KseniaLaresApiClient",
    "KseniaLaresApiClientAuthenticationError",
    "KseniaLaresApiClientCommunicationError",
    "KseniaLaresApiClientError",
]
