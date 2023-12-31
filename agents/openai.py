import ast
import httpx
import inspect
import json
import os
import re
from pathlib import Path
from pprint import pprint
from utils.envs import enver
from utils.tokenizer import WordTokenizer


def print_output(*args, **kwargs):
    output_widget = kwargs.pop("output_widget", None)
    update_widget = kwargs.pop("update_widget", None)
    level = kwargs.pop("level", None)
    end = kwargs.pop("end", "\n")

    if output_widget:
        with output_widget:
            if level == "info":
                s = f"<p style='color:cyan'>{args[0]}</p>"
                print(s, *args[1:], **kwargs)
            else:
                print(*args, **kwargs)
    elif update_widget:
        if level == "info":
            text = f"<p style='color:cyan'>{args[0]}</p>" + end
        else:
            if len(args) > 0:
                text = args[0] + end
            else:
                text = end
        update_widget.update_text(text)
    else:
        print(*args, end=end, **kwargs)


class OpenAIAgent:
    """
    OpenAI API doc:
      * https://platform.openai.com/docs/api-reference/chat/create
    """

    endpoint_apis = {
        "openai": {
            "url": "https://api.openai.com/v1",
            "chat": "/chat/completions",
            "models": "/models",
        },
        "ninomae": {
            "chat": "/chat/completions",
            "models": "/models",
        },
        "pplx": {
            "chat": "/chat/completions",
            "models": "/models",
        },
    }
    continuous_token_thresholds = {
        "gpt-4": 950,
        "poe-gpt-3.5-turbo-16k": 2000,
        "gpt-3.5-turbo": 1500,
    }

    def __init__(
        self,
        name="",  # name of the agent, also use "role" as alias
        endpoint_name="pplx",
        model="pplx-7b-online",
        temperature=0,
        system_message=None,
        history_messages=None,
        max_input_message_chars=None,
        continuous=False,
        memory=False,
        record=True,
        output_widget=None,
        update_widget=None,
    ):
        """
        # ANCHOR[id=agent-init]
        """
        self.name = name
        self.endpoint_name = endpoint_name
        self.endpoint = self.endpoint_apis[self.endpoint_name]
        if "url" in self.endpoint:
            self.endpoint_url = self.endpoint["url"]
        else:
            with open(Path(__file__).parents[1] / "secrets.json", "r") as rf:
                secrets = json.load(rf)
            self.endpoint_url = secrets[f"{self.endpoint_name}_endpoint"]

        self.chat_api = self.endpoint_url + self.endpoint["chat"]
        self.memory = memory
        self.record = record
        self.output_widget = output_widget
        self.update_widget = update_widget

        if history_messages:
            self.history_messages = history_messages
        else:
            self.history_messages = []

        self.response_content = ""

        self.model = model
        self.temperature = temperature
        self.continuous = continuous
        self.system_message = system_message
        self.max_input_message_chars = max_input_message_chars
        self.word_tokenizer = WordTokenizer()
        self.calc_max_input_message_chars()
        self.init_history_messages()

    def print_output(self, *args, **kwargs):
        print_output(
            *args,
            **kwargs,
            output_widget=self.output_widget,
            update_widget=self.update_widget,
        )

    def init_history_messages(self):
        if self.system_message:
            self.history_messages.insert(
                0, self.content_to_message("system", self.system_message)
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
        # ANCHOR[id=agent-available-models]
        gpt-3.5-turbo, gpt-4,
        poe-gpt-3.5-turbo, poe-gpt-3.5-turbo-16k, poe-gpt-4
        poe-saga, poe-claude-instant, poe-google-palm,
        poe-llama-2-7b, poe-llama-2-13b, poe-llama-2-70b,
        """
        self.models_api = self.endpoint_url + self.endpoint["models"]
        self.available_models = []
        env_params = {
            f"{self.endpoint_name}": True,
        }
        enver.set_envs(secrets=True, set_proxy=False, **env_params)
        os.environ = enver.envs
        # print(os.environ.get("http_proxy"))
        requests_headers = {
            # "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {enver.envs['OPENAI_API_KEY']}",
        }
        response = httpx.get(self.models_api, headers=requests_headers)
        data = response.json()["data"]

        enver.restore_envs()
        os.environ = enver.envs

        for item in data:
            self.available_models.append(item["id"])
        # self.print_output(self.available_models)
        pprint(self.available_models)

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

    # ANCHOR[id=agent-chat]
    def chat(
        self,
        prompt="",
        stream=True,
        continuous=None,
        memory=None,
        record=None,
        show_role=False,
        show_prompt=False,
        show_tokens_count=True,
        output_widget=None,
        update_widget=None,
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

        if output_widget:
            self.output_widget = output_widget
        if update_widget:
            self.update_widget = update_widget

        continuous = continuous if continuous is not None else self.continuous

        env_params = {
            f"{self.endpoint_name}": True,
        }
        enver.set_envs(secrets=True, set_proxy=False, **env_params)
        os.environ = enver.envs
        # print(os.environ.get("http_proxy"))
        self.requests_headers = {
            # "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {enver.envs['OPENAI_API_KEY']}",
        }

        if type(prompt) == str:
            prompt = [prompt]

        user_prompt_messages = [self.content_to_message("user", p) for p in prompt]

        if record:
            for p in prompt:
                if p.strip():
                    self.update_history_messages("user", p)

        # ANCHOR[id=agent-request-messages]
        if memory:
            request_messages = self.history_messages
        else:
            request_messages = self.get_messages_without_memory()
            request_messages.extend(user_prompt_messages)

        self.request_messages = request_messages
        # pprint(request_messages)

        if show_prompt:
            self.print_output(f"[Human]: {prompt}")
        if show_role:
            self.print_output(f"[{self.name}]:", end="", flush=True)

        self.prompt_tokens_count = self.word_tokenizer.count_tokens(
            " ".join([message["content"] for message in request_messages])
        )

        if show_tokens_count:
            self.print_output(
                f"Prompt Tokens count: [{self.prompt_tokens_count}]", level="info"
            )
        # pprint(request_messages)

        # ANCHOR[id=agent-request-payload]
        self.requests_payload = {
            "model": self.model,
            "messages": self.request_messages,
            "temperature": self.temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        with httpx.stream(
            "POST",
            self.chat_api,
            headers=self.requests_headers,
            json=self.requests_payload,
            timeout=httpx.Timeout(connect=20, read=60, write=20, pool=None),
            # proxies=self.enver.envs.get("http_proxy"),
        ) as response:
            # https://docs.aiohttp.org/en/stable/streams.html
            # https://github.com/openai/openai-cookbook/blob/main/examples/How_to_stream_completions.ipynb
            response_content = ""
            for line in response.iter_lines():
                remove_patterns = [r"^\s*data:\s*", r"^\s*\[DONE\]\s*"]
                for pattern in remove_patterns:
                    line = re.sub(pattern, "", line).strip()

                if line:
                    try:
                        line_data = json.loads(line)
                    except Exception as e:
                        try:
                            line_data = ast.literal_eval(line)
                        except:
                            self.print_output(line)
                            raise e
                    # print(line_data)
                    delta_data = line_data["choices"][0]["delta"]
                    finish_reason = line_data["choices"][0]["finish_reason"]
                    if "role" in delta_data:
                        role = delta_data["role"]
                    if "content" in delta_data:
                        delta_content = delta_data["content"]
                        response_content += delta_content
                        self.print_output(delta_content, end="", flush=True)
                    if finish_reason == "stop":
                        self.print_output()

        if record:
            self.update_history_messages(role, response_content)
        # print("[Completed]")
        response_tokens_count = self.word_tokenizer.count_tokens(response_content)
        if show_tokens_count:
            self.print_output(
                f"Response Tokens count: [{response_tokens_count}] [{finish_reason}]",
                level="info",
            )

        continuous_token_threshold = self.continuous_token_thresholds.get(
            self.model, 4000
        )
        if continuous and response_tokens_count > continuous_token_threshold:
            self.print_output("Continue ...", level="info")
            response_content += self.chat(
                prompt="Complete last chat from the truncated part.",
                memory=True,
                **input_args,
            )

        # ANCHOR[id=agent-response-content]
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
        name="pplx",
        endpoint_name="pplx",
        # model="gpt-4",
        # model="poe-gpt-3.5-turbo-16k",
        model="pplx-7b-online",
        temperature=0.0,
        # system_message="Explain the following text in Chinese:",
    )
    # agent.test_prompt()
    # agent.chat(
    #     "Unraveling the “black-box” of artificial intelligence-based pathological analysis of liver cancer applications"
    # )
    # agent.get_available_models()
    # agent.chat("List most popular twitter posts today.")
    agent.chat("Rockstar latest tweet on X")

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
