import time
from agents.llm_agent import LLMAgent
from parsers.markdown_chunker import MarkdownChunker
from pathlib import Path
from utils.logger import logger
from parsers.tokenizer import count_tokens
from parsers.json_extractor import JSONExtractor


class SourceIndexAgent:
    def __init__(self):
        self.llm = LLMAgent(task="search")
        self.chunker = MarkdownChunker()
        self.jsoner = JSONExtractor()

    def construct_prompt_with_context(
        self,
        query,
        chunks,
        offset=0,
        total_count=0,
        past_result="",
    ):
        chunks_str = self.chunker.chunks_to_str(chunks, offset=offset)
        chunk_info_prompt = f"{len(chunks)} chunks (chunk {offset+1}-{offset+len(chunks)}) of {total_count} chunks"
        description_prompt = ""
        task_prompt = "Your are chunk scanner and source index retriever. Your task is to retrieve and recall all relevant chunks to answer the query."
        query_prompt = f"My query is: `{query}`."
        output_format_prompt = 'Your 1st output should be query analysis and user intention recognition. Your 2nd output should be scanning chunk by chunk based on query-relation analysis. Your 3rd output should be a json list ([]), starts from "```json", and ends with "```": The list items are indexes of chunks relevant to the query; Do not return non-relevant or too many; Return [] if no relevant chunk.'

        if past_result:
            past_result_str = f"\nFYI, here are the retrived chunks of past scans:\n```\n{past_result}\n```"
        else:
            past_result_str = ""

        prompt = (
            f"{description_prompt} {task_prompt}\n"
            f"{query_prompt}\n"
            f"{past_result_str}"
            f"\nHere are {chunk_info_prompt}:\n"
            f"\n{chunks_str}\n"
            f"Above are {chunk_info_prompt}.\n"
            f"Remember, {description_prompt} {task_prompt}\n"
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
        past_result_str = ""
        chunk_num = 10
        for offset in range(0, len(chunks), chunk_num):
            chunks_part = chunks[offset : offset + chunk_num]
            logger.note(
                f"> Scanning chunks: [{offset+1}-{offset+len(chunks_part)}]/{len(chunks)}"
            )
            prompt_with_context = self.construct_prompt_with_context(
                query=prompt,
                chunks=chunks_part,
                offset=offset,
                total_count=len(chunks),
                # past_result=past_result_str,
            )
            response_content = self.llm.chat(
                prompt_with_context,
                temperature=0.1,
                show_prompt=False,
            )

            indexes = self.jsoner.to_obj(response_content)
            if indexes:
                indexes_and_chunks_part = [
                    {"index": int(index), "chunk": chunks[int(index) - 1]}
                    for index in indexes
                    if offset <= int(index) - 1 < offset + chunk_num
                ]
                indexes_and_chunks.extend(indexes_and_chunks_part)
                past_result_chunks = [item["chunk"] for item in indexes_and_chunks_part]
                past_result_indexes = [
                    item["index"] - 1 for item in indexes_and_chunks_part
                ]
                past_result_str += self.chunker.chunks_to_str(
                    past_result_chunks, indexes=past_result_indexes
                )

        indexes_and_chunks = sorted(indexes_and_chunks, key=lambda x: x["index"])
        related_indexes = [item["index"] for item in indexes_and_chunks]
        logger.success(f"Related Indexes: {related_indexes}")
        for item in indexes_and_chunks:
            logger.note(f"=== Chunk {item['index']} ===")
            logger.line(f"{item['chunk']}")

        logger.success(f"Related chunks {len(indexes_and_chunks)}/{len(chunks)}")
        indexed_chunks_tokens = sum(
            [count_tokens(item["chunk"]) for item in indexes_and_chunks]
        )
        total_chunks_tokens = sum([count_tokens(chunk) for chunk in chunks])
        compression_ratio = indexed_chunks_tokens / total_chunks_tokens
        logger.success(
            f"Compress Ratio: {indexed_chunks_tokens}/{total_chunks_tokens} = {compression_ratio:.2}"
        )

        return indexes_and_chunks


if __name__ == "__main__":
    agent = SourceIndexAgent()
    markdown_root = Path(__file__).parents[1] / "data" / "wikipedia"
    markdown_path = list(markdown_root.glob("*.md"))[0]
    # query = "From what references can I know more about Three Laws of Robotics?"
    query = "list all level-2 headers"
    # query = "summarize this doc"
    # query = "who is the partner of Olivaw?"
    # query = "list the references related to the naked sun"
    # query = "list partners of olivaw"
    result = agent.chat(query, markdown_path)

    # python -m agents.source_index_agent
