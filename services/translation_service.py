import requests
import json
from config import TRANSLATION_CONFIG
import logging
from typing import Dict, List, Optional

class TranslationService:
    def __init__(self):
        self.api_key = TRANSLATION_CONFIG['api_key']
        self.base_url = TRANSLATION_CONFIG['base_url']
        self.supported_languages = TRANSLATION_CONFIG['supported_languages']
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='logs/translation_service.log'
        )
        self.logger = logging.getLogger(__name__)

    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text from source language to target language"""
        try:
            if source_lang not in self.supported_languages:
                raise ValueError(f"Source language {source_lang} not supported")
            if target_lang not in self.supported_languages:
                raise ValueError(f"Target language {target_lang} not supported")

            url = f"{self.base_url}/translate"
            params = {
                'api_key': self.api_key,
                'text': text,
                'source': source_lang,
                'target': target_lang
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()

            if 'translation' in result:
                return result['translation']
            else:
                raise ValueError("Translation not found in response")

        except requests.RequestException as e:
            self.logger.error(f"Translation API request failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error in translation: {str(e)}")
            raise

    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return self.supported_languages

    def detect_language(self, text: str) -> str:
        """Detect language of the given text"""
        try:
            url = f"{self.base_url}/detect"
            params = {
                'api_key': self.api_key,
                'text': text
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()

            if 'language' in result:
                return result['language']
            else:
                raise ValueError("Language detection failed")

        except requests.RequestException as e:
            self.logger.error(f"Language detection API request failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error in language detection: {str(e)}")
            raise
