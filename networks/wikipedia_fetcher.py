import requests
from pathlib import Path
from utils.logger import logger


class WikipediaFetcher:
    def __init__(self, lang="en"):
        self.lang = lang
        self.url_head = "https://en.wikipedia.org/wiki/"
        self.output_folder = Path(__file__).parents[1] / "data" / "wikipedia"

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

    def fetch(self, title, save=True, overwrite=False):
        logger.note(f"> Fetching from Wikipedia: [{title}]")
        self.output_path = self.output_folder / f"{title}.html"
        if not overwrite and self.output_path.exists():
            logger.mesg(f"  > HTML exists: {self.output_path}")
            return

        self.url = self.url_head + title
        req = requests.get(self.url, headers=self.headers)

        status_code = req.status_code
        if status_code == 200:
            logger.file(f"  - [{status_code}] {self.url}")
            if save:
                self.output_folder.mkdir(parents=True, exist_ok=True)
                with open(self.output_path, "w", encoding="utf-8") as wf:
                    wf.write(req.text)
                logger.success(f"  > Saved at: {self.output_path}")
        elif status_code == 404:
            logger.err(f"{status_code} - Page not found : [{title}]")
            return
        else:
            logger.err(f"{status_code} Error")


if __name__ == "__main__":
    fetcher = WikipediaFetcher()
    keyword = "R._Daneel_Olivaw"
    fetcher.fetch(keyword)
    # python -m networks.wikipedia_fetcher
