import json
from pathlib import Path
from openai import OpenAI
from utils.logger import logger, Runtimer
from tiktoken import get_encoding as tiktoken_get_encoding


class LLMAgent:
    def __init__(self, system_prompt="", source="chat"):
        self.system_prompt = system_prompt
        self.source = source
        self.tokenizer = tiktoken_get_encoding("cl100k_base")
        self.init_endpoint_and_key_by_source()

    def count_tokens(self, content):
        tokens = self.tokenizer.encode(content)
        return len(tokens)

    def init_endpoint_and_key_by_source(self):
        endpoints_json_path = Path(__file__).parents[1] / "configs" / "endpoints.json"
        if not endpoints_json_path.exists():
            raise FileNotFoundError(
                f"> Endpoints JSON not found: {endpoints_json_path}"
            )
        with open(endpoints_json_path, "r") as rf:
            endpoints = json.load(rf)

        llm_meta = endpoints[self.source]

        self.endpoint, self.api_key, self.model = list(
            map(llm_meta.get, ["endpoint", "api_key", "model"])
        )
        if any([not self.endpoint, not self.api_key, not self.model]):
            raise ValueError(f"> Invalid LLM Meta: {llm_meta}")

        self.client = OpenAI(base_url=self.endpoint, api_key=self.api_key)

    def content_to_message(self, role="user", content=""):
        return {"role": role, "content": content}

    def prompt_to_messages(self, prompt):
        messages = []
        if self.system_prompt:
            messages.append(
                self.content_to_message(role="system", content=self.system_prompt)
            )
        messages.append(self.content_to_message(role="user", content=prompt))
        return messages

    def chat(self, prompt, temeperature=0.5, show_prompt=True):
        timer = Runtimer(is_log=False)
        timer.start_time()
        if show_prompt:
            prompt_token_count = self.count_tokens(prompt)
            system_prompt_token_count = self.count_tokens(self.system_prompt)
            logger.note(f"User: {prompt} [{prompt_token_count} tokens]")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.prompt_to_messages(prompt),
            temperature=temeperature,
            stream=True,
        )
        result = ""
        for chunk in response:
            choice = chunk.choices[0]
            delta_content = choice.delta.content
            if delta_content:
                result += delta_content
                logger.mesg(delta_content, end="")
            elif choice.finish_reason == "stop":
                timer.end_time()
                elapsed_time_str = timer.time2str(timer.elapsed_time(), unit_sep="")
                result_token_count = self.count_tokens(result)
                total_token_count = (
                    result_token_count + prompt_token_count + system_prompt_token_count
                )
                logger.success(
                    # f"\n[Done] "
                    f"\n[{elapsed_time_str}] "
                    f"[Tokens: {result_token_count}/{total_token_count} (response/total)] "
                )
            else:
                pass

        return result


if __name__ == "__main__":
    agent = LLMAgent(
        source="chat",
        system_prompt="You are InfoNet, an Information Source Tracing Neural Network which can find sources from given context for user questions. You are developped by Hansimov.",
    )
    agent.chat("Tell me your short name.", temeperature=0.1)

    # python -m agents.llm_chatter
