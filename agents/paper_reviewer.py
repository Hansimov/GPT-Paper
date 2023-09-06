import json
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
    memory=True,
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

section_summarizer = OpenAIAgent(
    name="section_summarizer",
    model="gpt-4",
    system_message="你的任务是：对于提供的文本，只关注提供的主题，给出完全符合原文内容和主题的陈述。",
)


def section_sum_prompt_template(
    topic, queries_str, extra_prompt="", word_count=500, lang="en"
):
    lang_map = {"en": "英文", "zh": "中文"}
    lang_str = lang_map[lang]

    section_sum_prompt = f"""
    请你根据以下主题，给出{word_count}词的{lang_str}陈述：：
    
    ```
    {topic}
    ```
    
    下面是你参考的文本，你的结论必须从该文本中提取：
    
    ```
    {queries_str}
    ```

    你的输出格式：
    
    ```
    # Topic: {topic}
    
    # Statement:
    <文本段落1> [1.1, 2.1]. <文本段落2> [1.1]. <文本段落3> [3.1].
    ...
    
    # References:
    [1] <Referred pdf 1>: (1) P<page_idx>.<region_idx>; (2) P<page_idx>.<region_idx>
    [2] <Referred pdf 2>: P<page_idx>.<region_idx>
    ...
    
    ```
    
    参考文献格式要求：
    1. 参考文献的顺序依据你的输出顺序，即先输出的参考文献排在前面。
    2. 参考文献的格式为：`[<ref_idx>] '<pdf_name>': (<sub_ref_idx>) P(<page_idx>,<region_idx>)`。
    其中，`<ref_idx>`为参考PDF的顺序序号，从1开始递增。`<pdf_name>`为参考文献所在的PDF文件名，`<sub_ref_idx>`为参考片段的顺序，从1开始递增编号。`<page_idx>`为参考片段所在的页码，`<region_idx>`为参考片段所在的段落序号。
    
    请你根据上述要求，针对提供的主题，给出{word_count}词的{lang_str}陈述：：
    
    {extra_prompt}
    """
    return section_sum_prompt


retriever = DocumentsRetriever("cancer_review")


def summarize_and_translate_section(
    section: str,
    queries: list,
    extra_prompt="",
    query_count=20,
    word_count=500,
):
    # queries_str = json.dumps(queries, indent=2, ensure_ascii=False)
    queries_str = str(queries[:query_count])
    section_sum_prompt = section_sum_prompt_template(
        section, queries_str, extra_prompt=extra_prompt, word_count=word_count
    )
    section_sum_res = section_summarizer.chat(section_sum_prompt)
    section_trans_res = translator.chat(section_sum_res)
    return section_sum_res, section_trans_res