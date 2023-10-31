import re

from pathlib import Path
from requests_ntlm import HttpNtlmAuth


class UrlToPathConverter:
    def __init__(self, url):
        self.url = url
        self.html_dir = Path(__file__).parents[2] / "files" / "htmls"
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
                "ar5iv.labs.arxiv.org/html/(.*)",
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
