from pathlib import Path
from requests_html import HTMLSession
from documents.ar5iv_html_nodelizer import Ar5ivHTMLNodelizer


class HTMLFetcher:
    def __init__(self, url):
        self.url = url
        self.html_dir = Path(__file__).parents[1] / "files" / "htmls"
        self.url_to_path()

    def is_local_html_exists(self):
        if self.output_path.exists():
            return True

    def url_to_path(self):
        # https://ar5iv.labs.arxiv.org/html/1810.04805
        if "ar5iv.labs.arxiv" in self.url:
            self.output_filename = self.url.split("/")[-1] + ".html"
            self.output_dir = self.html_dir / "ar5iv"
            self.output_path = self.output_dir / self.output_filename

    def get(self):
        print(f"Fetching {self.url}")
        if self.is_local_html_exists():
            # print(f"HTML exists: {self.output_path}")
            return
        s = HTMLSession()
        r = s.get(self.url)
        self.html_str = r.html.html

    def save(self, overwrite=False):
        print(f"Dump HTML: {self.output_path}")
        if self.is_local_html_exists() and not overwrite:
            # print(f"HTML exists: {self.output_path}")
            return
        self.output_dir.mkdir(parents=True, exist_ok=True)

        with open(self.output_path, "w") as wf:
            wf.write(self.html_str)

    def run(self):
        if self.is_local_html_exists():
            print(f"URL cached: {self.url}")
            print(f"HTML exists: {self.output_path}")
        else:
            self.get()
            self.save()


if __name__ == "__main__":
    url = "https://ar5iv.labs.arxiv.org/html/1810.04805"
    html_fetcher = HTMLFetcher(url)
    html_fetcher.run()
    ar5iv_html_nodelizer = Ar5ivHTMLNodelizer(html_fetcher.output_path)
    ar5iv_html_nodelizer.run()
