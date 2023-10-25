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
