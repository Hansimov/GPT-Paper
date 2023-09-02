import aiohttp
import asyncio
import json
import os
import re
from termcolor import colored
from utils.envs import init_os_envs

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


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

    def __init__(
        self,
        name="",  # name of the agent, also use "role" as alias
        endpoint_name="ninomae",
        model="gpt-3.5-turbo",
        temperature=0,
        system_message=None,
        max_input_message_chars=None,
    ):

        self.name = name
        self.endpoint_name = endpoint_name
        self.endpoint = self.endpoint_apis[self.endpoint_name]
        self.endpoint_url = self.endpoint["url"]
        self.chat_api = self.endpoint_url + self.endpoint["chat"]

        env_params = {
            "secrets": True,
            "set_proxy": True,
            f"{self.endpoint_name}": True,
        }
        api_key_env = f"OPENAI_API_KEY"
        init_os_envs(**env_params)
        self.requests_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ[api_key_env]}",
        }

        self.model = model
        self.temperature = temperature
        self.system_message = system_message
        self.max_input_message_chars = max_input_message_chars

        self.calc_max_input_message_chars()

    async def get_available_models(self):
        self.models_api = self.endpoint_url + self.endpoint["models"]
        self.available_models = []

        async with aiohttp.ClientSession() as session:
            async with session.get(self.models_api) as response:
                data = (await response.json())["data"]
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

    def content_to_message(self, role, content):
        return {"role": role, "content": content}

    def construct_request_messages_with_prompt(self, prompt):
        request_messages = []
        if self.system_message:
            request_messages.append(
                self.content_to_message("system", self.system_message)
            )
        request_messages.append(self.content_to_message("user", prompt))
        return request_messages

    async def chat(
        self,
        # model,
        # temperature,
        messages,
        stream=False,
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
        curl -X 'POST' \
            'https://api.openai.com/v1/chat/completions' \
            -H 'accept: application/json' \
            -H 'Authorization: Bearer <API_KEY>' \
            -H 'Content-Type: application/json' \
            -d '{
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Say this is a test!"}],
                "temperature": 0
            }'
        ```
        
        ## Response
        ```json
        {
            "id": "chatcmpl-W0zJUER1GNIcrN3mLRp00fy6Tb8GO",
            "object": "chat.completion",
            "created": 1689055727,
            "model": "gpt-3.5-turbo",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "This is a test!"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "completion_tokens": 5,
                "prompt_tokens": 14,
                "total_tokens": 19
            }
        }
        ```
        """

        self.requests_payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "stream": stream,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.chat_api,
                headers=self.requests_headers,
                json=self.requests_payload,
                timeout=30,
            ) as response:
                if not stream:
                    response_data = await response.json()
                    print(
                        f'{[self.name]}: {response_data["choices"][0]["message"]["content"]}'
                    )
                    return response_data
                else:
                    # https://docs.aiohttp.org/en/stable/streams.html
                    # https://github.com/openai/openai-cookbook/blob/main/examples/How_to_stream_completions.ipynb
                    async for line in response.content:
                        # print(line)
                        line_str = line.decode("utf-8")
                        # print(line_str)
                        line_str = re.sub(r"^\s*data:\s*", "", line_str).strip()
                        if line_str:
                            line_data = json.loads(line_str)
                            delta_data = line_data["choices"][0]["delta"]
                            finish_reason = line_data["choices"][0]["finish_reason"]
                            if "role" in delta_data:
                                role = delta_data["role"]
                                print(f"{role}: ", end="", flush=True)
                            if "content" in delta_data:
                                delta_content = delta_data["content"]
                                print(delta_content, end="", flush=True)
                            if finish_reason == "stop":
                                print()
                                break

    async def test_prompt(self, stream=True):
        self.system_message = (
            f"你是一个专业的中英双语专家。如果给出中文，你需要如实翻译成英文；如果给出中文，你需要如实翻译成英文。"
            f"你的翻译应当是严谨的和自然的，不要删改原文。请按照要求翻译如下文本："
        )
        prompt = "In this paper, we introduce Semantic-SAM, a universal image segmentation model to enable segment and recognize anything at any desired granularity. Our model offers two key advantages: semantic-awareness and granularity-abundance. To achieve semantic-awareness, we consolidate multiple datasets across three granularities and introduce decoupled classification for objects and parts. This allows our model to capture rich semantic information."  # For the multi-granularity capability, we propose a multi-choice learning scheme during training, enabling each click to generate masks at multiple levels that correspond to multiple ground-truth masks. Notably, this work represents the first attempt to jointly train a model on SA-1B, generic, and part segmentation datasets. Experimental results and visualizations demonstrate that our model successfully achieves semantic-awareness and granularity-abundance. Furthermore, combining SA-1B training with other segmentation tasks, such as panoptic and part segmentation, leads to performance improvements. We will provide code and a demo for further exploration and evaluation."
        messages = self.construct_request_messages_with_prompt(prompt)
        print(messages, flush=True)

        if not stream:
            response = await self.chat(messages, stream=stream)
            content = response["choices"][0]["message"]["content"]
            print(content)
        else:
            # https://docs.aiohttp.org/en/stable/streams.html
            await self.chat(messages, stream=stream)

    def _test_prompt(self):
        asyncio.run(agent.test_prompt())


if __name__ == "__main__":
    agent = OpenAIAgent(name="ninomae", endpoint_name="ninomae")
    # asyncio.run(agent.get_available_models())
    # asyncio.run(agent.test_prompt())
    agent._test_prompt()
