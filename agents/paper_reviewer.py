from agents.openai import OpenAIAgent
from agents.documents_retriever import DocumentsRetriever

prompter = OpenAIAgent(
    name="prompter",
    model="gpt-4",
    system_message="你是一个擅长为大语言模型（LLM）撰写提示词（prompts）的专家。对于提供的文本，你总是能给出更易于LLM生成优质回复的prompts。下面是给出的文本：",
)
translator = OpenAIAgent(
    name="translator",
    model="gpt-3.5-turbo",
    system_message="你是一个专业的英译中专家。对于提供的英文，你需要如实翻译成中文。你的翻译应当是严谨的和自然的，不要删改原文。请按照要求翻译如下文本：",
)
summarizer = OpenAIAgent(
    name="summarizer",
    model="gpt-4",
    system_message="你是一个擅长总结文章的学术专家。对于提供的文本，你总是能给出易于理解和总结。下面是提供的文本：",
)
synonymer = OpenAIAgent(
    name="synonymer",
    system_message="你的任务是生成与提供的文本内容相近的文本。对于提供的文本，你总是给出三条长度和意思相近的文本。下面是提供的文本：",
)
outliner = OpenAIAgent(
    name="outliner",
    system_message="你的任务是针对给定的文本和话题，生成大纲。下面是提供的文本：",
)
polisher = OpenAIAgent(
    name="polisher",
    model="gpt-4",
    system_message="你的任务是针对提供的文本，进行逻辑和表达上的润色。润色后的内容应当更加严谨和丰富。下面是提供的文本：",
)
criticizer = OpenAIAgent(
    name="criticizer",
    system_message="你的任务是针对提供的文本，分别给出三类批评：对观点的批评，对逻辑的批评，对表达的批评。下面是提供的文本：",
)
backtracker = OpenAIAgent(
    name="backtracker",
    system_message="你的任务是根据提供的文本，猜测该段文本可能源于什么场景或问题。请给出三个可能的选项。下面是提供的文本：",
)
tasker = OpenAIAgent(
    name="tasker",
    model="gpt-4",
    system_message="你擅长将一个大任务分解成多个连续的子任务。下面是任务内容：",
)

outline_filler = OpenAIAgent(
    name="outline_filler",
    model="gpt-4",
    system_message="""
    你的任务是：对于所给的markdown格式的大纲，为各个子章节的填充一句话的简介(intro)，并以JSON格式返回结构化后的文档。
    
    你返回的 JSON 格式如下：
    
    ```
    [
        {
            "idx": 0,
            "level": "0",
            "title":<总标题>,
            "intro":<总标题的简介>
        },
        {
            "idx":<子章节的绝对位置>,
            "level":<章节层级>(例如 `1`),
            "title":<标题>,
            "intro":<简介>
        },
        {
            "idx":<子章节的绝对位置>,
            "level":<章节层级>(例如`2.1.2`),
            "title":<标题>,
            "intro":<简介>
        },
        ...
    ]
    ```

    其中：`idx` 从 1开始递增；`level` 为各子章节的层级，`title`为子章节的标题，`intro`为你为该子章节填充的简介。

    下面是给出的大纲：
    
    """,
)


class SectionSummarizer:
    def __init__(self):
        self.sum_agent = OpenAIAgent(
            name="section_summarizer",
            # model="gpt-3.5-turbo",
            model="poe-gpt-3.5-turbo-16k",
            # model="poe-claude-2-100k",
            # model="gpt-4",
            # system_message="你的任务是：对于提供的文本，只关注提供的主题，给出完全符合原文内容和主题的陈述。",
            system_message="Your task is to provide statements that are completely referred to the provided texts. You should focus only on the given topic.",
        )
        self.translate_agent = OpenAIAgent(
            name="translator",
            model="poe-gpt-3.5-turbo-16k",
            system_message="你是一个专业的英译中专家。对于提供的英文，你需要如实翻译成中文。你的翻译应当是严谨的和自然的，不要删改原文。请按照要求翻译如下文本：",
        )
        self.agents = [self.sum_agent, self.translate_agent]

    def chat(self, topic, queries, extra_prompt="", word_count=600, translate=False):
        sum_prompt = self.create_sum_prompt(
            topic=topic,
            queries=queries,
            extra_prompt=extra_prompt,
            word_count=word_count,
        )
        sum_content = self.sum_agent.chat(sum_prompt, continuous=True)
        if translate:
            translate_content = self.translate_agent.chat(sum_content, continuous=True)
        else:
            translate_content = ""
        return sum_content, translate_content

    def create_sum_prompt(
        self,
        topic,
        queries,
        query_count=20,
        extra_prompt="",
        word_count=500,
        lang="en",
        output_type="text",
    ):
        queries_str = str(queries[:query_count])
        lang_map = {"en": "英文", "zh": "中文"}
        lang_str = lang_map[lang]

        if output_type == "text":
            output_formats = f"""
            ```
            # Topic: {topic}
            
            # Statements:
            
            <statement 1> [<pdf_order>-<page_num>.<region_num>, ...]. <statement 2> [<pdf_order>-<page_num>.<region_num>, ...].
            <statement 3> [<pdf_order>-<page_num>.<region_num>, ...].
            ...
            
            # References:
            [1] <Referred pdf name 1>
            [2] <Referred pdf name 2>
            [3] <Referred pdf name 3>
            [<pdf_order>] ...
            ...
            
            ```

            Here is the requirements of reference formats:
            
            1. The order of references should follow the order of your output statements referred,
            meaning references used earlier should appear earlier.
            2. References with same `pdf_name` should be combined to a single one.
            3. `<pdf_num>` represents the order of the PDF referenced, starting from 1;
            `<page_idx>` indicates the corresponding page number in the PDF;
            and `<region_idx>` represents the sequence number of the text block.
            4. The values of `<page_idx>` and `<region_idx>` are the same with them in provided texts.
            """
        elif output_type == "json":
            output_formats = f"""
            ```json
            {{
                "topic": {topic},
                "statements": [
                    {{
                        "text": <文本段落1>,
                        "refs": ["<pdf_num>-<page_idx>.<region_idx>", ...]
                    }},
                    {{
                        "text": <文本段落2>,
                        "refs": ["<pdf_num>-<page_idx>.<region_idx>", ...]
                    }},
                    ...
                ],
                "references": {{
                    1: {{
                        "pdf_name": <Referred_PDF_1>,
                    }},
                    2: {{
                        "pdf_name": <Referred_PDF_2>,
                    }},
                    3: ...
                }}
            }}
            ```
            
            格式说明：
            1. "statements"中，`text`表示段落文本内容，`"refs"`中的`<ref_pdf_order>`表示该段文本所参考的PDF在"references"里的顺序，为整数，从1开始。根据你输出的陈述文本参考的PDF引用顺序排列，即先引用的参考文献排在前面。
            `<page_num>`表示PDF中对应的页码，`<region_num>`表示对应的文本块的序号。
            2. "references"中，关键字中的数字表示参考文献的顺序，为整数，从1开始。`"pdf_name"`表示参考文献所在的PDF文件名。
            """

        provided_texts_formats = f"""
        ```
        {{
            'pdf_name': '...',
            'regions': [
                {{  
                    'text': "...",
                    'page_idx': ...,
                    'region_idx': ...,
                    'score': ...
                }},
        }}
        ```
        """

        combined_prompt = f"""
        You should provide statements with {word_count} words based on the following topic.
        
        ```
        {topic}
        ```
        
        Here are the texts you should refer to,
        and your statements should be extracted and summarized from these texts only:
        
        ```
        {queries_str}
        ```

        Here is the structure of provided references text:
        
        {provided_texts_formats}

        Your output format:
        
        {output_formats}
        
        
        You should follow above requirements,
        to provide statements with {word_count} words based on the following topic.
        
        {extra_prompt}
        
        The language of your output should be {lang_str}.
        """
        return combined_prompt


retriever = DocumentsRetriever("cancer_review")
