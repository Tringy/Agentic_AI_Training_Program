# 📖 Recommended Reading

Curated list of essential papers, articles, and technical blog posts for AI engineers. Organized by topic and difficulty level.

---

## 📚 How to Use This Guide

**Reading Levels**:
- 🟢 **Beginner**: Accessible to those new to the topic
- 🟡 **Intermediate**: Requires basic ML/AI knowledge
- 🔴 **Advanced**: Requires deep technical background

**Reading Strategy**:
1. Start with 🟢 papers in your area of interest
2. Read the abstract and conclusion first
3. Skip heavy math sections on first pass
4. Implement concepts in code to solidify understanding
5. Return to papers multiple times as you grow

**Time Commitment**:
- Quick read (blog post): 10-30 minutes
- Standard paper: 1-3 hours
- Dense research paper: 4-8 hours

---

## 🎯 Essential Reading (Must-Read Papers)

### The Foundational 10

Every AI engineer should read these papers:

1. **[Attention Is All You Need](https://arxiv.org/abs/1706.03762)** 🟡
   - Vaswani et al., 2017
   - The paper that started it all - Transformer architecture
   - **Key concept**: Self-attention mechanism
   - **Why read**: Understanding the foundation of all modern LLMs

2. **[Language Models are Few-Shot Learners (GPT-3)](https://arxiv.org/abs/2005.14165)** 🟡
   - Brown et al., 2020
   - Demonstrates in-context learning
   - **Key concept**: Prompting for zero/few-shot learning
   - **Why read**: Foundation of prompt engineering

3. **[Chain-of-Thought Prompting Elicits Reasoning](https://arxiv.org/abs/2201.11903)** 🟢
   - Wei et al., 2022
   - Shows "Let's think step by step" dramatically improves reasoning
   - **Key concept**: Intermediate reasoning steps
   - **Why read**: Most impactful prompting technique

4. **[ReAct: Synergizing Reasoning and Acting](https://arxiv.org/abs/2210.03629)** 🟢
   - Yao et al., 2022
   - Interleaving thought, action, and observation
   - **Key concept**: Agents that think then act
   - **Why read**: Foundation of modern agentic systems

5. **[Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073)** 🟡
   - Bai et al., 2022 (Anthropic)
   - How Claude is trained to be helpful and harmless
   - **Key concept**: AI-generated feedback for training
   - **Why read**: Understanding AI safety and alignment

6. **[Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401)** 🟡
   - Lewis et al., 2020
   - Combining retrieval with generation
   - **Key concept**: Use external knowledge for generation
   - **Why read**: Foundation of all RAG systems

7. **[GPT-4 Technical Report](https://arxiv.org/abs/2303.08774)** 🟢
   - OpenAI, 2023
   - First major multimodal LLM
   - **Key concept**: Capabilities and limitations
   - **Why read**: Understanding current SOTA

8. **[Tree of Thoughts](https://arxiv.org/abs/2305.10601)** 🟡
   - Yao et al., 2023
   - Deliberate search over thought paths
   - **Key concept**: Explore multiple reasoning paths
   - **Why read**: Advanced reasoning technique

9. **[Lost in the Middle](https://arxiv.org/abs/2307.03172)** 🟢
   - Liu et al., 2023
   - LLMs struggle with middle context
   - **Key concept**: Position of information matters
   - **Why read**: Critical for RAG system design

10. **[The Illustrated Transformer (Blog)](https://jalammar.github.io/illustrated-transformer/)** 🟢
    - Jay Alammar, 2018
    - Visual explanation of Transformer architecture
    - **Why read**: Best introduction to Transformers
    - **Time**: 30 minutes

---

## 📂 Papers by Topic

### Transformer Architecture & Fundamentals

**Beginner** 🟢
- [BERT: Pre-training of Deep Bidirectional Transformers](https://arxiv.org/abs/1810.04805) (2018)
  - Bidirectional context understanding
- [The Annotated Transformer](https://nlp.seas.harvard.edu/2018/04/03/attention.html) (Blog, 2018)
  - Line-by-line implementation guide
- [Transformer from Scratch](https://e2eml.school/transformers.html) (Blog, 2021)
  - Build your own Transformer

**Intermediate** 🟡
- [BERT, RoBERTa, DistilBERT, ALBERT Compared](https://arxiv.org/abs/1910.01108) (2019)
  - RoBERTa improvements over BERT
- [T5: Text-to-Text Transfer Transformer](https://arxiv.org/abs/1910.10683) (2019)
  - Unified text-to-text framework
- [XLNet: Generalized Autoregressive Pretraining](https://arxiv.org/abs/1906.08237) (2019)
  - Permutation language modeling

**Advanced** 🔴
- [Formal Algorithms for Transformers](https://arxiv.org/abs/2207.09238) (2022)
  - Mathematical foundations
- [Flash Attention](https://arxiv.org/abs/2205.14135) (2022)
  - Fast and memory-efficient attention
- [Mixture of Experts (MoE)](https://arxiv.org/abs/2401.04088) (2024)
  - Mixtral architecture explanation

---

### Prompting Techniques

**Beginner** 🟢
- [Chain-of-Thought Prompting](https://arxiv.org/abs/2201.11903) (2022) ⭐ **Must Read**
  - "Let's think step by step"
- [Large Language Models are Zero-Shot Reasoners](https://arxiv.org/abs/2205.11916) (2022)
  - Zero-shot CoT with simple prompting
- [Prompt Engineering Guide](https://www.promptingguide.ai/) (Website)
  - Comprehensive online resource

**Intermediate** 🟡
- [Self-Consistency Improves CoT Reasoning](https://arxiv.org/abs/2203.11171) (2022)
  - Sample multiple paths, majority vote
- [Least-to-Most Prompting](https://arxiv.org/abs/2205.10625) (2022)
  - Break complex problems into simpler ones
- [Tree of Thoughts](https://arxiv.org/abs/2305.10601) (2023) ⭐ **Must Read**
  - Deliberate search over reasoning paths
- [ReAct](https://arxiv.org/abs/2210.03629) (2022) ⭐ **Must Read**
  - Reasoning + Acting in sync

**Advanced** 🔴
- [Graph of Thoughts](https://arxiv.org/abs/2308.09687) (2023)
  - Model reasoning as a graph
- [Reflexion: Language Agents with Verbal Reinforcement](https://arxiv.org/abs/2303.11366) (2023)
  - Self-reflection for agents
- [Large Language Models Can Self-Improve](https://arxiv.org/abs/2210.11610) (2022)
  - Self-training with CoT

---

### Agents & Tool Use

**Beginner** 🟢
- [ReAct: Synergizing Reasoning and Acting](https://arxiv.org/abs/2210.03629) (2022) ⭐ **Must Read**
  - Foundational agent paper
- [HuggingGPT](https://arxiv.org/abs/2303.17580) (2023)
  - ChatGPT orchestrating AI models
- [ToolLLM](https://arxiv.org/abs/2307.16789) (2023)
  - Tool learning with APIs

**Intermediate** 🟡
- [Toolformer](https://arxiv.org/abs/2302.04761) (2023)
  - Teaching LLMs to use tools
- [Reflexion](https://arxiv.org/abs/2303.11366) (2023)
  - Self-reflecting agents
- [AutoGPT: An Autonomous GPT-4 Experiment](https://arxiv.org/abs/2306.02224) (2023)
  - First popular autonomous agent
- [Generative Agents](https://arxiv.org/abs/2304.03442) (2023)
  - Interactive simulacra with memory

**Advanced** 🔴
- [MemGPT: Towards LLMs as Operating Systems](https://arxiv.org/abs/2310.08560) (2023)
  - Virtual context management
- [AutoGen: Enabling Next-Gen LLM Applications](https://arxiv.org/abs/2308.08155) (2023)
  - Multi-agent framework (Microsoft)
- [MetaGPT: Meta Programming for Multi-Agent Systems](https://arxiv.org/abs/2308.00352) (2023)
  - Agents as software company
- [Voyager: An Open-Ended Embodied Agent](https://arxiv.org/abs/2305.16291) (2023)
  - Lifelong learning agent in Minecraft

---

### RAG (Retrieval-Augmented Generation)

**Beginner** 🟢
- [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401) (2020) ⭐ **Must Read**
  - Original RAG paper
- [Lost in the Middle](https://arxiv.org/abs/2307.03172) (2023) ⭐ **Must Read**
  - Context position matters
- [Contextual Retrieval (Anthropic Blog)](https://www.anthropic.com/news/contextual-retrieval) (2024)
  - Improve RAG accuracy with context

**Intermediate** 🟡
- [Self-RAG](https://arxiv.org/abs/2310.11511) (2023)
  - Self-reflective retrieval
- [CRAG: Corrective Retrieval Augmented Generation](https://arxiv.org/abs/2401.15884) (2024)
  - Critique and correct retrieval
- [HyDE: Hypothetical Document Embeddings](https://arxiv.org/abs/2212.10496) (2022)
  - Generate hypothetical docs for better retrieval
- [Query Rewriting for RAG](https://arxiv.org/abs/2305.14283) (2023)
  - Improve queries before retrieval

**Advanced** 🔴
- [RAPTOR: Recursive Abstractive Processing](https://arxiv.org/abs/2401.18059) (2024)
  - Tree-based retrieval
- [RAG vs Fine-tuning](https://arxiv.org/abs/2312.05934) (2023)
  - When to use each approach
- [Adaptive RAG](https://arxiv.org/abs/2403.14403) (2024)
  - Dynamically adjust retrieval strategy

---

### Evaluation & Benchmarking

**Beginner** 🟢
- [Holistic Evaluation of Language Models (HELM)](https://arxiv.org/abs/2211.09110) (2022)
  - Comprehensive benchmark
- [TruthfulQA: Measuring How Models Mimic Human Falsehoods](https://arxiv.org/abs/2109.07958) (2021)
  - Testing truthfulness
- [BIG-Bench: Beyond the Imitation Game](https://arxiv.org/abs/2206.04615) (2022)
  - 200+ diverse tasks

**Intermediate** 🟡
- [MMLU: Measuring Massive Multitask Language Understanding](https://arxiv.org/abs/2009.03300) (2021)
  - 57 subjects benchmark
- [HumanEval: Evaluating Large Language Models](https://arxiv.org/abs/2107.03374) (2021)
  - Code generation benchmark
- [Judging LLM-as-a-Judge](https://arxiv.org/abs/2306.05685) (2023)
  - Using LLMs to evaluate LLMs
- [Chatbot Arena: Elo Ratings](https://arxiv.org/abs/2403.04132) (2024)
  - Crowdsourced evaluation

**Advanced** 🔴
- [Understanding the Capabilities of LLMs](https://arxiv.org/abs/2310.04988) (2023)
  - Systematic capability analysis
- [BBH: BIG-Bench Hard](https://arxiv.org/abs/2210.09261) (2022)
  - Challenging tasks for CoT

---

### Fine-tuning & Training

**Beginner** 🟢
- [Parameter-Efficient Fine-Tuning (Blog)](https://huggingface.co/blog/peft) (2023)
  - PEFT overview from Hugging Face
- [LoRA: Low-Rank Adaptation](https://arxiv.org/abs/2106.09685) (2021)
  - Efficient fine-tuning method

**Intermediate** 🟡
- [QLoRA: Efficient Finetuning of Quantized LLMs](https://arxiv.org/abs/2305.14314) (2023)
  - Fine-tune large models on single GPU
- [Instruction Tuning](https://arxiv.org/abs/2109.01652) (2021)
  - Teaching models to follow instructions
- [RLHF: Training Language Models to Follow Instructions](https://arxiv.org/abs/2203.02155) (2022)
  - Reinforcement learning from human feedback

**Advanced** 🔴
- [Direct Preference Optimization (DPO)](https://arxiv.org/abs/2305.18290) (2023)
  - Alternative to RLHF
- [Constitutional AI](https://arxiv.org/abs/2212.08073) (2022) ⭐ **Must Read**
  - AI-generated feedback for training
- [Scaling Laws for Neural Language Models](https://arxiv.org/abs/2001.08361) (2020)
  - Understanding model size vs performance

---

### Multimodal AI

**Beginner** 🟢
- [CLIP: Connecting Text and Images](https://arxiv.org/abs/2103.00020) (2021)
  - Vision-language pre-training
- [GPT-4V System Card](https://cdn.openai.com/papers/GPTV_System_Card.pdf) (2023)
  - Vision capabilities and limitations

**Intermediate** 🟡
- [Flamingo: Visual Language Model](https://arxiv.org/abs/2204.14198) (2022)
  - Few-shot learning with vision
- [LLaVA: Visual Instruction Tuning](https://arxiv.org/abs/2304.08485) (2023)
  - Open source vision-language model
- [Multimodal Chain-of-Thought](https://arxiv.org/abs/2302.00923) (2023)
  - CoT reasoning over images

**Advanced** 🔴
- [Gemini: A Family of Multimodal Models](https://arxiv.org/abs/2312.11805) (2023)
  - Google's multimodal LLM
- [Set-of-Mark Prompting](https://arxiv.org/abs/2310.11441) (2023)
  - Visual prompting technique

---

### Context & Memory

**Beginner** 🟢
- [Extending Context Window (Blog)](https://blog.gopenai.com/techniques-to-improve-reliability-54482b8c2fda) (2023)
  - Practical techniques
- [Prompt Caching (Anthropic)](https://www.anthropic.com/news/prompt-caching) (2024)
  - Reducing costs with caching

**Intermediate** 🟡
- [Transformer-XL: Attentive Language Models](https://arxiv.org/abs/1901.02860) (2019)
  - Segment-level recurrence
- [Memorizing Transformers](https://arxiv.org/abs/2203.08913) (2022)
  - Explicit memory for long-range
- [MemGPT](https://arxiv.org/abs/2310.08560) (2023)
  - OS-like memory management

**Advanced** 🔴
- [Unlimiformer: Long-Range Transformers](https://arxiv.org/abs/2305.01625) (2023)
  - Unlimited input length
- [LongNet: Scaling Transformers to 1B Tokens](https://arxiv.org/abs/2307.02486) (2023)
  - Dilated attention for extreme length

---

### Security & Safety

**Beginner** 🟢
- [Jailbroken: Evaluating LLM Safety](https://arxiv.org/abs/2307.02483) (2023)
  - Common jailbreak techniques
- [OWASP Top 10 for LLMs (Website)](https://owasp.org/www-project-top-10-for-large-language-model-applications/) (2023)
  - Security vulnerabilities

**Intermediate** 🟡
- [Universal and Transferable Adversarial Attacks](https://arxiv.org/abs/2307.15043) (2023)
  - Prompt injection attacks
- [Constitutional AI](https://arxiv.org/abs/2212.08073) (2022)
  - Training safe models
- [Red Teaming Language Models](https://arxiv.org/abs/2209.07858) (2022)
  - Finding vulnerabilities

**Advanced** 🔴
- [Many-Shot Jailbreaking (Anthropic)](https://arxiv.org/abs/2404.02151) (2024)
  - Long-context vulnerabilities
- [Prompt Injection in LLMs](https://arxiv.org/abs/2306.05499) (2023)
  - Comprehensive analysis
- [Defending Against Backdoor Attacks](https://arxiv.org/abs/2307.16802) (2023)
  - Model security

---

### Production & Systems

**Beginner** 🟢
- [Building Production-Ready RAG Systems (Blog)](https://www.anthropic.com/news/contextual-retrieval) (2024)
  - Anthropic's guide
- [LLMOps: Best Practices (Blog)](https://huyenchip.com/2023/04/11/llm-engineering.html) (2023)
  - Chip Huyen's guide

**Intermediate** 🟡
- [Serving LLMs in Production](https://arxiv.org/abs/2312.03863) (2023)
  - Systems challenges
- [FlashAttention-2](https://arxiv.org/abs/2307.08691) (2023)
  - Faster inference
- [vLLM: PagedAttention for LLM Serving](https://arxiv.org/abs/2309.06180) (2023)
  - Efficient serving system

**Advanced** 🔴
- [Speculative Decoding](https://arxiv.org/abs/2211.17192) (2022)
  - Faster inference with small models
- [Medusa: Simple Framework for LLM Inference](https://arxiv.org/abs/2401.10774) (2024)
  - 2x speedup
- [Optimizing LLM Inference](https://arxiv.org/abs/2312.12870) (2023)
  - Comprehensive systems paper

---

## 📰 Essential Blog Posts & Articles

### Technical Deep Dives

**Lilian Weng (OpenAI Research)**
- [Prompt Engineering](https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/)
- [LLM-Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/)
- [Building LLM Applications for Production](https://lilianweng.github.io/posts/2023-01-27-the-transformer-family/)

**Jay Alammar**
- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)
- [The Illustrated GPT-2](https://jalammar.github.io/illustrated-gpt2/)
- [Visualizing A Neural Machine Translation Model](https://jalammar.github.io/visualizing-neural-machine-translation-mechanics-of-seq2seq-models-with-attention/)

**Chip Huyen**
- [Building LLM Applications for Production](https://huyenchip.com/2023/04/11/llm-engineering.html)
- [RLHF: Reinforcement Learning from Human Feedback](https://huyenchip.com/2023/05/02/rlhf.html)
- [Real-time ML](https://huyenchip.com/2022/01/02/real-time-machine-learning.html)

**Eugene Yan**
- [Patterns for Building LLM Applications](https://eugeneyan.com/writing/llm-patterns/)
- [Improving RAG with Reranking](https://eugeneyan.com/writing/reranking/)
- [System Design for Large Scale ML](https://eugeneyan.com/writing/system-design-for-discovery/)

**Simon Willison**
- [Prompt injection explained](https://simonwillison.net/2023/Apr/14/worst-that-can-happen/)
- [Embeddings: What they are and why they matter](https://simonwillison.net/2023/Oct/23/embeddings/)
- [LLM series](https://simonwillison.net/series/llms/) - All LLM posts

### Company Research Blogs

**Anthropic**
- [Introducing Claude](https://www.anthropic.com/index/introducing-claude)
- [Constitutional AI paper explained](https://www.anthropic.com/constitutional.pdf)
- [Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)
- [Prompt Caching](https://www.anthropic.com/news/prompt-caching)

**OpenAI**
- [GPT-4 Research](https://openai.com/research/gpt-4)
- [Weak-to-Strong Generalization](https://openai.com/research/weak-to-strong-generalization)
- [Practices for Governing Agentic AI Systems](https://openai.com/research/practices-for-governing-agentic-ai-systems)

**Google DeepMind**
- [Gemini: A Family of Models](https://blog.google/technology/ai/google-gemini-ai/)
- [AlphaCode: Competitive Programming](https://www.deepmind.com/blog/competitive-programming-with-alphacode)

---

## 📅 Reading Plans

### 30-Day Reading Plan (Foundations)

**Week 1: Transformers & Basics**
- Day 1-2: [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)
- Day 3-4: [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- Day 5-7: [GPT-3 Paper](https://arxiv.org/abs/2005.14165)

**Week 2: Prompting**
- Day 8-9: [Chain-of-Thought](https://arxiv.org/abs/2201.11903)
- Day 10-11: [ReAct](https://arxiv.org/abs/2210.03629)
- Day 12-14: [Tree of Thoughts](https://arxiv.org/abs/2305.10601)

**Week 3: Agents & RAG**
- Day 15-16: [Generative Agents](https://arxiv.org/abs/2304.03442)
- Day 17-18: [RAG Paper](https://arxiv.org/abs/2005.11401)
- Day 19-21: [Lost in the Middle](https://arxiv.org/abs/2307.03172)

**Week 4: Production & Safety**
- Day 22-24: [Constitutional AI](https://arxiv.org/abs/2212.08073)
- Day 25-27: [GPT-4 Technical Report](https://arxiv.org/abs/2303.08774)
- Day 28-30: Blog posts from Chip Huyen, Eugene Yan

### 90-Day Deep Dive Plan

See [LEARNING-PATHS.md](LEARNING-PATHS.md) for comprehensive learning roadmaps.

---

## 🎯 Papers by Use Case

### Building Chat Applications
1. GPT-3 Paper (few-shot learning)
2. Constitutional AI (safety)
3. Prompt Engineering Guide (techniques)

### Building RAG Systems
1. RAG Paper (fundamentals)
2. Lost in the Middle (context position)
3. Self-RAG (self-reflection)
4. HyDE (hypothetical docs)
5. Contextual Retrieval (Anthropic blog)

### Building Agents
1. ReAct (reasoning + acting)
2. Toolformer (tool use)
3. Reflexion (self-reflection)
4. AutoGen (multi-agent)

### Code Generation
1. Codex Paper
2. HumanEval (evaluation)
3. AlphaCode

---

## 💡 Reading Tips

**For Academic Papers**:
1. Read abstract and conclusion first
2. Look at figures and tables
3. Read introduction
4. Skip heavy math on first pass
5. Focus on intuition and results
6. Implement key concepts

**For Blog Posts**:
1. Scan headings first
2. Read code examples carefully
3. Try examples in your environment
4. Take notes on key insights

**Building a Reading Habit**:
- Set aside 30-60 minutes daily
- Use tools like [Arxiv Sanity](http://www.arxiv-sanity.com/)
- Join reading groups or book clubs
- Share summaries with others
- Keep a reading log

---

## 📚 Related Resources

- [RESOURCES.md](RESOURCES.md) - Links and documentation
- [LEARNING-PATHS.md](LEARNING-PATHS.md) - Structured learning roadmaps
- [TOOLS-ECOSYSTEM.md](TOOLS-ECOSYSTEM.md) - Tools and frameworks
- [COMMUNITY.md](COMMUNITY.md) - Discussion and communities

---

## 🔄 Staying Current

**Paper Aggregators**:
- [Arxiv Sanity](http://www.arxiv-sanity.com/)
- [Papers with Code](https://paperswithcode.com/)
- [Hugging Face Papers](https://huggingface.co/papers)

**Newsletters**:
- The Batch (DeepLearning.AI)
- Import AI (Jack Clark)
- TLDR AI

**Follow Researchers**:
- Twitter/X: @AnthropicAI, @OpenAI, @GoogleAI
- Personal blogs (listed above)

---

**Last Updated**: 2026-01-08

*Reading is fundamental. Set aside time every day to learn from the best.*
