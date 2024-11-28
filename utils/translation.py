from googletrans import Translator

translator = Translator()

def translate_text(text, target_language):
    """Translates text to the specified target language."""
    translated_text = translator.translate(text, dest=target_language).text
    return translated_text
