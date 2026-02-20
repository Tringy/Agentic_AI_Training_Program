# 📚 Additional Resources & References

Curated high-quality resources to expand your knowledge beyond this training program. All resources are in English and selected for quality, relevance, and depth.

---

## 🎯 Quick Navigation

- [Official Documentation](#official-documentation)
- [Day 1: Foundations & Vibe Coding](#day-1-foundations--vibe-coding)
- [Day 2: Advanced Prompting](#day-2-advanced-prompting)
- [Day 3: Agent Architectures](#day-3-agent-architectures)
- [Day 4: RAG & Evaluation](#day-4-rag--evaluation)
- [Day 5: Production Systems](#day-5-production-systems)
- [Research Papers](#research-papers)
- [Video Courses & Tutorials](#video-courses--tutorials)
- [Blogs & Newsletters](#blogs--newsletters)
- [Interactive Playgrounds](#interactive-playgrounds)

---

## 📖 Official Documentation

### Core LLM Providers

**Anthropic (Claude)**
- [Claude Documentation](https://docs.anthropic.com/) - Official API docs
- [Anthropic Cookbook](https://github.com/anthropics/anthropic-cookbook) - Code examples and guides
- [Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering) - Best practices
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification
- [Claude Code Documentation](https://github.com/anthropics/claude-code) - CLI tool docs

**OpenAI**
- [OpenAI Platform Docs](https://platform.openai.com/docs) - API reference
- [OpenAI Cookbook](https://github.com/openai/openai-cookbook) - Examples and guides
- [GPT Best Practices](https://platform.openai.com/docs/guides/gpt-best-practices) - Prompt engineering
- [Function Calling Guide](https://platform.openai.com/docs/guides/function-calling) - Tool use patterns

**Google (Gemini)**
- [Gemini API Docs](https://ai.google.dev/docs) - Official documentation
- [Google AI Studio](https://aistudio.google.com/) - Interactive playground
- [Gemini Cookbook](https://github.com/google-gemini/cookbook) - Code examples

**Other Providers**
- [Cohere Documentation](https://docs.cohere.com/) - Specialized in RAG and embeddings
- [Together AI](https://docs.together.ai/) - Open source model hosting
- [Replicate](https://replicate.com/docs) - Run open source models

---

## Day 1: Foundations & Vibe Coding

### Understanding LLMs

**Foundational Resources**
- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/) - Visual explanation (Jay Alammar)
- [LLM Visualization](https://bbycroft.net/llm) - Interactive 3D visualization of GPT
- [Transformer Explainer](https://poloclub.github.io/transformer-explainer/) - Interactive deep dive
- [Hugging Face NLP Course](https://huggingface.co/learn/nlp-course/chapter1/1) - Comprehensive free course

**Deep Technical Understanding**
- [Attention Is All You Need (Paper)](https://arxiv.org/abs/1706.03762) - Original Transformer paper
- [The Annotated Transformer](https://nlp.seas.harvard.edu/2018/04/03/attention.html) - Line-by-line implementation
- [Transformer from Scratch](https://e2eml.school/transformers.html) - Build it yourself
- [GPT in 60 Lines](https://jaykmody.com/blog/gpt-from-scratch/) - Minimal GPT implementation

**Model Capabilities & Limitations**
- [Language Models are Few-Shot Learners (GPT-3 Paper)](https://arxiv.org/abs/2005.14165)
- [Constitutional AI Paper](https://arxiv.org/abs/2212.08073) - How Claude is trained
- [Scaling Laws for Neural LMs](https://arxiv.org/abs/2001.08361) - Understanding model size
- [Emergent Abilities of LLMs](https://arxiv.org/abs/2206.07682) - What happens at scale

### AI-Assisted Coding

**Cursor IDE**
- [Cursor Documentation](https://docs.cursor.com/) - Official docs
- [Cursor Tips & Tricks](https://cursor.directory/) - Community patterns
- [Cursor Composer Guide](https://www.cursor.com/blog/composer) - Multi-file editing

**GitHub Copilot**
- [Copilot Documentation](https://docs.github.com/en/copilot) - Official guide
- [Copilot Best Practices](https://github.blog/2023-06-20-how-to-write-better-prompts-for-github-copilot/) - Effective prompting
- [Copilot Workspace](https://githubnext.com/projects/copilot-workspace) - Project-level AI

**Other AI Coding Tools**
- [Windsurf IDE](https://codeium.com/windsurf) - Agentic coding assistant
- [Aider](https://aider.chat/) - AI pair programming in terminal
- [Continue.dev](https://continue.dev/) - Open source autopilot for VS Code/JetBrains
- [Cody by Sourcegraph](https://sourcegraph.com/cody) - Code intelligence

**Vibe Coding Philosophy**
- [The End of Programming (Matt Welsh)](https://cacm.acm.org/magazines/2023/1/267976-the-end-of-programming/fulltext)
- [Software 2.0 (Andrej Karpathy)](https://karpathy.medium.com/software-2-0-a64152b37c35)
- [AI-First Development](https://www.youtube.com/watch?v=c3b-JASoPi0) - GitHub Universe talk

---

## Day 2: Advanced Prompting

### Prompt Engineering Fundamentals

**Comprehensive Guides**
- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering) - Official best practices
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering) - Techniques and examples
- [Prompt Engineering Guide (DAIR.AI)](https://www.promptingguide.ai/) - Comprehensive community resource
- [Learn Prompting](https://learnprompting.org/) - Free interactive course

**Advanced Techniques**
- [Chain-of-Thought Prompting Paper](https://arxiv.org/abs/2201.11903) - Original CoT research
- [ReAct: Synergizing Reasoning and Acting](https://arxiv.org/abs/2210.03629) - Reasoning + Action
- [Tree of Thoughts Paper](https://arxiv.org/abs/2305.10601) - Deliberate problem solving
- [Self-Consistency Paper](https://arxiv.org/abs/2203.11171) - Multiple reasoning paths

**Prompt Patterns & Libraries**
- [Awesome ChatGPT Prompts](https://github.com/f/awesome-chatgpt-prompts) - Community prompts
- [Anthropic Prompt Library](https://docs.anthropic.com/claude/prompt-library) - Production-ready prompts
- [OpenAI Examples](https://platform.openai.com/examples) - Use case templates
- [PromptBase](https://promptbase.com/) - Marketplace for prompts

### Multimodal AI

**Vision + Language Models**
- [GPT-4V System Card](https://cdn.openai.com/papers/GPTV_System_Card.pdf) - Capabilities and limitations
- [Claude Vision Capabilities](https://www.anthropic.com/claude/vision) - Official vision guide
- [Gemini Multimodal Guide](https://ai.google.dev/tutorials/multimodal_quickstart) - Working with vision

**Document Processing**
- [LlamaParse](https://github.com/run-llama/llama_parse) - Advanced PDF parsing
- [Marker](https://github.com/VikParuchuri/marker) - Convert PDFs to markdown
- [Unstructured.io](https://unstructured.io/) - Process any document type
- [PyMuPDF](https://pymupdf.readthedocs.io/) - Python PDF library

**Image Understanding**
- [CLIP Paper](https://arxiv.org/abs/2103.00020) - Connecting text and images
- [Visual Prompting Guide](https://www.anthropic.com/research/visual-prompting) - Anthropic research
- [Multimodal CoT Paper](https://arxiv.org/abs/2302.00923) - Reasoning over images

---

## Day 3: Agent Architectures

### Agent Frameworks

**LangChain / LangGraph**
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction) - Official docs
- [LangChain Cookbook](https://github.com/langchain-ai/langchain/tree/master/cookbook) - Practical examples
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/) - Agent graphs
- [LangSmith](https://docs.smith.langchain.com/) - Debugging and monitoring
- [LangChain Templates](https://github.com/langchain-ai/langchain/tree/master/templates) - Pre-built apps

**Other Agent Frameworks**
- [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) - Autonomous GPT-4
- [BabyAGI](https://github.com/yoheinakajima/babyagi) - Minimal autonomous agent
- [CrewAI](https://github.com/joaomdmoura/crewAI) - Multi-agent orchestration
- [Microsoft AutoGen](https://microsoft.github.io/autogen/) - Multi-agent framework
- [Semantic Kernel](https://learn.microsoft.com/en-us/semantic-kernel/) - Microsoft's SDK

**Agent Design Patterns**
- [Langroid](https://github.com/langroid/langroid) - Multi-agent programming framework
- [MetaGPT](https://github.com/geekan/MetaGPT) - Multi-agent software company
- [AgentGPT](https://github.com/reworkd/AgentGPT) - Browser-based autonomous agents

### Agent Research

**Foundational Papers**
- [ReAct Paper](https://arxiv.org/abs/2210.03629) - Reasoning and Acting in LLMs
- [Reflexion Paper](https://arxiv.org/abs/2303.11366) - Self-reflection agents
- [Toolformer Paper](https://arxiv.org/abs/2302.04761) - Teaching LLMs to use tools
- [HuggingGPT Paper](https://arxiv.org/abs/2303.17580) - Solving AI tasks with ChatGPT

**Memory Systems**
- [MemGPT Paper](https://arxiv.org/abs/2310.08560) - Virtual context management
- [Generative Agents Paper](https://arxiv.org/abs/2304.03442) - Interactive simulacra
- [ChatDB Paper](https://arxiv.org/abs/2306.03901) - Augmenting LLMs with databases

**Multi-Agent Systems**
- [Communicative Agents Paper](https://arxiv.org/abs/2307.07924) - Multi-agent collaboration
- [AutoGen Paper](https://arxiv.org/abs/2308.08155) - Microsoft's multi-agent framework
- [MetaGPT Paper](https://arxiv.org/abs/2308.00352) - Multi-agent collaboration

### Tool Use & Function Calling

**Documentation**
- [Anthropic Tool Use Guide](https://docs.anthropic.com/claude/docs/tool-use) - Official Claude guide
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling) - Detailed guide
- [Gorilla Paper](https://arxiv.org/abs/2305.15334) - LLM for API calls

---

## Day 4: RAG & Evaluation

### Vector Databases

**Popular Vector DBs**
- [Pinecone](https://docs.pinecone.io/) - Managed vector database
- [Weaviate](https://weaviate.io/developers/weaviate) - Open source vector search
- [Qdrant](https://qdrant.tech/documentation/) - High-performance vector DB
- [Milvus](https://milvus.io/docs) - Open source, scalable
- [ChromaDB](https://docs.trychroma.com/) - Embedded vector database
- [pgvector](https://github.com/pgvector/pgvector) - Postgres extension

**Vector Search Techniques**
- [FAISS by Meta](https://github.com/facebookresearch/faiss) - Efficient similarity search
- [Annoy by Spotify](https://github.com/spotify/annoy) - Approximate nearest neighbors
- [hnswlib](https://github.com/nmslib/hnswlib) - Fast ANN algorithm

### Embeddings

**Embedding Models**
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings) - text-embedding-3
- [Cohere Embed](https://docs.cohere.com/docs/embeddings) - Multilingual embeddings
- [Sentence Transformers](https://www.sbert.net/) - Open source embeddings
- [BGE Embeddings](https://huggingface.co/BAAI/bge-large-en-v1.5) - SOTA open source
- [E5 Embeddings](https://huggingface.co/intfloat/e5-large-v2) - Microsoft's embeddings

**Embedding Resources**
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) - Embedding benchmarks
- [Massive Text Embedding Benchmark](https://arxiv.org/abs/2210.07316) - MTEB paper
- [Text Embeddings Explained](https://simonwillison.net/2023/Oct/23/embeddings/) - Simon Willison

### RAG Techniques

**RAG Fundamentals**
- [RAG Paper (Original)](https://arxiv.org/abs/2005.11401) - Retrieval-Augmented Generation
- [LlamaIndex Documentation](https://docs.llamaindex.ai/) - RAG framework
- [LlamaIndex Patterns](https://docs.llamaindex.ai/en/stable/examples/) - Advanced RAG
- [Haystack by deepset](https://haystack.deepset.ai/) - NLP framework for RAG

**Advanced RAG**
- [Self-RAG Paper](https://arxiv.org/abs/2310.11511) - Self-reflective RAG
- [CRAG Paper](https://arxiv.org/abs/2401.15884) - Corrective RAG
- [HyDE Paper](https://arxiv.org/abs/2212.10496) - Hypothetical document embeddings
- [Lost in the Middle Paper](https://arxiv.org/abs/2307.03172) - Context position matters
- [Contextual Retrieval (Anthropic)](https://www.anthropic.com/news/contextual-retrieval) - Improved RAG accuracy

**RAG Optimization**
- [Query Rewriting Techniques](https://arxiv.org/abs/2305.14283)
- [Reranking for RAG](https://www.pinecone.io/learn/series/rag/rerankers/) - Improve retrieval
- [Cohere Rerank](https://docs.cohere.com/docs/reranking) - Reranking API
- [Parent Document Retrieval](https://python.langchain.com/docs/modules/data_connection/retrievers/parent_document_retriever)

### Evaluation & Testing

**Evaluation Frameworks**
- [RAGAS](https://docs.ragas.io/) - RAG Assessment framework
- [TruLens](https://www.trulens.org/) - LLM app evaluation
- [DeepEval](https://docs.confident-ai.com/) - Unit testing for LLMs
- [LangChain Evaluators](https://python.langchain.com/docs/guides/evaluation/) - Built-in evaluation

**Benchmarks & Datasets**
- [MMLU](https://github.com/hendrycks/test) - Massive Multitask Language Understanding
- [HumanEval](https://github.com/openai/human-eval) - Code generation benchmark
- [TruthfulQA](https://github.com/sylinrl/TruthfulQA) - Truthfulness benchmark
- [BIG-Bench](https://github.com/google/BIG-bench) - Beyond the Imitation Game
- [Chatbot Arena](https://chat.lmsys.org/) - Live LLM comparison

**Testing Strategies**
- [Promptfoo](https://www.promptfoo.dev/) - Test prompts systematically
- [Giskard](https://github.com/Giskard-AI/giskard) - ML quality testing
- [pytest-llm](https://github.com/npi-ai/pytest-llm) - pytest plugin for LLMs

---

## Day 5: Production Systems

### Deployment Platforms

**Serverless / PaaS**
- [Vercel AI SDK](https://sdk.vercel.ai/) - Build AI apps with React
- [Railway](https://docs.railway.app/) - Deploy anything
- [Render](https://render.com/docs) - Unified cloud
- [Modal](https://modal.com/docs) - Run code in the cloud
- [Replicate](https://replicate.com/docs) - Deploy ML models

**Container Orchestration**
- [Docker for ML](https://docs.docker.com/get-started/) - Containerization basics
- [Kubernetes Patterns](https://kubernetes.io/docs/concepts/) - Orchestration
- [AWS SageMaker](https://docs.aws.amazon.com/sagemaker/) - End-to-end ML platform
- [GCP Vertex AI](https://cloud.google.com/vertex-ai/docs) - Managed ML

### Monitoring & Observability

**LLM Observability**
- [LangSmith](https://docs.smith.langchain.com/) - LangChain monitoring
- [Helicone](https://docs.helicone.ai/) - LLM observability platform
- [Weights & Biases](https://docs.wandb.ai/) - Experiment tracking
- [Phoenix by Arize](https://docs.arize.com/phoenix/) - LLM observability
- [Lunary](https://lunary.ai/docs) - LLM monitoring

**Traditional Observability**
- [Datadog](https://docs.datadoghq.com/) - Full stack monitoring
- [Grafana](https://grafana.com/docs/) - Visualization and dashboards
- [Sentry](https://docs.sentry.io/) - Error tracking
- [Prometheus](https://prometheus.io/docs/) - Metrics collection

### Cost Optimization

**LLM Cost Management**
- [OpenAI Token Counting](https://github.com/openai/tiktoken) - Count tokens accurately
- [LiteLLM](https://docs.litellm.ai/) - Unified LLM API with cost tracking
- [PromptLayer](https://promptlayer.com/docs) - Prompt management and analytics
- [LangFuse](https://langfuse.com/docs) - Open source LLM engineering platform

**Caching Strategies**
- [GPTCache](https://github.com/zilliztech/GPTCache) - Semantic cache for LLMs
- [Redis for AI](https://redis.io/docs/stack/) - Vector similarity + caching
- [Prompt Caching (Anthropic)](https://docs.anthropic.com/claude/docs/prompt-caching) - Built-in caching

**Model Optimization**
- [OpenRouter](https://openrouter.ai/docs) - Route to cheapest model
- [Together AI](https://docs.together.ai/) - Open source models at scale
- [Groq](https://console.groq.com/docs) - Ultra-fast inference

### Integration Patterns

**Webhooks & APIs**
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python API framework
- [Hono](https://hono.dev/) - Fast TypeScript web framework
- [Webhook.site](https://webhook.site/) - Test webhooks
- [ngrok](https://ngrok.com/docs) - Expose local servers

**Message Queues**
- [Celery](https://docs.celeryq.dev/) - Distributed task queue (Python)
- [Bull](https://docs.bullmq.io/) - Redis-based queue (Node.js)
- [RabbitMQ](https://www.rabbitmq.com/documentation.html) - Message broker
- [Apache Kafka](https://kafka.apache.org/documentation/) - Event streaming

**Event-Driven Architecture**
- [AWS EventBridge](https://docs.aws.amazon.com/eventbridge/) - Serverless event bus
- [Azure Event Grid](https://learn.microsoft.com/en-us/azure/event-grid/) - Event routing
- [GCP Pub/Sub](https://cloud.google.com/pubsub/docs) - Async messaging

---

## 📄 Research Papers

### Must-Read Papers (Foundational)

**Transformers & Attention**
1. [Attention Is All You Need](https://arxiv.org/abs/1706.03762) (2017) - Original Transformer
2. [BERT](https://arxiv.org/abs/1810.04805) (2018) - Bidirectional Transformers
3. [GPT-3](https://arxiv.org/abs/2005.14165) (2020) - Language Models are Few-Shot Learners
4. [GPT-4 Technical Report](https://arxiv.org/abs/2303.08774) (2023) - Multimodal LLM

**Prompting & In-Context Learning**
5. [Chain-of-Thought Prompting](https://arxiv.org/abs/2201.11903) (2022)
6. [ReAct: Reasoning and Acting](https://arxiv.org/abs/2210.03629) (2022)
7. [Tree of Thoughts](https://arxiv.org/abs/2305.10601) (2023)
8. [Large Language Models are Zero-Shot Reasoners](https://arxiv.org/abs/2205.11916) (2022)

**Agents & Tool Use**
9. [Toolformer](https://arxiv.org/abs/2302.04761) (2023) - Teaching LLMs to use tools
10. [Reflexion](https://arxiv.org/abs/2303.11366) (2023) - Self-reflecting agents
11. [Generative Agents](https://arxiv.org/abs/2304.03442) (2023) - Interactive simulacra
12. [AutoGPT: An Autonomous GPT-4 Experiment](https://arxiv.org/abs/2306.02224) (2023)

**RAG & Retrieval**
13. [RAG: Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401) (2020)
14. [Self-RAG](https://arxiv.org/abs/2310.11511) (2023) - Self-reflective RAG
15. [Lost in the Middle](https://arxiv.org/abs/2307.03172) (2023) - Long context challenges

**Evaluation & Safety**
16. [Constitutional AI](https://arxiv.org/abs/2212.08073) (2022) - Training helpful, harmless AI
17. [TruthfulQA](https://arxiv.org/abs/2109.07958) (2021) - Measuring truthfulness
18. [RLHF for Language Models](https://arxiv.org/abs/2203.02155) (2022)

### Recent Important Papers (2023-2024)

- [Mixture of Experts](https://arxiv.org/abs/2401.04088) - Mixtral architecture
- [Anthropic's Many-Shot Jailbreaking](https://arxiv.org/abs/2404.02151) - Security research
- [Scaling Monosemanticity](https://transformer-circuits.pub/2024/scaling-monosemanticity/) - Interpretability
- [Long Context Prompting](https://arxiv.org/abs/2404.02060) - Working with long contexts

### Paper Reading Tools

- [Arxiv Sanity](http://www.arxiv-sanity.com/) - Browse ML papers
- [Papers with Code](https://paperswithcode.com/) - Papers + implementations
- [Hugging Face Papers](https://huggingface.co/papers) - Daily ML papers
- [Connected Papers](https://www.connectedpapers.com/) - Visualize paper relationships

---

## 🎥 Video Courses & Tutorials

### Comprehensive Courses

**Andrew Ng (DeepLearning.AI)**
- [ChatGPT Prompt Engineering for Developers](https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/) - Free
- [Building Systems with ChatGPT API](https://www.deeplearning.ai/short-courses/building-systems-with-chatgpt/) - Free
- [LangChain for LLM Application Development](https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/) - Free
- [LangChain: Chat with Your Data](https://www.deeplearning.ai/short-courses/langchain-chat-with-your-data/) - Free
- [Building and Evaluating Advanced RAG](https://www.deeplearning.ai/short-courses/building-evaluating-advanced-rag/) - Free

**Other Quality Courses**
- [Full Stack LLM Bootcamp](https://fullstackdeeplearning.com/llm-bootcamp/) - Free (The Full Stack)
- [CS25: Transformers United](https://web.stanford.edu/class/cs25/) - Stanford (Free)
- [CS324: Large Language Models](https://stanford-cs324.github.io/winter2022/) - Stanford (Free)
- [Practical Deep Learning](https://course.fast.ai/) - fast.ai (Free)

### YouTube Channels

**Technical Deep Dives**
- [Andrej Karpathy](https://www.youtube.com/@AndrejKarpathy) - Building GPT from scratch
- [3Blue1Brown](https://www.youtube.com/@3blue1brown) - Visual math explanations
- [Yannic Kilcher](https://www.youtube.com/@YannicKilcher) - Paper reviews
- [AI Explained](https://www.youtube.com/@aiexplained-official) - Latest AI news and papers

**Practical AI Development**
- [Sam Witteveen](https://www.youtube.com/@samwitteveenai) - LangChain and agents
- [Greg Kamradt](https://www.youtube.com/@DataIndependent) - LLM applications
- [Prompt Engineering](https://www.youtube.com/@engineerprompt) - Prompt techniques
- [Matt Williams](https://www.youtube.com/@technovangelist) - AI tools and reviews

**Company Channels**
- [OpenAI](https://www.youtube.com/@OpenAI) - Official updates
- [Anthropic](https://www.youtube.com/@AnthropicAI) - Claude updates
- [LangChain](https://www.youtube.com/@LangChain) - Framework tutorials

---

## 📰 Blogs & Newsletters

### Essential Newsletters

**Daily/Weekly**
- [The Batch (DeepLearning.AI)](https://www.deeplearning.ai/the-batch/) - Weekly AI news
- [Import AI (Jack Clark)](https://jack-clark.net/) - Weekly AI policy and research
- [TLDR AI](https://tldr.tech/ai) - Daily AI news
- [AI Breakfast](https://aibreakfast.beehiiv.com/) - Daily AI digest

**Technical Deep Dives**
- [Sebastian Raschka](https://magazine.sebastianraschka.com/) - Research scientist perspectives
- [LLMs from Scratch](https://substack.com/@rasbt) - Implementation details
- [The Gradient](https://thegradient.pub/) - AI research magazine
- [Interconnects (Nathan Lambert)](https://www.interconnects.ai/) - AI alignment and RLHF

### Must-Follow Blogs

**Individual Researchers**
- [Lilian Weng (OpenAI)](https://lilianweng.github.io/) - Comprehensive technical posts
- [Jay Alammar](https://jalammar.github.io/) - Visual explanations
- [Sebastian Ruder](https://www.ruder.io/) - NLP research
- [Andrej Karpathy](https://karpathy.github.io/) - Deep learning insights

**Company Blogs**
- [Anthropic Research](https://www.anthropic.com/research) - Claude research
- [OpenAI Research](https://openai.com/research) - Latest papers
- [Google AI Blog](https://ai.googleblog.com/) - Research updates
- [Hugging Face Blog](https://huggingface.co/blog) - Open source ML

**Practical AI Engineering**
- [Simon Willison](https://simonwillison.net/) - Practical LLM development
- [Eugene Yan](https://eugeneyan.com/) - Applied ML in production
- [Chip Huyen](https://huyenchip.com/blog/) - ML systems design
- [Full Stack Deep Learning](https://fullstackdeeplearning.com/blog/) - Production ML

---

## 🎮 Interactive Playgrounds

### Prompt Testing

- [Claude.ai](https://claude.ai/) - Chat with Claude
- [ChatGPT](https://chat.openai.com/) - Chat with GPT-4
- [Google AI Studio](https://aistudio.google.com/) - Gemini playground
- [Poe](https://poe.com/) - Multiple LLMs in one place
- [Hugging Chat](https://huggingface.co/chat) - Open source models

### Code Playgrounds

- [LangChain Templates](https://templates.langchain.com/) - Try agent templates
- [Replit](https://replit.com/) - Browser-based coding with AI
- [StackBlitz](https://stackblitz.com/) - Instant dev environments
- [Google Colab](https://colab.research.google.com/) - Free Jupyter notebooks

### Embedding & Vector Search

- [Atlas by Nomic](https://atlas.nomic.ai/) - Visualize embeddings
- [Embedding Projector](https://projector.tensorflow.org/) - TensorFlow visualizations
- [Qdrant Demo](https://qdrant.tech/demo/) - Vector search demo

---

## 🛠️ Datasets for Practice

### General Purpose
- [Hugging Face Datasets](https://huggingface.co/datasets) - 100k+ datasets
- [Kaggle Datasets](https://www.kaggle.com/datasets) - ML competitions
- [Papers with Code Datasets](https://paperswithcode.com/datasets) - Research datasets

### For RAG Systems
- [BEIR Benchmark](https://github.com/beir-cellar/beir) - Information retrieval
- [MS MARCO](https://microsoft.github.io/msmarco/) - Passage ranking
- [Natural Questions](https://ai.google.com/research/NaturalQuestions/) - QA dataset
- [SQuAD](https://rajpurkar.github.io/SQuAD-explorer/) - Reading comprehension

### For Evaluation
- [HumanEval](https://github.com/openai/human-eval) - Code generation
- [MMLU](https://github.com/hendrycks/test) - Multitask understanding
- [TruthfulQA](https://github.com/sylinrl/TruthfulQA) - Truthfulness
- [BBH (Big-Bench Hard)](https://github.com/suzgunmirac/BIG-Bench-Hard) - Challenging tasks

---

## 🔧 Development Tools

### Prompt Management
- [PromptLayer](https://promptlayer.com/) - Version control for prompts
- [Humanloop](https://humanloop.com/) - Prompt engineering platform
- [Promptable](https://promptable.ai/) - Organize and test prompts
- [LangFuse](https://langfuse.com/) - Open source LLM engineering

### Testing & Debugging
- [Promptfoo](https://www.promptfoo.dev/) - Test and compare prompts
- [LangSmith](https://smith.langchain.com/) - Debug LangChain apps
- [Phoenix](https://phoenix.arize.com/) - LLM observability
- [Weights & Biases](https://wandb.ai/) - Experiment tracking

### Code Quality
- [Ruff](https://github.com/astral-sh/ruff) - Fast Python linter
- [Black](https://black.readthedocs.io/) - Python code formatter
- [ESLint](https://eslint.org/) - JavaScript linter
- [Prettier](https://prettier.io/) - Code formatter

---

## 📚 Books

### AI & Machine Learning
- **[Build a Large Language Model (From Scratch)](https://www.manning.com/books/build-a-large-language-model-from-scratch)** by Sebastian Raschka
- **[Designing Machine Learning Systems](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/)** by Chip Huyen
- **[Natural Language Processing with Transformers](https://www.oreilly.com/library/view/natural-language-processing/9781098136789/)** by Tunstall, von Werra, Wolf

### Software Engineering
- **[The Pragmatic Programmer](https://pragprog.com/titles/tpp20/)** - Timeless best practices
- **[Clean Code](https://www.oreilly.com/library/view/clean-code/9780136083238/)** by Robert Martin
- **[System Design Interview](https://www.amazon.com/System-Design-Interview-insiders-Second/dp/B08CMF2CQF)** by Alex Xu

---

## 🎯 What's Next?

After completing this training:

1. **Build Projects** - Apply knowledge to real problems
2. **Read Papers** - Stay current with research ([RECOMMENDED-READING.md](RECOMMENDED-READING.md))
3. **Join Communities** - Learn from others ([COMMUNITY.md](COMMUNITY.md))
4. **Follow Learning Paths** - Continue growing ([LEARNING-PATHS.md](LEARNING-PATHS.md))
5. **Explore Tools** - Master the ecosystem ([TOOLS-ECOSYSTEM.md](TOOLS-ECOSYSTEM.md))

---

## 📖 Using These Resources

**Strategy for Learning:**
1. **During Training** - Use as reference when topics are introduced
2. **After Training** - Deep dive into areas of interest
3. **Ongoing** - Stay updated with newsletters and communities
4. **Projects** - Reference when building real applications

**Recommended Approach:**
- Start with official documentation
- Follow with interactive tutorials
- Read papers for deep understanding
- Join communities for support
- Build projects to solidify knowledge

---

**Last Updated**: 2026-01-08
**Maintained by**: Training Program Contributors

*This resource list is continuously updated. Bookmark for future reference!*
