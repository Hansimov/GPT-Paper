import itertools
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from thefuzz import fuzz


class KeywordSearcher:
    def __init__(self, keyword, text_to_search):
        self.keyword = keyword
        self.text_to_search = text_to_search
        self.search()

    def search(self, fuzzy=True, fuzzy_threshold=90):
        self.searched_texts = []
        keyword_is_found = False
        search_score = 0

        if self.keyword.strip().lower() in self.text_to_search.strip().lower():
            keyword_is_found = True
            search_score = 100

        if fuzzy:
            fuzzy_score = fuzz.token_set_ratio(self.keyword, self.text_to_search)
            if fuzzy_score >= fuzzy_threshold:
                keyword_is_found = True

        if keyword_is_found:
            self.searched_texts.append(self.keyword)

        self.search_score = max(search_score, fuzzy_score)
        return self.searched_texts, self.search_score


class ImportantKeywordSearcher:
    def __init__(self, corpus, keywords):
        self.corpus = corpus
        self.original_keywords = keywords

    def split_keywords(self):
        keywords = self.original_keywords.lower()
        keywords = re.sub(r"\W+", " ", keywords)
        if isinstance(keywords, str):
            self.keywords = keywords.split()
        elif isinstance(keywords, list):
            self.keywords = [keyword.split() for keyword in keywords]
            self.keywords = list(itertools.chain.from_iterable(self.keywords))
        else:
            raise ValueError("Keywords must be str or list[str]!")

    def vectorize_corpus(self):
        self.tfidf_vectorizer = TfidfVectorizer(vocabulary=self.keywords)
        self.count_vectorizer = CountVectorizer(vocabulary=self.keywords)

    def search(self):
        self.split_keywords()
        self.vectorize_corpus()

        tfidf_scores = self.tfidf_vectorizer.fit_transform(self.corpus)

        df = pd.DataFrame(
            tfidf_scores.toarray(),
            columns=self.tfidf_vectorizer.get_feature_names_out(),
        )

        # count_scores = self.count_vectorizer.fit_transform(self.corpus)
        # df = pd.DataFrame(
        #     count_scores.toarray(),
        #     columns=self.count_vectorizer.get_feature_names_out(),
        # )

        df["tfidf_score_sum"] = df[df.columns].sum(axis=1)
        df["corpus"] = self.corpus
        df = df[df.iloc[:, :-2].sum(axis=1) > 0]
        df = df.sort_values(by="tfidf_score_sum", ascending=False)
        df = df.reset_index(drop=True)
        print(df)


if __name__ == "__main__":
    # url = "https://arxiv.org/abs/2303.08774"
    from networks.html_fetcher import HTMLFetcher
    from documents.htmls.html_nodelizer import HTMLNodelizer

    html_fetcher = HTMLFetcher(url)
    html_fetcher.run()
    html_nodelizer = HTMLNodelizer(
        html_path=html_fetcher.output_path,
        url=html_fetcher.html_url,
        domain=html_fetcher.domain,
    )
    html_nodelizer.run()

    keywords = "who are the authors"
    print(keywords)
    corpus = [
        node.get_full_text()
        for node in html_nodelizer.nodes
        if not node.type.endswith("group")
    ]
    important_keyword_searcher = ImportantKeywordSearcher(
        keywords=keywords, corpus=corpus
    )
    important_keyword_searcher.search()
