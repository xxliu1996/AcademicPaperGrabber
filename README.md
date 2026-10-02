# AcademicPaperGrabber

每周抓一次最近七天的热门 AI 论文，**六个方向各 10 篇，合成一份中文周报**，同时产出 Markdown、单文件 HTML 和一个 GitHub Pages 静态站点。

| 主题 slug | 章节 | 收录 |
|---|---|---|
| `llm` | 大语言模型 | 10 |
| `vlm` | 多模态 / 视觉语言 | 10 |
| `agent` | Agent | 10 |
| `deep-learning` | 其他深度学习 | 10 |
| `robotics` | 机器人与具身智能 | 10 |
| `wearable-xr` | 智能眼镜 / 可穿戴 / 第一人称视觉 | 10 |

抓取、打分、建站是纯 Python 标准库脚本，**不需要 venv、不需要装任何依赖**。正文由 Claude Code 写（见[用法](#用法)），所以抓取逻辑可测试可复现，文案质量交给模型。

## 快速开始

```bash
git clone https://github.com/<你的账号>/AcademicPaperGrabber.git
cd AcademicPaperGrabber

# 只抓取，看看选出来什么（约 4–7 分钟，arXiv 要求请求间隔 3 秒）
python3 scripts/fetch_papers.py --outdir reports/$(date +%F)/raw --quiet-stdout

# 想快点看效果：只跑一个主题、跳过星数查询
python3 scripts/fetch_papers.py --theme robotics --no-github --emit 10 | python3 -m json.tool | head -40
```

抓完之后用 Claude Code 生成正文和网站（见下）。只重建网站：

```bash
python3 scripts/build_site.py && open docs/index.html
```

**零配置**：站点地址从 `git remote get-url origin` 自动推导（GitHub Pages 的地址就是 `https://<owner>.github.io/<repo>`），所以 fork 之后不用改任何文件。想自定义就看[配置](#配置)。

## 用法

整个流程封装成一个 Claude Code 斜杠命令，定义在 [`.claude/commands/papers-weekly.md`](.claude/commands/papers-weekly.md)：

```
/papers-weekly              # 用今天的日期
/papers-weekly 2026-10-01   # 指定日期
```

它做八件事：抓数据 → 每主题选 10 篇 → **六个并行子 agent 各写一章** → 拼成 `report.md` → 机器校验 → 建站 → 提交 → 汇报。

第三步是关键设计：论文摘要在抓取阶段就随 API 一起拿到了，写正文的子 agent 直接读本地 JSON，**全程不联网**，比去抓网页快得多也省得多。

## 目录结构

```
AcademicPaperGrabber/
├── config/
│   └── topics.json         # 六个主题的 arXiv 分类 / 关键词权重 / 打分权重 —— 调方向改这里，不动代码
├── scripts/
│   ├── fetch_papers.py     # 抓取 + 打分 + 主题归属，输出分主题 JSON
│   ├── check_report.py     # 机器校验正文与数据是否一致（--fix 可自动修元信息行）
│   ├── build_site.py       # reports/ → docs/ 静态站 + RSS + 单文件报告
│   ├── send_email.py       # 可选的邮件推送，凭据从 keychain 读
│   ├── siteconf.py         # 配置解析（站点地址从 git remote 推导）
│   ├── install_schedule.sh # 生成并装载 launchd 定时任务
│   └── run_weekly.sh       # 定时任务入口
├── reports/
│   └── YYYY-MM-DD/
│       ├── raw/<theme>.json  # 脚本原始输出（含打分明细），一并提交便于复现
│       ├── picks.json        # 选稿名单
│       ├── report.md         # 周报正文
│       └── report.html       # 同一份报告的自带样式单文件版
└── docs/                   # GitHub Pages 发布目录，由 build_site.py 全量重建，不要手改
```

`docs/` 是**生成物**：`build_site.py` 每次跑都会先 `rmtree` 再重建，手改的东西下一轮就没了。

## 数据来源

### 1. Hugging Face Papers —— 主来源，唯一有真实热度数值的地方

`https://huggingface.co/api/daily_papers`，按日期逐天拉取并用 `p=` 分页。返回 `upvotes`（社区投票数）、完整摘要、作者、机构，以及提交者标注的 GitHub 仓库。

一周大约 340 篇。**注意 `limit` 被服务端限制在 100**，单日经常超过 100 篇（实测某天 109 篇），所以必须分页，不能图省事只拉一页。

### 2. arXiv API —— 覆盖来源，没有任何热度信号

`https://export.arxiv.org/api/query`，按 `(cat:A OR cat:B) AND (abs:"词1" OR abs:"词2") AND submittedDate:[...]` 逐主题查询。cs.RO 一周就有 680 多篇，覆盖面完全够。

必须用 **https**（http 返回空），日期区间的方括号要 URL 编码，官方要求请求间隔 3 秒。**arXiv 会按 IP 硬限流**：短时间内重复跑全量抓取会收到 429 且不带 `Retry-After`，可能持续几十分钟。脚本的退避是 30/60/120/240 秒阶梯，调参时请用 `--rescore` 而不是重抓。

### 不用的源

- **Papers with Code 已经停运**：`paperswithcode.com` 现在 301 跳到 `huggingface.co/papers/trending`。
- `paperswithcode.co`（.co 域名）是第三方仿站，纯 JS 渲染、无 API，数据大概率是 HF 的二手转载。
- **alphaXiv** 没有公开 API。

## 热度打分

```
score = 1.0 * 上票数^0.5                 ← 实测热度，主导排序
      + min(1.2 * log1p(星数), 6.0)      ← 仅当确认是论文自己的仓库，且有上限
      + 0.25 * (关键词分 + 分类分)        ← 只作兜底排序
      + 有代码 / 有项目页 bonus
```

### 四个坑，都是实跑踩出来的，改权重前先读

**一、关键词分不能全权重参与章节内排序。** 同一章节里的论文都已经是主题相关的，让关键词分主导排序会把真·高票论文压下去——实测出现过 271 赞排在 90 赞之后。所以归属判断用全权重，章节内排序只按 0.25 折算。

**二、上票不能用 log 压缩。** `log1p` 下 271 赞只比 90 赞高 3.4 分，还不如"有代码 + 有项目页"的加分，于是关注度高三倍的论文反而排在后面。改成 `上票^0.5`。

**三、GitHub 星数经常不是这篇论文的。** 从摘要里抽的链接常指向被引用的仓库，而**HF 提交者标注的链接一样不可靠**。实测三例：一篇稀疏注意力论文挂上了它要打败的基线（765★）、一篇视频生成论文挂上了它所基于的底座模型（2652★）、一篇音乐模型挂上了自己的上一代（10694★）。

`LongLive-Plug` 指向 `LongLive` 这种情况，任何机械规则都分不出真假。所以：**报告里一概不印星数**，只印「有代码」+ 链接，读者自己点进去看；星数仅作内部排序信号，且必须通过「仓库名包含论文名」校验、并有 6.0 分上限。宁可少算真实热度，也不能把别人的数字说成这篇的。

**四、arXiv 上绝大多数论文拿不到任何热度数据。** 全网没有 arXiv 单篇的公开阅读量接口。所以每篇都带 `heat_source`（`hf` / `none`）和脚本预计算的 `heat_label`，正文**必须逐篇如实标注**，`none` 的一个字都不能提热度，更不准进「本周最值得读的 5 篇」。

热度标签由脚本算、不让模型拼，`check_report.py` 还会逐篇核对——这是整个项目最容易出问题的地方，所以用机器兜住。

参考：某一周（六主题各 25 篇候选）的实测覆盖率是 llm/vlm/agent 各 25/25，机器人 24/25，其他深度学习 15/25，可穿戴 4/25。主流方向几乎全有实测热度；可穿戴方向要诚实承认排序主要靠主题相关性。

## 主题归属

一篇论文**只进一个章节**。归属 = `关键词分 + 分类分 + claim_bonus` 取最大值，打平时按 `claim_order`（冷门主题先认领，否则跨领域论文会被 LLM/VLM 全吸走）。

两条入选通道：关键词分到 `min_score`，或者「关键词分 + 分类分」到 `min_affinity`（兜住摘要用词冷僻、但 arXiv 分类已把方向说清楚的论文）。

两条都没进、但 HF 上票 ≥ 20 的，按 **arXiv 分类**路由到最贴近的主题，分类也看不出来就丢进 `fallback_theme`。早期版本这里按 `claim_bonus` 路由，结果把一篇稀疏注意力论文塞进了智能眼镜章节——分类是论文自己声明的领域，才是这里唯一靠得住的依据。

## 常用命令

```bash
python3 scripts/fetch_papers.py --list-themes            # 看配了哪些主题
python3 scripts/fetch_papers.py --outdir <目录>           # 跑全部六主题并落盘
python3 scripts/fetch_papers.py --theme llm --no-github  # 只跑一个主题，跳过星数查询
python3 scripts/fetch_papers.py --no-arxiv --outdir <目录> # arXiv 挂了/被限流时的降级模式
python3 scripts/fetch_papers.py --rescore <目录>          # 改完权重重新打分，不重新抓取
python3 scripts/check_report.py <日期> --fix              # 校验正文，顺手修元信息行
python3 scripts/build_site.py                            # 重建 docs/ 和单文件报告
python3 scripts/siteconf.py                              # 打印当前 checkout 解析出的配置
```

`fetch_papers.py` 其他参数：`--week-of YYYY-MM-DD` 指定周锚点、`--emit N` 每主题输出条数、`--max-results N` 每条 arXiv 查询上限、`--quiet-stdout` 不往 stdout 刷 JSON。不传时一律用 `config/topics.json` 里的值。

退出码 `2` 表示有主题候选数低于 `min_papers`——这不算整体失败，那个主题少写几篇或整章跳过即可。

## 定时运行

```bash
./scripts/install_schedule.sh                      # 默认周日 22:00
./scripts/install_schedule.sh --day 6 --hour 23    # launchd 编号：0=周日 … 6=周六
./scripts/install_schedule.sh --run                # 立刻手动触发一次
./scripts/install_schedule.sh --uninstall
tail -f logs/$(date +%F).log
```

plist 在安装时按当前 clone 路径生成，不进仓库——launchd 需要绝对路径，而那在每台机器上都不一样。

macOS 专属。Linux 上直接把同一个入口挂到 cron：`0 22 * * 0 /path/to/repo/scripts/run_weekly.sh`。

`run_weekly.sh` 会校验 `report.md` **是不是本次运行写的**（只检查文件存在会让重跑伪装成功）、论文数是否够、正文与数据是否一致、网站是否重建成功，任一不满足就退出非零并弹失败通知。它也会自动找 `claude` 可执行文件，找不到时用 `CLAUDE_BIN` 指定。

## 配置

全部可选。解析顺序：环境变量 → `config/local.json`（已 gitignore）→ 默认值。

| 键 | 环境变量 | 默认 |
|---|---|---|
| `site_url` | `PAPERS_SITE_URL` | 从 git remote 推导 |
| `site_title` | `PAPERS_SITE_TITLE` | AI 论文周报 |
| `site_tagline` | `PAPERS_SITE_TAGLINE` | 见 `siteconf.py` |
| `mail_from` / `mail_to` | `PAPERS_MAIL_FROM` / `PAPERS_MAIL_TO` | 空（不发邮件） |
| `smtp_host` / `smtp_port` | `PAPERS_SMTP_HOST` / `PAPERS_SMTP_PORT` | smtp.gmail.com / 465 |
| `keychain_service` | `PAPERS_KEYCHAIN_SERVICE` | AcademicPaperGrabber-smtp |

另外 `GITHUB_TOKEN` 可选：有它星数查询限额从 60/小时 提到 5000/小时。`run_weekly.sh` 会从 git credential helper 里读，不需要你写进文件。

### 邮件推送（可选，默认关）

填好 `mail_from` / `mail_to`，再把应用专用密码放进 keychain：

```bash
security add-generic-password -a "$USER" -s AcademicPaperGrabber-smtp \
         -w '<myaccount.google.com/apppasswords 生成的 16 位>'
```

密码只在运行时从 keychain 读进环境变量，不落盘、不进日志。缺任一项就直接跳过，不影响周报生成。普通 Google 密码不行，Gmail SMTP 只认应用专用密码。

## 开启 GitHub Pages

推送之后，在仓库 Settings → Pages 里把 Source 设为 `main` 分支的 `/docs` 目录；或者用 CLI：

```bash
gh api -X POST repos/<owner>/<repo>/pages -f "source[branch]=main" -f "source[path]=/docs"
```

站点随后出现在 `https://<owner>.github.io/<repo>/`。

## License

MIT
