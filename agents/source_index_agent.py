import time
from agents.llm_agent import LLMAgent
from parsers.markdown_chunker import MarkdownChunker
from pathlib import Path
from utils.logger import logger
from parsers.tokenizer import count_tokens
from parsers.json_extractor import JSONExtractor


class SourceIndexAgent:
    def __init__(self):
        self.llm = LLMAgent(task="index")
        self.chunker = MarkdownChunker()
        self.jsoner = JSONExtractor()

    def construct_prompt_with_context(self, query, chunks, offset=0, total_count=0):
        chunks_str = self.chunker.chunks_to_str(chunks, offset=offset)
        chunk_info_prompt = f"{len(chunks)} chunks from {offset+1} to {offset+len(chunks)} of {total_count} chunks."
        description_prompt = ""
        task_prompt = "Your task is to find most related chunks to answer my query."
        query_prompt = f"My query is: `{query}`."
        output_format_prompt = 'The 1st output is your question analysis and chunks scanning. The 2nd output should be a json list ([]), starts from "```json", and ends with "```". The list items are indexe numbers of chunks most related to answer the query. Do not return unrelated or too many. Return [] if no chunk related.'
        prompt = (
            f"Here are {chunk_info_prompt}. {description_prompt} {task_prompt}\n"
            f"{query_prompt}\n"
            f"{chunks_str}\n"
            f"Above are {chunk_info_prompt}. Remember, {description_prompt} {task_prompt}\n"
            f"{output_format_prompt}\n"
            f"Remember, {query_prompt}\n"
        )
        return prompt

    def chat(self, prompt, filepath, show_prompt=True):
        if show_prompt:
            prompt_token_count = count_tokens(prompt)
            logger.note(f"User: {prompt} [{prompt_token_count} tokens]")

        chunks = self.chunker.md_to_chunks_list(markdown_path=filepath)

        indexes_and_chunks = []
        chunk_num = 31
        for offset in range(0, len(chunks), chunk_num):
            chunks_part = chunks[offset : offset + chunk_num]

            prompt_with_context = self.construct_prompt_with_context(
                query=prompt, chunks=chunks_part, offset=offset, total_count=len(chunks)
            )
            response_content = self.llm.chat(
                prompt_with_context,
                temperature=0.1,
                show_prompt=False,
            )

            indexes = self.jsoner.to_obj(response_content)
            if indexes:
                indexes_and_chunks_part = [
                    {"index": index, "chunk": chunks[index - 1]}
                    for index in indexes
                    if offset <= index - 1 < offset + chunk_num
                ]
                indexes_and_chunks.extend(indexes_and_chunks_part)

        indexes_and_chunks = sorted(indexes_and_chunks, key=lambda x: x["index"])
        for item in indexes_and_chunks:
            logger.note(f"=== Chunk {item['index']} ===")
            logger.line(f"{item['chunk']}")

        logger.success(f"Related chunks {len(indexes_and_chunks)}/{len(chunks)}")

        return indexes_and_chunks


if __name__ == "__main__":
    agent = SourceIndexAgent()
    markdown_root = Path(__file__).parents[1] / "data" / "wikipedia"
    markdown_path = list(markdown_root.glob("*.md"))[0]
    # query = "From what references can I know more about Three Laws of Robotics?"
    query = "level 2 subheadings of toc in this doc"
    # query = "summarize this article"
    # query = "who is the partner of Olivaw?"
    # query = "3th reference of this article"
    result = agent.chat(query, markdown_path)

    # python -m agents.source_index_agent
