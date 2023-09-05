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
    model="claude-2",
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

markdown_filler = OpenAIAgent(
    name="article_decomposer",
    model="gpt-4",
    system_message="""
    你的任务是：对于所给的markdown格式的大纲，为各个子章节的填充一句话的简介(intro)，并以JSON格式返回结构化后的文档。
    在JSON中，每个子章节的绝对位置（从1开始递增的数字）、章节层级（例如`2.1.2`）、标题和简介，分别在"idx"、"level"、"title"和"intro"下。
    下面是给出的大纲：
    """,
)

section_summarizer = OpenAIAgent(
    name="section_summarizer",
    model="gpt-4",
    # model="claude-2",
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
    <段落1> [1,2]. <段落2> [1,3]. <段落3> [4].
    ...
    
    # References:
    [1] <文章1>: Page <页码>, Region <区域编号>
    [2] <文章2>: Page <页码>, Region <区域编号>
    ...
    ```
        
    {extra_prompt}
    """
    return section_sum_prompt


retriever = DocumentsRetriever("cancer_review")


def summarize_and_translate_section(
    section: str,
    queries: list,
    extra_prompt="",
    word_count=200,
):
    # queries_str = json.dumps(queries, indent=2, ensure_ascii=False)
    queries_str = str(queries)
    section_sum_prompt = section_sum_prompt_template(
        section, queries_str, extra_prompt=extra_prompt, word_count=word_count
    )
    section_sum_res = section_summarizer.chat(section_sum_prompt)
    section_trans_res = translator.chat(section_sum_res)
    return section_sum_res, section_trans_res
