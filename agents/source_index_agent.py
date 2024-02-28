from agents.llm_agent import LLMAgent
from parsers.markdown_chunker import MarkdownChunker
from pathlib import Path
from utils.logger import logger
from parsers.tokenizer import count_tokens


class SourceIndexAgent:
    def __init__(self):
        self.llm = LLMAgent(
            task="index",
            system_prompt="You are InfoNet, an Information Source Tracing Neural Network which can find sources from given context for user questions. You are developped by Hansimov.",
        )
        self.chunker = MarkdownChunker()

    def construct_prompt_with_context(self, query, filepath):
        chunks = self.chunker.to_list(filepath)
        chunks_str = self.chunker.to_str(filepath)
        chunk_info_prompt = f'{len(chunks)} chunks from file: "{filepath.name}"'
        task_prompt = "Your task is to find all related chunks to answer my query."
        query_prompt = f"My query is: `{query}`"
        output_format_prompt = "Your output should be a json list, which starts from '```json', and ends with '```'. The list items must be the indexes of all related chunks answer my query."
        prompt = (
            f"Here are {chunk_info_prompt}. {task_prompt}\n"
            f"{query_prompt}\n"
            f"{chunks_str}\n"
            f"Above are {chunk_info_prompt}. Remember, {task_prompt}\n"
            f"{output_format_prompt}\n"
            f"Remember, {query_prompt}\n"
        )
        return prompt

    def chat(self, prompt, filepath, show_prompt=True):
        if show_prompt:
            prompt_token_count = count_tokens(prompt)
            logger.note(f"User: {prompt} [{prompt_token_count} tokens]")

        prompt_with_context = self.construct_prompt_with_context(prompt, filepath)
        result = self.llm.chat(prompt_with_context, temperature=0.1, show_prompt=False)
        return result


if __name__ == "__main__":
    agent = SourceIndexAgent()
    markdown_root = Path(__file__).parents[1] / "data" / "wikipedia"
    markdown_path = list(markdown_root.glob("*.md"))[0]
    # query = "From what references can I know more about Three Laws of Robotics?"
    query = "table of content of this article"
    agent.chat(query, markdown_path)

    # python -m agents.source_index_agent
