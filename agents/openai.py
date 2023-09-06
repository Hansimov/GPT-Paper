import httpx
import inspect
import json
import os
import re
from utils.envs import enver
from utils.tokenizer import WordTokenizer


class OpenAIAgent:
    """
    OpenAI API doc:
      * https://platform.openai.com/docs/api-reference/chat/create
    """

    endpoint_apis = {
        "openai": {
            "url": "https://api.openai.com",
            "chat": "/v1/chat/completions",
            "models": "/v1/models",
        },
        "ninomae": {
            "url": "https://api-thanks.ninomae.live",
            "chat": "/chat/completions",
            "models": "/models",
        },
    }
    continous_token_thresholds = {
        "gpt-4": 950,
    }

    def __init__(
        self,
        name="",  # name of the agent, also use "role" as alias
        endpoint_name="ninomae",
        model="gpt-3.5-turbo",
        temperature=0,
        system_message=None,
        max_input_message_chars=None,
        memory=False,
        record=True,
    ):
        self.name = name
        self.endpoint_name = endpoint_name
        self.endpoint = self.endpoint_apis[self.endpoint_name]
        self.endpoint_url = self.endpoint["url"]
        self.chat_api = self.endpoint_url + self.endpoint["chat"]
        self.memory = memory
        self.record = record
        self.history_messages = []
        self.response_content = ""

        self.model = model
        self.temperature = temperature
        self.system_message = system_message
        self.max_input_message_chars = max_input_message_chars
        self.word_tokenizer = WordTokenizer()
        self.calc_max_input_message_chars()
        self.init_history_messages()

    def init_history_messages(self):
        if self.system_message:
            self.history_messages.append(
                self.content_to_message("system", self.system_message)
            )

    def content_to_message(self, role, content):
        return {"role": role, "content": content}

    def update_history_messages(self, role, content):
        message = self.content_to_message(role, content)
        self.history_messages.append(message)

        if role == "system":
            self.system_message = content
        self.update_system_message()

    def update_system_message(self, system_message=None):
        """It assumes that there is at most one system message."""
        if system_message:
            self.system_message = system_message
        if not self.system_message:
            return

        def get_system_message_idx():
            for idx, message in enumerate(self.history_messages):
                if message["role"] == "system":
                    return idx
            return None

        system_message_idx = get_system_message_idx()
        if system_message_idx is None:
            self.history_messages.insert(
                0, self.content_to_message("system", self.system_message)
            )
        else:
            self.history_messages[system_message_idx]["content"] = self.system_message

    def get_messages_without_memory(self):
        messages = [
            message for message in self.history_messages if message["role"] == "system"
        ]
        return messages

    def clear_history_messages(self, keep_system_message=True):
        self.history_messages = []
        if keep_system_message:
            self.init_history_messages()

        self.models_api = self.endpoint_url + self.endpoint["models"]
        self.available_models = []

    def get_available_models(self):
        """
        gpt-3.5-turbo, gpt-4, gpt-4-internet, claude-2,
        poe-llama-2-7b, poe-llama-2-13b, poe-llama-2-70b,
        poe-gpt-3.5-turbo, poe-saga, poe-claude-instant, poe-google-palm,
        """
        self.models_api = self.endpoint_url + self.endpoint["models"]
        self.available_models = []
        response = httpx.get(self.models_api)
        data = response.json()["data"]

        for item in data:
            self.available_models.append(item["id"])
        print(self.available_models)

        return self.available_models

    def calc_max_input_message_chars(self):
        if self.max_input_message_chars is None:
            max_input_chars_per_model = {
                16000: [
                    "gpt-3.5-turbo-16k",
                    "gpt-3.5-turbo-16k-openai",
                    "gpt-3.5-turbo-16k-poe",
                ],
                32000: ["gpt-4-32k", "gpt-4-32k-poe"],
                100000: ["claude-2-100k", "claude-instant-100k"],
            }
            self.max_input_message_chars = 8000
            for max_chars, models in max_input_chars_per_model.items():
                if self.model in models:
                    self.max_input_message_chars = max_chars
                    break

    def chat(
        self,
        prompt="",
        stream=True,
        record=True,
        continous=False,
        continous_token_threshold=950,
        memory=False,
        show_role=False,
        show_prompt=False,
        show_tokens_count=True,
        top_p=1,
        n=1,
        stop=None,
        max_tokens=8096,
        functions=None,
        function_call=None,
        presence_penalty=0,
        frequency_penalty=0,
        logit_bias=None,
        user=None,
    ):
        """
        ## Request:
        
        ```sh
        curl -X 'POST' 'https://api.openai.com/v1/chat/completions' \
            -H 'accept: application/json' \
            -H 'Authorization: Bearer <OPENAI_API_KEY>' \
            -H 'Content-Type: application/json' \
            -d '{
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Say this is a test!"}],
                "temperature": 0
            }'
        ```
        """
        input_args = inspect.getargvalues(inspect.currentframe()).locals
        for arg_key in ["self", "prompt", "memory"]:
            input_args.pop(arg_key)

        memory = memory if memory is not None else self.memory
        record = record if record is not None else self.record

        env_params = {
            f"{self.endpoint_name}": True,
        }
        enver.set_envs(secrets=True, set_proxy=True, **env_params)
        os.environ = enver.envs
        self.requests_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {enver.envs['OPENAI_API_KEY']}",
        }

        if record:
            self.update_history_messages("user", prompt)

        if memory:
            request_messages = self.history_messages
        else:
            request_messages = self.get_messages_without_memory()
            request_messages.append(self.content_to_message("user", prompt))

        # pprint.pprint(request_messages)
        if show_prompt:
            print(f"[Human]: {prompt}")
        if show_role:
            print(f"[{self.name}]:", end="", flush=True)

        self.prompt_tokens_count = self.word_tokenizer.count_tokens(
            " ".join([message["content"] for message in request_messages])
        )

        if show_tokens_count:
            print(f"Prompt Tokens count: [{self.prompt_tokens_count}]")

        self.requests_payload = {
            "model": self.model,
            "messages": request_messages,
            "temperature": self.temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        with httpx.stream(
            "POST",
            self.chat_api,
            headers=self.requests_headers,
            json=self.requests_payload,
            timeout=httpx.Timeout(connect=15, read=60, write=15, pool=None),
            # proxies=self.enver.envs.get("http_proxy"),
        ) as response:
            # https://docs.aiohttp.org/en/stable/streams.html
            # https://github.com/openai/openai-cookbook/blob/main/examples/How_to_stream_completions.ipynb
            response_content = ""
            for line in response.iter_lines():
                # print(line)
                line = re.sub(r"^\s*data:\s*", "", line).strip()
                if line:
                    try:
                        line_data = json.loads(line)
                    except Exception as e:
                        print(line_data)
                        raise e
                    delta_data = line_data["choices"][0]["delta"]
                    finish_reason = line_data["choices"][0]["finish_reason"]
                    if "role" in delta_data:
                        role = delta_data["role"]
                    if "content" in delta_data:
                        delta_content = delta_data["content"]
                        response_content += delta_content
                        print(delta_content, end="", flush=True)
                    if finish_reason == "stop":
                        print()

        if record:
            self.update_history_messages(role, response_content)
        # print("[Completed]")
        response_tokens_count = self.word_tokenizer.count_tokens(response_content)
        if show_tokens_count:
            print(f"Response Tokens count: [{response_tokens_count}] [{finish_reason}]")

        if continous and response_tokens_count > continous_token_threshold:
            print("Continue ...")
            response_content += self.chat(
                prompt="Complete last chat from the truncated part.",
                memory=True,
                **input_args,
            )

        self.response_content = response_content

        enver.restore_envs()
        os.environ = enver.envs

        return response_content

    def test_prompt(self):
        self.system_message = (
            f"你是一个专业的中英双语专家。如果给出英文，你需要如实翻译成中文；如果给出中文，你需要如实翻译成英文。"
            f"你的翻译应当是严谨的和自然的，不要删改原文。请按照要求翻译如下文本："
        )
        prompt = "In this paper, we introduce Semantic-SAM, a universal image segmentation model to enable segment and recognize anything at any desired granularity. Our model offers two key advantages: semantic-awareness and granularity-abundance. To achieve semantic-awareness, we consolidate multiple datasets across three granularities and introduce decoupled classification for objects and parts. This allows our model to capture rich semantic information."  # For the multi-granularity capability, we propose a multi-choice learning scheme during training, enabling each click to generate masks at multiple levels that correspond to multiple ground-truth masks. Notably, this work represents the first attempt to jointly train a model on SA-1B, generic, and part segmentation datasets. Experimental results and visualizations demonstrate that our model successfully achieves semantic-awareness and granularity-abundance. Furthermore, combining SA-1B training with other segmentation tasks, such as panoptic and part segmentation, leads to performance improvements. We will provide code and a demo for further exploration and evaluation."
        self.chat(prompt)


if __name__ == "__main__":
    agent = OpenAIAgent(
        name="ninomae",
        endpoint_name="ninomae",
        model="gpt-3.5-turbo",
        temperature=0.0,
    )
    # agent.test_prompt()
    agent.system_message = "Explain the following text in Chinese:"
    agent.chat(
        "Unraveling the “black-box” of artificial intelligence-based pathological analysis of liver cancer applications"
    )
    # prompt1 = "To achieve semantic-awareness, we consolidate multiple datasets across three granularities and introduce decoupled classification for objects and parts. This allows our model to capture rich semantic information."
    # agent = OpenAIAgent(
    #     name="ninomae",
    #     endpoint_name="ninomae",
    #     system_message=system_message,
    #     model="gpt-3.5-turbo",
    #     temperature=0.0,
    # )
    # agent.chat(prompt1)
    # prompt2 = "For the multi-granularity capability, we propose a multi-choice learning scheme during training, enabling each click to generate masks at multiple levels that correspond to multiple ground-truth masks."
    # agent.chat(prompt2)
