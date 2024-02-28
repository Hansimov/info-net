import re
from pathlib import Path
from utils.logger import logger


class MarkdownChunker:
    def __init__(self):
        self.sep = "=" * 4

    def to_chunk_list(self):
        with open(self.markdown_path, "r", encoding="utf-8") as rf:
            markdown_str = rf.read()
        chunks = re.split(r"\n{2,}", markdown_str)
        chunks = [chunk for chunk in chunks if chunk.strip()]
        return chunks

    def to_chunks_str(self, markdown_path):
        self.markdown_path = markdown_path
        chunks = self.to_chunk_list()
        chunks_str = ""
        for i, chunk in enumerate(chunks):
            chunk_head = f"{self.sep} Chunk {i+1} {self.sep}"
            chunks_str += f"{chunk_head}\n{chunk}\n\n"
        return chunks_str


if __name__ == "__main__":
    markdown_root = Path(__file__).parents[1] / "data" / "wikipedia"
    markdown_path = list(markdown_root.glob("*.md"))[0]
    chunker = MarkdownChunker()
    chunks_str = chunker.to_chunks_str(markdown_path)
    logger.mesg(chunks_str)
    # python -m parsers.markdown_chunker