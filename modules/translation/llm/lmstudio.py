from typing import Any
from .custom import CustomTranslation


class LMStudioTranslation(CustomTranslation):
    """Translation engine using LM Studio's local OpenAI-compatible API."""

    DEFAULT_URL = "http://localhost:1234/v1"

    def __init__(self):
        super().__init__()
        self.api_base_url = self.DEFAULT_URL
        self.timeout = 120

    def initialize(self, settings: Any, source_lang: str, target_lang: str, tr_key: str, **kwargs) -> None:
        # BaseLLMTranslation.initialize for shared settings
        super(CustomTranslation, self).initialize(settings, source_lang, target_lang, **kwargs)

        credentials = settings.get_credentials(settings.ui.tr('LM Studio'))
        self.api_key = credentials.get('api_key', 'lm-studio')  # LM Studio accepts any key
        self.model = credentials.get('model', '')
        custom_url = credentials.get('api_url', '').strip().rstrip('/')
        self.api_base_url = custom_url if custom_url else self.DEFAULT_URL
        self.timeout = 120
