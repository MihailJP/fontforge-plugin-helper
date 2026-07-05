from locale import getlocale, LC_MESSAGES


def _locale() -> str:
    return (getlocale(LC_MESSAGES)[0]) or (getlocale()[0]) or 'C'


class Translations():
    _translation = {}

    def set(self, lang: str, english: str, translation: str):
        self._translation.setdefault(english, {})
        self._translation[english][lang] = translation

    def setTranslations(self, lang: str, translations: dict[str, str]):
        for k, v in translations.items():
            self.set(lang, k, v)

    def get(self, english: str) -> str:
        if english not in self._translation:
            return english
        elif _locale() in self._translation[english]:
            return self._translation[english][_locale()]
        elif (lang := _locale().split('_')[0]) in self._translation[english]:
            return self._translation[english][lang]
        else:
            return english
