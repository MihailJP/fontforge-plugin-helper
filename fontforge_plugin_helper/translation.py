"""Translation-related class for Fontforge plugins"""

from locale import getlocale, LC_MESSAGES
from typing import Dict


def _locale() -> str:
    return (getlocale(LC_MESSAGES)[0]) or (getlocale()[0]) or 'C'


class Translations():
    """Class for message translation in Fontforge plugins"""
    _translation = {}

    def set(self, lang: str, english: str, translation: str):
        """Set a translation for given English message for given language

        :param lang: Language code with or without country code, \
            such as ``fr`` or ``en_UK``.
        :param english: An English message to translate.
        :param translation: The translation corresponding to ``english`` parameter.
        """

        self._translation.setdefault(english, {})
        self._translation[english][lang] = translation

    def setTranslations(self, lang: str, translations: Dict[str, str]):
        """Append translations for given language

        :param lang: Language code with or without country code, \
            such as ``fr`` or ``en_UK``.
        :param translations: A ``dict`` whose keys are English messages and \
            values are corresponding translations.
        """

        for k, v in translations.items():
            self.set(lang, k, v)

    def get(self, english: str) -> str:
        """Get translation for current locale

        :param english: An English message to translate.
        :return: Translated message for current locale, \
            same as ``english`` if not defined.
        """

        if english not in self._translation:
            return english
        elif _locale() in self._translation[english]:
            return self._translation[english][_locale()]
        elif (lang := _locale().split('_')[0]) in self._translation[english]:
            return self._translation[english][lang]
        else:
            return english
