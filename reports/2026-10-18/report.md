# AI 论文周报（2026-10-12 – 2026-10-18）

本周最显眼的现象是"决策模型"(System One / Jev 系列) 突然集中爆发——Jeva、VideoJev、MJev-Spatial、StartLux-Decision、DecisionRobust 等多篇论文几乎同时在做同一件事：把本该由大模型自回归生成的选择题，改造成一次前向打分，用来换取数量级的推理加速。与之呼应的是"在线策略蒸馏"(on-policy distillation) 这条线也在快速分化出新变体——Waypoint-OPD、CriticOPD、ActionOPD、VRSD 分别从早晚策略一致性、教师可恢复性、动作级对齐、熵保持四个角度修补同一个基础配方。Agent 方向的重心则从"能不能完成任务"转向"脚手架本身该不该自我演化"，Self-Evolving Agent Harness、Harness²、WorkRover 都在给智能体的执行框架装上反馈闭环；FDE-Gym、AgentSWE 两篇基准论文则不约而同地给这股热情浇了冷水——即便功能通过率很高，真正可靠交付的比例仍然很低。机器人方向，VLA 与世界动作模型(WAM)的融合继续加深，GreenWAM、LeWAM、WAVE-0 都在探索"一个模型同时做预测与控制"。相比之下，智能眼镜/可穿戴方向本周明显安静，没有出现热度和技术突破都突出的工作。

---

## ⭐ 本周最值得读的 5 篇

1. **Waypoint-OPD：用早晚策略偏移一致性引导的在线策略蒸馏**（其他深度学习）— 本周 HF 热度最高的论文，只加一次额外打分就能让蒸馏效果更稳健｜[arXiv:2610.21601](https://arxiv.org/abs/2610.21601)
2. **OmniCompass：全模态视频定位与理解基准**（多模态 / 视觉语言）— 578 个 HF 赞，揭示开源模型在音视频联合理解上全面落后闭源模型｜[arXiv:2610.18829](https://arxiv.org/abs/2610.18829)
3. **Jeva：从第一性原理出发的系统一决策模型**（其他深度学习）— 本周"决策模型"浪潮的代表作之一，用结构化架构同时搞定空值检测、顺序不变与可缓存｜[arXiv:2610.18773](https://arxiv.org/abs/2610.18773)
4. **Player-1：从合成经验中学习玩游戏**（Agent）— 用合成环境把电脑操作智能体的游戏控制成功率从12.63%拉到38.33%｜[arXiv:2610.20584](https://arxiv.org/abs/2610.20584)
5. **GroundingPI：面向物理智能的视觉定位基础模型**（机器人与具身智能）— 4B 定位模型超越更大的 GPT-6 Astra，同时提升机器人操作与自动驾驶下游表现｜[arXiv:2609.39601](https://arxiv.org/abs/2609.39601)

---

## 一、大语言模型

### 1. 思维惯性：被要求"别思考"时，大模型依然在思考

**Thinking Inertia: LLMs Keep Thinking When Told Not To**
Stanford University ｜ 🔥 HF 250 赞 ｜ 💻 [代码](https://github.com/thinking-inertia/code) ｜ [arXiv:2610.11765](https://arxiv.org/abs/2610.11765)

- **问题**：模型即便开启"无思考模式"或被明确要求不推理，仍常暗中进行显式推理，现有衡量方式并不可靠。
- **做法**：将回复拆为预答案轨迹与最终答案，设计三级指标，在六模型、三类任务上评测六种提示干预。
- **效果**：显式控制无法可靠消除推理痕迹，开放式任务中"答案合规"与准确率存在权衡。
- **值得看**：揭示"不思考"本身是需要系统评估的能力，而非简单开关。

### 2. Vela：用用户行为数据作监督信号激发大模型智能

**Vela: User Behavior as Supervision Sparks LLM Intelligence**
AllSpark Research ｜ 🔥 HF 87 赞 ｜ 💻 [代码](https://github.com/AllSpark-Research/Vela) ｜ [arXiv:2610.14709](https://arxiv.org/abs/2610.14709)

- **问题**：现有训练依赖静态文本或合成数据，难以捕捉真实用户行为随时间演化的规律。
- **做法**：Vela将10万用户匿名行为转化为91种任务模板、约7.5万条训练轨迹用于微调与强化学习。
- **效果**：Qwen3.6-35B-A3B微调后用户相关任务提升最多11.5分，通用基准平均提升4分。
- **值得看**：证明大规模真实用户行为是可扩展的新监督来源，能带动模型整体智能。

### 3. Cortex：把上下文记忆固化进模型参数

**Cortex: Consolidating Context into Parametric Memory**
ByteDance Seed ｜ 🔥 HF 67 赞 ｜ [arXiv:2610.20399](https://arxiv.org/abs/2610.20399)

- **问题**：上下文带来的性能增益一旦移除上下文就会消失，如何将其固化进参数仍是难题。
- **做法**：受记忆巩固启发，生成前瞻查询并将上下文条件输出蒸馏为可合并的低秩/结构化更新。
- **效果**：14B模型连续50次编辑后，Cortex-Structural恢复88.9%增益，同时保留99.8%原有能力。
- **值得看**：统一了上下文编辑、技能学习与行为引导，覆盖4B到120B多种模型。

### 4. UltraBERT：把BERT预训练推向极限

**UltraBERT: Beyond the Limit of BERT Pre-Training**
🔥 HF 72 赞 ｜ [arXiv:2610.15028](https://arxiv.org/abs/2610.15028)

- **问题**：双向编码器预训练沿用小模型旧经验，没有模型能同时在分类和检索上都表现优异。
- **做法**：重新审视掩码率、蒸馏等核心设计，按掩码率分设LM头并限定蒸馏目标。
- **效果**：UltraBERT在GLUE达91.0、BEIR达47.7，首次让单一编码器两类任务都达最优。
- **值得看**：为编码器类模型的计算分配与掩码率设计提供了实证新准则。

### 5. 一题多解：为LLM推荐器的GRPO训练去除"回复者噪声"

**Many Right Answers, One Training Example: Removing Responder Noise from GRPO for LLM Recommenders**
Nanyang Technological University ｜ 🔥 HF 70 赞 ｜ 💻 [代码](https://github.com/LiXin97/ReMaRk) ｜ [arXiv:2610.17771](https://arxiv.org/abs/2610.17771)

- **问题**：同一推荐请求常有多条有效回复，Rank-GRPO只挑一条做奖励对象，优势估计被"选中哪条"主导。
- **做法**：提出ReMaRk，将生成列表与所有回复标题并集一次性打分，并对每个请求均匀采样。
- **效果**：七个骨干模型、三数据集上，用25%-53%步数即达2000步按条训练的召回水平，更省算力。
- **值得看**：给出强化学习面对多个有效人类答案时的简单规则——联合奖励所有正确答案。

### 6. LatentLoop：用非对称算力分配扩展循环MoE模型

**LatentLoop: Scaling Looped MoE Models with Asymmetric Compute Allocation**
🔥 HF 67 赞 ｜ 💻 [代码](https://github.com/lcqysl/LatentLoop) ｜ [arXiv:2610.19975](https://arxiv.org/abs/2610.19975)

- **问题**：循环MoE中多次循环共享参数但角色不同，各次循环的算力分配方式尚不明确。
- **做法**：发现首次循环贡献更小，遂压缩其序列长度、保留第二次全分辨率，节省算力用于增大隐藏维度。
- **效果**：15组1.3B-7B配置实验中验证NLL持续下降，较普通MoE与循环基线分别省19.0%、7.9%算力。
- **值得看**：为循环MoE模型扩展提供了计算效率更高的新方向。

### 7. 带言语正则化的自蒸馏方法

**Self-Distillation with Verbal Regularization**
King's College London ｜ 🔥 HF 38 赞 ｜ 💻 [代码](https://github.com/lijiazheng99/VRSD) ｜ [arXiv:2610.16354](https://arxiv.org/abs/2610.16354)

- **问题**：同模型自蒸馏中，教师因看到"特权信息"走捷径推理，导致输出分布过早收敛、熵骤降。
- **做法**：提出VRSD，用系统提示约束教师对特权信息的依赖，促使其保持探索，并推导熵不塌陷的条件。
- **效果**：三模型四任务的12种组合中，11种设置下Pass@1相比普通自蒸馏平均提升3.9个百分点。
- **值得看**：几乎零成本即可缓解自蒸馏"抄捷径"问题的实用技巧。

### 8. DeltaTTG：用"剩余步数进度表"训练多轮智能体

**DeltaTTG: Training Multi-Turn Agents with a Token-to-Go Progress Meter**
Nanyang Technological University ｜ 🔥 HF 34 赞 ｜ 💻 [代码](https://github.com/Xuyan923r/DeltaTTG) ｜ [arXiv:2610.17666](https://arxiv.org/abs/2610.17666)

- **问题**：多轮智能体RL只有稀疏终局奖励，难以反映每一步的质量。
- **做法**：学习可复用"进度表"，以剩余生成token数为监督信号，依其估计变化重新分配各步优势而不改总奖励。
- **效果**：ALFWorld、PaperSearchQA、BFCLv3上较GRPO平均提升5.7、7.2分，训练成本相当。
- **值得看**：提供低成本、任务无关的步骤级奖励重分配思路，提升样本效率与跨域泛化。

### 9. 面向可验证奖励强化学习的大模型谱驱动自适应秩优化器

**Spectral-Driven Adaptive-Rank Optimizer for Large Language Model Reinforcement Learning with Verifiable Rewards**
RUC-AIBOX ｜ 🔥 HF 10 赞 ｜ 💻 [代码](https://github.com/RUCAIBox/Ares) ｜ [arXiv:2610.16533](https://arxiv.org/abs/2610.16533)

- **问题**：RLVR训练仍沿用监督训练时代的优化器，但其梯度几何可能截然不同。
- **做法**：发现RLVR梯度能量会随训练收缩进一个越来越小的子空间，据此提出Ares动态估计并限定更新秩。
- **效果**：不同规模大模型上，Ares相比常用优化器提升准确率，在多种RLVR算法和任务上均有效。
- **值得看**：提出"优化器应匹配训练动态几何"的新思路，为RLVR提供针对性方案。

### 10. LLM到流模型蒸馏：用自然语言目标教会科学生成模型

**LLM-to-Flow Distillation: Teaching Natural Language Goals to Scientific Generators**
ETH Zurich ｜ 🔥 HF 11 赞 ｜ 💻 [代码](https://github.com/FedericoDiGennaro/LLM-to-Flow-Distillation) ｜ [arXiv:2610.17246](https://arxiv.org/abs/2610.17246)

- **问题**：大模型懂科学知识却不会生成分子/序列，专用生成器擅长生成却难对接自然语言目标，且常无现成奖励函数。
- **做法**：提出LFD，用冻结大模型作教师，依生成器现有能力构造渐进子目标课程，判断采样结果并通过DPO蒸馏偏好。
- **效果**：治疗性多肽与小分子设计实验显示，即便初始概率近零也能有效引导生成逼近目标区域。
- **值得看**：无需显式奖励模型即可用自然语言对齐任意领域专用生成器的新范式。

---

## 二、多模态 / 视觉语言

### 1. OmniCompass：面向全模态视频定位与理解的综合基准

**OmniCompass: A Holistic Benchmark for Omni-Modal Video Grounding and Understanding**
VCLab ｜ 🔥 HF 578 赞 ｜ 💻 [代码](https://github.com/PolyU-VCLab/OmniCompass) ｜ [arXiv:2610.18829](https://arxiv.org/abs/2610.18829)

- **问题**：现有视频理解基准评测维度不全，难以系统诊断多模态大模型的全模态视频理解能力。
- **做法**：构建涵盖视觉语言和音视频两条赛道、时间/空间定位与问答三类任务的综合基准，共820个视频2460条实例。
- **效果**：评测50个模型发现开源模型明显落后闭源模型，精确时空定位仍是普遍难题。
- **值得看**：首个真正意义上的全模态视频定位综合评测体系。

### 2. VideoJev：面向视频理解与交互的系统一模型

**VideoJev: System One Model for Video Understanding and Interaction**
Multimedia Computing Group-Nanjing University ｜ 🔥 HF 369 赞 ｜ 💻 [代码](https://github.com/MCG-NJU/VideoJev) ｜ [arXiv:2610.18615](https://arxiv.org/abs/2610.18615)

- **问题**：视觉智能体需要对视频流做出及时决策，但自回归生成答案效率太低。
- **做法**：用打分头替代自回归解码，统一时间定位与多选问答，并复用视觉计算做缓存与联合推理。
- **效果**：时间定位mIoU提升6.7-10.8点，推理速度提升2.8-3.1倍，问答场景提速超100倍。
- **值得看**：为复杂视觉决策工作流提供了统一高效的接口范式。

### 3. MJev-Spatial：基于原生注意力匹配的系统一空间智能

**MJev-Spatial: System One Spatial Intelligence via Native Attention Matching**
Mind Lab ｜ 🔥 HF 355 赞 ｜ 💻 [代码](https://github.com/Fr0zenCrane/MJev-Spatial) ｜ [arXiv:2610.22276](https://arxiv.org/abs/2610.22276)

- **问题**：VLM处理空间任务时用自由文本生成，输出空间本就紧凑却要付出自回归解码成本。
- **做法**：将选项、数值、坐标点都当作分类候选，复用预训练投影矩阵打分，一次前向完成决策。
- **效果**：基于Qwen3.5-4B训练，12个基准总分65.64%排名第一，比基线快2.5-5.6倍。
- **值得看**：无需新增参数即可把空间推理变成极速分类问题，思路干净。

### 4. S-Space：探索多模态语言模型的空间工作区

**S-Space: Exploring Spatial Workspace in Multimodal Language Models**
MirroS ｜ 🔥 HF 298 赞 ｜ 💻 [代码](https://github.com/mirros-lab/s-space) ｜ [arXiv:2610.13527](https://arxiv.org/abs/2610.13527)

- **问题**：多模态模型的空间推理内部机制长期不透明。
- **做法**：发现并验证S-Space——一个用坐标轴编码物体位置的线性子空间，并用因果干预验证其作用。
- **效果**：证实感知写入、推理变换、语言选择性读取该空间，暴露出视角变换推理的瓶颈。
- **值得看**：为诊断空间推理失败提供了可解释的内部工具。

### 5. AesCode：基于解耦跨模态奖励的美学代码生成

**AesCode: Aesthetic Code Generation with Decoupled Cross-Modal Rewards**
Microsoft ｜ 🔥 HF 137 赞 ｜ 💻 [代码](https://github.com/microsoft/AesCode) ｜ [arXiv:2610.18860](https://arxiv.org/abs/2610.18860)

- **问题**：代码模型生成幻灯片、海报等视觉产物时看不到渲染效果，布局配色质量受限。
- **做法**：用同prompt生成的图像作美学参照，构建设计图并拆解出可验证与VLM评判的解耦奖励做强化学习。
- **效果**：AesCode-8B/32B相比同规模Qwen3-VL基线美学得分提升22.4-31.1个百分点，接近GPT-5.5水平。
- **值得看**：把"看得见"的美学反馈引入代码生成训练，思路新颖。

### 6. Intern Lumina U2：面向全视觉理解与图像生成的多码本扩散大模型

**Intern Lumina U2: A Multi-Codebook Diffusion Large Language Model for Omni-Visual Understanding and Image Generation**
Shanghai AI Laboratory ｜ 🔥 HF 43 赞 ｜ 💻 [代码](https://github.com/InternLM/InternLumina-U2) ｜ [arXiv:2610.20818](https://arxiv.org/abs/2610.20818)

- **问题**：统一多模态生成中文本与图像建模空间不一致，存在优化冲突。
- **做法**：首创全离散空间下的多码本视觉token表示，扩散骨干并行处理、轻量自回归头预测码本。
- **效果**：在理解、生成、编辑任务上领先同类统一模型，推理加速4.45倍。
- **值得看**：兼顾高容量视觉表示与文本离散建模兼容性的新架构方向。

### 7. Multics：带分层通信的多人生成式世界模型

**Multics: Generative Multi-Player World Model with Hierarchical Communication**
ARC Lab, Tencent ｜ 🔥 HF 74 赞 ｜ 💻 [代码](https://github.com/TencentARC/Multics) ｜ [arXiv:2610.17201](https://arxiv.org/abs/2610.17201)

- **问题**：多人交互世界模型扩展玩家数量时，全连接通信成本随人数平方增长，集中式方案又存在事件干扰。
- **做法**：引入玩家-小组-全局三层通信结构，共享组token参数并基于相机轨迹动态分组。
- **效果**：在4/6人场景达到最优效果，并可零训练泛化到6-10人推理，同时降低注意力计算量。
- **值得看**：为多人交互视频生成的可扩展通信结构提供了优雅方案。

### 8. LensErase：通用万物擦除基础模型

**LensErase: A Foundation Model for Erase Anything**
Microsoft ｜ 🔥 HF 43 赞 ｜ 💻 [代码](https://github.com/LensFamily/LensErase) ｜ [arXiv:2610.18072](https://arxiv.org/abs/2610.18072)

- **问题**：现有图像擦除方法难以覆盖物体、文字、水印等多样场景和尺度。
- **做法**：构建1.01亿对数据，从Lens文生图模型出发，设计Mask-Aware RoPE注入掩码信息，并用RL微调。
- **效果**：在六个公开基准及自建LensErase-Bench上取得显著提升。
- **值得看**：作为擦除任务的通用基础模型，覆盖面和工程完整度都很扎实。

### 9. WorldCast：探索世界状态预测中的智能视觉生成

**WorldCast: Exploring Intelligent Visual Generation in World State Prediction**
LongCat ｜ 🔥 HF 29 赞 ｜ 💻 [代码](https://github.com/teal024/WorldCast) ｜ [arXiv:2610.20731](https://arxiv.org/abs/2610.20731)

- **问题**：多模态生成模型预测世界状态演变的能力尚缺乏系统评测。
- **做法**：提出四级能力层级框架，构建320例、八类别的WorldCast基准评测12个代表模型。
- **效果**：GPT-Image-2.5系统得分72.8，Nano Banana Pro仅42.8，最好开源模型只有20.1，差距明显。
- **值得看**：揭示了前沿模型与开源模型在复杂世界状态推理上的巨大鸿沟。

### 10. InfoVis：统一的幻灯片图像生成与编辑

**InfoVis: Unified Slide Image Generation and Editing**
Beijing Academy of Artificial Intelligence ｜ 🔥 HF 28 赞 ｜ 💻 [代码](https://github.com/VectorSpaceLab/InfoVis) ｜ [arXiv:2610.16784](https://arxiv.org/abs/2610.16784)

- **问题**：幻灯片生成编辑需要文字渲染、指令遵循、视觉定位、美学设计多能力兼备，现有工作覆盖不全。
- **做法**：构建1300万+预训练与190万微调数据及VisSlideBench基准，训练9B统一生成编辑模型InfoVis。
- **效果**：在VisSlideBench上全面领先开源模型，综合得分7.94，接近Nano-Banana-2的7.99。
- **值得看**：首个面向幻灯片场景的大规模统一生成编辑模型及配套基准。

---

## 三、Agent

### 1. Player-1：从合成经验中学习玩游戏

**Player-1: Learning to Play from Synthetic Experience**
ARC Lab, Tencent ｜ 🔥 HF 334 赞 ｜ 💻 [代码](https://github.com/TencentARC/Player-1) ｜ [arXiv:2610.20584](https://arxiv.org/abs/2610.20584)

- **问题**：电脑操作智能体在玩视觉丰富、机制多样的游戏时仍远逊于通用控制水平。
- **做法**：扩展操作动作空间，先用6044条游玩轨迹做监督微调，再在16个合成环境上用PPO强化学习。
- **效果**：Player-1-9B在MineDojo-300成功率达38.33%，远超最强基线的12.63%。
- **值得看**：证明合成环境经验能大幅提升游戏控制能力，且可泛化到训练集之外。

### 2. OpenGCUA：通用电脑操作智能体的全开源技术栈

**OpenGCUA: Toward a Fully Open Stack for Generalist Computer Use**
Tongyi-MAI ｜ 🔥 HF 318 赞 ｜ 💻 [代码](https://github.com/Tongyi-MAI/OpenGCUA) ｜ [arXiv:2610.22200](https://arxiv.org/abs/2610.22200)

- **问题**：前沿通用电脑操作智能体（如GPT-6 Astra）高度闭源，难以系统研究其设计。
- **做法**：开源代码执行驱动的智能体框架，并提出将部分观测与状态决策从固定脚手架转移给模型本身。
- **效果**：在OSWorld-v2上八个模型平均得分提升19.6分，步数减少53.0%。
- **值得看**：附带真机测试台与跨设备SDK，是少见的全链路开源方案。

### 3. FDE-Gym：AI交付的最后一公里

**FDE-Gym: The Last Mile of AI Delivery**
DeepLethe ｜ 🔥 HF 284 赞 ｜ 💻 [代码](https://github.com/deeplethe/fde-gym) ｜ [arXiv:2610.22350](https://arxiv.org/abs/2610.22350)

- **问题**：现有基准多测试需求明确的任务，而真实客户交付需要澄清模糊需求、发现隐藏约束。
- **做法**：构建95个跨18个行业的真实交付任务，模拟客户环境与利益相关者互动并打分。
- **效果**：最佳模型配置平均得分仅0.56，95个任务里只解决14个。
- **值得看**：揭示了"解决明确任务"与"真正交付价值"之间的巨大差距。

### 4. AgentSWE：编码智能体能造出你真正想要的智能体吗

**AgentSWE: Can Coding Agents Build the Agent You Actually Want?**
🔥 HF 234 赞 ｜ 💻 [代码](https://github.com/VectorSpaceLab/AgentSWE) ｜ [arXiv:2610.13361](https://arxiv.org/abs/2610.13361)

- **问题**：编码智能体被委托构建其他智能体时，交付物是否真正满足需求尚无基准检验。
- **做法**：设计覆盖创建、编辑、优化三阶段的25项"委托式"任务，用需求导出的评分标准严格验收。
- **效果**：所有被测编码智能体均未能可靠达成需求，过拟合可见案例、空壳实现等问题普遍存在。
- **值得看**：暴露了"看起来完成"与"真正完成"之间常态化的鸿沟。

### 5. Agent-Reflex：教语言智能体学会反思式行动

**Agent-Reflex: Teaching Language Agents to Act Reflectively**
NLPIR Lab @ RUC ｜ 🔥 HF 213 赞 ｜ 💻 [代码](https://github.com/RUC-NLPIR/Agent-Reflex) ｜ [arXiv:2610.17953](https://arxiv.org/abs/2610.17953)

- **问题**：现实部署中工具反馈嘈杂、用户会中途纠正，但现有方法缺乏对反思与故障恢复的有效监督。
- **做法**：三阶段框架：挖掘成败对总结反思技能、转化为监督微调数据，再用在线策略优化强化反思行为。
- **效果**：基于Qwen3-8B，五个长程工具使用基准综合得分58.6，超过多个强基线。
- **值得看**：系统性解决智能体在噪声交互下的鲁棒性问题，训练动态也更稳定。

### 6. 自演化智能体脚手架

**Self-Evolving Agent Harness**
ZGCAGI ｜ 🔥 HF 203 赞 ｜ 💻 [代码](https://github.com/zgcagi/Harness-RSI) ｜ [arXiv:2610.18813](https://arxiv.org/abs/2610.18813)

- **问题**：在固定模型权重下，如何让提示词、记忆、工作流等"脚手架"持续自我改进缺乏理论保障。
- **做法**：提出反馈驱动的持续改进框架，用连续PAC学习理论给出泛化界、保留界与高置信度准入规则。
- **效果**：给出可证明的脚手架修订准入机制，并配套66页详尽的理论与算法讨论。
- **值得看**：从理论角度为智能体自我改进的可靠性与安全边界提供了严谨分析。

### 7. MAI-Gym：移动与电脑环境下GUI智能体评测与强化学习训练平台

**MAI-Gym: An Open All-in-One Platform for GUI Agent Evaluation and RL Training across Mobile and Computer Environments**
Tongyi-MAI ｜ 🔥 HF 156 赞 ｜ 💻 [代码](https://github.com/Tongyi-MAI/MAI-Gym) ｜ [arXiv:2610.20939](https://arxiv.org/abs/2610.20939)

- **问题**：GUI智能体的强化学习受限于交互环境成本高、真实训练任务稀缺。
- **做法**：统一评测、数据采集与在线RL训练的平台，支持2万并行环境实例及可重置模拟App。
- **效果**：9B模型在MobileWorld达78.4%、OSWorld-Verified达76.2%，真机订票任务成功率从28.8%提升到48.1%。
- **值得看**：证明了模拟环境中训练的能力可迁移到真实物理设备。

### 8. WorkRover：通过递归环境演化扩展长程协作智能体训练

**WorkRover: Scaling Long-Horizon Cowork Agent Training Via Recursive Environment Evolution**
Nex AGI ｜ 🔥 HF 85 赞 ｜ 💻 [代码](https://github.com/workrover/WorkRover) ｜ [arXiv:2610.18067](https://arxiv.org/abs/2610.18067)

- **问题**：长程协作智能体训练环境需反复迭代修正，现有构建流程难以保持任务与校验器同步一致。
- **做法**：提出递归环境演化框架，结合最小修复回放机制与基于工作进度校验的细粒度信用分配。
- **效果**：Qwen3.5-35B-A3B经训练后在JobBench提升26.27分，OfficeQA Pro提升29.32分，GDPval v2提升413 Elo。
- **值得看**：为可扩展训练长程办公协作智能体提供了一套完整方法论。

### 9. 最后安全代码基准：你"随手写"的代码安全吗

**Last Secure Code Benchmark: Is the Code You Vibe Secure?**
Qwen ｜ 🔥 HF 74 赞 ｜ 💻 [代码](https://github.com/alibaba/last-secure-code-benchmark) ｜ [arXiv:2610.14766](https://arxiv.org/abs/2610.14766)

- **问题**：AI编码智能体写的代码功能上大多可用，但安全性长期缺乏系统评估。
- **做法**：基于150个真实漏洞构建450个任务，覆盖七种语言和24类CWE，仅以功能需求提示、隐藏安全测试打分。
- **效果**：功能通过率高达73.6%-91.3%，但最强模型（Claude Fable 5）同时安全达标的比例仅25.1%。
- **值得看**：直观揭示了"vibe coding"流行背后被忽视的安全风险。

### 10. DeltaStreamer：面向类人化的智能体流式视频理解

**DeltaStreamer: Towards Human-Like Agentic Streaming Video Understanding**
ByteDance ｜ 🔥 HF 36 赞 ｜ 💻 [代码](https://github.com/BBBBchan/DeltaStreamer) ｜ [arXiv:2610.19849](https://arxiv.org/abs/2610.19849)

- **问题**：流式视频理解需要在不知道未来查询需求前保留证据，现有方法压缩历史时常丢失细节且无法补救。
- **做法**：结合变化感知记忆与查询驱动的规划，按需回放历史帧找回被忽略的视觉细节。
- **效果**：在OVO-Bench和StreamingBench上综合得分分别达66.07%和59.53%，优于现有流式理解方法。
- **值得看**：模拟人类"先观察记忆、后针对性调查"的认知方式，思路新颖。

---

## 四、其他深度学习

### 1. Waypoint-OPD：用早晚策略偏移的一致性引导在线策略蒸馏

**Waypoint-OPD: Transferring RL-Induced Policy Shifts via Gated On-Policy Distillation**
🔥 HF 669 赞 ｜ 💻 [代码](https://github.com/hhhbxloveai/WaypointOPD) ｜ [arXiv:2610.21601](https://arxiv.org/abs/2610.21601)

- **问题**：终点策略偏移无法反映RL训练过程中局部动作偏好是否稳定演化。
- **做法**：引入中间教师检查点，比较早期与后期策略偏移方向是否一致，用门控机制筛选终点偏移用于蒸馏。
- **效果**：在六组学生-领域组合中均取得蒸馏方法中最高平均分，去除或打乱门控会显著降低数学推理表现。
- **值得看**：仅需一次额外冻结教师打分，开销极小却能稳健提升蒸馏质量。

### 2. Jeva：从第一性原理出发的系统一决策模型

**Jeva: System One Models from First Principles**
National University of Singapore ｜ 🔥 HF 419 赞 ｜ 💻 [代码](https://github.com/LiQiiiii/Jeva) ｜ [arXiv:2610.18773](https://arxiv.org/abs/2610.18773)

- **问题**：现有快速决策模型忽视了空缺识别、顺序不变、候选可扩展、可缓存四项结构需求。
- **做法**：共享编码器独立表示请求与各选项，用对称聚合与覆盖度估计构建可复用的决策架构。
- **效果**：实现近乎完美的空值检测，任意排列下决策不翻转，可扩展到数千候选并显著降低延迟。
- **值得看**：为"选择题式"决策任务提供了一套结构化、可复用的新范式。

### 3. 动态频带划分：让音频分离模型按内容自适应切分频谱

**Learning Where to Split: Dynamic Band Splitting for Audio Source Separation**
Tsinghua Machine Learning Group ｜ 🔥 HF 134 赞 ｜ 💻 [代码](https://github.com/JusperLee/Dynamic-Band-Splitting) ｜ [arXiv:2610.14993](https://arxiv.org/abs/2610.14993)

- **问题**：固定频带划分无法适应不同混音的频谱结构，容易浪费或混淆关键信息。
- **做法**：提出DBS框架，在固定token预算下按内容预测边界并自适应池化生成频带token。
- **效果**：在DnR v2上DBS-BSRNN相对SI-SDR提升29.0%，在多个数据集上均优于静态基线。
- **值得看**：即插即用地增强多种分离骨干网络，且开源了代码与试听demo。

### 4. TPPO：追踪价值演化的PPO算法用于语言模型推理

**TPPO: Tracking-Value PPO For Language Model Reasoning**
🔥 HF 95 赞 ｜ 💻 [代码](https://github.com/LINs-lab/TPPO) ｜ [arXiv:2610.16794](https://arxiv.org/abs/2610.16794)

- **问题**：稀疏终局奖励下标准critic难以追踪轨迹中价值的逐步演化。
- **做法**：基于前缀价值的贝叶斯加法分解，提出按位置累加的价值参数化方法TPPO。
- **效果**：在Qwen3-4B/8B-Base上数学推理平均分比PPO提升7.0和8.4分，并增强分布外泛化。
- **值得看**：价值追踪更准、优势估计更可靠，代码开源，易于复现验证。

### 5. DoSA：基于证书式筛选的无损稀疏注意力加速

**DoSA: Dots Sparse Attention**
dots studio ｜ 🔥 HF 81 赞 ｜ 💻 [代码](https://github.com/llm-sys/flash-indexer) ｜ [arXiv:2610.13990](https://arxiv.org/abs/2610.13990)

- **问题**：稀疏注意力的Top-K选择仍需对每个候选键用索引头逐一打分，开销大。
- **做法**：用下界/上界证书快速排除不可能入选的候选，仅对存疑候选精确打分。
- **效果**：Indexer计算最高提速2.74倍（对比SGLang），GLM-5.2/DeepSeek-V3.2首token延迟最高降1.94倍。
- **值得看**：无损保证精确选择结果，是工程落地价值很高的推理加速方案。

### 6. 稀疏自编码器表征的行为可组合性研究

**Behavioral Compositionality of Sparse Autoencoder Representations**
OpenSAE ｜ 🔥 HF 107 赞 ｜ 💻 [代码](https://github.com/OpenSAE/SAE-Behavioral-Compositionality) ｜ [arXiv:2610.21261](https://arxiv.org/abs/2610.21261)

- **问题**：稀疏自编码器特征线性解码，但其对模型行为的下游影响是否可线性叠加尚不清楚。
- **做法**：提出SAR指标度量超出给定交互阶数的行为残差，并与随机旋转基线对比。
- **效果**：18个模型/行为设置中学习坐标残差更低；引入二阶项后排序保真度从0.587升至0.779。
- **值得看**：为可解释性研究中"特征可叠加"假设提供了量化检验工具。

### 7. 评分越高答得越差：基于协议级评分准则缓解规则化RL中的奖励作弊

**Scoring Higher, Answering Worse: Mitigating Reward Hacking in Rubric-Based RL via Protocol-Level Rubrics**
ByteDance ｜ 🔥 HF 70 赞 ｜ 💻 [代码](https://github.com/Estrellajer/ProRubric) ｜ [arXiv:2609.38847](https://arxiv.org/abs/2609.38847)

- **问题**：加权求和聚合评分准则时各条目可相互补偿，导致模型漏掉关键判断却靠无关内容拿分。
- **做法**：提出ProRubric，将准则分组为协议维度，组内条目需同时满足才计分，不改变优化器本身。
- **效果**：在医疗咨询场景中适当性提升10.8分且未损失覆盖率，七个基准平均表现最优。
- **值得看**：揭示了奖励有效性不仅取决于准则本身，更取决于其聚合方式，具有普遍参考价值。

### 8. 你的Transformer其实暗藏弹性：免重训练的动态算力适配

**Your Transformer Is Secretly Elastic**
Video & Image Sense Lab ｜ 🔥 HF 5 赞 ｜ 💻 [代码](https://github.com/WalterSimoncini/secretly-elastic) ｜ [arXiv:2610.20588](https://arxiv.org/abs/2610.20588)

- **问题**：预训练模型通常只提供少数固定规格，难以灵活匹配多变的硬件和负载需求。
- **做法**：提出免重训练方法，对每个MLP神经元和注意力头联合排序，在多稀疏度目标下软剪枝优化。
- **效果**：27个模型上60%稀疏度仍平滑退化，DINOv3剪去50%参数准确率仅降0.8%，吞吐提升1.8倍。
- **值得看**：几分钟内就能把现成模型"弹性化"，部署灵活性大幅提升且几乎零精度代价。

### 9. RSI-Anything：借助世界模型解锁递归自我改进

**RSI-Anything: Unlocking Recursive Self-Improvement with World Models**
PhAI Labs ｜ 🔥 HF 50 赞 ｜ 💻 [代码](https://github.com/Gen-Verse/RSI-Anything) ｜ [arXiv:2610.13912](https://arxiv.org/abs/2610.13912)

- **问题**：递归自我改进依赖昂贵的外部反馈，而世界模型预测又随策略演化逐渐失准。
- **做法**：提出RSI-Anything，用预测性世界模型指导动作与训练数据筛选，并配合兼容性检查更新策略。
- **效果**：代码修复成功率从26.3%提升至31.2%，反应优化平均最优产率达96.15%，远超贝叶斯优化的82.16%。
- **值得看**：跨多个科学与计算领域验证了"用世界模型自我迭代"的通用性和实际增益。

### 10. ProbabilityBench：基于精确真实不确定性的模型评估与校准基准

**ProbabilityBench: Model Evaluation and Calibration with Exact Ground-Truth Uncertainty**
ishidalab ｜ 🔥 HF 10 赞 ｜ 💻 [代码](https://github.com/ishida-lab/ProbabilityBench) ｜ [arXiv:2610.17016](https://arxiv.org/abs/2610.17016)

- **问题**：现实数据每个样本只有单一标签，难以直接评估模型报告的概率是否准确。
- **做法**：构建三个可解析数据生成过程的模拟领域，精确计算真实类别概率和贝叶斯误差作为基准。
- **效果**：用KL散度直接度量概率质量，16个模型测试显示Jev等决策模型位于成本-质量帕累托前沿。
- **值得看**：首次提供可精确求真值的不确定性评估基准，也可反过来检验校准指标本身的准确性。

---

## 五、机器人与具身智能

### 1. GroundingPI：面向物理智能的视觉定位基础模型

**GroundingPI: A Grounding Foundation Model towards Physical Intelligence with Visual Primitives**
XPENG AI ｜ 🔥 HF 321 赞 ｜ 💻 [代码](https://github.com/groundingpi/GroundingPI) ｜ [arXiv:2609.39601](https://arxiv.org/abs/2609.39601)

- **问题**：现有VLA感知骨干在杂乱场景和小物体的精准定位上不够快、不够准，难以支撑闭环控制。
- **做法**：训练4B定位基础模型，统一输出点与框坐标，结合多模态预训练、监督微调与GRPO强化学习。
- **效果**：34个基准上平均73.68%超越更大的GPT-6 Astra，RoboTwin 2.0分布外场景最高领先24.8%。
- **值得看**：验证了"定位优先"作为具身智能感知基础的路线，兼顾操作与自动驾驶双任务。

### 2. Reflex：视觉驱动的人形机器人反应式控制

**Reflex: Visually Grounded Reactive Humanoid Control**
University of Washington ｜ 🔥 HF 153 赞 ｜ 💻 [代码](https://github.com/ToberJ/reflex) ｜ [arXiv:2610.12772](https://arxiv.org/abs/2610.12772)

- **问题**：人形机器人难以像人一样在一秒内凭视觉接住抛来的物体并做全身协调反应。
- **做法**：三阶段训练：先用强化学习学全身接球，再学推断物体动力学，最后用第一视角RGB-D还原该表征。
- **效果**：仿真中纯视觉接球成功率85.7%，真实G1机器人在2.5米和5米处分别达65%和40%成功率。
- **值得看**：把"反应式全身控制"拆解为可分阶段训练的子能力，视觉学习更可扩展。

### 3. GreenWAM：面向机器人的世界基础模型

**GreenWAM: A World Foundation Model for Robotics**
Sber Robotics Center ｜ 🔥 HF 107 赞 ｜ 💻 [代码](https://github.com/greenvla/GreenWAM) ｜ [arXiv:2610.18774](https://arxiv.org/abs/2610.18774)

- **问题**：世界模型和策略通常分开构建，且不同机器人动作格式各异，难以共享一个世界模型。
- **做法**：构建涵盖20种机器人本体的统一动作空间，联合训练视觉、动作条件与世界-动作模式，并拆分动作专家。
- **效果**：在WorldArena、RoboTwin 2.0、LIBERO-plus等多项基准领先，真实人形机器人上优于π0.5和Cosmos 3 Edge适配版本。
- **值得看**：证明单一世界模型可同时胜任预测与控制，且跨本体专精能双向提升效果。

### 4. LeWAM：基于JEPA的端到端世界与动作建模

**LeWAM: End-to-End World and Action Modeling with JEPAs**
LeWAM ｜ 🔥 HF 78 赞 ｜ 💻 [代码](https://github.com/MinghaoFu/lewam) ｜ [arXiv:2610.12818](https://arxiv.org/abs/2610.12818)

- **问题**：现有JEPA世界模型通常分阶段训练表征、动力学与策略，流程割裂且规划效率低。
- **做法**：提出端到端JEPA，联合训练下一状态预测与动作流匹配，并对潜状态加高斯约束以支持直接执行和快速规划。
- **效果**：接触密集任务成功率从28.6%升至89.7%，长程任务从10.9%升至46.2%，规划速度快32.3倍。
- **值得看**：展示了无需像素重建的紧凑世界模型也能兼顾控制精度与规划速度。

### 5. VLA-Δ：为视觉-语言-动作模型学习物理状态转移

**VLA-Δ: Learning Physical State Transition for Vision-Language-Action Models**
ZJU-OmniAI ｜ 🔥 HF 55 赞 ｜ 💻 [代码](https://github.com/ZJU-OmniAI/VLA-Delta) ｜ [arXiv:2610.21306](https://arxiv.org/abs/2610.21306)

- **问题**：现有VLA直接拟合观测到动作的映射，缺乏对中间物理状态变化的显式监督，容易过拟合。
- **做法**：构建大规模预训练数据集并标注物理状态转移，将当前与未来状态间的物理变化作为显式学习目标。
- **效果**：在LIBERO、RoboTwin上与SOTA相当，真实机器人实验中超越π0.5，且推理无额外开销。
- **值得看**：提供了一种无需增加推理成本就能强化动作生成物理一致性的训练范式。

### 6. WAVE-0：用轻量潜在未来预测连接VLA策略与世界动作模型

**WAVE-0: Bridging VLA Policies and WAMs with Lightweight Latent Future Prediction**
🔥 HF 47 赞 ｜ 💻 [代码](https://github.com/AutoLab-SAI-SJTU/WAVE-0) ｜ [arXiv:2610.18568](https://arxiv.org/abs/2610.18568)

- **问题**：VLA策略生成动作时不显式建模后果，而现有世界动作模型依赖昂贵的视频生成或次优潜在动作推断。
- **做法**：在预训练VLA上加257M轻量世界模型，将潜在动作计划转为未来表征以指导动作专家，用反事实排序目标直接训练。
- **效果**：RoboTwin 2.0成功率91.47%，LIBERO达98.7%，真实任务把π0.5成功率从38.3%提升到73.3%。
- **值得看**：无需像素重建或大规模视频预训练即可获得未来预测增益，工程成本低。

### 7. 迈向智能体化机器人：模型、数据、环境与中间件综述

**Towards Agentic Robots: Model, Data, Environment, and Harness**
🔥 HF 34 赞 ｜ 💻 [代码](https://github.com/chonghanqin/Awesome-Agentic-Robots) ｜ [arXiv:2610.20442](https://arxiv.org/abs/2610.20442)

- **问题**：机器人基础模型正从单纯动作预测走向目标导向的智能体化编排，但相关研究零散缺乏统一视角。
- **做法**：系统梳理从策略到智能体系统的演进，按模型、数据、环境、中间件四大领域归纳出十七个子类。
- **效果**：给出了对VLA、世界模型、世界动作模型及其组合方式的统一综述框架。
- **值得看**：是把握"智能体化机器人"这一新兴范式全貌的入门地图，适合快速建立知识体系。

### 8. EgoExplorer：面向人类移动操作的视觉-动作-触觉观测数据集

**EgoExplorer: A Vision-Motion-Touch Observatory for Human Loco-Manipulation In Situ**
Intern Robotics ｜ 🔥 HF 32 赞 ｜ 💻 [代码](https://github.com/InternRobotics/EgoExplorer) ｜ [arXiv:2610.18872](https://arxiv.org/abs/2610.18872)

- **问题**：现有数据集只能片面记录人类移动与操作协同过程，难以支撑人形机器人从示范中学习。
- **做法**：用可穿戴系统采集100小时第一视角视频、全身动作、手指动作与触觉数据，并设计标定-补全-约束流程处理稀疏传感。
- **效果**：相比最强基线，身体关键点误差降低71.9%，手部稳定性与接触估计也有提升。
- **值得看**：首个同步记录运动、姿态与触觉的大规模专业活动数据集，为仿真人形控制提供新素材。

### 9. HumanoidToolBench：从工具选择到移动执行的人形机器人工具使用基准

**HumanoidToolBench: Benchmarking Humanoid Tool Use from Selection to Mobile Execution**
SNU PI ｜ 🔥 HF 27 赞 ｜ 💻 [代码](https://github.com/SNU-PI/HumanoidToolBench) ｜ [arXiv:2610.02089](https://arxiv.org/abs/2610.02089)

- **问题**：缺乏同时评估人形机器人工具选择、操作与移动协调能力的综合基准。
- **做法**：构建18任务、3场景、3执行等级的基准HumanoidToolBench，并收集3100条仿真与真实G1示范数据ToolBook。
- **效果**：评测七种仿真策略和三种真实策略，发现工具选择与任务完成之间存在明显差距。
- **值得看**：填补了人形机器人"选工具+用工具"联合评测的空白，暴露当前策略的真实短板。

### 10. TouchScale：500小时人类视觉触觉学习数据集

**TouchScale: 500 Hours of Human Vision and Touch for Visual-Tactile Learning**
2077AI ｜ 🔥 HF 19 赞 ｜ 💻 [代码](https://github.com/phai-lab/touchscale) ｜ [arXiv:2610.10288](https://arxiv.org/abs/2610.10288)

- **问题**：现有视觉触觉数据集规模远小于人类视频数据，且传感器与标注流程不统一，难以研究数据规模效应。
- **做法**：用单一可穿戴设备采集500小时同步第一视角RGB-D、腕部视频与双手触觉数据，覆盖约2000个任务描述。
- **效果**：未见触觉传感器上零样本接触IoU从0.134升到0.383，机器人接触密集任务成功率从22.5%提升到57.5%。
- **值得看**：证明统一传感、规模化采集的人类触觉数据能同时惠及感知与机器人操作性能。

---

## 六、智能眼镜 / 可穿戴 / 第一人称视觉

本周该方向动静不大，只精选了 8 篇真正相关、有实质内容的工作，没有为了凑数纳入边缘论文。

### 1. 立体聆听世界：面向沉浸式视频-音频联合生成的动态空间对应学习

**Hear the World in Stereo: Learning Dynamic Spatial Correspondence for Immersive Joint Video-Audio Generation**
🔥 HF 68 赞 ｜ 💻 [代码](https://github.com/vivoCameraResearch/StereoBind) ｜ [arXiv:2609.38748](https://arxiv.org/abs/2609.38748)

- **问题**：AR/VR 和互动游戏需要立体声随画面中声源运动同步变化，现有视频-音频生成模型普遍忽略这种动态空间一致性。
- **做法**：提出 StereoBind，用运动轨迹把视觉运动与立体声生成绑定，并构建大规模配对数据集 StereoWorld-29K 及专用评测基准。
- **效果**：在保持整体音视频质量的同时，大幅提升立体声生成的空间对齐精度。
- **值得看**：为沉浸式内容生成提供了声音随画面运动"跟脚"的关键技术路径。

### 2. DAO 与 JING：持久化世界状态与第一人称交互式世界模拟

**Generative World Simulation with DAO and JING**
XGEN-Labs ｜ 🔥 HF 8 赞 ｜ 💻 [代码](https://github.com/XGEN-Labs/XGEN-JING) ｜ [arXiv:2610.19726](https://arxiv.org/abs/2610.19726)

- **问题**：现有生成式世界模型缺乏能持续记忆历史、随动作演化、支持多视角共享的交互世界。
- **做法**：DAO 计算式世界引擎维护角色、物体与空间状态，驱动第一人称体验模型 JING 据此生成每个观察者的实时音视频体验。
- **效果**：实现了持续演化、保留历史的沉浸式交互世界，代码与模型均已开源。
- **值得看**：将世界状态管理与第一人称画面生成解耦又联动，为可穿戴/XR 长时交互提供新范式。

### 3. FlowAvatar：消费级 XR 设备上基于稀疏第一人称输入的实时全身化身重建

**FlowAvatar: Real-Time Full-Body Avatars from Sparse Egocentric Inputs on Consumer XR Devices**
热度未测得 ｜ 💻 [代码](https://github.com/SPICExLAB/FlowAvatar) ｜ [arXiv:2610.16277](https://arxiv.org/abs/2610.16277)

- **问题**：现有化身系统很少能在消费级头显上统一实时还原全身姿态、手部、表情和视线，多依赖专业实验室设备。
- **做法**：仅用 Quest Pro 自带稀疏第一人称传感数据，实时重建带个性化外观的全身、手部与面部化身。
- **效果**：姿态模型空间精度有竞争力、时序一致性达最优；两次用户实验证实追踪完整度与个性化外观需共同作用才能带来最佳具身感。
- **值得看**：首个在单台消费级头显上统一追踪全身要素的实时系统，已被 IEEE ISMAR 2026 接收。

### 4. VISTA：面向盲人与低视力用户目标导向辅助的多模态第一人称基准

**VISTA: A Multimodal Egocentric Benchmark for Goal-Oriented Perception and Assistance to Blind and Low-Vision Users**
热度未测得 ｜ [arXiv:2610.22822](https://arxiv.org/abs/2610.22822)

- **问题**：现有视觉辅助基准多局限于图文问答，缺乏结合注视、惯性、轨迹等可穿戴多模态信号的目标导向指引评测。
- **做法**：用 Project Aria 眼镜采集约1000段第一人称多模态录像，覆盖十类任务，评测14个视觉语言模型及一个融合六种模态的轻量基线。
- **效果**：现有模型能描述场景，但生成真正目标导向的辅助指引能力有限。
- **值得看**：填补了可穿戴视觉辅助从"看懂"到"引导"之间的评测空白，数据代码已开源。

### 5. EgoProbe：流式第一人称视频中长程与精确记忆的基准测试

**EgoProbe: Benchmarking Long-Range and Exact Memory in Streaming Egocentric Videos**
热度未测得 ｜ [arXiv:2610.17128](https://arxiv.org/abs/2610.17128)

- **问题**：可穿戴 AI 助手流式处理第一人称视频时，既要能跨长时间回忆，又要在相似重复事件中准确定位细节，此前缺乏系统评测。
- **做法**：构建含无干扰长程回忆子集与含相似干扰事件子集的基准，并设计由粗到细的多轮追问考察模型记忆。
- **效果**：评测显示现有模型长程回忆普遍受限，即使答对粗粒度问题也常无法复原具体事件细节。
- **值得看**：揭示了流式第一人称记忆中一个此前被忽视的失败模式，对可穿戴助手记忆设计有参考价值。

### 6. EgoWholeView：纯摄像头头戴式全身与双手动作捕捉系统

**EgoWholeView: Camera-Only Head-Mounted Capture of Body and Bimanual Hand Motion for Embodied Demonstrations**
热度未测得 ｜ [arXiv:2610.16256](https://arxiv.org/abs/2610.16256)

- **问题**：单目第一人称相机做动捕时视野有限、尺度模糊、手物遮挡严重，难以同时准确捕捉全身与双手动作。
- **做法**：用六个同步广角 RGB 相机构建头戴系统，外向相机世界定位，俯视相机对身体与手部参数按可靠性融合。
- **效果**：相比单目预测，身体误差降低 3.7%、手部降低 11.2%，时序平滑后手部加速度误差降低超 40%。
- **值得看**：纯 RGB、无需第三人称视角即可实现低成本便携的第一人称全身动捕，对远程操作与具身示教有实用价值。

### 7. PocketTSLM：面向隐私保护手机端推理的设备上软提示时间序列语言模型

**PocketTSLM: Deploying an On-Device Soft-Prompt Time-Series Language Model for Privacy-Preserving Smartphone Reasoning**
热度未测得 ｜ 💻 [代码](https://github.com/SchmiedmayerLab/PocketTSLM) ｜ [arXiv:2610.21308](https://arxiv.org/abs/2610.21308)

- **问题**：可穿戴设备的生理时序数据上传云端会牺牲隐私和延迟，而手机本地模型又难以在有限算力下保留时序结构。
- **做法**：将时序语言模型的软提示变体移植到手机端，把时序窗口编码为嵌入直接注入模型，而非序列化为文本。
- **效果**：相比文本序列化方案，时序 token 数减少约12倍，在睡眠分期和心电图任务上实现全程设备端推理，无数据外传。
- **值得看**：展示了可穿戴健康数据"数据不出机"的可行路径，代码已开源。

### 8. EgoOmniWorld：以自我-动作-世界交互统一第一人称视频理解

**EgoOmniWorld: Unifying Egocentric Understanding via Ego-Action-World Interactions**
热度未测得 ｜ [arXiv:2610.18499](https://arxiv.org/abs/2610.18499)

- **问题**：第一人称视频理解的各类能力和评测方式长期割裂研究，未能反映真实世界中感知、决策、行动与反馈的紧密耦合。
- **做法**：提出"自我-动作-世界"交互闭环，构建含节点、边、链、环四种结构的基准，用证据驱动流程生成结构化问答。
- **效果**：基准含 24166 组问答，评测显示现有多模态大模型在各交互结构上表现参差，在该基准上训练可提升泛化能力。
- **值得看**：为第一人称视频理解提供了统一的交互视角评测框架，数据代码模型将开源。
