# AcademicPaperGrabber 设计方案

> 状态：**规划已定稿，等待开工确认**
> 日期：2026-10-01
> 参考项目：`/Users/xingxingliu/Projects/CluadeProjects/GitHubRepoGrabber`（沿用其「脚本做确定性抓取排序、agent 写文案」的分工）

---

## 1. 目标

每周自动抓取六个方向最近一周的热门论文，每个方向 10 篇，合并成**一份**周报，同时产出 Markdown 和网页，推到 GitHub 公开仓库并由 GitHub Pages 发布。

- 开发期工作目录：`/Users/xingxingliu/Projects/CluadeProjects/AcademicPaperGrabber`
- 上线后仓库位置：`/Users/xingxingliu/Projects/xxliu1996_githubrepos/AcademicPaperGrabber`
- 站点：`https://xxliu1996.github.io/AcademicPaperGrabber/`

---

## 2. 数据源：验证结果

三个候选源都在 2026-10-01 实测过，结论如下。

### 2.1 Hugging Face Papers ✅ 主来源

`GET https://huggingface.co/api/daily_papers?limit=100`

- 支持 `sort=trending`、`date=YYYY-MM-DD` 参数（实测有效）
- 返回字段：`paper.upvotes`、`paper.summary`（完整摘要）、`paper.id`（arXiv ID）、`paper.authors`、`paper.githubRepo`、`paper.githubStars`、`organization`、`projectPage`、`thumbnail`
- 实测 `limit=100` 覆盖约 16 天（2026-09-14 → 09-29），即**每周约 50 篇**
- 上票分布实测：最高 222、221、147、107、99…… 长尾大量 0–1 票

**这是全网唯一能拿到单篇论文真实热度数值的公开接口。** 但覆盖面严重偏科：绝大多数是 LLM / VLM / Agent，机器人和可穿戴方向基本不上榜。

### 2.2 arXiv API ✅ 覆盖来源

`GET https://export.arxiv.org/api/query`

- 必须用 **https**（http 实测返回空）
- 日期区间查询必须 URL 编码：`search_query=cat:cs.RO AND submittedDate:[202609240000 TO 202610010000]`
- 实测：cs.RO 过去 7 天 **681 篇**；cs.CL 总量 12 万+
- 返回 title / summary（摘要全文）/ authors / categories / published / comment
- 官方建议请求间隔 ~3 秒

覆盖面完全够，**但没有任何热度信号**——这是本项目最核心的技术约束，见 §4。

### 2.3 Papers with Code ❌ 不接

- `paperswithcode.com` 实测 **301 跳转到 `huggingface.co/papers/trending`**，原站已停止运营
- `paperswithcode.co`（.co 域名）是第三方仿站：标题 "Papers with Code — Trending research and open source"，纯 JS 渲染，`/api/*`、`/trending` 均 404，只有 sitemap.xml 可用
- 内容大概率是 HF 的二手转载，接它既增加脆弱性又不带来新信息

**决策：不接。** 同时探测过 alphaXiv，无公开 API（`api.alphaxiv.org` 404），同样放弃。

---

## 3. 主题划分

| slug | 标题 | arXiv 分类 | 收录数 |
|---|---|---|---|
| `llm` | 大语言模型 | cs.CL, cs.LG | 10 |
| `vlm` | 多模态 / 视觉语言 | cs.CV, cs.MM, cs.CL | 10 |
| `agent` | Agent | cs.AI, cs.MA, cs.SE | 10 |
| `deep-learning` | 其他深度学习 | cs.LG, cs.NE, stat.ML | 10 |
| `robotics` | 机器人与具身智能 | cs.RO | 10 |
| `wearable-xr` | 智能眼镜 / 可穿戴 / 第一人称视觉 | cs.HC, cs.CV, cs.MM | 10 |

### 关于「智能眼镜」口径（已确认：扩展）

严格意义的「智能眼镜」论文一周凑不出 10 篇。口径放宽到：egocentric vision（第一人称视觉）、AR/XR 交互、头显、always-on 助手、gaze / HCI、可穿戴感知。这样每周能稳定凑够 8–10 篇真正相关的。

### 跨主题去重

一篇论文**只进一份章节**。认领优先级（冷门主题先挑，否则会被 LLM/VLM 全部吸走）：

```
wearable-xr > robotics > agent > vlm > llm > deep-learning
```

所有口径（分类、关键词权重、门槛、pick 数）写在 `config/topics.json`，**调方向只改这个文件，不动 Python**。沿用 GitHubRepoGrabber 的约定。

---

## 4. 热度打分 —— 本项目最关键也最诚实的一节

### 打分公式

```
score = 3.0 * log1p(HF upvotes)      ← 实测热度，权重最高
      + 1.5 * log1p(GitHub stars)    ← 从摘要/comment 抽 github 链接，再查 GitHub API
      + keyword_score                ← 主题关键词加权匹配
      + bonus(有代码链接 / 有项目页)
```

GitHub 星数通过已有的 keychain `GITHUB_TOKEN` 流程获取（限额 5000/小时），只对进入候选池的前 N 篇做富化，省配额。

### 必须写明的限制

**arXiv 上每周数千篇论文中，绝大多数拿不到任何真实热度数据。** 关键词分只能保证「这篇属于这个主题」，不能证明「这篇火」。全网没有 arXiv 单篇的公开阅读量/下载量接口，这是数据本身的限制，不是实现偷懒。

应对措施（硬性要求，写进 slash command）：

1. 每篇**逐条标注热度来源**：`🔥 HF 222 赞` / `💻 1.2k★` / `热度未测得`
2. 「本周最值得读的 5 篇」**只从有实测热度（HF 上票或 GitHub 星）的条目里选**，绝不拿零信号论文冒充爆款
3. 无实测热度的条目，正文措辞不得出现「爆火」「刷屏」「本周最热」等暗示热度的词

这条和 GitHubRepoGrabber 里「`source: search` 的估算周增量不能说成实测值」是同一个原则。

---

## 5. 目录结构

```
AcademicPaperGrabber/
├── PLAN.md                      # 本文档
├── README.md
├── config/
│   └── topics.json              # 6 主题：arXiv 分类 / 关键词权重 / 门槛 / pick 数
├── scripts/
│   ├── fetch_papers.py          # 纯标准库：HF + arXiv → 打分 → raw/<theme>.json
│   ├── build_site.py            # 纯标准库：reports/ → docs/ 静态站 + feed.xml
│   └── run_weekly.sh            # launchd 入口
├── reports/
│   └── YYYY-MM-DD/
│       ├── raw/<theme>.json     # 候选池 + 打分明细，分主题存
│       ├── picks.json           # 主 agent 的选稿名单
│       └── report.md            # ★ 一份合并周报（最终产物）
├── docs/                        # GitHub Pages 发布目录，build_site.py 全量重建，不要手改
│   ├── index.html               # 最近三个月
│   ├── archive.html             # 全部历史
│   ├── r/<DATE>.html            # 每周一页
│   ├── feed.xml                 # RSS
│   ├── data/reports.json
│   └── assets/site.css
├── logs/
└── .claude/commands/papers-weekly.md
```

`raw/` 按主题分文件存，是为了让 6 个并行子 agent 各读各的那一份，避免把 60 篇摘要全灌进主上下文。

`docs/` 是**生成物**：`build_site.py` 每次先 `rmtree` 再重建，手改的东西下轮就没了。

---

## 6. 周报结构

一份合并周报，顶部 Top5 精选，然后 6 个章节。每篇**结构化四行**。

```markdown
# AI 论文周报（2026-09-28 – 2026-10-04）

<导语：本周这 60 篇里看到的真实趋势是什么。要有观点，别写「以下是本周热门论文」这种废话。>

---

## ⭐ 本周最值得读的 5 篇

<跨主题精选，只选有实测热度的，每篇一句话说清为什么是它>

---

## 一、大语言模型

### 1. 技能健身房：SkillGym

**SkillGym: Training Skill-Use Agents with Automatic Verifiable Environment Generation**
MBZUAI ｜ 🔥 HF 222 赞 ｜ 💻 1.2k★ ｜ [arXiv:2609.37539](https://arxiv.org/abs/2609.37539)

- **问题**：Agent 用 skill 已普及，但训练数据怎么造、怎么训没人管
- **做法**：爬全网 skill，筛出能离线复现的，builder-reviewer 管线生成 6.8k 可验证环境
- **效果**：9B SFT 模型在两个 benchmark 上超过未训练的 397B
- **值得看**：带可执行 verifier 的环境生成管线，可直接复用

### 2. ...

---

## 二、多模态 / 视觉语言
...
```

格式硬性要求（`build_site.py` 靠这个结构渲染，改格式网站就错）：

- H1 只有一行，紧跟的段落是导语
- 每篇必须是 `### <序号>. <中文译名>`，章节内连续编号
- 第二行加粗英文原题，第三行是「机构 ｜ 热度标记 ｜ arXiv 链接」
- 四条要点固定用 `问题 / 做法 / 效果 / 值得看` 这四个词开头
- 所有链接取自 raw.json，不手拼

---

## 7. 执行流程 `/papers-weekly`

| 步 | 动作 | 说明 |
|---|---|---|
| 1 | `fetch_papers.py` 跑 6 个主题 | 约 2–4 分钟；输出 `raw/<theme>.json` |
| 2 | 主 agent 读 6 份 raw，各挑 10 篇 | 写 `picks.json`，执行跨主题去重 |
| 3 | **6 个并行子 agent，各写一章** | 摘要已在 raw.json 里，**完全不需要 WebFetch** |
| 4 | 主 agent 写导语 + Top5，拼 `report.md` | |
| 5 | `build_site.py` 重建 `docs/` + `feed.xml` | 检查每周条目 count 不为 0 |
| 6 | `git commit && push` | Pages 自动更新 |
| 7 | 汇报 | 报告路径、各主题名单、站点地址 |

第 3 步是相对 GitHubRepoGrabber 的主要改进：那边子 agent 要去 WebFetch 二十多个 README，这边摘要在抓取阶段就随 API 一起拿到了，子 agent 只做「摘要 → 中文四行提炼」，更快更省。

**无条件重跑**：`reports/<DATE>/` 已存在也照样全部覆盖重做。定时任务无人值守，静默跳过会伪装成成功。

---

## 8. 上线与定时

- 跑通一次真实周报并人工验收后，整体迁到 `xxliu1996_githubrepos/AcademicPaperGrabber`
- `gh repo create xxliu1996/AcademicPaperGrabber --public`（gh 已登录 xxliu1996，keyring）
- 开启 Pages，发布目录 `docs/`，加 `.nojekyll`
- launchd：`com.xingxingliu.academicpapergrabber`，**周日 22:00**（错开 GitHubRepoGrabber 的周六 22:00，两个任务不抢 GitHub API 配额）
- `run_weekly.sh` 照抄 GitHubRepoGrabber 的成熟处理：显式 PATH、`USER`/`LOGNAME`（keychain 查 token 必需）、从 git credential 读 `GITHUB_TOKEN`、跑前 stash+pull、跑后校验产物**是否在本次运行中被重写**（只检查文件存在会让重跑伪装成功）、osascript 通知

**路径约定**：开发期脚本**不写死绝对路径**，用和现有命令一样的 ROOT 探测，这样从 CluadeProjects 迁到 xxliu1996_githubrepos 时不用改代码。

---

## 9. 衍生产物

| 产物 | 状态 |
|---|---|
| `report.md` + 网站 | ✅ 主线 |
| 一页纸「本周最值得读的 5 篇」 | ✅ 做，放报告顶部 + 网站首屏 |
| RSS `feed.xml` | ✅ 做，零依赖 |
| 邮件推送 | ⚠️ 见遗留项 |
| 小红书文案 | ❌ 先不做（raw.json 都在，以后随时加） |

---

## 10. 遗留项（需你拍板）

1. **邮件推送**需要 SMTP 凭据。计划走 Gmail 应用专用密码存 keychain（和 `GITHUB_TOKEN` 同一路子），`run_weekly.sh` 里留好开关，密码由你自己塞进 keychain 后生效——**我不碰你的密码**。确认后再实现。
2. **仓库名** `AcademicPaperGrabber`，决定 Pages 网址。无异议即按此创建。

---

## 11. 分阶段实施

| 阶段 | 内容 | 验收 |
|---|---|---|
| 一 | `config/topics.json` + `fetch_papers.py` | 跑一次真实抓取，人工看 6 份 raw.json 的 top10 是否「确实属于该主题 + 确实值得读」，不合格就调权重 |
| 二 | `.claude/commands/papers-weekly.md` + 生成一份真实周报 | 人工读 `report.md`，检查四行提炼是否准确、热度标注是否诚实 |
| 三 | `build_site.py` + 本地预览 | `open docs/index.html`，6 主题筛选、归档、RSS 都正常 |
| 四 | 迁仓库、建 public repo、开 Pages、装 launchd | 手动触发一次 launchd 跑通，站点线上可访问 |

第一阶段的验收最关键：**打分效果不行的话，后面做得再漂亮都是在给垃圾选题排版。**
