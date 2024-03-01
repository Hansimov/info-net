import re
from pathlib import Path
from utils.logger import logger


class MarkdownChunker:
    def __init__(self):
        self.sep = ">" * 6
        self.chunk_sep_head = "<" * 3
        self.chunk_sep_tail = ">" * 3

    def md_to_chunks_list(self, markdown_path=None, markdown_str=None):
        if (not markdown_path) and (not markdown_str):
            raise ValueError("Either markdown_path or markdown_str should be provided.")
        if markdown_path:
            with open(markdown_path, "r", encoding="utf-8") as rf:
                markdown_str = rf.read()
        chunks = re.split(r"\n{2,}", markdown_str)
        chunks = [chunk for chunk in chunks if chunk.strip()]
        return chunks

    def chunks_to_str(self, chunks, offset=0, indexes=None):
        chunks_str = ""
        if not chunks:
            return chunks_str
        if not indexes:
            indexes = list(range(offset, offset + len(chunks)))
        for idx, chunk in zip(indexes, chunks):
            chunk_head = (
                f"{self.chunk_sep_head} Chunk {idx+1} Start {self.chunk_sep_tail}"
            )
            chunk_tail = f"{self.chunk_sep_head} {self.chunk_sep_tail}"
            chunks_str += f"{chunk_head}\n{chunk}\n{chunk_tail}\n\n"
        # chunks_str = f"{self.sep}\n{chunks_str}\n{self.sep}\n"
        chunks_str = f"{chunks_str}"
        return chunks_str

    def md_to_chunks_str(self, markdown_path=None, markdown_str=None, offset=0):
        chunks = self.md_to_chunks_list(
            markdown_path=markdown_path, markdown_str=markdown_str
        )
        chunks_str = self.chunks_to_str(chunks, offset=offset)
        txt_path = Path(markdown_path).with_suffix(".txt")
        with open(txt_path, "w", encoding="utf-8") as wf:
            wf.write(chunks_str)
        return chunks_str


if __name__ == "__main__":
    markdown_root = Path(__file__).parents[1] / "data" / "wikipedia"
    markdown_path = list(markdown_root.glob("*.md"))[0]
    chunker = MarkdownChunker()
    chunks_str = chunker.to_str(markdown_path)
    logger.mesg(chunks_str)

    # python -m parsers.markdown_chunker
