import json
import re
import requests

from pathlib import Path
from requests_ntlm import HttpNtlmAuth


class UrlToPathConverter:
    def __init__(self, url):
        self.url = url
        self.html_dir = Path(__file__).parents[1] / "files" / "htmls"
        self.url_to_path()

    def url_to_path(self):
        self.domain, match_res = self.match_pattern()
        if self.domain == "arxiv":
            # https://ar5iv.labs.arxiv.org/html/1810.04805
            # https://arxiv.org/pdf/1810.04805.pdf
            # https://arxiv.org/abs/1810.04805
            self.output_dir = self.html_dir / "arxiv"
            self.output_filename = match_res.group(1) + ".html"
            self.output_path = self.output_dir / self.output_filename
            self.html_url = f"https://ar5iv.labs.arxiv.org/html/{match_res.group(1)}"
            self.requests_auth = None
        elif self.domain == "docs.com":
            # https://docs.***.com/documents/**.html
            self.output_dir = self.html_dir / match_res.group(1).replace("%20", " ")
            self.output_filename = match_res.group(2).replace("%20", " ")
            self.output_path = self.output_dir / self.output_filename
            self.html_url = self.url
            self.requests_auth = "ntlm"
        else:
            raise NotImplementedError(f"Not supported URL format: {self.url}")

    def match_pattern(self):
        domain_patterns = {
            "arxiv": [
                "ar5iv\.labs\.arxiv\.org/html/(.*)",
                "arxiv.org/pdf/(.*).pdf",
                "arxiv.org/abs/(.*)",
            ],
            "docs.com": ["docs\.(.*)\.com/documents/(.*\.html)"],
        }
        for domain in domain_patterns.keys():
            for pattern in domain_patterns[domain]:
                match_res = re.search(pattern, self.url)
                if match_res:
                    return domain, match_res
        return None, None


class HTMLFetcher:
    def __init__(self, url):
        self.url = url
        url_converter = UrlToPathConverter(self.url)
        self.output_path = url_converter.output_path
        self.requests_auth = url_converter.requests_auth
        self.domain = url_converter.domain
        self.html_url = url_converter.html_url

    def get(self, overwrite=True):
        print(f"Fetching {self.html_url}")
        if self.output_path.exists() and not overwrite:
            # print(f"HTML exists: {self.output_path}")
            return

        if self.requests_auth is None:
            res = requests.get(self.url)
        elif self.requests_auth == "ntlm":
            print("(Using NTLM auth)")
            with open(Path(__file__).parents[1] / "secrets.json") as rf:
                secrets = json.load(rf)
            user, password, cert = secrets["user"], secrets["password"], secrets["cert"]
            cert_path = Path(__file__).parents[1] / cert
            res = requests.get(
                self.html_url, auth=HttpNtlmAuth(user, password), verify=cert_path
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

        with open(self.output_path, "w", encoding="utf-8") as wf:
            wf.write(self.html_str)

    def run(self, overwrite=False):
        if self.output_path.exists() and not overwrite:
            print(f"URL cached: {self.url}")
            print(f"HTML exists: {self.output_path}")
        else:
            self.get(overwrite=overwrite)
            self.save(overwrite=overwrite)


if __name__ == "__main__":
    # url = "https://ar5iv.labs.arxiv.org/html/1810.04805"
    url = "https://arxiv.org/abs/1810.04805"
    html_fetcher = HTMLFetcher(url)
    html_fetcher.run()
