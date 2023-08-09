import tiktoken
from utils.logger import Logger


logger = Logger().logger


class Tokenizer:
    """
    * How to count tokens with tiktoken · openai-cookbook
        * https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb


    Encoding name	    | OpenAI models
    :-------------------|:-------------------------------------------------
    cl100k_base	        | gpt-4, gpt-3.5-turbo, text-embedding-ada-002
    p50k_base	        | Codex models, text-davinci-002, text-davinci-003
    r50k_base (or gpt2)	| GPT-3 models like davinci
    -----------------------------------------------------------------------
    """

    def __init__(self, model="text-embedding-ada-002"):
        self.model = model
        self.encoding_name = None
        self.get_encoder_by_model()

    def get_encoder_by_model(self):
        self.encoding_model_map = {
            "cl100k_base": ["gpt-4", "gpt-3.5-turbo", "text-embedding-ada-002"],
            "p50k_base": ["Codex models", "text-davinci-002", "text-davinci-003"],
        }

        for encoding, models in self.encoding_model_map.items():
            if self.model in models:
                self.encoding_name = encoding
                self.encoder = tiktoken.get_encoding(self.encoding_name)
                break

        if not self.encoding_name:
            raise ValueError(f"No valid encoding for model: {self.model}")

    def count_tokens(self, text):
        tokens = self.encoder.encode(text)
        token_cnt = len(tokens)
        logger.debug(f"{token_cnt} tokens of text: [{text}]")
        return token_cnt


if __name__ == "__main__":
    tokenizer = Tokenizer()
    tokenizer.count_tokens("你好吗？我的朋友。")
