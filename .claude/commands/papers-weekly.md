---
description: 抓取过去一周六个方向的热门论文，各 10 篇，合成一份周报，并重建 GitHub Pages 站点
argument-hint: [YYYY-MM-DD 可选，默认今天]
---

生成本周的 AI 论文周报。**六个主题合成一份报告**，然后重建网站。

**第 0 步：定位仓库根目录 `<ROOT>`**（本地和云端 sandbox 路径不同，必须先确定）：

```bash
for d in /Users/xingxingliu/Projects/xxliu1996_githubrepos/AcademicPaperGrabber \
         /Users/xingxingliu/Projects/CluadeProjects/AcademicPaperGrabber; do
  [ -d "$d/scripts" ] && echo "$d" && break
done || git rev-parse --show-toplevel
```

后续所有路径都以 `<ROOT>` 为基准，不要写死绝对路径。

**重要：无条件重新生成。** 如果 `<ROOT>/reports/<DATE>/` 已经存在，**照样从第 1 步开始全部重跑并覆盖**，不要因为"文件已存在"就跳过、也不要反问用户要不要重做。定时任务是无人值守的，静默跳过会伪装成成功。

约定：
- `<DATE>` = `$ARGUMENTS`，为空就用今天（`date +%F`）
- 六个主题 `<THEME>`：`wearable-xr`、`robotics`、`agent`、`vlm`、`llm`、`deep-learning`
- 本周产物落在 `<ROOT>/reports/<DATE>/`：`raw/<THEME>.json`（抓取结果）、`picks.json`（选稿名单）、`report.md`（最终周报）

| 主题 slug | 章节标题 | 收录 |
|---|---|---|
| `llm` | 大语言模型 | 10 |
| `vlm` | 多模态 / 视觉语言 | 10 |
| `agent` | Agent | 10 |
| `deep-learning` | 其他深度学习 | 10 |
| `robotics` | 机器人与具身智能 | 10 |
| `wearable-xr` | 智能眼镜 / 可穿戴 / 第一人称视觉 | 10 |

报告里的章节顺序按上表（LLM 在前），但**抓取和归属**按 `config/topics.json` 的 `claim_order`（冷门主题先认领）。

---

## 1. 抓数据

```bash
cd <ROOT> && python3 scripts/fetch_papers.py --outdir reports/<DATE>/raw --week-of <DATE> --quiet-stdout
```

- 脚本纯标准库，不需要 venv。一次跑完六个主题，约 4–7 分钟（arXiv 要求请求间隔 3 秒）。
- **把 stderr 的 `[grab]` / `WARN:` 日志展示给用户**。
- 看到 `arXiv returned 0 parsed entries for a non-empty result set`，说明 arXiv 的 Atom 结构变了，先修 `scripts/fetch_papers.py` 的解析再继续，不要拿残缺数据往下走。
- 退出码 2 表示有主题的候选数低于 `min_papers`。**这不算整体失败**：那个主题少写几篇或整章跳过，继续做其余主题，最后在汇报里说明。
- 环境里有 `GITHUB_TOKEN` 时会自动用上（星数查询限额从 60/小时 提到 5000/小时）。

## 2. 每个主题选出 10 篇

逐个读 `reports/<DATE>/raw/<THEME>.json`（每份约 25 篇候选，含完整摘要）。判断标准：

- **必须真的属于这个主题**。打分是启发式，脚本已经做了跨主题去重（一篇只会出现在一个主题的 json 里），但漏网之鱼要手动剔掉。
- **优先有实测热度的**：`heat_source` 为 `hf`（HF 上票）或 `github`（仓库星数）的排前面。`none` 的只有主题相关性，没有任何热度证据。
- 尽量覆盖不同子方向，不要一章里十篇全是同一类 benchmark。
- `score_breakdown.keyword_matched` 可以用来判断这篇为什么被选中——如果只靠一个边缘词命中，大概率是误收，剔掉。
- **冷门主题宁缺毋滥**：`wearable-xr` 某些周凑不满 10 篇真正值得写的，凑不满就少写几篇，在章节开头说明"本周该方向动静不大"，不要为了凑数把明显边缘的论文写进去。

把名单写进 `reports/<DATE>/picks.json`：

```json
{ "llm": ["2609.12345", "..."], "vlm": [...], "agent": [...],
  "deep-learning": [...], "robotics": [...], "wearable-xr": [...] }
```

## 3. 并行子 agent 写六个章节

**在同一条消息里并行发起 6 个 Agent 调用**（`subagent_type: general-purpose`，`run_in_background: false`），一个 agent 负责一个主题。

每个子 agent 的 prompt 里必须写清：

- 它负责的主题 slug、章节标题、以及 `picks.json` 里属于它的 arXiv ID 列表
- 让它 **Read `<ROOT>/reports/<DATE>/raw/<THEME>.json`**，摘要已经在里面了 —— **禁止 WebFetch / 联网**。摘要是抓取阶段随 API 一起拿到的，再去抓网页纯属浪费。
- 严格照抄第 4 步的条目骨架，按 `picks.json` 的顺序编号
- **不许夸大热度**：`heat_source: "none"` 的论文，一个字都不能提热度，不准出现"爆火""刷屏""本周最热"这类词
- 每条四个要点合计控制在 120 字左右，别复述摘要、别贴公式、别展开实验细节
- 中文译名要意译得像人话，不要机翻腔；原题照抄英文原文

子 agent 返回拼好的章节 Markdown，主 agent 负责组装，不要让子 agent 直接写文件（六个 agent 同时写一个文件会互相覆盖）。

## 4. 写 `report.md`

写入 `reports/<DATE>/report.md`。**格式必须严格照抄下面的骨架** —— `scripts/build_site.py` 靠这个结构把 Markdown 转成网页，改了格式网站就会渲染错：

```markdown
# AI 论文周报（<week_start> – <week_end>）

<一段导语：本周这批论文的共同趋势是什么。要有观点，别写"以下是本周热门论文"这种废话。
哪个方向本周特别热闹、哪个方向反而安静，都可以说。>

---

## ⭐ 本周最值得读的 5 篇

1. **<中文译名>**（<章节名>）— <一句话说清为什么是它>｜[arXiv:xxxx.xxxxx](https://arxiv.org/abs/xxxx.xxxxx)
2. ...

---

## 一、大语言模型

### 1. <中文译名>

**<English Title Verbatim>**
<机构，没有就省略> ｜ 🔥 HF <N> 赞 ｜ 💻 <N>★ ｜ [arXiv:<id>](https://arxiv.org/abs/<id>)

- **问题**：<这篇要解决什么>
- **做法**：<怎么做的>
- **效果**：<关键结果，有数字就给数字>
- **值得看**：<对读者的价值，别复述前三条>

### 2. ...

---

## 二、多模态 / 视觉语言
...
```

硬性要求：

- **H1 只有一行，紧跟着的段落就是导语**，建站脚本把导语渲染成高亮块。
- **Top5 用 `## ⭐ 本周最值得读的 5 篇`，一字不差**，建站脚本靠它定位首屏区块。
- **章节标题必须是 `## <中文序号>、<章节标题>`**（一、二、三……），顺序照上面的表。
- **每篇的标题行必须是 `### <序号>. <中文译名>`**，章节内从 1 连续编号。建站脚本用这行正则提取论文清单，格式不对网站上就显示成 0 篇。
- **热度标记只写有的**：有 HF 上票写 `🔥 HF N 赞`，有星数写 `💻 N★`，两样都没有就写 `热度未测得`，不要留空也不要编。
- **Top5 只能从 `heat_source` 不是 `none` 的论文里选。** 没有实测热度的论文不准进 Top5 —— 那等于拿零信号的论文冒充爆款。
- 每个链接都用 `raw/<THEME>.json` 里的 `abs_url`，不要手拼。
- 导语要针对**本周整体**写，别写成六个章节导语的拼接。

## 5. 重建网站

```bash
cd <ROOT> && python3 scripts/build_site.py
```

它会清空并重建 `docs/`（GitHub Pages 的发布目录）：首页放最近三个月、`archive.html` 放全部历史、每周一个 `docs/r/<DATE>.html`、`docs/feed.xml` 是 RSS，主题筛选是纯前端的。

跑完检查 `docs/data/reports.json` 里本周那条的 `counts`：如果某个主题是 0，说明那一章的 `###` 格式写错了，回第 4 步修，别放着不管。

## 6. 提交

```bash
cd <ROOT> && git add reports/<DATE> docs && \
git commit -m "Weekly paper digest: <DATE>"
```

然后 `git push`（远端是 `origin main`）。push 失败就报告错误，不要吞掉 —— 不 push 网站就不会更新。

## 7. 汇报

告诉用户：

- `report.md` 路径，以及哪个主题本周没凑满 10 篇（如果有）
- Top5 名单
- 六个主题各自的收录数，以及其中有实测热度的篇数（诚实交代：`none` 占比高说明这周这个方向缺公开热度数据）
- 网站地址：https://xxliu1996.github.io/AcademicPaperGrabber/
