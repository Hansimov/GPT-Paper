from documents.keyword_searcher import KeywordSearcher
from documents.htmls.html_keyword_highlighter import HTMLKeywordHighlighter


class NodeSearcher:
    def __init__(self, nodes, keywords):
        self.nodes = nodes
        self.keywords = keywords
        self.search()

    def search(self, search_full_text=True, return_full_node=True):
        searched_nodes = []
        for node in self.nodes:
            if not node.type.endswith("group"):
                if search_full_text:
                    text_to_search = node.get_full_text()
                else:
                    text_to_search = node.get_text()

                if text_to_search is None:
                    print(node.element)
                    print("search_by_keyword(): node.get_text() is None!")
                    raise NotImplementedError

                keyword_searcher = KeywordSearcher(self.keywords, text_to_search)
                if keyword_searcher.searched_texts:
                    print(keyword_searcher.search_score)

                    if return_full_node:
                        searched_node = node.get_full_node(keyword=self.keywords)
                    else:
                        searched_node = node

                    if type(searched_node) == list:
                        searched_nodes.extend(searched_node)
                    else:
                        searched_nodes.append(searched_node)

        searched_nodes = self.remove_duplicated_nodes(searched_nodes)

        for idx, node in enumerate(searched_nodes):
            print(f"{idx+1}: {node.type} ({node.idx})")
            # print(f"{node.get_full_text()}")
            node.marked_element = HTMLKeywordHighlighter(
                node.element, self.keywords
            ).marked_element
        return searched_nodes

    def remove_duplicated_nodes(self, nodes):
        return sorted(
            list({node.idx: node for node in nodes}.values()), key=lambda x: x.idx
        )
