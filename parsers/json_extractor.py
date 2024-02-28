import re
import json

from utils.logger import logger


class JSONExtractor:
    def to_str(self, text):
        json_res = re.search(r"```(json)?(.+?)```", text, re.DOTALL)
        if json_res:
            json_str = json_res.group(2).strip()
            return json_str
        else:
            return None

    def to_obj(self, text):
        json_res = self.to_str(text)
        if json_res:
            try:
                json_obj = json.loads(json_res)
                return json_obj
            except:
                return None


if __name__ == "__main__":
    extractor = JSONExtractor()
    text = """
    Here is the JSON output:
    ```json
    [5, 6, 20, 29]
    ```
    This output is a list of integers.
    """
    json_obj = extractor.to_obj(text)
    logger.success(json_obj)

    # python -m parsers.json_extractor
