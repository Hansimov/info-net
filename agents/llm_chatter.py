import json
from pathlib import Path
from openai import OpenAI
from utils.logger import logger


class LLMAgent:
    def __init__(self, system_prompt="", source="chat"):
        self.system_prompt = system_prompt
        self.source = source
        self.init_endpoint_and_key_by_source()

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
        if show_prompt:
            logger.note(f"User: {prompt}")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.prompt_to_messages(prompt),
            temperature=temeperature,
            stream=True,
        )
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                logger.mesg(chunk.choices[0].delta.content, end="")
            elif chunk.choices[0].finish_reason == "stop":
                logger.success("\n[Finished]")
            else:
                pass


if __name__ == "__main__":
    agent = LLMAgent(source="chat")
    agent.chat("Hello, how are you?")

    # python -m agents.llm_chatter
