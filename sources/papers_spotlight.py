from typing import List, Dict, Any

# Curated catalog of high-impact classic and foundational research papers
FOUNDATIONAL_PAPERS = [
    {
        "id": "paper:deepseek-r1",
        "title": "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning",
        "author": "DeepSeek-AI",
        "year": "2025",
        "topic": "Reasoning & Thinking Models",
        "url": "https://arxiv.org/abs/2501.12948",
        "special": "Demonstrates that reasoning behaviors (self-reflection, verification) emerge purely through large-scale RL without supervised fine-tuning.",
        "use_cases": "Next-generation reasoning systems, math/coding problem solvers, test-time compute scaling.",
        "specs": "Pure RL post-training (DeepSeek-R1-Zero) + multi-stage distillation into dense Qwen/Llama models."
    },
    {
        "id": "paper:attention-is-all-you-need",
        "title": "Attention Is All You Need (The Transformer Architecture)",
        "author": "Vaswani et al. (Google Brain)",
        "year": "2017",
        "topic": "New Architectures & Non-Transformers",
        "url": "https://arxiv.org/abs/1706.03762",
        "special": "Replaced recurrence and convolutions with multi-head self-attention, establishing the foundational architecture for all modern LLMs.",
        "use_cases": "GPT-4, Claude, LLaMA, Whisper, Sora, and virtually all modern AI foundation models.",
        "specs": "Multi-Head Self-Attention + Positional Encodings. Linear complexity in training parallelization."
    },
    {
        "id": "paper:mamba-ssm",
        "title": "Mamba: Linear-Time Sequence Modeling with Selective State Spaces",
        "author": "Gu & Dao (Carnegie Mellon / Princeton)",
        "year": "2023",
        "topic": "New Architectures & Non-Transformers",
        "url": "https://arxiv.org/abs/2312.00752",
        "special": "Introduced selective state space models (SSMs) achieving linear-time inference and scaling to 1M+ token contexts without quadratic attention bottlenecks.",
        "use_cases": "Ultra-long document understanding, continuous sensor stream processing, low-latency edge inference.",
        "specs": "Selective State Space (SSM) hardware-aware kernel, 5x inference throughput over standard transformers."
    },
    {
        "id": "paper:lora",
        "title": "LoRA: Low-Rank Adaptation of Large Language Models",
        "author": "Hu et al. (Microsoft Research)",
        "year": "2021",
        "topic": "New LLMs & Model Weights",
        "url": "https://arxiv.org/abs/2106.09685",
        "special": "Freezes pretrained weights and injects trainable rank decomposition matrices, reducing trainable parameters by 10,000x with zero latency overhead.",
        "use_cases": "Fine-tuning 70B+ LLMs on consumer GPUs, personalized models, fast domain adaptation.",
        "specs": "Low-rank matrix decomposition: W + B*A. Reduces GPU VRAM by up to 3x."
    },
    {
        "id": "paper:flashattention",
        "title": "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness",
        "author": "Dao et al. (Stanford University)",
        "year": "2022",
        "topic": "New Architectures & Non-Transformers",
        "url": "https://arxiv.org/abs/2205.14135",
        "special": "Redesigned attention algorithm to minimize memory reads/writes between GPU HBM and SRAM, yielding 2-4x wall-clock speedup with zero approximation.",
        "use_cases": "Every modern training & inference engine: vLLM, HuggingFace transformers, PyTorch SDPA.",
        "specs": "Tiled attention computation + kernel fusion. Sub-quadratic memory footprint."
    },
    {
        "id": "paper:whisper",
        "title": "Robust Speech Recognition via Large-Scale Weak Supervision (Whisper)",
        "author": "Radford et al. (OpenAI)",
        "year": "2022",
        "topic": "ASR & Speech-to-Text",
        "url": "https://arxiv.org/abs/2212.04356",
        "special": "Trained on 680,000 hours of multilingual web audio, achieving human-level zero-shot robustness across accents, background noise, and technical jargon.",
        "use_cases": "Real-time speech transcription, multilingual subtitle generation, voice interfaces.",
        "specs": "Encoder-decoder Transformer trained in sequence-to-sequence multi-task format."
    },
    {
        "id": "paper:f5-tts",
        "title": "F5-TTS: A Fairytaler that Fakes Fluent and Faithful Speech with Flow Matching",
        "author": "Chen et al.",
        "year": "2024",
        "topic": "TTS & Voice Generation",
        "url": "https://arxiv.org/abs/2410.06885",
        "special": "Non-autoregressive flow matching speech generator that eliminates complex text aligners, producing ultra-realistic voice clones from a 3-second audio prompt.",
        "use_cases": "Zero-shot voice cloning, emotional narration, podcast dubbing, real-time gaming dialogue.",
        "specs": "Diffusion Transformer (DiT) with ConvNeXt v2 backbones and Flow Matching objective."
    },
    {
        "id": "paper:react-agents",
        "title": "ReAct: Synergizing Reasoning and Acting in Language Models",
        "author": "Yao et al. (Princeton & Google Brain)",
        "year": "2022",
        "topic": "AI Agents & Autonomous Systems",
        "url": "https://arxiv.org/abs/2210.03629",
        "special": "Combines reasoning traces ('thought') with action execution ('tool calls'), creating the foundational architecture powering modern agent frameworks.",
        "use_cases": "Autonomous coding agents, web browser bots, Devin-like software engineers, tool use.",
        "specs": "Interleaved Thought -> Action -> Observation execution loop."
    },
    {
        "id": "paper:sora-diffusion",
        "title": "Video Generation Models as World Simulators (Sora Tech Report)",
        "author": "OpenAI",
        "year": "2024",
        "topic": "Video Generation & World Models",
        "url": "https://openai.com/research/video-generation-models-as-world-simulators",
        "special": "Treats video patches as spacetime tokens inside a Diffusion Transformer (DiT), demonstrating 3D physical consistency and camera motion persistence.",
        "use_cases": "Cinematic visual generation, robotic physics simulation, synthetic training data.",
        "specs": "Spacetime latent patchification + scalable Diffusion Transformer architecture."
    },
    {
        "id": "paper:dpo",
        "title": "Direct Preference Optimization: Your Language Model is Secretly a Reward Model",
        "author": "Rafailov et al. (Stanford University)",
        "year": "2023",
        "topic": "New LLMs & Model Weights",
        "url": "https://arxiv.org/abs/2305.18290",
        "special": "Replaced complex RLHF (PPO + separate reward model) with an elegant closed-form loss directly on model logits, dramatically stabilizing alignment.",
        "use_cases": "Fine-tuning open weights models for instruction following, chat alignment, preference tuning.",
        "specs": "Closed-form policy optimization directly optimizing cross-entropy on preferred vs rejected pairs."
    }
]

class PapersSpotlightScout:
    """Surfaces curated high-impact breakthrough and foundational research papers."""
    def fetch_spotlight_papers(self) -> List[Dict[str, Any]]:
        results = []
        for p in FOUNDATIONAL_PAPERS:
            results.append({
                "id": p["id"],
                "title": f"{p['title']} ({p['year']})",
                "description": f"Foundational Research Paper by {p['author']}. {p['special']}",
                "url": p["url"],
                "source": f"Classic Research Spotlight ({p['year']})",
                "author": p["author"],
                "tags": ["research", "paper", "foundational", p["topic"].lower()],
                "extra": {
                    "special": p["special"],
                    "use_cases": p["use_cases"],
                    "specs": p["specs"]
                }
            })
        return results
