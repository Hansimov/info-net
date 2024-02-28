import wikipediaapi
from utils.logger import logger


class WikipediaFetcher:
    def __init__(self, lang="en"):
        self.lang = lang
        user_agent = "https://github.com/Hansimov/info-net"
        self.wk = wikipediaapi.Wikipedia(
            user_agent=user_agent,
            language=self.lang,
            extract_format=wikipediaapi.ExtractFormat.HTML,
        )

    def fetch(self, title):
        logger.note(f"> Fetching from Wikipedia: [{title}]")

        page = self.wk.page(title)
        if not page.exists():
            logger.warn(f"Page does not exist: [{title}]")
        else:
            fullurl = page.fullurl
            logger.file(f"  - {fullurl}")
            # summary = page.summary
            text = page.text
            links = page.links
            logger.success(f"  - {text}")
            # logger.success(page.wiki)
            logger.note(dir(page))
            # logger.success(page.links)
            for k, v in links.items():
                logger.file(f"    - {k}: {v}")


if __name__ == "__main__":
    fetcher = WikipediaFetcher()
    keyword = "R._Daneel_Olivaw"
    fetcher.fetch(keyword)
    # python -m networks.wikipedia_fetcher
