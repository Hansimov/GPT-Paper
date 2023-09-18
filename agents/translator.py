import os
from PyDeepLX import PyDeepLX
from deep_translator import (
    GoogleTranslator,
    MicrosoftTranslator,
    PonsTranslator,
    PapagoTranslator,
    DeeplTranslator,
    YandexTranslator,
    PapagoTranslator,
)
from utils.envs import enver


class Translator:
    TRANSLATOR_ENGINES = {
        "google": GoogleTranslator,
        "microsoft": MicrosoftTranslator,
        "papago": PapagoTranslator,
        "deepl": DeeplTranslator,
        "yandex": YandexTranslator,
        "papago": PapagoTranslator,
        "pons": PonsTranslator,
    }

    def __init__(self, source="auto", target="zh-CN", engine="deeplx"):
        self.source = source
        self.target = target
        self.engine = engine.lower()

    def translate(self, text):
        enver.set_envs(set_proxy=True)
        os.environ = enver.envs
        if self.engine == "deeplx":
            self.source = "auto"
            self.target = "ZH"
            translated_text = PyDeepLX.translate(
                text=text,
                sourceLang=self.source,
                targetLang=self.target,
                numberAlternative=1,
            )
        else:
            self.translator = self.TRANSLATOR_ENGINES[self.engine](
                source=self.source, target=self.target
            )
            translated_text = self.translator.translate(
                text, sources=self.source, targets=self.target
            )
        enver.restore_envs()
        os.environ = enver.envs
        return translated_text

    def translate_file(self, file_path):
        with open(file_path, "r") as rf:
            text = rf.read()
        translated_text = self.translate(text)
        return translated_text


if __name__ == "__main__":
    text = """
    The AI-based diagnosis was the first implementation of computer vision in pathology. Many pioneering studies had demonstrated that AI could approach even surpass pathologists on same specific tasks with reduced inter-observer variability.
    The auto-diagnosis of liver cancer via biopsy or surgical specimens were the first application of AI-based techniques in this filed. (JHEP Reports P 3-4) (JOH P1352). Kriegsmann et al. Implemented deep learning algorithms in liver pathology to optimize the diagnosis of benign lesions and adenocarcinoma metastasis, which showed high prediction capability with a case accuracy of 94%. In summary, the automated identification and diagnosis of tumor tissue in medical images is an effective replication of human pathologists’ jobs and help paving the path for more advanced tasks for AI, such as prognostification.
    """
    google_translator = Translator(engine="google")
    print(google_translator.translate(text))
    deeplx_translator = Translator(engine="deeplx")
    print(deeplx_translator.translate(text))
