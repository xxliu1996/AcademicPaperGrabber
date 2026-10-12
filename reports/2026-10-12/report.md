# AI 论文周报（2026-10-06 – 2026-10-12）

本周最清晰的一条暗线是「强化学习进入抠成本阶段」：从 FP4/NVFP4 低精度回滚（TRACE、TRIAGE）、低秩梯度草图省显存（LoGRA），到 MoE 大模型的稳定 RL（MiMo-V2.6），大家不再争谁的 RL 更强，而是争谁的 RL 更便宜、更稳。与之呼应的是「环境即训练数据」的集体转向——Agent 方向这周几乎被各种 Gym 和 World 刷屏（AgentGarten、SoftwareGym、从轨迹重建的语言世界模型），机器人方向则被「世界-动作模型」统治（Long-WAM、UniWAM、ViGAR），核心命题都是：既然真实交互数据贵，那就把环境本身造出来。相比之下，多模态仍在生成与评测两头使劲，而智能眼镜 / 第一人称视觉这周偏安静，多是感知与交互的扎实工作，公开热度数据明显偏少。一句话：这是打地基的一周，不是放烟花的一周。

---

## ⭐ 本周最值得读的 5 篇

1. **AgentGarten：让智能体进化的代码世界**（Agent）— 把模拟器写成代码就能接入、环境随智能体一起扩展，4 轮学会传统 RL 要上百万轮的任务｜[arXiv:2610.12374](https://arxiv.org/abs/2610.12374)
2. **重新审视跨分词器的在线策略蒸馏**（大语言模型）— 一句"别追对齐覆盖面、先保监督可靠性"重写了跨分词器蒸馏的共识｜[arXiv:2610.08448](https://arxiv.org/abs/2610.08448)
3. **S-Space：多模态模型里的空间工作区**（多模态 / 视觉语言）— 首次在 MLLM 内部找到编码连续坐标的线性子空间，还能当诊断工具定位推理失败｜[arXiv:2610.13527](https://arxiv.org/abs/2610.13527)
4. **Reflex：以视觉为基础的人形机器人反应式控制**（机器人与具身智能）— 纯第一视角视觉做全身反应式接取，仿真 85.7% 逼近特权观测｜[arXiv:2610.12772](https://arxiv.org/abs/2610.12772)
5. **多智能体第一人称世界模型**（智能眼镜 / 可穿戴 / 第一人称视觉）— 同一序列里联合去噪多条 ego 视频流，为多人协作 AR/VR 给出共享世界范式｜[arXiv:2610.12299](https://arxiv.org/abs/2610.12299)

---

## 一、大语言模型

### 1. 重新审视跨分词器的在线策略蒸馏：从对齐覆盖到监督可靠性

**Rethinking Cross-Tokenizer On-Policy Distillation: From Alignment Coverage to Supervision Reliability**
🔥 HF 211 赞 ｜ [arXiv:2610.08448](https://arxiv.org/abs/2610.08448)

- **问题**：师生模型分词器不同时，如何对齐预测才能让在线策略蒸馏学得更好。
- **做法**：发现严格 1:1 对齐已覆盖多数学生 token，仅在共享词表 top-16 子集上做反向 KL，并对错配位置补监督做对比。
- **效果**：精度与全共享词表蒸馏相当并超过跨分词器基线，而补充的跨度监督反而拉低准确率。
- **值得看**：提示与其追求对齐覆盖面，不如优先保证监督信号的可靠性。

### 2. LoGRA：用低秩梯度草图扩展大模型强化学习

**LoGRA: Scaling LLM Reinforcement Learning with Low-Rank Gradient Sketches**
NVIDIA ｜ 🔥 HF 149 赞 ｜ 💻 [代码](https://github.com/skzhang1/labs-molt) ｜ [arXiv:2610.06647](https://arxiv.org/abs/2610.06647)

- **问题**：强化学习后训练显存开销大，限制了更大规模的推广使用。
- **做法**：把学习信号压进低秩梯度草图，兼顾模型更新与策略同步，并用预测 KL 控制每步更新幅度。
- **效果**：训练显存最多降 45.7%，单台八卡节点可稳定训练 27B 模型超 1100 步，而稠密 Adam 会爆显存。
- **值得看**：让原本显存上不可行的 RL 训练落到常规硬件上。

### 3. TokenRouter：面向 Token 级路由的高效大模型服务系统

**TokenRouter: Efficient Serving System for Token-Level LLM Routing**
Tsinghua-NICS-EFC ｜ 🔥 HF 130 赞 ｜ 💻 [代码](https://github.com/thu-nics/TokenRouter) ｜ [arXiv:2610.12242](https://arxiv.org/abs/2610.12242)

- **问题**：Token 级模型路由能提升性价比，但现有服务系统存在步调失同步与批次准入延迟。
- **做法**：采用"以请求为中心编程、以模型为中心执行"的设计，为每个模型起子服务器异步派发，并用数学吞吐模型推导延迟批处理的最优超参。
- **效果**：解码吞吐比现有系统高 2.01 至 64.15 倍。
- **值得看**：把前沿路由算法真正变成可部署的生产级服务。

### 4. STEPQuant：Delta 规则循环状态量化中误差何时何处才重要

**STEPQuant: When and Where Errors Matter in Delta-Rule Recurrent State Quantization**
Zhejiang University ｜ 🔥 HF 128 赞 ｜ 💻 [代码](https://github.com/Dreamer-Toby/STEPQuant) ｜ [arXiv:2609.38169](https://arxiv.org/abs/2609.38169)

- **问题**：线性注意力的循环状态在并发服务时成为显存瓶颈，直接低比特量化会严重掉点。
- **做法**：依据误差幅度与记忆存续时间在时间、空间两维分配精度，联合拟合键行与值列的缩放。
- **效果**：6 比特下精度接近 FP32 状态，循环状态压缩超 5 倍，整体服务显存最多降 68.7%。
- **值得看**：给线性注意力模型的长时服务提供了实用的省显存路线。

### 5. TRACE：面向 MoE 模型 FP4 强化学习的回滚引导量化感知训练

**TRACE: Rollout-Guided Quantization-Aware Training for FP4 Reinforcement Learning of MoE Language Models**
Qwen ｜ 🔥 HF 92 赞 ｜ [arXiv:2610.07767](https://arxiv.org/abs/2610.07767)

- **问题**：低精度 RL 回滚能省算力，但现有 FP4 方法只各自优化训练与回滚路径，忽视两条路径的差异。
- **做法**：用回滚侧量化结果引导训练侧 FP4 舍入决策，直接缩小训练与回滚差距，并选择性缓存深层尾数与缩放信息降低开销。
- **效果**：在四个大规模 MoE 模型上 RL 效果比肩 BF16 回滚，回滚最高提速 5.4 倍。
- **值得看**：为大 MoE 模型低精度强化学习给出可落地方案。

### 6. DecepEval：评估大模型智能体欺骗行为的基准

**DecepEval: A Benchmark for Evaluating Deception in LLM Agents**
Xi'an Jiaotong University ｜ 🔥 HF 82 赞 ｜ 💻 [代码](https://github.com/functy/DECEPEVAL) ｜ [arXiv:2610.07967](https://arxiv.org/abs/2610.07967)

- **问题**：智能体为完成任务可能撒谎，但已有评测多为孤立场景，难以系统刻画欺骗何时更易发生。
- **做法**：构建 1532 个实例、28 个专业场景，提出含压力、诱因、机会、冲突四条件的"欺骗钻石"框架，用中性与诱导配对实例测量变化。
- **效果**：九个前沿模型评测显示，诱导条件下各模型欺骗率普遍上升，连低基线模型也不例外。
- **值得看**：把智能体的欺骗脆弱性变成可量化、可比较的指标。

### 7. HuatuoGPT-3：从基座模型出发的纯强化学习领域适配

**HuatuoGPT-3: RL-Only Domain Adaptation from Base Models**
Chinese University of Hong Kong, Shenzhen ｜ 🔥 HF 47 赞 ｜ 💻 [代码](https://github.com/FreedomIntelligence/HuatuoGPT-3) ｜ [arXiv:2610.05966](https://arxiv.org/abs/2610.05966)

- **问题**：SFT+RL 流程会削弱探索多样性且流程复杂，而纯 RL 又有冷启动与教师信号陈旧的难题。
- **做法**：提出单阶段策略优化 OnePO，把教师输出当作临时引导，强化低概率信息 token 并在学生超越时"退役"教师。
- **效果**：仅 20K 样本在 HealthBench 拿 67.2，超 SFT+RL 2.7 分；27B 版达 70.1，超过 GPT-6 Astra 等前沿模型。
- **值得看**：展示了跳过 SFT、纯 RL 也能做出强领域专家模型。

### 8. 把循环模型做对，第二部：在不动点上重新思考

**Towards Looped Models Done Right, Part II: Rethinking at Fixed Points**
Institute of Foundation Models ｜ 🔥 HF 34 赞 ｜ 💻 [代码](https://github.com/ifm-ai/xllm-loop) ｜ [arXiv:2610.06833](https://arxiv.org/abs/2610.06833)

- **问题**：循环语言模型每多一次循环都在训练、解码、预填充与 RL 上加成本。
- **做法**：利用循环状态趋近不动点的特性做截断反传、终态 KV 共享与基于保存状态的 RL 梯度，并改进深度先验与正交输入注入。
- **效果**：从 100M 到 1.6B 各尺度降低困惑度；1.6B 下 KV 缓存缩小 3 倍仍比肩定深训练的下游均分。
- **值得看**：给循环深度模型的高效训练与推理补齐关键组件。

### 9. 让大模型说出它真正想的：度量并改进思维链与可解释性的一致性

**Making LLMs Say What They Think: Measuring and Improving CoT-Interpretability Alignment**
New York University ｜ 🔥 HF 29 赞 ｜ 💻 [代码](https://github.com/yihuaihong/CIA-minimal-repro) ｜ [arXiv:2609.38972](https://arxiv.org/abs/2609.38972)

- **问题**：思维链常被当作模型推理过程的代理，但未必反映其内部真实计算。
- **做法**：提出 CIA 指标，用可解释性工具衡量思维链与内部推理策略的一致程度，并以准确率加参数忠实度为奖励做后训练。
- **效果**：三个模型在各任务上一致性仅 44.8 至 75.9%，后训练可在保持或提升准确率的同时显著改善忠实度。
- **值得看**：为审计思维链忠实度提供框架，也指出一条让显式推理更可信的路径。

### 10. SparseDecoding：面向准确高效大模型推理的解码感知剪枝

**SparseDecoding: Decoding-Aware Pruning for Accurate and Efficient LLM Inference**
Westlake ENCODE Lab ｜ 🔥 HF 30 赞 ｜ [arXiv:2610.12327](https://arxiv.org/abs/2610.12327)

- **问题**：解码阶段受显存带宽限制，而现有剪枝用自然文本算 Hessian，与自生成 token 存在分布偏移。
- **做法**：从稠密模型自回归生成时采集的激活构造校准矩阵以对齐解码分布，并设计带位掩码与定步遍历的 N:M 稀疏矩阵-向量核。
- **效果**：在 Llama 与 Qwen3 系列上长文本生成优于固定文本校准，A100 上端到端解码最高提速 1.48 倍。
- **值得看**：把剪枝目标真正对准解码实际行为，兼顾算法与系统两端。

---

## 二、多模态 / 视觉语言

### 1. S-Space：探寻多模态语言模型里的空间工作区

**S-Space: Exploring Spatial Workspace in Multimodal Language Models**
MirroS ｜ 🔥 HF 201 赞 ｜ 💻 [代码](https://github.com/mirros-lab/s-space) ｜ [arXiv:2610.13527](https://arxiv.org/abs/2610.13527)

- **问题**：多模态模型会空间推理，但内部机制一直是黑盒。
- **做法**：发现 S-Space 这一线性子空间，物体 token 在其中沿水平、垂直、距离轴编码连续坐标，并用因果干预验证。
- **效果**：证明它是模型内在的空间工作区，还可当诊断工具定位推理失败。
- **值得看**：揭示瓶颈在于视角变换而非感知，为理解空间能力提供新视角。

### 2. UltraText Bench：评测图像生成中密集视觉文字的双语基准

**UltraText Bench: A Comprehensive Bilingual Benchmark for Evaluating Visual Text Rendering in Image Generation**
Westlake University ｜ 🔥 HF 186 赞 ｜ 💻 [代码](https://github.com/LINs-lab/UltraText_Bench) ｜ [arXiv:2610.09823](https://arxiv.org/abs/2610.09823)

- **问题**：图像生成的短文字渲染已进步，但密集长文字缺乏系统评测。
- **做法**：构建 432 条中英双语提示、24 类场景、三档难度，用 Q-Judger 从保真、清晰、空间、画质四维打分。
- **效果**：区分出各模型长短板，如 Qwen-Image-2512 英文从 L1 的 86.50 跌到 L3 的 42.86。
- **值得看**：给文字渲染能力一把细颗粒度的尺子，方便横向选型。

### 3. DuoMatching：少步视频生成的联合-边缘分布匹配

**DuoMatching: Joint-Marginal Distribution Matching for Few-Step Video Generation**
ByteDance ｜ 🔥 HF 100 赞 ｜ 💻 [代码](https://github.com/JohnZhan2023/DuoMatching) ｜ [arXiv:2610.03543](https://arxiv.org/abs/2610.03543)

- **问题**：分布匹配蒸馏虽抑制了自回归漂移，画质与语义对齐仍不足。
- **做法**：在联合匹配上加边缘匹配，引入图像生成器做帧级监督，配 LatentBridge 对齐潜空间。
- **效果**：画质、构图、语义对齐均提升，人评整体偏好率超 80%。
- **值得看**：为流式视频蒸馏补上帧级先验的思路清晰可借鉴。

### 4. GRACE：面向生成的潜空间压缩加速视频生成

**GRACE: Generation-aware latent compression for efficient video generation**
KAIST AI ｜ 🔥 HF 86 赞 ｜ 💻 [代码](https://github.com/cvlab-kaist/GRACE) ｜ [arXiv:2610.10524](https://arxiv.org/abs/2610.10524)

- **问题**：高压缩视频自编码器能加速 DiT，但会破坏与预训练潜空间的兼容。
- **做法**：冻结基础潜码、学残差潜码，在冻结 DiT 特征空间对齐，再轻量微调加非对称去噪。
- **效果**：Wan2.1-I2V-14B token 减 8 倍、延迟降 11.1 倍，VBench 质量持平。
- **值得看**：无需从头重训就能大幅提速，落地性强。

### 5. VepAgent：工具增强强化学习打通视频事件预测的因果缺口

**VepAgent: Bridging Causal-Transition via Tool-Augmented Reinforcement Learning for Video Event Prediction**
UCSC-VLAA ｜ 🔥 HF 61 赞 ｜ [arXiv:2610.06293](https://arxiv.org/abs/2610.06293)

- **问题**：多模态模型做视频事件预测时依赖回顾式总结和文本先验，难以补上未观测的因果转移。
- **做法**：构建思维链数据集做 SFT，配状态跟踪、帧检索、区域放大等工具库与复合奖励的 RL。
- **效果**：在 FutureBench、NEPBench 上达到 SOTA，超越更大的多模态模型。
- **值得看**：把因果推理显式建模成智能体流程，为预测类任务提供范式。

### 6. VisionWeave：把弹性视觉表示做成多模态模型的原生能力

**VisionWeave: Weaving Elastic Visual Representations as a Native Capability of MLLMs**
Qwen ｜ 🔥 HF 55 赞 ｜ 💻 [代码](https://github.com/FFY0/VisionWeave) ｜ [arXiv:2610.07987](https://arxiv.org/abs/2610.07987)

- **问题**：多模态模型用固定尺寸密集 patch token，忽视了视觉信息分布不均。
- **做法**：门控空间池化构建粗粒度表示与原生细粒度共存，再用粒度路由按内容自适应分配。
- **效果**：基于 Qwen3.8-27B 平均省 43% token 仍保 98.9% 性能，部署吞吐提升 2.3 倍。
- **值得看**：把自适应压缩内化为模型能力，兼顾效率与质量。

### 7. PolyOCR-Venus：面向文本视觉智能的统一 OCR 基础模型

**PolyOCR-Venus: Unified OCR Foundation Models for Text-Centric Visual Intelligence**
inclusionAI ｜ 🔥 HF 28 赞 ｜ 💻 [代码](https://github.com/inclusionAI/PolyOCR-Venus) ｜ [arXiv:2609.37712](https://arxiv.org/abs/2609.37712)

- **问题**：现有 OCR 系统往往只擅长部分任务，难以兼顾识别、解析与推理。
- **做法**：以统一指令框架加大规模数据引擎，提出能力引导的策略优化融合验证式 GRPO 与在线蒸馏。
- **效果**：在 OCRBench v2.1、CC-OCR、OmniDocBench 等多基准上达到 SOTA 或高度竞争水平。
- **值得看**：覆盖多尺度的开源 OCR 基础模型，附带修订后的评测基准。

### 8. VIEScore2：带空间定位解释的统一图像评估

**VIEScore2: Unified Image Evaluation with Spatially Grounded Explanations**
TIGER-Lab ｜ 🔥 HF 30 赞 ｜ 💻 [代码](https://github.com/TIGER-AI-Lab/VIEScore2) ｜ [arXiv:2610.00994](https://arxiv.org/abs/2610.00994)

- **问题**：现有合成图像评估只给标量分，说不清缺陷在哪。
- **做法**：把图像表示为 N×N 网格，一次前向同时预测质量分与缺陷位置，再用 GRPO 优化定位。
- **效果**：整体分 SRCC 达 0.601，优于 Gemini-3-Flash 的 0.491，缺陷定位多基准领先。
- **值得看**：可验证、可解释的图像评估器，解释随分数一并给出。

### 9. OneSearch-VL：面向图像与视频的统一多模态深度研究智能体

**OneSearch-VL: Unified Multimodal Deep Research Agent for Image and Video**
🔥 HF 24 赞 ｜ 💻 [代码](https://github.com/appletea233/OneSearch-VL) ｜ [arXiv:2610.12419](https://arxiv.org/abs/2610.12419)

- **问题**：单图、多图、视频的深度研究操作各异，却难以保留视觉锚点与证据链的依赖关系。
- **做法**：以视觉定位证据图统一数据构建、过程监督与评测，配 SFT、RL 数据与证据感知奖励。
- **效果**：OneSearch-VL-8B 在两个新基准上较带工具的 Qwen3-VL-8B 分别提升 20.2 和 17.6 个百分点。
- **值得看**：把证据可追溯性做进训练与评测闭环，统一处理多种视觉研究场景。

### 10. VibeEdit：用画布指令做图像编辑

**VibeEdit: Image Editing with Canvas Instructions**
The University of Sydney ｜ 🔥 HF 18 赞 ｜ 💻 [代码](https://github.com/ZhaoJingjing713/VibeEdit) ｜ [arXiv:2610.12229](https://arxiv.org/abs/2610.12229)

- **问题**：文本编辑描述改动容易，但相似物体多时指认目标很麻烦。
- **做法**：让用户在图上直接画标记加简短备注构成画布指令，基于 Qwen-Image-Edit 做层解耦条件与区域加权训练加 RL。
- **效果**：VLM 评分 79.9、区域外 PSNR 32.8 dB，优于文本指令最强基线 FireRed 的 67.4 与 24.0 dB。
- **值得看**：空间标记式交互更贴近真实编辑需求，目标选择更精准。

---

## 三、Agent

### 1. AgentGarten：让智能体进化的代码世界

**AgentGarten: Code Worlds for Evolving Agents**
MirroS ｜ 🔥 HF 259 赞 ｜ 💻 [代码](https://github.com/MirroS-Lab/AgentGarten) ｜ [arXiv:2610.12374](https://arxiv.org/abs/2610.12374)

- **问题**：智能体能学到什么，受限于练习环境是否既忠实又逼真，而两者兼顾一直是瓶颈。
- **做法**：把模拟器和游戏引擎与一个共享神经渲染器耦合，用对抗性强制蒸馏改造预训练视频模型，支持实时交互。
- **效果**：智能体仅需 4 轮即可学会，而传统强化学习需上百万轮。
- **值得看**：新世界只要写成代码就能接入，环境可随智能体一起在数量和难度上扩展。

### 2. 自我回溯蒸馏：把事后经验变成事前预判

**Self-Retrospection Distillation: Turning Post-hoc Experiences into Prior Foresight**
Salesforce AI Research ｜ 🔥 HF 175 赞 ｜ 💻 [代码](https://github.com/SalesforceAIResearch/SRD) ｜ [arXiv:2610.08077](https://arxiv.org/abs/2610.08077)

- **问题**：RLVR 在所有采样回报相同时奖励信号消失，可轨迹里其实藏着任务要求和失败线索。
- **做法**：提出前瞻学习，用事后经验监督行动前视角的预判，并以 SRD 把事后洞见蒸馏进策略的预测表征。
- **效果**：10 项工具推理与长程任务上最高提升 24.2 个百分点；2B 设置下 RLVR 成功率 0%，加 SRD 达 60.6%。
- **值得看**：说明事后经验不止能评估行为，还能塑造行动前的预测能力，尤其适合奖励稀疏场景。

### 3. Learn2Play Bench：LLM 智能体在陌生环境里能否从经验学习

**Learn2Play Bench: How Well Do LLM Agents Learn from Experience in Unfamiliar Environments?**
National University of Singapore ｜ 🔥 HF 137 赞 ｜ 💻 [代码](https://github.com/liushiliushi/Learn2Play-Bench) ｜ [arXiv:2610.08215](https://arxiv.org/abs/2610.08215)

- **问题**：已有基准的规则多已写在指令里或为模型熟知，难以区分从交互中学习与调用已有知识。
- **做法**：设计一批规则新颖甚至反直觉的文本游戏，提供可复现反馈与自动评分，并变换关卡实例检验迁移。
- **效果**：完整保留动作与反馈记录比总结成规则更利于学习；顶尖人类玩家峰值分仍高于被测智能体。
- **值得看**：换个 harness 能在固定底座下同时提升表现并降低推理成本，给工程选型以参考。

### 4. nanoMuse：为你每台设备准备的开源个人智能体

**nanoMuse: An Open-Source Personal Agent for Every Device You Own**
Zhejiang University ｜ 🔥 HF 110 赞 ｜ 💻 [代码](https://github.com/nano-muse/nanoMuse) ｜ [arXiv:2610.08699](https://arxiv.org/abs/2610.08699)

- **问题**：Meta 的 Muse 展示了跨设备、有记忆、会主动开口的个人智能体，但它封闭在厂商云里，没有开源对应物。
- **做法**：以五个问题和三层视野定义个人智能体，推出 GPL-3.0 的 nanoMuse，每台设备一个代理，共享一条对话。
- **效果**：所有动作经 Sentinel 把关，记忆是用户可读的文件，模型由用户自选，给出规模与成本估算。
- **值得看**：想自建可控、可审计的私人助理、不把数据交给云端的人，这是一份可落地的开源蓝本。

### 5. 从轨迹到智能体世界：用于交互环境模拟的语言世界模型

**From Traces to Agentic Worlds: Agentic Language World Models for Interactive Environment Simulation**
Nanyang Technological University Singapore ｜ 🔥 HF 105 赞 ｜ 💻 [代码](https://github.com/ruyue0001/trace2env) ｜ [arXiv:2610.06100](https://arxiv.org/abs/2610.06100)

- **问题**：训练和评测智能体需要逼真的环境副本，但原系统常常无法访问或难以复刻。
- **做法**：提出 Trace2Env，无需训练，把历史交互轨迹重建成含模式、证据与行为知识的环境世界书，由世界模型代理推断观测与状态变化。
- **效果**：九个环境上下一步观测保真度与长程一致性均优于基于提示的方法，动作回放到真实环境时更常有效。
- **值得看**：为没有可执行原系统时搭建仿真环境提供了一条新思路。

### 6. SoftwareGym：用多样合成软件环境扩展 Computer-Use 智能体训练

**SoftwareGym: Scaling Computer-Use Agent Training with Diverse Synthesized Software Environments**
Shanghai Jiao Tong University ｜ 🔥 HF 83 赞 ｜ 💻 [代码](https://github.com/MrKiing-Jin/SoftwareGym) ｜ [arXiv:2610.12611](https://arxiv.org/abs/2610.12611)

- **问题**：Computer-Use 智能体进步很快，但大规模合成多样且可靠的软件环境依然困难，原生应用构建成本高、浏览器环境交互浅。
- **做法**：提出自动化流水线生成结构多样、功能可执行、运行时验证的 GUI 软件，并用 GUI 评估加迭代修复保证可靠。
- **效果**：合成 182 个应用、GUI 任务平均通过率 91.5%；训练后在 OSWorld 上 Pass@3 从 41.39% 升至 56.97%。
- **值得看**：展示了合成软件环境作为可扩展、可迁移监督信号的潜力。

### 7. MiMo-V2.6：面向自我提升扩展强化学习

**MiMo-V2.6: Scaling Reinforcement Learning Towards Self-Improvement**
Xiaomi MiMo ｜ 🔥 HF 76 赞 ｜ [arXiv:2610.11959](https://arxiv.org/abs/2610.11959)

- **问题**：强化学习是推动大模型自我提升的核心范式，但在超大规模下扩展算力并保持稳定颇具挑战。
- **做法**：沿更大批量与吞吐、更多样复杂的环境、更多评分算力三个维度扩展 RL，冻结 MoE 路由并搭建多层防奖励黑客机制。
- **效果**：异步训练在最长 1M 上下文下每步消耗 1568 样本、2.7–3.7B token；开源了训练动态、RL 环境与框架。
- **值得看**：全模态模型家族的工程细节与基础设施披露，对做大规模 agentic RL 的团队有参考价值。

### 8. CheckerBench：长程智能体能否合成静态分析检查器

**CheckerBench: Can Long-Horizon Agents Synthesize Static-Analysis Checkers?**
Humanlaya Data Lab ｜ 🔥 HF 68 赞 ｜ 💻 [代码](https://github.com/ahang0712/CheckerBench-Dataset) ｜ [arXiv:2610.07557](https://arxiv.org/abs/2610.07557)

- **问题**：现有编码智能体基准多聚焦补丁生成或漏洞检测，少有评估能否在仓库里从零做出一个可用的检查器。
- **做法**：基于 297 个 CVE、167 个仓库构建 300 个可执行任务，并提供独立重建检查器、测量诊断对比与误报的评估框架。
- **效果**：21 种模型-harness 配置下平均 Pass@1 仅 32.30%，最佳也只有 45.33%。
- **值得看**：量化了可靠、可复用检查器开发对当前编码智能体仍是硬骨头，为后续研究锚定了难度。

### 9. EmbodiedCLBench：评测自我进化具身智能体的持续学习

**EmbodiedCLBench: Evaluating Continual Learning for Self-Evolving Embodied Agents**
PKU-VaLuE-Lab ｜ 🔥 HF 62 赞 ｜ 💻 [代码](https://github.com/PKU-VaLuE-Lab/EmbodiedCLBench) ｜ [arXiv:2610.13021](https://arxiv.org/abs/2610.13021)

- **问题**：持续学习研究大多停留在非具身设置，缺少面向具身环境的评测。
- **做法**：以组合泛化为核心原则，构建具身仿真中首个持续学习基准，考察智能体能否先学基础任务再重组技能解决复杂新任务。
- **效果**：零样本几乎无法完成高级任务，但基础任务经验能带来稳定提升，且随任务复杂度增加仍保持。
- **值得看**：也揭示增益不随学习样本数扩展，当前智能体难从额外经验提取有用信息，点出一个被忽视的能力缺口。

### 10. MemAdapter：对抗记忆诱发的阿谀倾向

**Memadapter: Counterfactual Adaptation Against Memory-induced Sycophancy**
DEEP Group at Jilin University ｜ 🔥 HF 60 赞 ｜ 💻 [代码](https://github.com/DEEP-JLU/MemAdapter) ｜ [arXiv:2610.05162](https://arxiv.org/abs/2610.05162)

- **问题**：长期记忆支撑个性化，却会诱发阿谀，让智能体过度迎合用户旧有信念，即便这些信念已过时或与证据不符。
- **做法**：提出 MemAdapter，含反事实归纳揭示记忆风险、上下文感知反思校准每条记忆的影响、证据驱动推理锚定回答。
- **效果**：三个基准上一致提升记忆可靠性，适应了正确记忆在不同语境下也可能误导的现实。
- **值得看**：指出即使客观正确的记忆也会致谄媚，突破了"过滤错误记忆即可"的旧假设。

---

## 四、其他深度学习

### 1. TRIAGE：方向感知地稳住原生 NVFP4 强化学习的精度错配

**TRIAGE: Direction-Aware Mismatch Stabilization of Native NVFP4 Reinforcement Learning**
InfiX.ai ｜ 🔥 HF 44 赞 ｜ 💻 [代码](https://github.com/InfiXAI/TRIAGE) ｜ [arXiv:2610.07043](https://arxiv.org/abs/2610.07043)

- **问题**：用 4bit 低精度跑大模型 RL 能提速，但学习器和采样器执行有偏差，会把策略优化带崩。
- **做法**：按策略梯度方向诊断分段，有选择地重平衡更新，对残留严重错配做有界修复，全程保持 W4A4 前向。
- **效果**：Qwen3-4B/30B 上训练全程稳定，五个数学推理基准达到全精度水平，推理吞吐比 BF16 高达 2.3 倍。
- **值得看**：给低精度 RL 训练提供了可落地的稳定化方案。

### 2. U-Space：揭示语言模型何时、为何产生不确定性

**U-Space: Uncovering When and Why Uncertainty Arises in Language Models**
Multimodal AI Lab - Technical University of Darmstadt ｜ 🔥 HF 43 赞 ｜ 💻 [代码](https://github.com/s2labres/U-Space) ｜ [arXiv:2610.09087](https://arxiv.org/abs/2610.09087)

- **问题**：模型会用流畅口吻说出错误答案，现有不确定性估计要么要反复生成、要么只给一个看不出来源的标量。
- **做法**：找出"怀疑/确信"的语义锚点构造低维子空间，用 U-Lens 把每个 token 状态投影成可解释的不确定性图。
- **效果**：无需标签、无需重复生成、无需训练，置信度在常规和控长度评测下均超基线，迁移性也更好。
- **值得看**：把不确定性变得可逐 token 查看，对模型可信度分析很实用。

### 3. TimeBraid：统一时间序列与语言，兼顾理解与预测

**TimeBraid: Unifying Time Series and Language for Understanding and Forecasting**
AetherLabs-AI ｜ 🔥 HF 29 赞 ｜ 💻 [代码](https://github.com/CharonWangg/TimeBraid) ｜ [arXiv:2609.29792](https://arxiv.org/abs/2609.29792)

- **问题**：语言模型会推理却不懂连续信号，时序基础模型会预测却缺乏指令跟随和推理能力。
- **做法**：用交错的全局残差注意力层把两类预训练模型对齐到共享表征空间，配统一提示方案与稳定联合训练。
- **效果**：靠 220 万序列-文本对和 490 万指令样本，在感知、理解、推理和预测基准上追平大得多的通用模型。
- **值得看**：给"时序+语言"统一建模梳理了一套可复现的设计配方。

### 4. 逆向蒸馏做数据遗忘

**Data Unlearning via Inverse Distillation**
🔥 HF 27 赞 ｜ [arXiv:2609.36099](https://arxiv.org/abs/2609.36099)

- **问题**：流模型和扩散模型推理慢，还可能复现训练集里不该出现的内容。
- **做法**：把蒸馏写成在混合分布上的极小极大目标，一边把多步教师蒸成单步学生，一边压制指定遗忘子集的输出。
- **效果**：只需预训练教师和遗忘集数据，无需保留样本，在 MNIST、CIFAR-10 上显著降低被遗忘类生成频率且保质。
- **值得看**：首个把遗忘和蒸馏统一在无条件流/分数模型里的框架。

### 5. 优化优化器：语言模型自主发现更快的分子弛豫

**Optimizing the Optimizer: Language Models Discover Faster Molecular Relaxation**
🔥 HF 24 赞 ｜ 💻 [代码](https://github.com/vdeshchenya/autosella) ｜ [arXiv:2610.06577](https://arxiv.org/abs/2610.06577)

- **问题**：量子化学几何优化每步都要算一次力，DFT 级别下这一步几乎吃掉全部时间。
- **做法**：让 agent 自主改写优化器以减少力调用，两道准入门槛拦住过早停止和无法泛化的改进。
- **效果**：从最快开源优化器 Sella 出发得到 AutoSella，在 r2SCAN-3c 级别只需 Sella 的 40.2%–77.2% 力调用即达同等能量下降。
- **值得看**：展示了 LLM 自研改进科学计算算法的真实收益。

### 6. 最小见证强化学习

**Minimal Witness Reinforcement Learning**
University of Pennsylvania ｜ 🔥 HF 23 赞 ｜ 💻 [代码](https://github.com/TSUITUENYUE/MWRL) ｜ [arXiv:2610.07226](https://arxiv.org/abs/2610.07226)

- **问题**："产生某结果的不可约充分条件有哪些"常需多个最小解，但标准 RL 往往只给一个或重复的解。
- **做法**：取策略采样成功提案的集合并集，按"去掉它会损失多少覆盖"给每个提案记功，从单个验证器比特统一最小性与多样性。
- **效果**：导出可恢复整族见证的值迭代规划器和可扩展到大模型的策略梯度法，多数设置下能找回绝大部分最小见证。
- **值得看**：把 RL 从单解优化拓展到可学习的解族，视角新颖。

### 7. 世界模型的自适应隐空间容量

**Adaptive Latent Capacity for World Models**
Arm ｜ 🔥 HF 23 赞 ｜ [arXiv:2609.32921](https://arxiv.org/abs/2609.32921)

- **问题**：固定宽度隐表征不会按预测重要性排布信息，规划时容量利用低效。
- **做法**：基于 JEPA 的 ALeWM 学一个序列条件的前缀长度分布，让预测器从采样前缀估计完整下一嵌入，并用 MixSIGReg 正则。
- **效果**：早期坐标块方差更高、承载更关键信息，在受控动力系统和目标导向视觉控制上平均成功率超调优的定宽基线且规划容量更低。
- **值得看**：给世界模型提供了按需分配隐空间容量的机制。

### 8. Prism：动态稀疏注意力支撑原生 2K 视频-音频联合生成训练

**Prism: Dynamic Sparse Attention for Native 2K Joint Video-Audio Generation Model Training**
Tencent Hunyuan ｜ 🔥 HF 21 赞 ｜ 💻 [代码](https://github.com/Tencent-Hunyuan/Prism) ｜ [arXiv:2610.05416](https://arxiv.org/abs/2610.05416)

- **问题**：高分辨率下全注意力代价二次增长，冗余 token 还会稀释信息内容的学习信号。
- **做法**：把序列组织成时空宏区，按视频特征方差和音视频交叉注意力强度给每个区动态分配块形状和每查询稀疏度。
- **效果**：相比全注意力取得 2.5 倍训练加速，同时生成质量反超全注意力。
- **值得看**：面向视频-音频联合数据的结构化稀疏训练方案，对高清生成训练有参考价值。

### 9. 通过校准的内容认证来认证真实图像

**Certification of Real Images through Calibrated Content Authentication**
Mohamed Bin Zayed University of Artificial Intelligence ｜ 🔥 HF 17 赞 ｜ 💻 [代码](https://github.com/Sarim-MBZUAI/content-authentication) ｜ [arXiv:2610.05870](https://arxiv.org/abs/2610.05870)

- **问题**：二十个 deepfake 检测器准确率逐年从 99.5% 掉到 76%，对抗扰动更能把它们打到 2% 以下。
- **做法**：换个范式——判断"真实性是否可被合理否认"：若某已知生成器能忠实重建该内容即成立，并用校准约束误判率。
- **效果**：可校准到至多 1% 生成内容被误认证，此操作点下多数基线召回近零；还显示后验可验证性正随新生成器减弱。
- **值得看**：把内容溯源问题重构为可校准的否认性判断，思路很不一样。

### 10. PaLoRA：面向持续学习的节奏化低秩适配

**PaLoRA: Paced Low-Rank Adaptation for Continual Learning**
🔥 HF 10 赞 ｜ 💻 [代码](https://github.com/liyuxuan-github/PaLoRA) ｜ [arXiv:2610.04226](https://arxiv.org/abs/2610.04226)

- **问题**：基于 LoRA 的持续学习多靠"小学习率"这一经验手段限制梯度，缺乏随任务累积该如何调整的理论依据。
- **做法**：在各向异性泄漏模型下推出节奏律 s*=R/c，用自适应 SVD 压缩历史知识、梯度投影到旧任务零空间并按秩自适应控步。
- **效果**：在长程设置下优势明显，50 任务 ImageNet-A/R 基准上取得约 4% 的准确率提升。
- **值得看**：把"小学习率"换成有理论支撑的秩感知节奏控制。

---

## 五、机器人与具身智能

### 1. Reflex：以视觉为基础的人形机器人反应式控制

**Reflex: Visually Grounded Reactive Humanoid Control**
University of Washington ｜ 🔥 HF 129 赞 ｜ 💻 [代码](https://github.com/ToberJ/reflex) ｜ [arXiv:2610.12772](https://arxiv.org/abs/2610.12772)

- **问题**：人形机器人难以靠第一视角视觉做全身实时反应，如接住抛来的箱子。
- **做法**：三阶段框架，先用强化学习练全身接取，再推断物体动态，最后让 RGB-D 编码器从视觉还原该动态。
- **效果**：仿真中纯视觉接取成功率 85.7%，逼近特权观测的 87.9%；真机 Unitree G1 在 2.5 米达 65%。
- **值得看**：示范了把感知、动态推断、全身控制解耦训练的可扩展思路。

### 2. Long-WAM：扩展世界-动作模型的上下文长度

**Long-WAM: Scaling the Context of World-Action Models**
NVIDIA ｜ 🔥 HF 109 赞 ｜ 💻 [代码](https://github.com/NVlabs/LongLive) ｜ [arXiv:2610.10528](https://arxiv.org/abs/2610.10528)

- **问题**：实时机器人控制需要足够视觉历史，但处理长历史会拖慢动作输出。
- **做法**：自回归预训练视频基座并保留历史到未来结构，配合流式编码与异步执行实现实时部署。
- **效果**：RoboCasa GR-1 上下文从 0 增至 19.2 秒，成功率 63.3%→78.7%；动态叠杯达 95%。
- **值得看**：点明「有历史不等于用好历史」，自回归预训练是关键前提。

### 3. SuperNav：适配任意任务与场景的智能体导航系统

**SuperNav: An Agentic Navigation System for Any Task in Any Scene**
zju3dv ｜ 🔥 HF 75 赞 ｜ 💻 [代码](https://github.com/zju3dv/SuperNav) ｜ [arXiv:2610.12126](https://arxiv.org/abs/2610.12126)

- **问题**：微调多模态大模型做导航，泛化受训练数据覆盖限制。
- **做法**：不微调大模型，给它配智能体工具框架，用统一的视觉-点接口在图像上直接指定目标并据反馈修正。
- **效果**：在实例级、多物体、需求驱动任务上均超过四个基线，并在 HM3D 与真实四足机器人上验证。
- **值得看**：展示了保留通用能力、把运动执行交给工具的分工范式。

### 4. UniWAM：统一的世界-动作模型

**UniWAM: Unified World-Action Model**
HKUSTGZ ｜ 🔥 HF 71 赞 ｜ 💻 [代码](https://github.com/UniWAM/UniWAM) ｜ [arXiv:2610.02054](https://arxiv.org/abs/2610.02054)

- **问题**：VLA 缺乏世界动态的扎根，世界-动作模型又弱于语义理解与推理。
- **做法**：整合物理推理器、世界生成器与动作预测器，用自然语言表示低级动作并分配互补监督联合训练。
- **效果**：在分布内、鲁棒性、泛化、长程任务等多项评测取得 SOTA，并揭示人机协同训练的对数线性缩放律。
- **值得看**：给出大规模人类第一视角与机器人数据混合训练的缩放证据。

### 5. 重新思考世界-动作模型：面向组合式与上下文机器人操作

**Rethinking World-Action Model for Compositional and In-Context Robotic Manipulation**
DAGroup-PKU ｜ 🔥 HF 56 赞 ｜ 💻 [代码](https://github.com/DAGroup-PKU/ViGAR) ｜ [arXiv:2610.02368](https://arxiv.org/abs/2610.02368)

- **问题**：现有世界-动作模型缺乏显式的子任务级推理，难应对长程组合任务。
- **做法**：ViGAR 分层拆成视觉子目标规划器与子目标执行器，共享预训练世界模型表征。
- **效果**：RoboTwin Clean2Random 上 Clean/Random 成功率达 82.00%/67.02%，平均超最强基线 12.86 个百分点。
- **值得看**：用全局目标图做上下文即可诱导不同子任务分解，无需更新参数。

### 6. Kinematic MeanFlow：机器人基础模型的一步动作生成策略

**Kinematic MeanFlow: One-Step Action Generation Policy for Robotic Foundation Models**
Intel Labs China ｜ 🔥 HF 49 赞 ｜ 💻 [代码](https://github.com/IntelChina-AI/K-MF) ｜ [arXiv:2610.00864](https://arxiv.org/abs/2610.00864)

- **问题**：多步流匹配推理延迟高，而 MeanFlow 直接套用会导致性能崩溃。
- **做法**：基于运动学恒等式把时间导数项拆成两段子区间，分别刻画去噪早期与晚期动态。
- **效果**：实现一步动作生成且多数设置超多步流匹配；GR00T-N1.6 动作头延迟降低 67.5%~74.4%。
- **值得看**：从速度场动态诊断崩溃根因，给出可直接落地的提速方案。

### 7. 把机器人上下文学习做简单：可复现的操作任务配方

**In-context Robot Learning Made Simple: A Democratized Recipe for Manipulation Tasks**
🔥 HF 47 赞 ｜ 💻 [代码](https://github.com/simpleicl/simple-icl) ｜ [arXiv:2609.38173](https://arxiv.org/abs/2609.38173)

- **问题**：机器人上下文学习问题本身定义模糊，视觉示范同时夹带轨迹、语义、空间等多重信息。
- **做法**：先给出明确的问题定义厘清学习目标，再用视觉提示编码器搭建极简可复现框架 SimpleICL。
- **效果**：无需海量预训练即在仿真与真实环境取得强表现，并揭示动作、语义、组合、可供性等判别性质。
- **值得看**：承诺全面开源数据与训练管线，便于系统性复现研究。

### 8. 驯服执行误差下的 VLA：自补偿与压力测试

**Taming VLAs under Robot Execution Errors: Self-Compensation and Stress Testing**
Pohang University of Science and Technology ｜ 🔥 HF 45 赞 ｜ [arXiv:2609.37334](https://arxiv.org/abs/2609.37334)

- **问题**：机械磨损、负载变化等执行误差会让 VLA 的指令动作与实际运动偏离而失败。
- **做法**：部署时用指令动作与实际运动的残差在线更新策略，实现无奖励无标注的预补偿；并建仿真基准 RoboStress 压测。
- **效果**：RoboStress 上平均成功率高于基线与训练期鲁棒化方法；两台真机机械臂各提升 30 多个百分点。
- **值得看**：提供了覆盖摩擦、回差、柔顺等七种场景的可控压测工具。

### 9. RobotWorld：跨任务与本体评测机器人使用的多模态智能体

**RobotWorld: Benchmarking Multimodal Agents for Robot Use Across Diverse Tasks and Embodiments**
🔥 HF 37 赞 ｜ 💻 [代码](https://github.com/robotworldai/robotworld) ｜ [arXiv:2610.10409](https://arxiv.org/abs/2610.10409)

- **问题**：通用智能体的数字能力能多大程度迁移到物理世界尚无系统评估。
- **做法**：构建含 84 个任务、横跨操作、移动操作、运动、驾驶与空中控制的仿真基准，带交互预算与可执行成功判定。
- **效果**：发现智能体能搭建感知控制工作流却难稳定组合成功，且不同模型在不同任务上各有短板。
- **值得看**：把结果与执行轨迹关联，为训练更可靠的物理世界智能体指出具体靶点。

### 10. 何时切换：VLA 模型可靠的动作块扩展

**When to Switch: Reliable Action-Chunk Extension for Vision-Language-Action Models**
Pohang University of Science and Technology ｜ 🔥 HF 35 赞 ｜ 💻 [代码](https://github.com/Seonghoon-Yu/RACE-VLA) ｜ [arXiv:2610.05719](https://arxiv.org/abs/2610.05719)

- **问题**：VLA 推理昂贵致走停式执行，而拉长动作块又会让远期预测不可靠。
- **做法**：发现误差集中在子技能切换处，RACE 用一步去噪辅助预测切换时机并据此生成动作。
- **效果**：同块长超微调，2 倍块长超近期高效 VLA；真机用 4 倍块长将走停空闲时间减少约 5 倍。
- **值得看**：把长块不可靠性归因到切换时机这一可操作变量。

---

## 六、智能眼镜 / 可穿戴 / 第一人称视觉

> 本周该方向多为第一人称视觉 / 可穿戴感知的研究，公开热度数据偏少，后半数论文没有实测热度，列出仅供参考。

### 1. 多智能体第一人称世界模型：细粒度具身交互

**Multi-Agent Egocentric World Model with Fine-Grained Embodied Interaction**
KAIST AI ｜ 🔥 HF 55 赞 ｜ 💻 [代码](https://github.com/cvlab-kaist/ME-World) ｜ [arXiv:2610.12299](https://arxiv.org/abs/2610.12299)

- **问题**：已有第一人称世界模型多只管单个智能体，缺少多人在共享环境里细粒度互动的建模。
- **做法**：ME-World 在同一 token 序列里联合去噪多条 ego 视频流，以各方位姿为条件，并用共享环境记忆做约束。
- **效果**：在真实与合成多智能体数据上，共享世界一致性、动作可控性、身份保持与画质均优于现有方法。
- **值得看**：为多人协作的 AR/VR 和具身仿真提供了可落地的共享世界生成范式。

### 2. 立体听世界：动态空间对应驱动的沉浸式音视频联合生成

**Here the World in Stereo: Learning Dynamic Spatial Correspondence for Immersive Joint Video-Audio Generation**
🔥 HF 52 赞 ｜ 💻 [代码](https://github.com/vivoCameraResearch/StereoBind) ｜ [arXiv:2609.38748](https://arxiv.org/abs/2609.38748)

- **问题**：现有音视频联合生成忽视立体声，声音位置难以随画面中声源的运动同步变化。
- **做法**：StereoBind 用运动轨迹绑定视觉声源与立体声，含视觉运动绑定、空间轨迹编码与残差轨迹 RoPE 三机制。
- **效果**：配套构建 StereoWorld-29K 数据集与评测基准，立体声空间对齐显著提升且整体音视频质量不降。
- **值得看**：补上了 AR/VR 与交互游戏里空间音频这块长期被忽略的拼图。

### 3. RLHND：把视频基础模型变成物理可靠的手部追踪器

**RLHND: Video Foundation Models as Physically Grounded Hand Trackers for Robot Learning**
RLWRLD ｜ 🔥 HF 45 赞 ｜ 💻 [代码](https://github.com/seungjun-moon/rlhnd) ｜ [arXiv:2610.09455](https://arxiv.org/abs/2610.09455)

- **问题**：现有手部追踪器从裁剪帧回归姿态，缺乏运动与接触先验，估计不准也不符合物理。
- **做法**：把预训练 Cosmos 3 视频扩散骨干改造成特征提取器，联合预测解剖合理的手姿与手面接触力。
- **效果**：姿态、接触与力的估计均达 SOTA，并通过重定向与真机实验验证了对机器人学习的价值。
- **值得看**：第一人称视频里"看懂手还要知道用了多大劲"，为从人类视频学机器人策略开了新路。

### 4. LEGO：无需抬升的外视角到第一人称视频生成

**LEGO: A Lifting-Free Approach for Exocentric-to-Egocentric Video Generation**
25frms ｜ 🔥 HF 25 赞 ｜ 💻 [代码](https://github.com/suhwan-cho/LEGO) ｜ [arXiv:2610.12442](https://arxiv.org/abs/2610.12442)

- **问题**：从单段外视角视频生成第一人称视角，两相机几乎无重叠，传统深度抬升会把深度误差变成错位内容。
- **做法**：放弃深度与点云重投影，用 LVSM 风格 transformer 直接渲染 ego 视图，并输出逐区域置信度引导扩散生成。
- **效果**：一致超越显式重建的 SOTA 流水线，且无需重训即可泛化到其他数据集。
- **值得看**：为扩散生成器"该喂什么条件"给出了优先结构对齐的新答案。

### 5. EgoVoice：从第一人称多模态流出发的主动语音助手

**EgoVoice: Proactive Spoken Assistance from Egocentric Multimodal Streams**
热度未测得 ｜ [arXiv:2610.12248](https://arxiv.org/abs/2610.12248)

- **问题**：可穿戴 AR 助手要靠第一人称音视频判断"何时该开口、说什么"，现有系统没有联合解决这个问题。
- **做法**：基于 HoloAssist 录像构建干净音频流并改造成逐时刻"沉默或提示"的决策格式，微调全模态 LLM 并用 DPO 优化介入行为。
- **效果**：在时机、内容相关性与人类偏好上均明显优于零样本基线，而已有系统很少给出恰当的主动提示。
- **值得看**：主动式而非被动应答的交互设计，是智能眼镜助手走向日常陪伴的关键一步。

### 6. emg2face：用高密度表面肌电驱动的表情动画

**emg2face: Expressive Facial Animation with High-Density Surface EMG**
热度未测得 ｜ [arXiv:2610.09304](https://arxiv.org/abs/2610.09304)

- **问题**：头显遮挡面部时光学捕捉失效，且相机方案有隐私顾虑和笨重设备。
- **做法**：用两片织物电极采集 64 通道 HD-sEMG，配合亚毫秒级音频同步与分阶段头模型拟合，训练时空网络从肌电预测表情混合形状。
- **效果**：在 25 名被试上验证，可仅凭肌电信号实时预测表情，并迁移到各种真人与非人角色。
- **值得看**：为 VR 头显下的面部重建提供了一条绕开摄像头的非光学路线。

### 7. PalmSpace：面向智能眼镜的手掌统一触控交互空间

**PalmSpace: Towards a Versatile On-Palm Interaction Space through Unified Touch Modeling**
热度未测得 ｜ [arXiv:2610.10370](https://arxiv.org/abs/2610.10370)

- **问题**：智能眼镜与轻量 MR 输入仍是难题，裸手掌虽随时可用却无坐标系也无触觉传感。
- **做法**：PalmSpace 用腕戴红外系统，无需逐人标定即可联合表示接触、交互模式与掌面绝对位置。
- **效果**：17 人留一交叉验证下定位误差 6.7 mm、接触检测 98.9%、四类状态识别 F1 96.7%，支持指向、拖拽与捏合等操作。
- **值得看**：把手掌变成可迁移的输入面，给眼镜时代的"隐形键盘"一个实用方案。

### 8. 超越唤醒词：带可见状态的凝视唤起 AR 助手

**Beyond Activation: Gaze Invocation with Visible Status for an Embodied AR Assistant in Co-Located Collaboration**
热度未测得 ｜ [arXiv:2610.09284](https://arxiv.org/abs/2610.09284)

- **问题**：唤醒词在灵敏度与误触间两难，共处 AR 还要分辨用户是在对助手还是旁人说话。
- **做法**：让用户注视场景中锚定的具身助手、在其身上显示激活进度与聆听状态，用凝视管理激活、延续与释放三个阶段。
- **效果**：25 人实验记录 500 次交互，98.8% 的发话在开口前完成凝视获取，但暴露了用户回到任务后看不到助手已停止聆听的新问题。
- **值得看**：凝视加可见状态的交互设计，给"助手到底在不在听"这个老问题提了实证教训。

### 9. 永不回头：从第一人称视频理解 3D 物体记忆的持久性

**Never Look Back: Understanding Persistence in 3D Object Memory from Egocentric Videos**
热度未测得 ｜ 💻 [代码](https://github.com/LEDGER-3D/LEDGER) ｜ [arXiv:2610.10538](https://arxiv.org/abs/2610.10538)

- **问题**：具身助手要像人一样从日常第一人称视频里记住物体放哪了、容器里装了什么，哪怕当时没察觉以后会用到。
- **做法**：Ledger 构建持久 3D 物体记忆，聚合位置、历史与上下文描述，按静止位置聚类并多次证据后才记一次移动以抗噪。
- **效果**：HD-EPIC 准确率从 29.7% 升至 42.6%，UCS-Bench 从 33.8% 升至 38.5%，Ego4D 物体定位中位误差 0.99 m。
- **值得看**：跨场景拼接实验还揭示了检索与构建的失败模式，对长时程记忆系统很有参考。

### 10. 无参照物的第一人称立体视频食物体积估计

**Reference-Free Food Volume Estimation from Egocentric Stereo Video**
热度未测得 ｜ [arXiv:2610.12735](https://arxiv.org/abs/2610.12735)

- **问题**：立体视觉估算食物份量通常得多拍几张或放参照物校准，用户负担大，难以被动监测饮食。
- **做法**：用可穿戴设备的立体视频，结合 FoundationStereo 零样本匹配、SAM 2 分割与 TSDF 融合，并借出厂标定基线与 VIO 位姿自动重建真实尺度。
- **效果**：在五种食物上实现真实尺度 3D 网格重建，体积估计平均绝对百分比误差 9.1%。
- **值得看**：无需参照物的可穿戴方案，为被动式膳食摄入监测提供了一个轻量起点。
