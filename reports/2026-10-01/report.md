# AI 论文周报（2026-09-25 – 2026-10-01）

本周 60 篇里最清晰的信号是**蒸馏与自进化**：同族 on-policy 蒸馏的缩放定律、把教师当"方向"而非"终点"的表示空间外插、多教师反馈的音量校准、统一多模态模型拿自评当特权信息自蒸馏、代码 Agent 的分组评审信用重分配，一路排到揭露自进化搜索里"出题器与解题器串通作弊"的诊断工作。研究重心明显不在堆更大的模型，而在**把已有能力更省地搬到另一个模型或另一段推理里，同时防住自我改进过程中的指标幻觉**。

第二个高频信号是"harness"这个词本身——Raven 做"harness 的 harness"、Omni-IO 给已有 Agent 外挂全模态手脚、Mid-Harness 在模型与执行层之间插一道动作验证、MaLiang-Harness 把图像生成组织成构建-检查-修订流程，还有机器人侧的递归 harness 蒸馏。共同点是**不碰模型权重，改模型外面那层执行环境**。世界模型这条线也出现了类似的收敛：实证表明收益来自"准备未来"而非"生成未来"，一次前向就够。

两点需要如实说明：机器人方向本周 25 篇候选里有 24 篇拿到了社区投票，数据相当扎实；但**智能眼镜方向本周没有任何以眼镜硬件或整机系统为主题的论文**，25 篇候选里只有 5 篇有公开热度数据，那一章的排序主要靠主题相关性，不是靠热度。

---

## ⭐ 本周最值得读的 5 篇

1. **Raven：会自己造 harness 的 harness**（Agent）— 501 赞，本周最高；把"模型+harness"当可组合单元，是跨域多智能体编排目前最完整的一份参考架构｜[arXiv:2609.33439](https://arxiv.org/abs/2609.33439)
2. **MaLiang-Harness：用可执行程序画图，还得会自己验货**（多模态）— 实测发现通用能力榜分数与视觉生成能力严重错位，选模型别只看综合榜｜[arXiv:2609.34309](https://arxiv.org/abs/2609.34309)
3. **机器人的上下文学习：方法与应用全景综述**（机器人）— 百页综述配文献仓库，入门或选技术路线时可以当地图用｜[arXiv:2609.36012](https://arxiv.org/abs/2609.36012)
4. **后训练留下的行为暗影**（大语言模型）— 本周最反直觉的发现：不用任务样例、不碰 logits 和参数，只靠无关文本就能迁移能力，既是极简蒸馏路径也是一条安全警示｜[arXiv:2609.29233](https://arxiv.org/abs/2609.29233)
5. **YuE2：用乐谱规划统一符号与音频的音乐生成**（其他深度学习）— 中间乐谱是人和模型都能改的接口，支持改谱重生成与零样本翻唱｜[arXiv:2609.33757](https://arxiv.org/abs/2609.33757)

---

## 一、大语言模型

这一批论文几乎都在同一个问题上发力：如何把强模型已有的能力更省、更准地搬到另一个模型或另一段推理里。蒸馏方向占了半壁江山，其余几篇则从注意力分配、量化、循环深度等角度压缩同等能力下的算力开销。

### 1. 同门蒸馏的缩放定律

**Scaling Properties of Same-Family On-Policy Distillation**
Zhejiang University ｜ 🔥 HF 293 赞 ｜ [arXiv:2609.32722](https://arxiv.org/abs/2609.32722)

- **问题**：RL 练出的推理能力跨模型规模迁移多少、多快，一直没定量答案。
- **做法**：在弱教强、同底、强教弱三种配置上系统测 on-policy 蒸馏，并对峰值分数与迁移斜率拟合幂律。
- **效果**：早期训练中准确率随反向 KL 平方根近似线性上升；弱教强时学生峰值全部反超教师；教师规模的收益到学生规模附近即饱和。
- **值得看**：给出了选教师的反直觉准则——同等分数下小教师迁移更好，教师分数本身不代表监督价值。

### 2. 后训练留下的行为暗影

**Post-Training Leaves Behavioral Shadows on Unrelated Decisions**
Peking University ｜ 🔥 HF 271 赞 ｜ 💻 [代码](https://github.com/myboker/ATD) ｜ [arXiv:2609.29233](https://arxiv.org/abs/2609.29233)

- **问题**：后训练带来的能力变化，是否会泄漏到完全无关的生成内容里。
- **做法**：提出 ATD，只挑共同祖先模型近乎无偏好的两词选项，每个提示只取教师一个词作为训练信号，不用任务样例、logits 或参数。
- **效果**：Qwen2.5-1.5B 上 5664 条响应让 HumanEval+ 提升 5.34 个百分点，科学知识、常识推理、阅读理解上同样出现迁移。
- **值得看**：既是蒸馏的极简新路径，也是一条模型能力可能被无声泄漏的安全警示。

### 3. 教师是方向，不是终点

**The Teacher Is a Direction, Not a Destination: Extrapolating RL-Induced Representation Residuals in On-Policy Distillation**
🔥 HF 231 赞 ｜ 💻 [代码](https://github.com/xixixixixxxx/RIDE) ｜ [arXiv:2609.36484](https://arxiv.org/abs/2609.36484)

- **问题**：想让学生超越教师，在输出空间做外插会被语言模型头衰减、且被采样噪声放大而不稳。
- **做法**：RIDE 改在表示空间外插——逐层逐位置算教师与其 RL 前检查点的残差，把学生隐状态回归到沿该方向更远的目标。
- **效果**：四组不同规模、架构、预训练谱系的基座/RL 教师配对上，RIDE 均逼近或超过教师，是唯一均值达标的方法。
- **值得看**：把"RL 到底改了模型哪里"变成可测量的方向向量，这个视角对诊断后训练同样好用。

### 4. 多教师蒸馏的音量校准

**Beyond Teacher Assignment: Domain-Normalized Multi-Teacher On-Policy Distillation**
Nanyang Technological University ｜ 🔥 HF 176 赞 ｜ 💻 [代码](https://github.com/LiXin97/DN-MOPD) ｜ [arXiv:2609.35347](https://arxiv.org/abs/2609.35347)

- **问题**：把数学、代码、指令跟随几个专家合并成一个全能模型时，多教师蒸馏的学生居然打不过单个最强专家。
- **做法**：诊断出反馈失衡——指令跟随的反馈离散度高出数倍而主导更新；DN-MOPD 保留原路由，按各域实测离散度重新缩放反馈强度。
- **效果**：六个公开基准、三个模型尺寸、三个随机种子、两种长度限制下均优于原方法，并追回大部分数学增益。
- **值得看**：合并专家的关键不只是"谁来教"，还有"谁的话算几分"，这条经验对任何多源监督都适用。

### 5. Transformer 能同时想两件事

**Your Transformer Can Hold Two Thoughts at Once: Evidence of Linear Superposition in LLMs**
🔥 HF 100 赞 ｜ [arXiv:2609.29845](https://arxiv.org/abs/2609.29845)

- **问题**：充满非线性组件的大模型，是否藏着某种基础线性结构。
- **做法**：把两段不同文本的输入线性叠加，观察输出是否等于各自下一词分布的叠加，并用轻量微调尝试恢复这种线性。
- **效果**：叠加线性确实存在，且是架构固有属性而非训练涌现——预训练越久反而越弱；微调可大幅拉回，配合引导解码能一次前向生成两段连贯续写。
- **值得看**：为可解释性提供了一个干净的结构性结论，顺带给出并行生成的新思路。

### 6. 搜索与解题的双层共进化

**EvoDuet: Bilevel Co-Evolution of Web Searching and Task Solving for Scientific Discovery**
Minnesota NLP ｜ 🔥 HF 97 赞 ｜ 💻 [代码](https://github.com/Open-Galapagos/EvoDuet) ｜ [arXiv:2609.40340](https://arxiv.org/abs/2609.40340)

- **问题**：模型驱动的进化搜索一旦卡在知识盲区就停滞，而直接挂个搜索工具只会反复召回同一批网页。
- **做法**：双层优化同时进化解法和查询词，检索门控让模型自判知识缺口，内层按预测得分排序文档，外层并行生成候选并回写结果。
- **效果**：21 项优化任务上，GPT-5.6-Luna 的归一化发现增益从 74.1% 升至 78.0%，Gemini-3.8-Flash 从 61.3% 升至 82.3%；八项任务刷新此前最佳，但 Qwen3.5-9B 没有受益。
- **值得看**：检索不再是外挂，而是和解题一起被优化的对象；小模型无收益这个负面结果也很有信息量。

### 7. 分离式量化：预填充与解码各走一路

**Disaggregated Quantization: Specializing LLM Prefill and Decode**
 IST Austria Distributed Algorithms and Systems Lab ｜ 🔥 HF 90 赞 ｜ 💻 [代码](https://github.com/IST-DASLab/disaggregated-quantization) ｜ [arXiv:2609.26333](https://arxiv.org/abs/2609.26333)

- **问题**：预填充要的是低精度算力，解码要的是小权重省带宽，一套量化方案满足不了两边。
- **做法**：为两个阶段分别定制计算格式、权重和存储位置；再用卸载式预填充从 SSD 流式加载额外权重，把加载开销摊进提示长度。
- **效果**：27B 模型上 NVFP4 预填充器让 1-bit 的 MMLU-Pro 提升 32.5 分、MMMU-Pro 提升 35.3 分且不改解码检查点；8K 提示下首词延迟加速 1.78 倍。
- **值得看**：部署侧立刻能用——不动既有解码权重就能大幅挽救极低比特模型的质量。

### 8. 让注意力自己分配算力

**MassAlloc Attention: Let Attention Allocate Its Own Compute**
Beijing Academy of Artificial Intelligence ｜ 🔥 HF 74 赞 ｜ 💻 [代码](https://github.com/HKUSTDial/flash-sparse-attention) ｜ [arXiv:2609.32712](https://arxiv.org/abs/2609.32712)

- **问题**：全注意力对大片得分空间只分到可忽略的归一化质量，稠密核却仍把完整后续计算跑完。
- **做法**：MALA 保留对所有合法因果交互的打分权限，按归一化贡献度分配打分后的计算；前向用在线 softmax 归一化因子，反向复用最终因子推出嵌套保留集合，训练与推理共用一个容差。
- **效果**：128K 张量并行下训练前反向延迟降 2.2 倍和 3.0 倍、解码降 1.6 倍；0.6B 到 14B 的缩放训练中困惑度紧跟全注意力，长上下文检索与推理分数相当。
- **值得看**：稀疏注意力常以牺牲可达性换速度，这里换成"全都能看、按贡献花钱"，范式更干净。

### 9. 自适应循环层拉高测试时缩放

**Improving Test-Time Scaling with Adaptive Looped Transformers**
Tsinghua-NICS-EFC ｜ 🔥 HF 54 赞 ｜ 💻 [代码](https://github.com/thu-nics/TaH) ｜ [arXiv:2609.35748](https://arxiv.org/abs/2609.35748)

- **问题**：复用层的循环 Transformer 省参数，但输出变长时能否改善测试时缩放，几乎没人验证。
- **做法**：以"解码算力翻倍带来的准确率增益"为斜率指标，发现固定深度循环把迭代浪费在不需要的 token 上；TaH2 用前瞻深度监督联合训练主干和一个迭代决策器。
- **效果**：AIME 上斜率比非循环基线提升 53%（2.74 对 1.79），同算力下峰值准确率高约 3.4 分；深度从 2 加到 8 时优势从 +2.8 分继续涨到 +3.9 分。
- **值得看**：把"该想多久"交给模型逐 token 自己决定，这是深度自适应少见的可落地做法。

### 10. 知道想不出来就去问

**Knowing When Thinking Is Not Enough: Teaching Small Reasoning Models to Reason Beyond Their Parametric Knowledge**
KAIST AI ｜ 🔥 HF 40 赞 ｜ 💻 [代码](https://github.com/tally0818/FlyBy) ｜ [arXiv:2609.34327](https://arxiv.org/abs/2609.34327)

- **问题**：小推理模型便宜，但一味加长思考并不总有用——自我反思多半只是把概率压到已经够得着的解上。
- **做法**：区分出执行瓶颈与知识瓶颈两类失败；FlyBy 先推理再自诊断，遇到知识瓶颈才向更强模型发问，由监督微调引导多层次提问动作、成本感知 RL 校准问不问、问什么、花多少。
- **效果**：六个基准 1158 道难题上，FlyBy-4B 取得 45.96% pass@8，超过 Qwen3-14B 的 41.64% 而服务成本低 2.7 倍；8B 版进一步到 51.81%。
- **值得看**：给"小模型加思考还是加求助"这个工程抉择提供了判据，路由式混合部署可以直接参考。

---

## 二、多模态 / 视觉语言

这一批的主线是"让多模态模型自己看见、自己验证、自己纠错"——无论是程序化生成后的渲染回检、潜空间推理的视觉证据监督，还是统一模型的自蒸馏，核心都在把视觉反馈接回训练与推理闭环；另一条副线则在重估架构地基：视觉骨干、视觉编码器、自编码器都被重新质询。

### 1. MaLiang-Harness：用可执行程序画图，还得会自己验货

**MaLiang-Harness: A Programmable Path to Image and Video Generation**
National University of Singapore ｜ 🔥 HF 386 赞 ｜ 💻 [代码](https://github.com/gulucaptain/MaLiang-Harness) ｜ [arXiv:2609.34309](https://arxiv.org/abs/2609.34309)

- **问题**：代码能跑通，画面却不符合要求的构图、外观或运动，作者称之为"程序到画面"(P2V) 落差。
- **做法**：把 MLLM 生成视觉内容组织成"构建—检查—修订"的持续流程，让程序、修改历史与校验共享同一份修订基准。
- **效果**：在自建图像与视频两个基准上评测 11 个闭源 MLLM，最强者生成成功率 100%，但图像 96.0%、视频仅 76.9% 全项达标。
- **值得看**：实测显示通用能力榜分数与视觉生成能力严重错位，选模型别只看综合榜。

### 2. VisionHOPE：会自己改写学习规则的视觉骨干

**VisionHOPE: Visual Backbones as Self-Modifying Learning Systems**
Mininglamp Technology ｜ 🔥 HF 319 赞 ｜ 💻 [代码](https://github.com/PSRben/VisionHOPE) ｜ [arXiv:2609.33325](https://arxiv.org/abs/2609.33325)

- **问题**：从 CNN 到 ViT、SSM、TTT，视觉计算越来越随输入自适应，但"怎么适应"仍由训练好的骨干写死。
- **做法**：基于嵌套学习构造五套耦合记忆，让记什么与怎么学在一张图内共同演化，并给出稳定性匹配的步长控制。
- **效果**：在 ImageNet-1K、COCO、ADE20K 上取得有竞争力的结果，并证明记忆动力学沿扫描非扩张。
- **值得看**：第一个把"自我改写"做成通用视觉骨干的样本，给架构设计开了条新口子。

### 3. UniEvo-VL：统一模型当自己的老师

**UniEvo-VL: An On-policy Self-Distillation Training Recipe for Multimodal Model Self-improvement**
Stanford NLP ｜ 🔥 HF 237 赞 ｜ [arXiv:2609.38721](https://arxiv.org/abs/2609.38721)

- **问题**：统一多模态模型既能看又能画，本该从自己的反馈里学，却仍普遍依赖更大的外部教师。
- **做法**：同一个模型分饰两角——教师看得到自评批注这份"特权信息"，学生只看原题，在学生自己的采样轨迹上对齐去噪分布。
- **效果**：基于开源 Qwen-image-2512，GenEval 从 0.747 升至 0.808，GenEval2 Soft-TIFA 从 32.97 升至 35.53。
- **值得看**：换更强的外部评判者天花板还会抬高，而文字渲染任务提升不均——递归自改进的边界被量了出来。

### 4. ReaLVR：给潜空间推理补上视觉证据

**Rethinking Latent Visual Reasoning: Grounding Latent Reasoning in Visual Evidence**
Amazon ｜ 🔥 HF 207 赞 ｜ 💻 [代码](https://github.com/xixiaouab/ReaLVR-code) ｜ [arXiv:2609.34563](https://arxiv.org/abs/2609.34563)

- **问题**：潜空间视觉推理不可直接观测，作者发现"证据—归因缺口"：改动图像到足以改变答案，潜 token 却几乎无反应。
- **做法**：诊断根因是 GRPO 只用最终答案奖励；ReaLVR 对比正误答案定位该加监督之处，再用匹配/错配的视觉证据指定该保留什么。
- **效果**：跨三个模型族稳定超越同类方法，Qwen2.5-VL-7B 五任务均分 63.7%，并首次在 235B 规模上仍见增益。
- **值得看**：潜式推理一直被诟病不可控，这篇给出了可操作的监督信号设计思路。

### 5. FuseReg：别再手挑编码器层

**FuseReg: Regularizing Layer Fusion Mitigates the Reconstruction-Generation Gap in Representation Autoencoders**
USC Physical Superintelligence (PSI) Lab ｜ 🔥 HF 157 赞 ｜ 💻 [代码](https://github.com/Hongyang-Du/FuseReg) ｜ [arXiv:2609.31620](https://arxiv.org/abs/2609.31620)

- **问题**：表征自编码器须选哪些编码器层组成隐空间，浅层保细节、深层利生成，固定启发式选法把两个阶段强行绑在一起。
- **做法**：改为在随机层子集上训练，理论上等价于惩罚模型对跨层分歧的敏感性。
- **效果**：单个解码器无需重训即可适配全层/稀疏/单层融合，PSNR 高于专用解码器；仅换解码器就把 gFID 降低 27%，联合正则化在 DiT-Base 上降 29%。
- **值得看**：不碰预训练编码器、只改下游训练方式就收窄重建—生成鸿沟，迁移成本极低。

### 6. Simple-WAM：预测未来有用，生成未来没必要

**What Makes World Action Models Generalize? An Empirical Study of Test-Time Future Modeling**
Tsinghua-LeapLab ｜ 🔥 HF 114 赞 ｜ 💻 [代码](https://github.com/LeapLabTHU/Simple-WAM) ｜ [arXiv:2609.34981](https://arxiv.org/abs/2609.34981)

- **问题**：世界动作模型推理时到底要不要生成未来帧？显式派去噪成完整画面，隐式派为省算力直接扔掉。
- **做法**：在环境扰动、数据效率、任务泛化三轴上做同骨干同预算对照，定位增益几乎全来自第一步去噪。
- **效果**：据此提出的 Simple-WAM 只做一次全噪视频 token 前向并适配训练噪声调度，泛化领先显式派而效率接近隐式派。
- **值得看**：一句"收益来自准备未来，而非生成未来"，直接改写了这条线的工程取舍。

### 7. WorldAuditBench：让多模态智能体去 3D 世界里查 bug

**WorldAuditBench: Interactive 3D World Auditing with Multimodal Agents**
University of California, Santa Barbara ｜ 🔥 HF 93 赞 ｜ 💻 [代码](https://github.com/UCSB-NLP-Chang/WorldAuditBench) ｜ [arXiv:2609.40325](https://arxiv.org/abs/2609.40325)

- **问题**：交互式 3D 世界里的悬空物体、可穿行墙面等异常需要人工排查，而查错要求"行动探索"与"视觉推理"紧密耦合。
- **做法**：用 UE5 与 Three.js 搭 13 个环境、213 个异常任务覆盖五类异常，在固定探索预算下比较两种审计范式。
- **效果**：五个前沿模型成功率仅 6.6%–42.3%，远低于人类的 83.4%。
- **值得看**：把"边推理边验证"这件事做成可测指标，暴露的是智能体在探索中收集与解读证据的短板。

### 8. GEB：给长视频里的每个物体写一本传记

**Beyond the Timeline: Augmenting Long-Video Memory with Grounded Entity Biographies**
Amazon Science ｜ 🔥 HF 88 赞 ｜ 💻 [代码](https://github.com/rhfeiyang/GEB) ｜ [arXiv:2609.38155](https://arxiv.org/abs/2609.38155)

- **问题**：跨数小时乃至数天的视频问答要追踪同一物体，但按时间排的描述留不住物理身份——描述相同的是两件东西，同一件东西的观测又彼此断联。
- **做法**：在建记忆阶段就把视觉落地的同一实例观测跨片段聚成可检索的"传记"，问答时与情节证据一并召回。
- **效果**：四个基准（含整日、整周录制）全面优于既有记忆框架，EgoLifeQA 达 72.0%，超最佳已发表结果 4.4 个百分点。
- **值得看**：消融表明光加描述补不回这部分收益，身份关联才是关键——长视频记忆的组织方式值得重想。

### 9. 还要多久能扔掉视觉编码器？

**How Far Are We from Removing the Visual Encoder? Scaling Laws for Encoder-Free Multimodal Pretraining**
Tencent Hunyuan ｜ 🔥 HF 64 赞 ｜ [arXiv:2609.35457](https://arxiv.org/abs/2609.35457)

- **问题**：无编码器 MLLM 直接从像素学表征，架构更统一，但缩放行为一直没被系统刻画。
- **做法**：并排拟合有/无编码器两类架构的缩放律，分别考察文本与多模态目标。
- **效果**：去掉编码器会把多模态最优算力分配推向更大模型；两者文本前沿几乎重合，多模态上无编码器小规模吃亏，预计约 10²² FLOPs 追平。
- **值得看**：还观察到语言模型会自发接管视觉角色——视觉处理前移、专家路由更集中，是架构路线决策的硬证据。

### 10. Imagine3D-LLM：先在脑子里搭个场景再回答

**Imagine3D-LLM: Teaching MLLMs to Imagine 3D Scenes Before Answering**
KAIST AI ｜ 🔥 HF 57 赞 ｜ 💻 [代码](https://github.com/cvlab-kaist/Imagine3D-LLM) ｜ [arXiv:2609.38177](https://arxiv.org/abs/2609.38177)

- **问题**：MLLM 处理单图不难，要把多视角证据整合成连贯的 3D 理解却仍远逊于人。
- **做法**：仿照人类先粗略配准、再拼出大致布局的做法，在图像 token 后接少量可学习摘要 token，解码成紧凑 3D 高斯表示并以光度重建损失联合训练。
- **效果**：多个空间推理与 3D 理解基准上稳定超越此前方法。
- **值得看**：只有摘要 token 受重建监督，却带动整个模型的跨帧对应变强——"想象场景"比"被告知逐像素几何"更有效。
---

## 三、Agent

本周 Agent 方向的主线是"harness"——不改模型权重，而是改模型外面那层执行环境：自动构造、自动优化、在模型与 harness 之间加一层动作校验，再配上自我改进与反作弊机制。

### 1. Raven：会自己造 harness 的 harness

**Raven: The Harness of Harnesses for Composable Agentic Intelligence**
EverMind ｜ 🔥 HF 501 赞 ｜ 💻 [代码](https://github.com/EverMind-AI/Raven) ｜ [arXiv:2609.33439](https://arxiv.org/abs/2609.33439)

- **问题**：harness 越做越复杂，手工设计不可扩展，且绑死单一领域。
- **做法**：把"模型+harness"当可组合的智能单元，Host Agent 拆解目标并调度，EverOS 与 Skill Forge 把经验沉淀成可复用流程。
- **效果**：复杂长程任务上显著超过现有 SOTA agent 系统，并给出组合能力扩展任务覆盖的理论条件。
- **值得看**：开源生态，能直接拿来做跨域多智能体编排的参考架构。

### 2. Omni-IO Skills：给已有 Agent 装上全模态手脚

**Omni-IO Skills: Harnessing Your Agent Omni-Native**
National University of Singapore ｜ 🔥 HF 272 赞 ｜ 💻 [代码](https://github.com/any2any-mllm/Omni-IO-Skill) ｜ [arXiv:2609.31847](https://arxiv.org/abs/2609.31847)

- **问题**：扩展模态要么重训模型，要么拼一堆专家工具却管不住依赖和中间产物。
- **做法**：即插即用 harness，分层 Skills + 统一多模态执行接口 + 依赖感知的声明式执行图 + 持久化资产注册表。
- **效果**：27 个 Skills 覆盖 38 类任务；UniM-90 上把 GPT-5.6 Sol 与 Claude Sonnet 5 的输入支持率从 40.0%/38.9% 拉到 100%。
- **值得看**：不动模型推理核心也能补齐能力，工程上最容易照搬的一条路。

### 3. 虚假前沿：自进化搜索 Agent 的"串通作弊"

**False Frontiers: Diagnosing and Mitigating Co-Cheating in Self-Evolving Search Agents**
Rutgers University ｜ 🔥 HF 190 赞 ｜ [arXiv:2609.39102](https://arxiv.org/abs/2609.39102)

- **问题**：出题器与解题器联合优化时会在同一批错误上达成共识，内部奖励涨、真实正确率不涨。
- **做法**：提出 CrossFit，把源文档分 A/B 两组交叉拟合，A 生成的题由只见过 B 的辅助解题器评分。
- **效果**：虚假一致率从 6.1%/8.8% 降到 3.0%/3.7%；七个搜索基准平均提升 8.8 / 8.4 分。
- **值得看**：自进化训练最隐蔽的指标幻觉，附带一套可直接用的审计方法。

### 4. GAGAR：给代码 Agent 的 RL 补上"写得好不好"

**Groupwise Agentic Grading and Advantage Redistribution for Code Agent RL**
Xiaomi MiMo ｜ 🔥 HF 124 赞 ｜ [arXiv:2609.32577](https://arxiv.org/abs/2609.32577)

- **问题**：测试通过即给同样 advantage，策略学不到"干净、不越界的实现更好"。
- **做法**：把同组轨迹放进共享工作区，由 SFT 训出的评审 Agent 排序，再做保和重分配把信用挪向高质量实现。
- **效果**：在 310B 与 1.02T 的 MiMo-V2.6 检查点上验证，代码表现更好、轨迹长度膨胀减缓、训练更稳。
- **值得看**：工业规模的真实经验，说明二值奖励之上还有一层质量信号可挖。

### 5. AREX-2：靠长程反思任务练出自我改进

**AREX-2: Advancing Self-Improving Agents through Long-Horizon Reflective Tasks**
Beijing Academy of Artificial Intelligence ｜ 🔥 HF 121 赞 ｜ 💻 [代码](https://github.com/VectorSpaceLab/AREX-2) ｜ [arXiv:2609.38288](https://arxiv.org/abs/2609.38288)

- **问题**：测试时反复打磨答案，需要反思与长程执行两种能力，但缺监督数据。
- **做法**：在机器学习与算法编程这两个有可验证反馈的领域合成长程改进轨迹，用来训练 Qwen3.8-27B。
- **效果**：MLE-bench Lite 81.8、Frontier-CS 70.7，并迁移到 BrowseComp 84.0、GAIA 92.2，轮数预算越多越强。
- **值得看**：验证了反思能力是跨域的，可以在易监督的场景里便宜地学到。

### 6. LEGO-Anything：让编码 Agent 把照片写成场景程序

**LEGO-Anything: Coding Agents for 3D Scene Reconstruction**
Amazon Web Services ｜ 🔥 HF 120 赞 ｜ [arXiv:2609.36380](https://arxiv.org/abs/2609.36380)

- **问题**：单图三维重建若只给渲染结果，就无法被检查、编辑和查询。
- **做法**：Image-to-Code，让编码 Agent 反复写 Blender 代码、看渲染图、改程序，配 LEGO-Bench 与免训练的 LEGO-Plugin。
- **效果**：最强模型室内 53.4%、室外 39.6%；插件让六个模型全部提升，总分最高涨 62.7%。
- **值得看**：诊断出三类通病——初始化弱、迭代中反向修改、自评不可靠，是 Agent 迭代设计的通用教训。

### 7. Mid-Harness：在模型与 harness 之间加一道动作验证

**Mid-Harness: Scaling Actions Between Model and Harness for Terminal Agents**
NVIDIA ｜ 🔥 HF 103 赞 ｜ [arXiv:2609.39982](https://arxiv.org/abs/2609.39982)

- **问题**：终端 Agent 能生成好动作不等于能可靠执行，一条坏命令就会污染环境。
- **做法**：在动作下发前采样多个候选并验证，只放行一个，生成器与 harness 都不改。
- **效果**：TerminalBench-Lite 上用 GPT-5.6 Sol 当验证器、采 8 个动作，Pass@1 从 50.00% 升到 68.03%；动作+轨迹双向扩展更省 token。
- **值得看**：把测试时算力花在动作粒度而非多跑轨迹，是性价比更高的新开关。

### 8. CorpusMap：按实体给语料画一张导航图

**Follow the Entities: A Corpus Map for Agentic Search**
Microsoft ｜ 🔥 HF 80 赞 ｜ [arXiv:2609.37226](https://arxiv.org/abs/2609.37226)

- **问题**：语料只是一堆扁平文件时，Agent 每次查询都要重新摸索文档间关系，漏证据又烧 token。
- **做法**：离线做跨文档实体对齐，给每个高频实体建一张 Entity Page 并链到所有相关文档，形成可遍历的实体-文档图。
- **效果**：7 个模型 × 3 个数据集上，证据发现与答案质量均优于裸语料检索，平均 token 更少，也胜过 4 种其他导航层。
- **值得看**：把一次性构建的结构复用到所有查询，企业知识库接 Agent 的实用方案。

### 9. RSIGame：递归自改进地做游戏

**RSIGame: Autonomous Agentic Game Development with Recursive Self-improvement**
RSIGame ｜ 🔥 HF 75 赞 ｜ 💻 [代码](https://github.com/WenyiWU0111/RSIGame) ｜ [arXiv:2609.39045](https://arxiv.org/abs/2609.39045)

- **问题**：生成的游戏能跑起来之后就难以继续变好，朴素迭代容易过拟合少量测试用例。
- **做法**：局部"探索-诊断-改进"循环配一份不断累积的检查清单，全局循环追踪质量、保留最优检查点、识别饱和与回退，并把成功经验回灌训练。
- **效果**：140 个 GameCraft-Bench 任务上，Qwen3.8-27B 达到 Godot 61.38、Phaser 58.53，超过 GPT-5.5 一次生成，token 还少 11 倍。
- **值得看**："经验内化"这一步让小模型用更少算力翻盘，思路可移植到其他长程开发任务。

### 10. LLM 本就是异步 Agent

**LLMs are General Asynchronous Agents**
Yandex Research ｜ 🔥 HF 67 赞 ｜ 💻 [代码](https://github.com/dvmazur/async_llm) ｜ [arXiv:2609.35427](https://arxiv.org/abs/2609.35427)

- **问题**：读-想-回的顺序循环不匹配现实——语音助手、具身体、监控系统都会在思考途中收到新输入。
- **做法**：做了一个异步 LLM 框架，允许用户或 Agent 自己定义带重叠记忆状态的推理协程。
- **效果**：Qwen 3.x 无需任务特定训练，就能胜任流式视频理解、电子游戏和监控三类并发场景。
- **值得看**：不必为每种并发单独做架构，异步能力可能已经藏在通用模型里。

---

## 四、其他深度学习

这一批论文集中在"主干之外的基础层"：音频与语音生成/评测、长上下文注意力的效率与隐患、数据管线系统、持续学习动力学与水印安全。共同点是都在拆解既有组件的内部机制——不是堆更大的模型，而是找出哪一层设计决定了效果与失效。

### 1. YuE2：用乐谱规划统一符号与音频的音乐生成

**YuE2: Unifying Symbolic and Audio Music Generation at Frontier Quality**
Multimodal Art Projection ｜ 🔥 HF 240 赞 ｜ 💻 [代码](https://github.com/multimodal-art-projection/YuE) ｜ [arXiv:2609.33757](https://arxiv.org/abs/2609.33757)

- **问题**：符号模型写得出谱但出不了成品，音频模型出歌却说不清作曲。
- **做法**：单个 AR-NAR 混合 Transformer 先写可读乐谱，再展开为语义 token，最后渲染成整首音频。
- **效果**：带规划的整体偏好 49.3% vs 34.6%；WildSongBench 6.73、best-of-8 达 6.96，超所有公开基线，专家听测优于 Suno v4.5。
- **值得看**：中间乐谱是人和模型都能改的接口，支持改谱重生成、零样本翻唱和外部语言模型做"代理式编曲"。

### 2. VoxMem：大音频语言模型的记忆到底记住了什么

**VoxMem: Benchmarking Multimodal Memory in Large Audio Language Models**
The University of Melbourne ｜ 🔥 HF 136 赞 ｜ 💻 [代码](https://github.com/swagshaw/voxmem) ｜ [arXiv:2609.32607](https://arxiv.org/abs/2609.32607)

- **问题**：语音记忆不只是"说了什么"，还有谁说的、怎么说的、背景有什么声，现有基准只测词面内容且只管单轮会话。
- **做法**：按"声学证据类型 × 记忆操作"两轴建分类体系，构建跨多会话、8K–64K 上下文分层的评测集。
- **效果**：3196 条样例、34743 段会话共 177 小时；15 个 LALM 在 32K 下无一超过 40%，说话人身份与副语言线索的差距随历史变长而扩大。
- **值得看**：给语音对话的记忆问题立了一套可拆解的坐标系，失败模式按证据类型区分，便于定位短板而非只看总分。

### 3. 周期性盲区：分块 KV 缓存压缩带来的相位敏感

**Periodic Weak Spots: Phase Sensitivity from Chunked KV-Cache Compression**
ByteDance Seed ｜ 🔥 HF 90 赞 ｜ [arXiv:2609.36322](https://arxiv.org/abs/2609.36322)

- **问题**：分块压缩 KV 缓存省了长上下文开销，却引入了"相位"这个新位置坐标，同一条信息在不同相位上检索难度不同。
- **做法**：在多种 KV 压缩设计上从头预训练一族 Transformer 复现该现象，再用因果干预做机制分析。
- **效果**：大型开源权重模型跨相位检索准确率最高相差 40 个百分点；不同注意力组件对不同源相位的贡献明显不对称。
- **值得看**：平均分会把周期性失效完全藏住——用了分块压缩就必须逐相位评测，这是上线前的硬检查项。

### 4. Duplex-MPE：多人对话里助手该不该开口

**Duplex-MPE: Benchmarking Multi-Party Interaction in Full-Duplex Dialogue**
Peking University ｜ 🔥 HF 89 赞 ｜ [arXiv:2609.31948](https://arxiv.org/abs/2609.31948)

- **问题**：全双工语音模型的基准多围绕"一个指定用户"，没测过助手身处多人聊天时如何判断该答、该闭嘴还是该停下。
- **做法**：2000 个三到四人加一个助手的场景，同一请求配显式/隐式两种称呼方式，只给连续音频、不给转写和轮次边界。
- **效果**：四项指标评五个开源语音系统，MiniCPM-o 4.5 三项领先；文本版 Gemini 3.1 Pro 对显式请求的应答率高出 64.3 个百分点，而语音系统对显隐式无显著差异。
- **值得看**：暴露出语音系统几乎不具备"被点名"的感知，爱说话不等于答得准——做语音助手产品的直接风险清单。

### 5. RayOrch：带血缘关系的多粒度数据预处理引擎

**RayOrch: Programming and Executing Lineage-Controlled Multi-Grain Dataflows for Foundation-Model Data Preparation**
Peking University ｜ 🔥 HF 54 赞 ｜ 💻 [代码](https://github.com/OpenDCAI/RayOrch) ｜ [arXiv:2609.18703](https://arxiv.org/abs/2609.18703)

- **问题**：文档和视频会被拆成数量长尾且有序的子项，GPU 想跨父项批处理，就得自己维护父子关系、顺序和结果归位。
- **做法**：编程模型声明变长展开与对应聚合，编译期校验配对，运行时记录成员归属、父项、不可变序号和终态，用 Per-Call FIFO 就绪队列跨父项组批。
- **效果**：H20 上 MinerU 从 4 卡到 64 卡加速 15.14 倍，视频管线 8 到 64 卡加速 7.82 倍；端到端比 Ray Data 快 13.1%、比 Daft 快 29.0%。
- **值得看**：血缘不是靠批边界"碰巧对齐"，而是由声明保证；失败只影响同一父项的兄弟任务，自建数据工厂的工程参考。

### 6. PISA：把块稀疏注意力的选块降到对数线性

**Block Sparse Attention with Log-Linear Complexity**
ByteDance Seed ｜ 🔥 HF 30 赞 ｜ [arXiv:2609.31093](https://arxiv.org/abs/2609.31093)

- **问题**：块稀疏注意力本身便宜，但"选哪些块"要给所有 query-block 对打分，复杂度仍是平方级。
- **做法**：金字塔式 Top-K——用池化造出 O(log N) 层由粗到细的 key 层级，每层在有界候选集上做 LogSumExp 打分逐级收窄。
- **效果**：整体复杂度降到 O(N log N)；训练与推理都有硬件感知 Triton 核，融合层级路由与打分、不物化 QK 分数矩阵；常识推理持平、检索任务更好。
- **值得看**：瓶颈从"算注意力"转移到"选块"之后，这是一条把选块本身也做成次平方的可落地路线。

### 7. EmoRES-TTS：免训练地把情感向量拆成两半来调

**EmoRES-TTS: Residual-Enhanced Vector Steering for Emotional Speech Generation**
Meta ｜ 🔥 HF 18 赞 ｜ 💻 [代码](https://github.com/facebookresearch/EmoRES-TTS) ｜ [arXiv:2609.38157](https://arxiv.org/abs/2609.38157)

- **问题**：情感 TTS 常表达不出指定情绪，而靠加训练提升可控性在算力和标注语音上都很贵。
- **做法**：发现情感向量可分解为"离开中性"的共享分量与"指向目标情绪"的残差分量，在冻结模型上分别控制二者。
- **效果**：IEMOCAP 上在 IndexTTS-2 与 CosyVoice2 两个骨干上四项客观指标全面超过 CoCoEmo，秩相关提升 26.13/12.97 个百分点；人听情绪识别率相对提升达 35.0%，自然度偏好率最高 63.8%。
- **值得看**：共享分量要保住、残差要加强——这条消融结论给所有表示引导类方法提供了可复用的调参直觉。

### 8. 水印残差为什么能被搬走：可迁移性的架构根源

**Residual Transferability in Neural Image Watermarking**
🔥 HF 12 赞 ｜ [arXiv:2609.32241](https://arxiv.org/abs/2609.32241)

- **问题**：从已发布图像里抽出带水印的残差，贴到无关内容上就能伪造，但到底什么决定了残差的可迁移性一直不清楚。
- **做法**：提出残差可迁移性（RT）指标量化迁移后水印证据的可解码程度，用对比分析与受控干预区分训练侧变化与架构设计的影响。
- **效果**：训练侧差异解释不了各系统间巨大的 RT 差距，架构才是主因；识别出两种让水印证据依赖载体图像的机制，并给出即插即用的 CoverLock。
- **值得看**：CoverLock 不改架构就能改善安全性与鲁棒性的权衡，对已部署的水印系统是现成补救方案。

### 9. 持续学习的动力学：数据归因、遗忘与可塑性丧失是同一件事

**Learning Dynamics of Continual Learning: A Unified View of Data Attribution, Forgetting, and Plasticity Loss**
🔥 HF 6 赞 ｜ 💻 [代码](https://github.com/Joshua-Ren/learning-dynamics-cl) ｜ [arXiv:2609.33620](https://arxiv.org/abs/2609.33620)

- **问题**：模型会被反复更新，而"选什么数据、这次更新改了什么、以后还能不能学"向来被当成三个独立问题。
- **做法**：对"从一个 token 学习如何改变另一处预测"做 token 级与层级分解，分离 softmax 作用力、共享读出几何与残差连接，得到可前向计算的近似。
- **效果**：正向交互指示有用样本，负向交互表现为集中碰撞或累积侵蚀；长期更新会重塑共享几何、削弱未来学习信号的传导，由此得出数据选择策略、针对性干扰控制和基于读出的可学习性诊断。
- **值得看**：一个局部交互量就同时解释了当下变化与未来学习能力，诊断指标恶化还能预测"重置读出层"能带来多少收益。

### 10. 预训练时就把注意力 softmax 量化会发生什么

**Pretraining Transformers with Quantized Softmax in Attention**
University of Illinois at Urbana-Champaign ｜ 🔥 HF 5 赞 ｜ [arXiv:2609.33591](https://arxiv.org/abs/2609.33591)

- **问题**：低精度 Transformer 普遍量化注意力矩阵乘法却把 softmax 留在高精度，而预训练阶段的近似 softmax 会同时改变前向计算和梯度。
- **做法**：用 K-interval attention 以 K+1 个网格值近似指数，系统比较逐行网格校准方式、插值与硬取整、直通替代相对归一化的放置位置，并推导相应反向规则。
- **效果**：detach 行极值虽不改前向却会让验证损失延迟上升；124M 参数、2.5B token 下固定窗口校准配后归一化替代在 K=4 时损失差仅 +0.019 nats，K=16 时前归一化替代为 +0.004 nats。
- **值得看**：量化的代价不在精度位数而在反向路径的几个设计开关上，改一个就能把差距拉回来——低精度训练的实操清单。
---

## 五、机器人与具身智能

这一批工作几乎都在绕开"端到端策略一条路走到黑"：把任务状态写成可检查的代码、把干预经验攒成可复用的手册、把感知拓宽到全景与空间音频、把潜在行为空间跨本体共享——核心都是让策略在新场景里还能站得住。

### 1. 机器人的上下文学习：方法与应用全景综述

**In-Context Learning for Robots: Methods and Applications**
Knowin AI ｜ 🔥 HF 360 赞 ｜ 💻 [代码](https://github.com/JethroJames/awesome-robots-icl) ｜ [arXiv:2609.36012](https://arxiv.org/abs/2609.36012)

- **问题**：通用机器人要靠少量示范临场理解新任务，但这类"不改权重的上下文学习"方法散落各处，缺乏统一梳理。
- **做法**：一篇百页综述，按"上下文证据如何接入执行"划成四类接口：上下文条件策略、几何示范迁移、世界模型控制、技能与智能体式执行。
- **效果**：横向对比各类接口的迁移假设，以及训练、对应关系、记忆三者的作用，并梳理了操作与导航上的评测实践。
- **值得看**：附项目页与文献仓库，想入门或选技术路线时可当地图用；末尾提出的"物理层面递归自我改进"议程值得留意。

### 2. PanoVLN：让全景视野真正用在视觉语言导航上

**PanoVLN: Towards Effective Panoramic Vision-and-Language Navigation**
Zhejiang University ｜ 🔥 HF 152 赞 ｜ 💻 [代码](https://github.com/wangzhen-w/PanoVLN) ｜ [arXiv:2609.34759](https://arxiv.org/abs/2609.34759)

- **问题**：全景图本该带来更完整的视觉上下文，但直接把透视图换成全景图，收益很有限。
- **做法**：三处改动配套——预测更长动作序列并用置信度决定何时重规划、构造多分叉路口的训练路线强化选路监督、融合 RGB 全景的语义与几何特征而不增加视觉 token。
- **效果**：4B 骨干、纯 RGB 输入，R2R-CE 和 RxR-CE Val-Unseen 成功率分别超过此前 SOTA 11.9% 和 8.7%；四足机器人实测走得更快、停顿更少。
- **值得看**：说明换传感器不等于换能力，输入变宽时动作空间、监督数据、表征得一起改——这个诊断思路可迁移到别的模态升级。

### 3. 自进化编码智能体：把物理任务写成可读可改的代码

**Self-Evolving Coding Agents: From Digital Programs to Physical-World Intelligence**
HexaFuture ｜ 🔥 HF 106 赞 ｜ 💻 [代码](https://github.com/HexaFuture/PhysicalCoding) ｜ [arXiv:2609.35432](https://arxiv.org/abs/2609.35432)

- **问题**：VLA/WAM 把任务要求、条件、进度、失败恢复全隐式压进动作序列，既难查看也难修改，布局或视角一变就崩。
- **做法**：提出 Physical Coding——用代码记录物体、关系、约束与进度（Code as World），用代码组织规划、校验、恢复与执行（Code as Policy）；据此构建 HexaAnything，调用感知/规划/控制工具（含 VLA 策略）并据外部反馈在环决策。
- **效果**：RoboCasa365 上 Composite-Unseen 与整体成功率超过 XR-1 VLA，用验证过的代码轨迹训出的 HexaModel 在每个 split 上都胜过基座；双臂 AgileX 真机自主完成物理实验与多数桌面任务。
- **值得看**：把数字编码智能体那套"显式状态 + 可改流程 + 反馈修正"搬到物理世界，并给出从工具到权重的自进化路线图。

### 4. 递归 Harness 蒸馏：把干预经验攒成跨智能体手册

**Recursive Harness Distillation across Agents for Robot Manipulation**
Seoul National University ｜ 🔥 HF 40 赞 ｜ [arXiv:2609.33378](https://arxiv.org/abs/2609.33378)

- **问题**：VLA 策略执行时若需诊断失败再调整行为往往力不从心，而强智能体摸索出的有效干预用完就丢。
- **做法**：强智能体把交互经验蒸馏成一本 playbook 交给轻量智能体，再用后者的执行反馈递归打磨这本手册；不更新任何模型参数即可在新任务实例上复用。
- **效果**：真机操作成功率从 37.3% 提到 64.0%；SimplerEnv Bridge 上带手册的轻量智能体达 66.7%（GR00T 基线 41.7%），同一本手册也让强智能体提升到 79.2%。
- **值得看**：提供了一条"经验资产化"的低成本路径——手册可读、可跨模型搬运，适合算力受限又想持续积累的团队。

### 5. OmniEcho：让具身智能体听得出方向

**OmniEcho: Spatial Audio Understanding for Embodied Agents**
PKU-VaLuE-Lab ｜ 🔥 HF 35 赞 ｜ 💻 [代码](https://github.com/PKU-VaLuE-Lab/OmniEcho) ｜ [arXiv:2609.23407](https://arxiv.org/abs/2609.23407)

- **问题**：人能轻松定位声源方向并与视觉结合推理，具身智能体却做不到，且该能力如何评测、如何建模都还没谱。
- **做法**：发布 OmniEchoBench（197 个真实空间音视频场景、2972 组问答、900 条带一阶 Ambisonics 音频的导航样本，取自 30 个真实环境），配一条保持几何一致性的可控空间音频渲染管线；模型侧提出带 FOA 空间编码器与预训练语义音频通路的 OmniEcho。
- **效果**：空间音视频感知达到 SOTA；声音引导导航的表现已接近传统视觉语言导航水平。
- **值得看**：补上了具身感知里长期缺位的空间听觉一环；也坦白指出细粒度定位与距离估计仍是硬骨头。

### 6. TERRA：让肌肉驱动的仿生运动走下平地

**TERRA: Terrain-Aware Reconstruction, Retargeting and Control for Musculoskeletal Locomotion**
Mathis Group @ EPFL ｜ 🔥 HF 32 赞 ｜ 💻 [代码](https://github.com/amathislab/terra) ｜ [arXiv:2609.38653](https://arxiv.org/abs/2609.38653)

- **问题**：肌骨模型 + 强化学习已能复现复杂人体动作，但基本只限平地——动作数据集很少配套地形几何，地形交互也难重定向到复杂肌骨身体。
- **做法**：端到端管线，仅凭运动学轨迹，结合地形先验、估计接触点与"负自由空间"证据反推出支撑几何；重定向阶段同时顾及解剖、肌腱连续性与接触约束。
- **效果**：用五个数据集生成的动作-地形配对，在 9.4 小时多样运动数据上训出单一肌肉驱动控制策略；重建、重定向与留出跟踪三类基准上地形精度提升、解剖与交互违例大幅减少，所支持地形族的完成率为观测最高。
- **值得看**：给"无场景动捕数据 → 非平整地形运动控制"铺了一条可用通路，对仿生运动与神经力学方向尤其实用。

### 7. 系统评测 GPT-6 Astra 当具身策略能走多远

**Systematically Exploring the Capabilities of GPT-6 Astra as Embodied Policies**
Galbot ｜ 🔥 HF 28 赞 ｜ 💻 [代码](https://github.com/anonymous-report-421/GPT-as-Policy) ｜ [arXiv:2609.38537](https://arxiv.org/abs/2609.38537)

- **问题**：Astra 能直接吐出数值化机器人动作，角色已超出高层规划，但它究竟能否充当通用具身策略，缺少系统答案。
- **做法**：横跨六大领域评测直接控制、与已训策略协作、以及反馈驱动的适应三种模式，覆盖夹爪操作、灵巧手、移动操作、导航、运动控制与人形 loco-manipulation。
- **效果**：混合控制在 RoboDojo 子集 48%、DexJoCo 十次试验 50%、RoboCasa365 38.7%；导航最强，RxR 指令跟随 92%、HM3D 物体搜索 82%；运动控制则不可靠，单个障碍赛道五次连续尝试全部未达目标。延迟是硬约束：30 秒运动控制需 250 次模型调用、每次平均 39.86 秒且推理期间物理暂停。
- **值得看**：把"任务决策有用"和"物理控制可靠"之间的鸿沟量化了，顺带给出的 token 与延迟账单，是评估大模型直控方案落地性的少见实测数据。

### 8. Tactile-JEPA：按传感器拓扑做自监督的电子皮肤表征

**Tactile-JEPA: Topology-Aware Self-Supervised Representation Learning for Distributed Tactile Sensors**
🔥 HF 22 赞 ｜ 💻 [代码](https://github.com/E-Kovtun/tactile) ｜ [arXiv:2609.24385](https://arxiv.org/abs/2609.24385)

- **问题**：视觉编码器早有预训练范式，触觉编码器却多从原始噪声信号从零训起；已有自监督方法又集中在视觉式触觉传感器，分布式电子皮肤的稀疏、不规则布点被忽略。
- **做法**：借传感器连通图引导空间掩码，从未遮挡部分预测被遮挡感知单元的嵌入；并用双尺度掩码同时抓局部接触细节与整体触觉面状态。
- **效果**：跨磁式与压阻式传感器、不同本体、单/双传感器配置的三个数据集上，力估计误差降 6.3%、手内姿态误差降 20.8%，策略学习等下游任务也普遍受益。
- **值得看**：论证了触觉这件事值不值，很大程度取决于编码器预训练质量——做接触密集操作前先看一眼编码器怎么来的。

### 9. CrossBFM：把人形机器人的潜在行为空间蒸馏成跨本体通用资产

**CrossBFM: Distilling a Shared Latent Behavior Space Across Humanoid Embodiments**
🔥 HF 21 赞 ｜ [arXiv:2609.38087](https://arxiv.org/abs/2609.38087)

- **问题**：行为基座模型的可提示潜在空间好用，但 Forward-Backward 表征单台机器人就要数百 GPU 小时，换一台又得到一个互不相通的新空间。
- **做法**：把潜在空间本身当作可迁移资产，用不含任何机器人专属参数的统一编码器同时蒸馏所有训练本体，再以常规 PPO 训练潜变量条件跟踪器输出全身控制。
- **效果**：编码器蒸馏不到 1 GPU 小时、跟踪器再 10 小时；三台人形上动作跟踪、姿态到达、奖励优化三种提示模式全部可迁移，41 个奖励提示全部可优化；只用四分之一动作语料训编码器仅损失 5% 跟踪性能，对形态相近的未见机器人可恢复 89% 性能，真机亦验证。
- **值得看**：把行为基座模型的训练成本压掉两个数量级，并让"换台机器人"从重训变成复用——对多本体机队部署意义直接。

### 10. REALM：会实时给反应的具身倾听者

**REALM: A Coarse-to-Fine Generative Framework for Embodied Reactive Listening**
Macquarie University ｜ 🔥 HF 20 赞 ｜ 💻 [代码](https://github.com/lipzh5/REALM) ｜ [arXiv:2609.33095](https://arxiv.org/abs/2609.33095)

- **问题**：具身对话 AI 要生成有反应的倾听者面部动作，难点在于既要对说话者线索的时序（常带延迟）作出回应并与自身动作保持连贯，又要兼顾难以确定性预测的短暂表情与眨眼。
- **做法**：由"反应式门控说话者-倾听者融合"模块以延迟中心的注意力先验与自适应门控把倾听者动作历史与说话者音频结合；粗解码器先给基础动作轨迹，再在表情子空间叠加音频条件的随机残差。
- **效果**：ViCo 与 L2L 上多项动作质量指标优于所测基线；另有延迟敏感性、门控行为与眨眼动态分析，并在 Ameca 人形机器人上部署，配主观用户研究验证。
- **值得看**：人机交互里"听的那一方"长期被忽视，这篇把它当成可建模、可上真机的问题，粗到细 + 随机残差的分工也值得借鉴。

---

## 六、智能眼镜 / 可穿戴 / 第一人称视觉

本周没有真正以智能眼镜硬件或整机系统为主题的论文，这一批集中在第一人称视觉、手势与视线估计、XR 交互和可穿戴感知这几条更偏研究侧的线上。该方向公开热度数据极少，十篇里只有少数几篇拿到社区投票，其余均未测得，因此排序主要依据主题相关性而非热度。

### 1. APM-Bench：跨会话持久记忆的第一人称视频助手评测集

**APM-Bench: Benchmarking Cross-session Persistent Memory for Egocentric Streaming Video Assistants**
Shanghai Jiao Tong University ｜ 🔥 HF 36 赞 ｜ 💻 [代码](https://github.com/Jianguo-Huang11/APM-Bench) ｜ [arXiv:2609.37559](https://arxiv.org/abs/2609.37559)

- **问题**：现有流式视频评测只看单段连续视频，而真实佩戴场景是断续发生的，记忆必须跨中断留存。
- **做法**：把交互重构成多会话生活轨迹，549 个会话、104 条轨迹、2719 个候选，含客观与开放题，并考察模型是否承认证据不足。
- **效果**：现有方法普遍卡在效用—延迟—存储的三角取舍上，长期回忆、低开销与主动提示难以兼得。
- **值得看**：给"随身助手的记忆"定了可比的靶子，做长期陪伴型助手可直接拿来对标。

### 2. InfiniHand：从第一人称视频流式还原世界坐标系下的手部动作

**InfiniHand: Streaming World-Space Hand Motion Estimation from Egocentric Video**
Shanghai AI Laboratory ｜ 🔥 HF 9 赞 ｜ 💻 [代码](https://github.com/infinihand/InfiniHand) ｜ [arXiv:2609.35743](https://arxiv.org/abs/2609.35743)

- **问题**：手姿估计器串 SLAM 的级联管线误差累积、算力开销大，世界坐标下漂移严重。
- **做法**：端到端流式前馈框架，直接从未标定视频联合输出 MANO 参数、相机轨迹与手部位置，持久时空记忆与手部特征耦合，两阶段训练，预训练语料约 5000 小时。
- **效果**：ARCTIC PA-p 比 ViDiHand 降 21.4%，野外视频泛化良好，11.19 FPS 为 HaWoR 两倍以上。
- **值得看**：眼镜端手势输入要的正是"单路视频、实时、不漂"，这是一条干净的技术路径。

### 3. MemLife：把上百小时第一人称录像整理成可检索的生活记忆

**MemLife: Curating and Reasoning over Long-Term Egocentric Video Memories**
Meta ｜ 🔥 HF 2 赞 ｜ [arXiv:2609.40195](https://arxiv.org/abs/2609.40195)

- **问题**：视频史长到数月数年后逐查重算不可行，而压缩成文本的记忆常丢证据或检索不中。
- **做法**：构建以实体为锚的第一人称文字情节，配时间索引的智能体阅读器；再用强化学习框架 MemOpt 优化记忆写入者，让记忆忠实、信息足、好检索。
- **效果**：免训练且查询时不读原视频，四个长程基准上超最强免训练基线 4.6–12.0%，MemOpt 再提升 2.7–5.0%。
- **值得看**：记忆"写得好"比"存得多"更关键，这个思路对任何长期个人化助手都通用。

### 4. EyeTAG：把视线轨迹变成显式变量的注视估计

**EyeTAG: Eye Trajectory-Aware Gaze Estimation**
热度未测得 ｜ 💻 [代码](https://github.com/peter8366/EyeTAG) ｜ [arXiv:2610.00922](https://arxiv.org/abs/2610.00922)

- **问题**：单帧方法逐帧独立预测导致抖动，多帧方法把运动隐式埋在外观特征里，轨迹从不是显式变量。
- **做法**：因果多帧框架，对自身近期预测做差分，把一阶视线先验作为紧凑运动 token 回灌；差分在视线空间平移不变，运动信息因此与个体偏置解耦。
- **效果**：Gaze360 平均角误差降约 1.0°，EVE 上 2.56° 与最强基线 2.58° 持平；消融显示是差分形式而非单纯时序上下文消除了扫视系统偏差。
- **值得看**：个体无关的运动表示是个漂亮的小技巧，视线驱动交互要落地先得消抖。

### 5. ESTHER：野外场景下的第一人称双目手部重建

**ESTHER: Egocentric Stereo Hand Estimation and Reconstruction in the Wild**
热度未测得 ｜ [arXiv:2609.34817](https://arxiv.org/abs/2609.34817)

- **问题**：第一人称双目本是 AR/VR 与机器人最自然的感知接口，却既无端到端模型也无野外基准。
- **做法**：针对可穿戴双目设计立体几何、时序推理与输出表示，用标定流水线产伪标签训练，并据此组建 ESTHER3D（野外大规模伪标注训练集 + 动捕真值测试集）。
- **效果**：精度达 SOTA，跨域泛化更好，对缺视角、掉帧、强光照与运动模糊稳健；换双目装置只需少量微调，退化为单目仍保住真实尺度。
- **值得看**：双目引导让模型学会把视觉尺度绑到真实深度，这个"能力留存"现象比指标本身更有启发。

### 6. 单目看不出问题：VR 立体视下的 3D 高斯泼溅质量研究

**Beyond Monoscopic Viewing: A Study on 3D Gaussian Splatting Quality in VR**
热度未测得 ｜ [arXiv:2609.38525](https://arxiv.org/abs/2609.38525)

- **问题**：3DGS 在稀疏采集下常出现漂浮物与错位结构，而标准图像指标和单目观看都看不出这些局部瑕疵。
- **做法**：把重建结果立体渲染进头显按真实观看方式评估，对比纯 SfM 初始化与 SfM 叠加 VGGT 稠密初始化，其余训练组件固定，再做用户偏好研究。
- **效果**：单目下偏好一致性更好的重建仅 58.4%，立体观看升至 78.2% 且全体受试一致，而 PSNR/SSIM/LPIPS 及立体感知指标差异都很小。
- **值得看**：评测媒介本身会掩盖缺陷，做头显内容的人该把立体评估当必选项。

### 7. VocalEyes：靠自我介绍认人的 AR 字幕

**VocalEyes: Speaker-Aware Augmented Reality Captioning through In-Conversation Registration**
热度未测得 ｜ [arXiv:2609.32983](https://arxiv.org/abs/2609.32983)

- **问题**：AR 字幕让语音可读，却把话和说话人剥离；传统声纹分离只给匿名簇，说话人识别又要求会前注册。
- **做法**：从自然的自我介绍中现场建立带名字的声纹档案，界面同时呈现带归属的字幕、固定档案卡和标示正在发言者面部的视觉提示。
- **效果**：20 名听力正常受试的被试内实验中，说话人识别准确率 88.0%，受试追踪说话人的准确率从纯字幕 47.2% 升至 87.3%，主观负荷也更低。
- **值得看**："对话中注册"这个设计绕开了部署门槛，是眼镜字幕很现实的一种形态。

### 8. 「黑镜？」：公众如何理解 AI 生活记录设备

**"Black Mirror?": Public Sensemaking of AI-Powered Lifelogging**
热度未测得 ｜ [arXiv:2609.34950](https://arxiv.org/abs/2609.34950)

- **问题**：AI 生活记录类可穿戴刚进入市场，公众对这种"可搜索记忆档案"的社会与道德判断尚无系统梳理。
- **做法**：以 Looki L1 为切口，分析中英文社交媒体 5053 条评论，结合主题聚类与归纳式主题分析。
- **效果**：普遍出现反乌托邦监控想象、隐私无力感与旁人顾虑；英文讨论更偏人际权力、取证用途与被黑风险，中文讨论更偏劳动压榨、治理监控与技术必然性。
- **值得看**：产品还没普及，舆论的阻力曲线已经成型，做硬件的得先读懂这份抵触从何而来。

### 9. Exo2EgoHOI：把第三人称操作视频翻成第一人称视角

**Exo2EgoHOI: Hand-Object-Interaction Aware Exocentric-to-Egocentric Video Generation**
热度未测得 ｜ [arXiv:2609.38615](https://arxiv.org/abs/2609.38615)

- **问题**：具身智能需要大量第一人称操作视频但采集昂贵，而视角转换生成常在大幅换视角时丢掉手物交互细节。
- **做法**：构建融合场景几何、关节手渲染与稠密手物关系场的统一 4D 交互先验，经双分支残差适配器注入生成主干；再用解耦门控交叉注意力分别编码物体与背景参考，做物体中心锚定。
- **效果**：ARCTIC-HOI 上物体 mIoU 提升 32.3%，MPJPE 与 PA-MPJPE 分别降 34.7% 和 50.0%，视觉保真度保持竞争力。
- **值得看**：第一人称训练数据的供给问题，可能靠生成而非采集解决。

### 10. 一个传感器看全身：只用一只耳机 IMU 估计 3D 人体姿态

**One Sensor, Whole Body - 3D Body Pose from a Single Consumer Earbud IMU**
热度未测得 ｜ 💻 [代码](https://github.com/ZhilinGuo/one-sensor-whole-body) ｜ [arXiv:2609.34978](https://arxiv.org/abs/2609.34978)

- **问题**：消费级耳机早已在头部持续输出惯性数据，但单个头部 IMU 能还原多少全身姿态、加传感器是否真有用，并无定论。
- **做法**：搭建多模态采集管线同步四视角 RGB-D、AirPods 头部 IMU 与两只 Striv 鞋垫 IMU，用 SAM 3D Body 生成伪真值，构成涵盖步态、转身、日常与临床动作的 35 组基准，并改造 IMUPoser 与 MobilePoser 两族模型。
- **效果**：单头部 IMU 下肢姿态刚性 MPJPE 79.0 mm、单脚触地 macro-F1 0.809，因果变体在流式延迟下基本保住精度；加鞋垫 IMU 从未显著提升，四种模型-划分组合里有两种反而显著变差，根因是鞋垫朝向质量而非脚部位置。
- **值得看**：约束是传感器可靠性而不是数量，这个结论对多设备融合的产品设计是个冷水也是个省钱的方向。
