from __future__ import annotations

from PySide6.QtCore import QCoreApplication
from typing import TYPE_CHECKING
from modules.inpainting.lama import LaMa
from modules.inpainting.mi_gan import MIGAN
from modules.inpainting.aot import AOT
from modules.inpainting.schema import Config
from app.ui.messages import Messages
from app.ui.settings.settings_page import SettingsPage

if TYPE_CHECKING:
    from controller import ComicTranslate

inpaint_map = {
    "LaMa": LaMa,
    "MI-GAN": MIGAN,
    "AOT": AOT,
}


def get_inpainter_backend(inpainter_key: str) -> str:
    inpainter_cls = inpaint_map[inpainter_key]
    return getattr(inpainter_cls, "preferred_backend", "onnx")

def get_config(settings_page: SettingsPage):
    strategy_settings = settings_page.get_hd_strategy_settings()
    if strategy_settings['strategy'] == settings_page.ui.tr("Resize"):
        config = Config(hd_strategy="Resize", hd_strategy_resize_limit = strategy_settings['resize_limit'])
    elif strategy_settings['strategy'] == settings_page.ui.tr("Crop"):
        config = Config(hd_strategy="Crop", hd_strategy_crop_margin = strategy_settings['crop_margin'],
                        hd_strategy_crop_trigger_size = strategy_settings['crop_trigger_size'])
    else:
        config = Config(hd_strategy="Original")

    return config

def _get_api_key_service(tool_name: str) -> str | None:
    """Return the credential service name for a given tool, or None if no key needed."""
    if not tool_name:
        return None
    if "Gemini" in tool_name:
        return "Google Gemini"
    if "GPT" in tool_name:
        return "Open AI GPT"
    if "Claude" in tool_name:
        return "Anthropic Claude"
    if "Deepseek" in tool_name:
        return "Deepseek"
    if "Microsoft" in tool_name:
        return "Microsoft Azure"
    return None


def validate_ocr(main: ComicTranslate):
    """Ensure API credentials are configured for the selected OCR engine."""
    settings_page = main.settings_page
    tr = settings_page.ui.tr
    settings = settings_page.get_all_settings()
    credentials = settings.get('credentials', {})
    ocr_tool = settings['tools']['ocr']

    if not ocr_tool:
        Messages.show_missing_tool_error(main, QCoreApplication.translate("Messages", "Text Recognition model"))
        return False

    service = _get_api_key_service(ocr_tool)
    if service:
        creds = credentials.get(tr(service), {})
        if service == "Microsoft Azure":
            if not creds.get('api_key_ocr') or not creds.get('endpoint'):
                Messages.show_api_key_not_configured_error(main, service)
                return False
        else:
            if not creds.get('api_key'):
                Messages.show_api_key_not_configured_error(main, service)
                return False

    return True


def validate_translator(main: ComicTranslate, target_lang: str):
    """Ensure API credentials are configured for the selected translator."""
    settings_page = main.settings_page
    tr = settings_page.ui.tr
    settings = settings_page.get_all_settings()
    credentials = settings.get('credentials', {})
    translator_tool = settings['tools']['translator']

    if not translator_tool:
        Messages.show_missing_tool_error(main, QCoreApplication.translate("Messages", "Translator"))
        return False

    if "Custom" in translator_tool:
        service = tr('Custom')
        creds = credentials.get(service, {})
        if not all([creds.get('api_key'), creds.get('api_url'), creds.get('model')]):
            Messages.show_custom_not_configured_error(main)
            return False
        return True

    service = _get_api_key_service(translator_tool)
    if service:
        creds = credentials.get(tr(service), {})
        if not creds.get('api_key'):
            Messages.show_api_key_not_configured_error(main, service)
            return False

    return True

def font_selected(main: ComicTranslate):
    if not main.render_settings().font_family:
        Messages.select_font_error(main)
        return False
    return True

def validate_settings(main: ComicTranslate, target_lang: str):
    if not validate_ocr(main):
        return False
    if not validate_translator(main, target_lang):
        return False
    if not font_selected(main):
        return False
    
    return True
