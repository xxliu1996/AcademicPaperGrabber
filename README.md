# AcademicPaperGrabber

每周自动抓取六个 AI 方向最近七天的热门论文，各选 10 篇，生成一份带观点的中文周报，并发布成静态网站。

**产出三种形式**：`report.md`（Markdown 原文）、`report.html`（零依赖单文件，可直接分享）、GitHub Pages 站点（可按主题筛选、带 RSS）。

[**▶ 看一份真实周报**](https://xxliu1996.github.io/AcademicPaperGrabber/)

| 章节 | 覆盖范围 |
|---|---|
| 大语言模型 | 预训练、后训练、推理效率、长上下文 |
| 多模态 / 视觉语言 | VLM、图像与视频生成、文档与视频理解 |
| Agent | 工具调用、Computer Use、多智能体、编码 Agent |
| 其他深度学习 | 架构、优化、表征学习、语音、可解释性 |
| 机器人与具身智能 | VLA、操作与运动控制、人形机器人、仿真到真机 |
| 智能眼镜 / 可穿戴 | AR 眼镜、头显交互、第一人称视觉、可穿戴感知 |

每篇论文写成固定四行：**问题 / 做法 / 效果 / 值得看**，附中文译名、英文原题、机构、热度标记和 arXiv 链接。

## 它和「论文列表」有什么不同

- **选题有真实热度依据。** 主来源是 Hugging Face Papers 的社区投票数，不是按发表时间倒序或引用数（一周前的论文还没有引用）。
- **拿不到热度就说拿不到。** arXiv 上绝大多数论文没有任何公开热度数据。这类论文标注「热度未测得」，正文不许暗示它受欢迎，也不许进「本周最值得读的 5 篇」。
- **正文由模型写，但数字由机器核。** 热度行和链接在发布前逐篇与抓取数据比对，不一致就整次运行失败。
- **一篇论文只进一个章节。** 跨领域论文按主题匹配度归属，不会在两章里重复出现。

## 工作原理

```
Hugging Face Papers API ─┐
                         ├─→ 打分 / 去重 / 主题归属 ─→ raw/<主题>.json
arXiv API ───────────────┘                                  │
                                                            ↓
                                        6 个并行子 agent，各写一章（离线读 JSON）
                                                            ↓
                                   report.md ─→ 机器校验 ─→ report.html + docs/ 站点
```

抓取、打分、建站是**纯 Python 标准库**脚本——不需要 venv，不需要 pip install。正文由 Claude Code 生成。这样分工的好处是抓取逻辑可测试可复现，文字质量交给模型。

写正文的子 agent **全程不联网**：论文摘要在抓取阶段就随 API 一起拿到并存进本地 JSON 了。

## 快速开始

需要 Python 3.9+ 和 [Claude Code](https://claude.com/claude-code)。

```bash
git clone https://github.com/<你的账号>/AcademicPaperGrabber.git
cd AcademicPaperGrabber
```

**先看抓取效果**（不写正文，约 4–7 分钟；arXiv 要求请求间隔 3 秒）：

```bash
python3 scripts/fetch_papers.py --outdir reports/$(date +%F)/raw --quiet-stdout
```

想快点出结果就只跑一个主题：

```bash
python3 scripts/fetch_papers.py --theme robotics --no-github --emit 10 | python3 -m json.tool | head -40
```

**生成完整周报**，在仓库目录里启动 Claude Code 然后执行：

```
/papers-weekly
```

它会依次完成抓数据 → 每主题选 10 篇 → 六个并行子 agent 写章节 → 拼成 `report.md` → 机器校验 → 生成 HTML 与站点 → 提交推送。命令定义在 [`.claude/commands/papers-weekly.md`](.claude/commands/papers-weekly.md)，想改流程改那个文件。

**发布到 GitHub Pages**：推送后在仓库 Settings → Pages 把 Source 设为 `main` 分支的 `/docs` 目录，或者：

```bash
gh api -X POST repos/<owner>/<repo>/pages -f "source[branch]=main" -f "source[path]=/docs"
```

站点随后出现在 `https://<owner>.github.io/<repo>/`。**站点地址由脚本从 git remote 自动推导**，fork 之后不用改任何文件。

## 调整选题方向

所有口径集中在 [`config/topics.json`](config/topics.json)——arXiv 分类、关键词权重、入选门槛、每主题篇数、打分权重。**改选题方向只动这个文件，不用碰 Python。**

改完权重后不要重新抓取（arXiv 会按 IP 限流），用现成数据重新打分：

```bash
python3 scripts/fetch_papers.py --rescore reports/<日期>/raw
```

想加一个新主题，就在 `themes` 里照抄一份并加进 `claim_order`。

## 命令参考

```bash
# 抓取
python3 scripts/fetch_papers.py --list-themes             # 看配了哪些主题
python3 scripts/fetch_papers.py --outdir <目录>            # 全部六主题，落盘
python3 scripts/fetch_papers.py --theme llm               # 只跑一个主题（调试）
python3 scripts/fetch_papers.py --rescore <目录>           # 改完权重重新打分，不重抓
python3 scripts/fetch_papers.py --no-arxiv --outdir <目录>  # arXiv 挂了或被限流时的降级模式
python3 scripts/fetch_papers.py --no-github --outdir <目录> # 跳过 GitHub 星数查询

# 校验与发布
python3 scripts/check_report.py <日期> --fix              # 校验正文与数据一致，并修正元信息行
python3 scripts/build_site.py                            # 重建 docs/ 与单文件 HTML 报告
python3 scripts/siteconf.py                              # 打印当前 checkout 解析出的配置
```

常用参数：`--week-of YYYY-MM-DD` 指定周锚点、`--emit N` 每主题输出候选数、`--max-results N` 每条 arXiv 查询上限。不传时一律取 `config/topics.json` 里的值。

退出码 `2` 表示某个主题的候选数低于 `min_papers`。这不算整体失败——冷门方向确实有安静的周，那一章少写几篇或整章跳过即可。

## 定时运行

```bash
./scripts/install_schedule.sh                      # 默认每周日 22:00
./scripts/install_schedule.sh --day 6 --hour 23    # launchd 编号：0=周日 … 6=周六
./scripts/install_schedule.sh --run                # 立刻手动触发一次
./scripts/install_schedule.sh --uninstall
tail -f logs/$(date +%F).log
```

launchd plist 在安装时按当前 clone 路径生成，不进仓库。macOS 专属；Linux 上把同一个入口挂到 cron 即可：

```
0 22 * * 0  /path/to/repo/scripts/run_weekly.sh
```

`run_weekly.sh` 是无人值守的，所以它把每一步都当会失败来处理：校验报告**是否在本次运行中被重写**（只检查文件存在会让重跑伪装成功）、论文数是否够、正文与数据是否一致、站点是否重建成功。任一不满足就退出非零并弹系统通知。

## 配置

全部可选。解析顺序：环境变量 → `config/local.json`（已 gitignore，可从 `config/local.example.json` 复制）→ 默认值。

| 键 | 环境变量 | 默认 |
|---|---|---|
| `site_url` | `PAPERS_SITE_URL` | 从 git remote 推导 |
| `site_title` | `PAPERS_SITE_TITLE` | AI 论文周报 |
| `site_tagline` | `PAPERS_SITE_TAGLINE` | 见 `siteconf.py` |
| `mail_from` / `mail_to` | `PAPERS_MAIL_FROM` / `PAPERS_MAIL_TO` | 空（不发邮件） |
| `smtp_host` / `smtp_port` | `PAPERS_SMTP_HOST` / `PAPERS_SMTP_PORT` | smtp.gmail.com / 465 |
| `keychain_service` | `PAPERS_KEYCHAIN_SERVICE` | AcademicPaperGrabber-smtp |

`GITHUB_TOKEN` 也是可选的：有它，星数查询的限额从 60/小时 提到 5000/小时。`run_weekly.sh` 会自动从 git credential helper 读取，不需要你写进任何文件。

### 邮件推送（可选，默认关）

填好 `mail_from` / `mail_to`，再把应用专用密码放进 keychain：

```bash
security add-generic-password -a "$USER" -s AcademicPaperGrabber-smtp \
         -w '<myaccount.google.com/apppasswords 生成的 16 位>'
```

密码只在运行时读进环境变量，不落盘、不进日志。缺任一项就跳过，不影响周报生成。Gmail SMTP 只认应用专用密码，普通账号密码无效。

## 目录结构

```
AcademicPaperGrabber/
├── config/
│   ├── topics.json         # 六个主题的口径与打分权重 ← 调方向改这里
│   └── local.example.json  # 可选配置模板
├── scripts/
│   ├── fetch_papers.py     # 抓取 + 打分 + 主题归属
│   ├── check_report.py     # 校验正文与数据一致
│   ├── build_site.py       # 生成站点、RSS 与单文件报告
│   ├── send_email.py       # 可选邮件推送
│   ├── siteconf.py         # 配置解析
│   ├── install_schedule.sh # 安装定时任务
│   └── run_weekly.sh       # 定时任务入口
├── reports/YYYY-MM-DD/
│   ├── raw/<主题>.json      # 抓取原始输出（含打分明细），一并提交便于复现
│   ├── picks.json          # 选稿名单
│   ├── report.md           # 周报正文
│   └── report.html         # 同一份报告的单文件版
├── docs/                   # GitHub Pages 发布目录（生成物，勿手改）
└── DESIGN.md               # 数据源选择与打分设计的来由
```

`docs/` 每次构建都会先删除再重建，手改的内容下一轮就没了。

## 数据来源

**Hugging Face Papers**（`/api/daily_papers`）是主来源，也是**全网唯一提供单篇论文公开热度数值的接口**——社区投票数。一周约 340 篇，但覆盖面偏向 LLM / 多模态 / Agent。

**arXiv API** 提供覆盖面，按主题的分类与关键词组合查询最近七天的投稿，单是 cs.RO 一周就有 680 多篇。但它**不提供任何热度信号**。

Papers with Code 已停止运营（域名现 301 跳转到 Hugging Face），其第三方仿站无 API；alphaXiv 无公开接口。两者均未采用。

详细取舍见 [DESIGN.md](DESIGN.md)。

## 排序与诚实标注

```
score = 上票数^0.5                      ← 实测热度，主导排序
      + min(1.2 × log1p(星数), 6.0)     ← 仅当确认是论文自己的仓库，且有上限
      + 0.25 × (关键词分 + 分类分)       ← 主题相关性，只作兜底排序
      + 有代码 / 有项目页加分
```

关键词分决定一篇论文**属于哪一章**，而不是在章内排第几——同一章里的论文都已经是主题相关的了。

**报告一概不印 GitHub 星数**，只印「有代码」加链接。论文关联的仓库经常是被引用的仓库（对比基线、底座模型、自己的上一代），把那个星数说成这篇论文的热度就是伪造数据。星数仅作内部排序信号，且必须通过仓库名校验。

每篇论文带 `heat_source` 字段：`hf`（有社区投票）或 `none`（无公开热度数据）。热度标记由脚本预计算，不由模型拼写，`check_report.py` 还会逐篇核对。

## License

MIT
