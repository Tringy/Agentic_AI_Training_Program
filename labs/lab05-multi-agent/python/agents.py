"""Worker agents for the multi-agent system."""

RESEARCHER_PROMPT = """You are a research specialist.
Your job is to gather and summarize information on a given topic.

For the given topic:
1. Identify key facts and concepts
2. Note important details
3. Highlight relationships between ideas
4. Summarize findings clearly

Be factual and cite what you're basing your information on."""

WRITER_PROMPT = """You are a professional writer.
Your job is to take research and turn it into polished content.

Given research material:
1. Organize information logically
2. Write clear, engaging prose
3. Use appropriate formatting
4. Ensure flow and readability

Match the requested tone and format."""

REVIEWER_PROMPT = """You are a content reviewer.
Your job is to review content for quality and accuracy.

For the given content:
1. Check for factual accuracy
2. Identify unclear sections
3. Suggest improvements
4. Rate overall quality (1-10)

Be constructive in your feedback."""


class WorkerAgent:
    """Base class for worker agents."""

    def __init__(self, llm_client, system_prompt: str, name: str):
        self.llm = llm_client
        self.system_prompt = system_prompt
        self.name = name

    def execute(self, task: str, context: str = "") -> str:
        """Execute a task and return result."""
        user_prompt = task
        if context:
            user_prompt = f"Context:\n{context}\n\nTask:\n{task}"

        response = self.llm.chat([
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ])

        return response


class ResearcherAgent(WorkerAgent):
    def __init__(self, llm_client):
        super().__init__(llm_client, RESEARCHER_PROMPT, "Researcher")


class WriterAgent(WorkerAgent):
    def __init__(self, llm_client):
        super().__init__(llm_client, WRITER_PROMPT, "Writer")


class ReviewerAgent(WorkerAgent):
    def __init__(self, llm_client):
        super().__init__(llm_client, REVIEWER_PROMPT, "Reviewer")
