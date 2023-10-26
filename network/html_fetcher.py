import json
import re
from pathlib import Path

# from requests_html import HTMLSession
import requests
from documents.ar5iv_html_nodelizer import Ar5ivHTMLNodelizer
from requests_ntlm import HttpNtlmAuth


class UrlToPathConverter:
    def __init__(self, url):
        self.url = url
        self.html_dir = Path(__file__).parents[1] / "files" / "htmls"
        self.url_to_path()

    def url_to_path(self):
        if self.match_pattern("ar5iv"):
            # https://ar5iv.labs.arxiv.org/html/1810.04805
            match_res = self.match_pattern("ar5iv")
            self.output_dir = self.html_dir / "ar5iv"
            self.output_filename = match_res.group(1) + ".html"
            self.output_path = self.output_dir / self.output_filename
            self.requests_auth = None
        elif self.match_pattern("docs.com"):
            # https://docs.***.com/documents/**.html
            match_res = self.match_pattern("docs.com")
            self.output_dir = self.html_dir / match_res.group(1)
            self.output_filename = match_res.group(2)
            self.output_path = self.output_dir / self.output_filename
            self.requests_auth = "ntlm"
        else:
            raise NotImplementedError(f"Not supported URL format: {self.url}")

    def match_pattern(self, pattern):
        patterns = {
            "ar5iv": "ar5iv\.labs\.arxiv\.org/html/(.*)",
            "docs.com": "docs\.(.*)\.com/documents/(.*\.html)",
        }
        return re.search(patterns[pattern], self.url)


class HTMLFetcher:
    def __init__(self, url):
        self.url = url
        url_to_path_converter = UrlToPathConverter(self.url)
        self.output_path = url_to_path_converter.output_path
        self.requests_auth = url_to_path_converter.requests_auth

    def get(self, overwrite=True):
        print(f"Fetching {self.url}")
        if self.output_path.exists() and not overwrite:
            # print(f"HTML exists: {self.output_path}")
            return

        if self.requests_auth is None:
            res = requests.get(self.url)
        elif self.requests_auth == "ntlm":
            print("(Using NTLM auth)")
            with open(Path(__file__).parents[1] / "secrets.json") as rf:
                secrets = json.load(rf)
            user = secrets["user"]
            password = secrets["password"]
            cert = secrets["cert"]
            cert_path = Path(__file__).parents[1] / cert
            res = requests.get(
                self.url, auth=HttpNtlmAuth(user, password), verify=cert_path
            )
        else:
            raise NotImplementedError(f"Not supported requests_auth: {requests_auth}")

        self.html_str = res.text

    def save(self, overwrite=True):
        print(f"Dump HTML: {self.output_path}")
        if self.output_path.exists() and not overwrite:
            # print(f"HTML exists: {self.output_path}")
            return
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_path, "w") as wf:
            wf.write(self.html_str)

    def run(self):
        overwrite = True
        if self.output_path.exists() and not overwrite:
            print(f"URL cached: {self.url}")
            print(f"HTML exists: {self.output_path}")
        else:
            self.get(overwrite=overwrite)
            self.save(overwrite=overwrite)


if __name__ == "__main__":
    url = "https://ar5iv.labs.arxiv.org/html/1810.04805"
    html_fetcher = HTMLFetcher(url)
    html_fetcher.run()
    ar5iv_html_nodelizer = Ar5ivHTMLNodelizer(html_fetcher.output_path)
    ar5iv_html_nodelizer.run()
