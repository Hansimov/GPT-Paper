from agents.openai import OpenAIAgent


class TaskRouter:
    def __init__(self):
        self.route_agent = OpenAIAgent(
            name="task_router",
            model="gpt-4",
            system_message="""Your task is to understand user's prompt and questions, then decide which agent to route to.
            
            Here are some examples:
            
            1. If user is intending to have a summary or understanding based on whole document, you should only output following text, and DO NOT ADD EXTRA words before or after:
            
            ```py
            document_level_understanding_agent.run(query, continous = True)
            ```

            2. If user is intending to ask about the part or details of the document, you should only output following text, and DO NOT ADD EXTRA words before or after:
            
            ```py
            query = [
                "<refinement 1 of user's intension>",
                "<refinement 2 of user's intension>",
                ...
            ]
            retrived_documents = content_retrieve_agent.run(query)
            
            new_agent = OpenAIAgent(
                system_message = "<Design the system message suitable for this task>"
            )
            new_agent.chat(prompt)
            ```
                        
            """,
        )


if __name__ == "__main__":
    task_router = TaskRouter()
    prompt = "summarize this paper"
    task_router.route_agent.chat(
        prompt=prompt, show_prompt=True, show_tokens_count=False
    )

    prompt = "what does figure 1 discuss"
    task_router.route_agent.chat(
        prompt=prompt, show_prompt=True, show_tokens_count=False
    )

    prompt = "list the references for me"
    task_router.route_agent.chat(
        prompt=prompt, show_prompt=True, show_tokens_count=False
    )

    prompt = "what does HCC mean in this paper?"
    task_router.route_agent.chat(
        prompt=prompt, show_prompt=True, show_tokens_count=False
    )

    prompt = "why paper authors use the framework?"
    task_router.route_agent.chat(
        prompt=prompt, show_prompt=True, show_tokens_count=False
    )
