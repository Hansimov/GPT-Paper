from pathlib import Path
from agents.translator import Translator
import pandas as pd
import pickle


class TextTranslator:
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.translations_cache_path = (
            Path(__file__).parents[1]
            / "pdfs"
            / project_dir
            / "_results"
            / "translations_cache.pkl"
        )
        self.translator = Translator(engine="deeplx")

    def translate(self, text, cache=True):
        # See below link for similar cache mechanism
        # LINK documents/multi_pdf_extractor.py#query-docs
        # LINK documents/multi_pdf_extractor.py#dump-query-results-indexes
        if cache:
            if self.translations_cache_path.exists():
                translations_cache_df = pd.read_pickle(self.translations_cache_path)

                cached_translations_row = translations_cache_df.loc[
                    translations_cache_df["text"] == text
                ]
                cached_translations_row_num = cached_translations_row.shape[0]
                if cached_translations_row_num >= 1:
                    translated_text = cached_translations_row["translation"].iloc[0]
                    return translated_text
            else:
                translations_cache_df = pd.DataFrame()

        translated_text = self.translator.translate(text)
        print(translated_text)

        if cache:
            translation_df = pd.DataFrame(
                [{"text": text, "translation": translated_text}]
            )
            translations_cache_df = pd.concat(
                [translations_cache_df, translation_df], ignore_index=True
            )
            translations_cache_df.to_pickle(self.translations_cache_path)

        return translated_text


if __name__ == "__main__":
    text_translator = TextTranslator("cancer_review")
    text = "Example-based explanation often optimizes the hidden layers deep in the neural network (i.e., the latent space) in such a way that similar points are close to each other in this latent space, while dissimilar points are further away in the latent space."
    text_translator.translate(text)
