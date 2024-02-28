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

    def construct_prompt_with_context(self, query, filepath):
        chunks = self.chunker.to_list(filepath)
        chunks_str = self.chunker.to_str(filepath)
        chunk_info_prompt = f'{len(chunks)} chunks from file: "{filepath.name}"'
        description_prompt = "You should treat symbols [1] as reference and citation."
        task_prompt = "Your task is to find most related chunks to answer my query."
        query_prompt = f"My query is: `{query}`"
        output_format_prompt = "Your output should be a json list, which starts from '```json', and ends with '```'. The list items are the indexes of all the most related chunks to answer the query. Do not return unrelated chunks or too many chunks."
        prompt = (
            f"Here are {chunk_info_prompt}. {description_prompt} {task_prompt}\n"
            f"{query_prompt}\n"
            f"{chunks_str}\n"
            f"Above are {chunk_info_prompt}. Remember, {description_prompt} {task_prompt}\n"
            f"{output_format_prompt}\n"
            f"Remember, {query_prompt}\n"
        )
        return prompt, chunks

    def chat(self, prompt, filepath, show_prompt=True):
        if show_prompt:
            prompt_token_count = count_tokens(prompt)
            logger.note(f"User: {prompt} [{prompt_token_count} tokens]")

        prompt_with_context, chunks = self.construct_prompt_with_context(
            prompt, filepath
        )
        response_content = self.llm.chat(
            prompt_with_context,
            temperature=0.1,
            max_tokens=int(2.5 * len(chunks)),
            show_prompt=False,
        )

        indexes = self.jsoner.to_obj(response_content)
        indexes_and_chunks = [
            {
                "index": index,
                "chunk": chunks[index - 1],
            }
            for index in indexes
            if index <= len(chunks)
        ]
        for item in indexes_and_chunks:
            logger.note(f"=== Chunk {item['index']} ===")
            logger.line(f"{item['chunk']}")

        return indexes_and_chunks


if __name__ == "__main__":
    agent = SourceIndexAgent()
    markdown_root = Path(__file__).parents[1] / "data" / "wikipedia"
    markdown_path = list(markdown_root.glob("*.md"))[0]
    # query = "From what references can I know more about Three Laws of Robotics?"
    query = "level 2 headers of this article"
    result = agent.chat(query, markdown_path)

    # python -m agents.source_index_agent
