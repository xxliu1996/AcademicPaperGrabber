# AcademicPaperGrabber

每周抓一次最近七天的热门论文，**六个方向各 10 篇，合成一份周报**，再编译成一个 GitHub Pages 静态站点。

| 主题 slug | 章节 | 收录 |
|---|---|---|
| `llm` | 大语言模型 | 10 |
| `vlm` | 多模态 / 视觉语言 | 10 |
| `agent` | Agent | 10 |
| `deep-learning` | 其他深度学习 | 10 |
| `robotics` | 机器人与具身智能 | 10 |
| `wearable-xr` | 智能眼镜 / 可穿戴 / 第一人称视觉 | 10 |

站点：<https://xxliu1996.github.io/AcademicPaperGrabber/> —— 首页是最近三个月，`archive.html` 是全部历史，`feed.xml` 是 RSS。报告页里可以按章节筛选。

## 设计

沿用 `GitHubRepoGrabber` 的分工：**脚本只负责确定性的抓取、打分和排序，输出 JSON；文字由 agent 写。** 抓取逻辑可测试可复现，文案质量交给模型。

```
AcademicPaperGrabber/
├── config/
│   └── topics.json         # 六个主题的 arXiv 分类 / 关键词权重 / 门槛 —— 调选题方向改这里，不用改代码
├── scripts/
│   ├── fetch_papers.py     # 纯标准库，一次跑完六个主题，分主题输出 JSON
│   ├── build_site.py       # 纯标准库，reports/ → docs/ 静态站 + RSS
│   ├── send_email.py       # 可选的邮件推送，凭据从 keychain 读
│   └── run_weekly.sh       # launchd 入口
├── reports/
│   └── YYYY-MM-DD/
│       ├── raw/<theme>.json  # 脚本原始输出（含打分明细），一并提交，便于复现
│       ├── picks.json        # 选稿名单
│       └── report.md         # 周报正文（build_site.py 靠它的结构渲染，格式别乱改）
└── docs/                   # GitHub Pages 发布目录，由 build_site.py 全量重建，不要手改
```

`docs/` 是**生成物**：`build_site.py` 每次跑都会先 `rmtree` 再重建，手动改的东西下一轮就没了。

## 用法

一条命令跑完整个流程：

```
/papers-weekly              # 用今天的日期
/papers-weekly 2026-10-01   # 指定日期
```

只想看抓到什么、不生成正文：

```bash
python3 scripts/fetch_papers.py --list-themes
python3 scripts/fetch_papers.py --theme robotics --no-github --emit 10 | python3 -m json.tool | head -60
```

常用参数：`--outdir <目录>`（分主题落盘，周报流程用这个）、`--theme <slug>`（只跑一个主题，调试用）、`--week-of YYYY-MM-DD`（指定周锚点）、`--emit N`（每主题输出条数）、`--max-results N`（每条 arXiv 查询最多取多少）、`--no-github`（跳过星数查询）、`--quiet-stdout`（不往 stdout 刷 JSON）。不传时一律用 `topics.json` 里的值。

只重建网站（改了样式或删了某篇报告之后）：

```bash
python3 scripts/build_site.py && open docs/index.html
```

## 数据来源

### 1. Hugging Face Papers —— 主来源，唯一有真实热度数值的地方

`https://huggingface.co/api/daily_papers`，按日期逐天拉取并用 `p=` 分页。返回 `upvotes`（社区投票数）、完整摘要、作者、机构、以及提交者标注的 GitHub 仓库和星数。

一周大约 340 篇。**注意 `limit` 被服务端限制在 100**，单日经常超过 100 篇（实测 2026-09-29 有 109 篇），所以必须分页，不能图省事只拉一页。

### 2. arXiv API —— 覆盖来源，没有任何热度信号

`https://export.arxiv.org/api/query`，按 `(cat:A OR cat:B) AND (abs:"词1" OR abs:"词2") AND submittedDate:[...]` 逐主题查询。cs.RO 一周就有 680 多篇，覆盖面完全够。

必须用 **https**（http 返回空），日期区间的方括号要 URL 编码，官方要求请求间隔 3 秒 —— 所以一次完整抓取要四到七分钟。

### 不用的源

- **Papers with Code 已经停运**：`paperswithcode.com` 现在 301 跳到 `huggingface.co/papers/trending`。
- `paperswithcode.co`（.co 域名）是第三方仿站，纯 JS 渲染、无 API，数据大概率是 HF 的二手转载，接它只增加脆弱性。
- **alphaXiv** 没有公开 API。

## 热度打分

```
score = 3.0 * log1p(HF 上票数)        ← 实测热度
      + 1.2 * log1p(GitHub 星数)      ← 仅当确认是论文自己的仓库
      + 0.25 * (关键词分 + 分类分)     ← 只作兜底排序
      + 有代码 / 有项目页 bonus
```

### 这里有三个坑，都是实测踩出来的

**一、关键词分不能参与章节内排序。** 同一章节里的论文都已经是主题相关的，让关键词分全权重参与排序会把真·高票论文压下去 —— 第一次全量跑出现过 271 赞的论文排在 90 赞之后。所以归属判断用全权重，章节内排序只按 0.25 折算。

**二、从摘要里抽的 GitHub 链接经常是别人的仓库。** 实测三例：一篇稀疏注意力论文挂上了它要打败的基线仓库（765★）、一篇视频生成论文挂上了它所基于的底座模型（2652★）、一篇音乐模型挂上了自己的上一代（10694★）。这些星数衡量的是别人的热度，算进来就是伪造数据。

所以：HF 提交者标注的仓库无条件采信；摘要里抽到的必须通过「仓库名包含论文名」校验，否则**只保留链接、不计星数、不查星数**。宁可少算真实热度，也不能多算不属于它的。

**三、arXiv 上绝大多数论文拿不到任何热度数据。** 全网没有 arXiv 单篇的公开阅读量接口。所以每篇都带 `heat_source` 字段（`hf` / `github` / `none`），写周报时**必须逐篇如实标注**，`none` 的一个字都不能提热度，更不准进「本周最值得读的 5 篇」。

实测一周的覆盖情况（2026-10-01）：

| 主题 | 候选 | 输出 top25 中有实测热度 |
|---|---|---|
| agent | 429 | 25 / 25 |
| llm | 456 | 24 / 25 |
| vlm | 290 | 22 / 25 |
| robotics | 309 | 14 / 25 |
| deep-learning | 214 | 13 / 25 |
| wearable-xr | 20 | 5 / 20 |

主流三个方向几乎全有实测热度；机器人和可穿戴方向要诚实承认排序主要靠主题相关性。

## 主题归属

一篇论文**只进一个章节**。归属 = `关键词分 + 分类分 + claim_bonus` 取最大值，打平时按 `claim_order`（冷门主题先认领，否则跨领域论文会被 LLM/VLM 全吸走）。

两条入选通道：关键词分到 `min_score`，或者「关键词分 + 分类分」到 `min_affinity`（兜住摘要用词冷僻、但 arXiv 分类已经把方向说清楚的论文）。

两条都没进、但 HF 上票 ≥ 20 的，按 **arXiv 分类**路由到最贴近的主题，分类也看不出来就丢进 `deep-learning`。
早期版本这里按 `claim_bonus` 路由，结果把一篇稀疏注意力论文塞进了智能眼镜章节 —— 分类是论文自己声明的领域，才是这里唯一靠得住的依据。

## 定时

launchd，**每周日 22:00**（错开 `GitHubRepoGrabber` 的周六 22:00，两个任务不抢 GitHub API 配额）。

```bash
launchctl load -w ~/Library/LaunchAgents/com.xingxingliu.academicpapergrabber.plist
launchctl start com.xingxingliu.academicpapergrabber     # 手动触发一次
tail -f logs/$(date +%F).log
```

`run_weekly.sh` 会校验 `report.md` **是不是本次运行写的**（只检查文件存在会让重跑伪装成功）、论文数是否够、以及网站是否重建成功，任一不满足就退出非零并弹失败通知。

### 邮件推送（可选，默认关）

把 Gmail 应用专用密码放进 keychain 后自动生效：

```bash
security add-generic-password -a "$USER" -s AcademicPaperGrabber-smtp \
         -w '<myaccount.google.com/apppasswords 生成的 16 位>'
```

密码只在运行时从 keychain 读进环境变量，不落盘、不进日志。没有这个 keychain 条目时直接跳过，不影响周报生成。普通 Google 密码不行，Gmail SMTP 只认应用专用密码。
