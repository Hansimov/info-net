import re
from pathlib import Path
from utils.logger import logger


class MarkdownChunker:
    def __init__(self):
        self.sep = "=" * 4

    def to_list(self, markdown_path):
        with open(markdown_path, "r", encoding="utf-8") as rf:
            markdown_str = rf.read()
        chunks = re.split(r"\n{2,}", markdown_str)
        chunks = [chunk for chunk in chunks if chunk.strip()]
        return chunks

    def to_str(self, markdown_path):
        chunk_sep = "=" * 8
        chunks = self.to_list(markdown_path)
        chunks_str = ""
        for i, chunk in enumerate(chunks):
            chunk_head = f"{self.sep} Chunk {i+1} {self.sep}"
            chunks_str += f"{chunk_head}\n{chunk}\n\n"
        chunks_str = f"{chunk_sep}\n{chunks_str}\n{chunk_sep}\n"
        return chunks_str


if __name__ == "__main__":
    markdown_root = Path(__file__).parents[1] / "data" / "wikipedia"
    markdown_path = list(markdown_root.glob("*.md"))[0]
    chunker = MarkdownChunker()
    chunks_str = chunker.to_str(markdown_path)
    logger.mesg(chunks_str)

    # python -m parsers.markdown_chunker
