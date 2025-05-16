import requests
from typing import Dict, List, Optional
from config import TRANSLATION_CONFIG

# Use the configuration values
LIBRETRANSLATE_API_URL = TRANSLATION_CONFIG['base_url']
SUPPORTED_LANGUAGES = TRANSLATION_CONFIG['supported_languages']

class TranslationService:
    def __init__(self):
        self.api_url = LIBRETRANSLATE_API_URL
        self.supported_languages = SUPPORTED_LANGUAGES
        self.cache = {}

    def translate_text(self, text: str, target_lang: str, source_lang: str = 'en') -> str:
        """Translate text to target language"""
        if target_lang not in self.supported_languages:
            return text
        
        cache_key = f"{source_lang}_{target_lang}_{text}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            response = requests.post(
                f"{self.api_url}/translate",
                json={
                    "q": text,
                    "source": source_lang,
                    "target": target_lang
                }
            )
            response.raise_for_status()
            translated_text = response.json()["translatedText"]
            
            # Cache the result
            self.cache[cache_key] = translated_text
            return translated_text
        except requests.exceptions.RequestException as e:
            print(f"Translation error: {e}")
            return text

    def translate_dict(self, data: Dict, target_lang: str, source_lang: str = 'en') -> Dict:
        """Translate all string values in a dictionary"""
        translated = {}
        for key, value in data.items():
            if isinstance(value, str):
                translated[key] = self.translate_text(value, target_lang, source_lang)
            elif isinstance(value, dict):
                translated[key] = self.translate_dict(value, target_lang, source_lang)
            elif isinstance(value, list):
                translated[key] = self.translate_list(value, target_lang, source_lang)
            else:
                translated[key] = value
        return translated

    def translate_list(self, items: List, target_lang: str, source_lang: str = 'en') -> List:
        """Translate all string items in a list"""
        translated = []
        for item in items:
            if isinstance(item, str):
                translated.append(self.translate_text(item, target_lang, source_lang))
            elif isinstance(item, dict):
                translated.append(self.translate_dict(item, target_lang, source_lang))
            elif isinstance(item, list):
                translated.append(self.translate_list(item, target_lang, source_lang))
            else:
                translated.append(item)
        return translated

    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return self.supported_languages

    def detect_language(self, text: str) -> str:
        """Detect the language of given text"""
        try:
            response = requests.post(
                f"{self.api_url}/detect",
                json={"q": text}
            )
            response.raise_for_status()
            return response.json()["language"]
        except requests.exceptions.RequestException as e:
            print(f"Language detection error: {e}")
            return 'en'  # Default to English if detection fails

    def translate_ui_texts(self, ui_texts: Dict, target_lang: str) -> Dict:
        """Translate UI texts for the application"""
        # Common UI texts that need translation
        ui_translations = {
            'en': {
                'emergency_alert': 'Emergency Alert',
                'risk_assessment': 'Risk Assessment',
                'volunteer_registration': 'Volunteer Registration',
                'send_alert': 'Send Emergency Alert',
                'assess_risk': 'Assess Risk',
                'register_volunteer': 'Register as Volunteer',
                'name': 'Name',
                'phone': 'Phone Number',
                'location': 'Location',
                'type': 'Type',
                'severity': 'Severity',
                'description': 'Description',
                'submit': 'Submit',
                'status': 'Status',
                'resources': 'Resources',
                'teams': 'Response Teams',
                'evacuation': 'Evacuation Plan',
                'weather': 'Weather',
                'alerts': 'Alerts',
                'dashboard': 'Dashboard'
            },
            'hi': {
                'emergency_alert': 'आपातकालीन अलर्ट',
                'risk_assessment': 'जोखिम मूल्यांकन',
                'volunteer_registration': 'स्वयंसेवक पंजीकरण',
                'send_alert': 'आपातकालीन अलर्ट भेजें',
                'assess_risk': 'जोखिम का आकलन करें',
                'register_volunteer': 'स्वयंसेवक के रूप में पंजीकृत करें',
                'name': 'नाम',
                'phone': 'फोन नंबर',
                'location': 'स्थान',
                'type': 'प्रकार',
                'severity': 'गंभीरता',
                'description': 'विवरण',
                'submit': 'जमा करें',
                'status': 'स्थिति',
                'resources': 'संसाधन',
                'teams': 'प्रतिक्रिया टीमें',
                'evacuation': 'निकासी योजना',
                'weather': 'मौसम',
                'alerts': 'अलर्ट',
                'dashboard': 'डैशबोर्ड'
            }
        }
        
        if target_lang in ui_translations:
            return ui_translations[target_lang]
        return ui_translations['en']  # Default to English if language not supported 