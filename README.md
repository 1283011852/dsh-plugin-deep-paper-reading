# dsh-plugin-deep-paper-reading

把「文献精读模式」（Deep Paper Reading）作为 **DSH 插件**分发：装好之后，预设选择器里会多出一个 `文献精读模式`，切进去就能对**单篇**生物医学文献做逐图、逐实验的结构化精读。

**v0.2.0 起，精读报告是图表化的**：全文逻辑链画成流程图（不再只用文字描述），图注对应、实验强度、主张-证据差距、局限风险、术语关系各有一张判定图，并附带一份 **Word 格式转换标准**，报告可直接导出成合规 `.docx`。

- 关键词：`dsh-plugin` · `deepseek-harness` · `agent-preset` · 文献精读 · 图表化 · DOCX
- 许可：MIT

---

## 0.2.0 变更

| 变化 | 内容 |
|---|---|
| **逻辑链图表化** | 新增 Phase 7「可视化构建」，**8 张必做图**（V1–V8）+ 4 张条件/可选图；纯文字（或 ASCII 框图）的逻辑链不再是合格交付 |
| **多图表判定** | 不只逻辑链：图注一致性矩阵、实验证据强度矩阵、主张-证据阶梯、局限风险散点、正文↔图映射、术语机制关系图 |
| **离线渲染器** | 新增 `scripts/render-diagram.py`：spec JSON → PNG + Mermaid，仅依赖 Pillow，无需 Node/Chromium/网络；缺 `source` 行直接报错 |
| **Word 格式转换标准** | 新增 `references/docx-conversion-standard.md`：页面、样式矩阵、表格列数上限、图表题位置、`○ △ × –` 字形集、25 项验收清单、渲染档位记录 |
| **检查强化** | `check-composition.py` 现在校验「SKILL.md 点名的文件必须真的打包」与 V1–V8 图约束；CI 增加渲染器自检（含 CJK 字体） |
| **技能不再逐字节原样** | 技能本体已按上述内容修改（原为上游逐字节副本），出处说明同步更新 |

---

## 能力一览

> 完整介绍（含四张能力图与「它不做什么」）见 [docs/skill-intro.md](docs/skill-intro.md)。

**八阶段工作流**——箭头方向即阅读顺序，每一步都有产出物，不是"读完再动手"：

![八阶段工作流](docs/capabilities/cap-1-workflow.png)

**八张必做图各回答哪个问题**——结构、证据、缺口、现场讲解四类问题分工明确：

![八张必做图的职责分工](docs/capabilities/cap-2-coverage.png)

另外两张：[交付物与质量关卡](docs/capabilities/cap-3-deliverables.png) ｜ [真实跑出来的样子](docs/capabilities/cap-4-sample.png)（Cell 2026 · mRNA-TCE 治疗难治性 ITP 的实际产出）

---

## 这个模式做什么

| 阶段 | 内容 |
|---|---|
| 1 | 论文获取与初扫（标题/摘要 → Introduction 末段 → 全部图注 → Discussion 首段 → Results 小标题），全文落盘 `sources/paper-fulltext.txt` |
| 2 | 正文逐行精读（Introduction / Results / Discussion / Methods 各自要点） |
| 3 | 补充材料同等严格对待，读不到就显式标注「缺失（正文引用但未获取）」 |
| 4 | **图注 ↔ 正文对应表** + 图 V3（正文↔图 二分图）+ 图 V4（一致性矩阵） |
| 5 | **逐实验四要素拆解**：目的 / 设计与工具 / 结果 / 解读 + 图 V5（证据强度总览） |
| 6 | 逻辑链重建，每个转折分类为排除、延伸、机制、应用、验证；无法归类的转折成为**虚线边** |
| 7 | **可视化构建**：渲染 V1–V8，逐张核对文件/像素/中文字形/图注三行 |
| 8 | 按模板产出报告；要 Word 时按内置格式转换标准导出 |

persona 里固化了三条硬约束：

- **证据边界**：不编图号、图注、数字、P 值、样本量、试剂货号；严格区分「数据实际显示了什么」与「作者说它显示了什么」；拿不到补充材料就写「缺失（正文引用但未获取）」，只读到摘要就写「证据等级：摘要级」。
- **图必须真看过**：判断若基于图注而非图像，必须写明。
- **图必须真画出来**：不许用 ASCII 框图、表格或空占位符冒充图；渲染不出来就写「图形未渲染（原因）」并保留 Mermaid 源码。

---

## 图表清单

| 编号 | 图名 | 类型 | 级别 |
|---|---|---|---|
| **V1** | 全文逻辑链主图（分层 + 过渡类型 + 断裂点虚线） | flow | 必做 |
| **V2** | 主干与分叉（只留三步） | flow | 必做 |
| **V3** | 正文↔图 映射二分图 | flow | 必做 |
| **V4** | 图注-正文一致性矩阵 | matrix | 必做 |
| **V5** | 实验证据强度总览 | matrix | 必做 |
| **V6** | 核心主张证据充分性阶梯 | matrix | 必做 |
| **V7** | 局限风险矩阵（影响 × 严重度） | scatter | 必做 |
| **V8** | 术语/机制关系图 | flow | 必做 |
| **V9** | 替代假说判别树 | flow/tree | 条件 |
| **V10** | 入组/队列流程图 | flow | 条件（临床/队列） |
| **V11** | 实验推进时间线 | timeline | 可选 |
| **V12** | 评估雷达 | — | 默认不画（虚假精度） |

**渲染阶梯**（用哪档记在图注里）：

| 档 | 工具 | 说明 |
|---|---|---|
| A | `mmdc`（mermaid-cli） | 复杂图最佳 |
| B | `npx -y @mermaid-js/mermaid-cli` | 需 Node + 网络 |
| C | `python scripts/render-diagram.py spec.json --out fig.png --mermaid fig.mmd` | **离线**，仅需 Pillow，支持 flow/matrix/scatter/timeline |
| D | 未渲染 | 保留 Mermaid 源码 + 显式标注 |

```sh
# 首次使用先自检（四类样图 + 「缺 source 必须报错」规则）
python presets/deep-paper-reading/skills/deep-paper-reading/scripts/render-diagram.py \
  --selftest --tmp /tmp/diagram-check
```

详见 `references/visualization-spec.md`（图形规范）与 `assets/diagram-specs.md`（可直接改写的 V1–V11 模板）。

---

## Word 导出与格式转换标准

`references/docx-conversion-standard.md` 是**规范性**文本，包含：

- 页面与分节数值（A4、边距、页眉页脚、封面/目录/正文分节）
- 样式矩阵（中文字体与西文字体分别设定、标题/正文/表格/图注/代码的字号与间距）
- 表格规范（**列数 ≤ 6**、表题在上、图题在下、跨页表头重复、判定列只用 `○ △ × –`）
- 图形规范（PNG 300 dpi、宽 15.5 cm、嵌入型、三行图注含「来源 + 渲染档」、alt text、未渲染占位规则）
- 数学与符号（基因斜体、*p*/*n* 斜体、单位空格、负号 U+2212）
- 9 步转换流水线与 25 项验收清单
- **已知限制**：python-docx 无法算目录页码（须提示用户更新域）、字体依赖客户端、SVG 支持不一、无渲染器时确实没有图

---

## 安装

三种方式，按你的环境选一种。

### 方式 1：插件（bundle）—— 有 `dsh` CLI 时

```sh
dsh plugin --profile web add github:1283011852/dsh-plugin-deep-paper-reading
```

DSH Desktop 里等价写法：

```sh
pnpm dsh plugin --profile web add github:1283011852/dsh-plugin-deep-paper-reading
```

> 从 git 安装拉的是**源码**，pnpm ≥10 默认拒绝运行 git 依赖的构建脚本。本包没有任何构建步骤（纯 JS + YAML + 一个 Python 脚本，无 npm 依赖、无 `prepare`），所以不需要 `allowBuilds` 授权。
>
> 装完重启 DSH，然后在预设选择器里就能看到 `文献精读模式`；卸载用 `dsh plugin --profile web remove dsh-plugin-deep-paper-reading`。

### 方式 2：预设包（`.dshpreset`）—— 零 CLI，推荐 Desktop 用户

到 [Releases](../../releases) 下载 `dsh-plugin-deep-paper-reading-<版本>.dshpreset`，然后在 DSH Desktop 里**导入预设**。桌面端会先校验、预览，确认后才原子写入用户预设根目录；已存在的同名预设 id 不会被覆盖。

这是 DSH Desktop 的原生预设交换格式（`manifest.json` + `preset/` 的 ZIP），不需要 `dsh` CLI，也不改动任何 profile 配置。

### 方式 3：只要技能，不要模式

```sh
cp -r presets/deep-paper-reading/skills/deep-paper-reading ~/.agents/skills/
```

之后在**任何**模式下都能用 `skill` 工具调用 `deep-paper-reading`，但没有配套的模式级 persona。技能目录自带 `scripts/render-diagram.py`，所以渲染能力随技能走。

> 顺带一提：如果你的技能原本放在 `~/.claude/skills/`（Claude Code 的根），DSH 不会扫描它，`skill` 调用会报 `unknown or no longer available`。

---

## 使用

1. 新建会话，预设选 **文献精读模式**
2. 把 PDF/DOI 丢进去，说「精读这篇」即可
3. 想要图更精致可以装 `mermaid-cli`；没有也能出图（走档 C）

默认输出约定（persona 里写死）：报告落到 `paper-reading/<短标题>-精读报告.md`，原文提取物与版面渲染放 `sources/`，图形 PNG + spec/Mermaid 源码放 `paper-reading/figures/`；若工作区已有既定结构（例如 `scientific-evidence/reports/`）则跟随既有结构。

技能假设本机有可用的 PDF 工具链（`python` + PyMuPDF 之类）。若缺失，agent 会先告诉你，而不是假装读过全文。

---

## 目录结构

```
├── package.json                    # dsh.bundle.patch → cordis.patch.yml
├── cordis.patch.yml                # 把本包的 presets/ 注册为预设 roster 的一个 root
├── index.js                        # 启动期自检行（预设目录缺失时打印原因）
├── presets/
│   └── deep-paper-reading/
│       ├── agent.cordis.yml        # 精读 persona（含 VISUALS 段）+ 内置技能目录挂载
│       ├── preset.yml              # 显示名与描述
│       ├── SOURCE.md               # 组合与技能的出处说明
│       └── skills/
│           └── deep-paper-reading/
│               ├── SKILL.md                    # 8 阶段工作流
│               ├── assets/report-template.md   # 报告模板（含图占位与三行图注）
│               ├── assets/diagram-specs.md     # V1–V11 模板（JSON + Mermaid）
│               ├── references/reading-checklist.md
│               ├── references/visualization-spec.md        # 图形规范
│               ├── references/docx-conversion-standard.md  # Word 转换标准
│               ├── references/biomedical-tools.md
│               └── scripts/render-diagram.py   # 离线渲染器（Pillow）
├── scripts/build-dshpreset.mjs     # 零依赖打包 .dshpreset
├── scripts/check-composition.py    # 组合 + 技能文件引用 + V1–V8 契约检查（CI 每次 push 跑）
├── scripts/check-render-selftest.py # 渲染器自检（四类图 + source 规则，CI 每次 push 跑）
├── docs/skill-intro.md             # 能力介绍（四张能力图 + 边界说明）
├── docs/capabilities/              # 能力图 PNG + 可重渲染的 JSON spec
└── .github/workflows/              # ci.yml 校验（含渲染器自检），release.yml 发版附包
```

---

## ⚠️ 已知影响

**本插件的 patch 会覆盖 `agent-presets` 行的整个 `config`。**

DSH 的 patch 语义是**整段替换目标行的 `config`，不做深合并**（见[打包与安装插件](https://deepseek-harness.github.io/deepseek-harness/develop/basic/publish)）。所以 `cordis.patch.yml` 里重述了该行需要的每一个键：

```yaml
- id: agent-presets
  config:
    default: standard
    includeShippedRoot: true
    includeUserRoot: true
    roots:
      - trust: system
        path: !!js "…解析到本包目录…/presets"
```

由此产生两个必须知道的后果：

1. **`roots` 归本插件所有。** 如果你还用别的 bundle 或自己的 `cordis.patch.yml` 给 `agent-presets` 配过 roots，后应用的层会整段胜出，先前那批 root 会消失。要两者共存，就在你自己的 profile patch 里手工把两个 `roots` 数组合并，而不是同时挂两个 bundle。
2. **`default` 被重述为 `standard`**（随附默认值）。你在 `$DSH_HOME/settings.yaml` 里设置的 `agent-presets.default` 属于 settings 层，优先级更高，不受影响。

不想承担这两点，就用**方式 2（`.dshpreset`）**——它完全不碰 profile 配置。

---

## 验证

**发布前实际做过的验证（不是"应该能行"）：**

- **预设挂载校验**：`agentPresets.standingKeyFor('deep-paper-reading')` → `mounted OK`，真正组合了一遍插件子树，不是文件格式检查。
- **内置技能随预设走**：组合里 `skill-filesystem` 行的 `customSkillDirs` 用的是 `new URL('skills/', baseUrl)`；预设 `Include` 会把 `baseUrl` 设为**组合自身目录**，所以不论预设是从用户根、本包 `presets/`，还是导入的 `.dshpreset` 挂载，技能目录都能解析到。
- **插件安装 + patch 生效**：建了一个一次性 profile，`dsh plugin add` 本包，然后在 profile 里加上 `dsh-web-app` 层再 `--dump-config`——确认注入行到位、`agent-presets` 行被覆盖且四个键（`default`/`includeShippedRoot`/`includeUserRoot`/`roots`）全部重述。
- **`!!js` 表达式可求值**：`dsh --profile <测试 profile> --help` 加载全部行并求值配置，退出码 0、无配置错误，并且插件自检行打印出 `registered from …\presets\deep-paper-reading`。表达式的路径数学另用 Node 单独跑过：解析结果正是包内的 `presets/`，其下 `agent.cordis.yml` 与 `SKILL.md` 都存在。
- **`--dump-config` 只证明 patch 应用，不证明求值**（它打印 `!!js` 原文），所以上面第 3 条才是关键那一步。
- **包格式**：打包脚本按 DSH Desktop 导入器的约束实现（`format`/`version`、id 规则、≤512 文件、单文件 ≤12 MB、解压后 ≤32 MB、压缩后 ≤16 MB），CI 里再用 `unzip` 回读校验包内布局与 manifest。v0.2.0 实跑：`12 files, 172.5 KiB → 71.2 KiB`，新增的渲染器/规范/模板文件均在包内。
- **组合静态检查**：`python3 scripts/check-composition.py`（CI 每次 push 都跑）。v0.2.0 起额外校验：SKILL.md 里以反引号点名的每个 `references/ · assets/ · scripts/` 路径必须真实打包；V1–V8 必须在 SKILL.md 与 `visualization-spec.md` 中都有定义。
- **渲染器自检**：`render-diagram.py --selftest` 渲染四类样图（flow / matrix / scatter / timeline）+ 断言「缺 `source` 的 spec 必须报错」。本机实跑四张 PNG 分别 1020×1640 / 1360×816 / 1760×1232 / 1984×876 px，均 ≥1200 px，中文为真字形。

**没验的**：

- 预设最终出现在你机器上的预设选择器里，需要你在真实 profile 装一次才能看到——那是唯一一步必须在真实环境发生的。
- 渲染器在**没有 CJK 字体**的 Linux 上会回退成方框（有 stderr 警告），此时应改走 mermaid-cli；CI 里装了 `fonts-noto-cjk` 以覆盖该路径。
- Word 导出的实际版式：本仓库只发布规范与模板，具体报告在不同 Word/WPS 版本下的回排需要目视复核（见标准第 13 节的 25 项清单）。

**你自己的机器上怎么验（不启动、不打扰现有会话）：**

```sh
dsh --profile web --dump-config | grep -n "== dsh-plugin-deep-paper-reading"
python presets/deep-paper-reading/skills/deep-paper-reading/scripts/render-diagram.py --selftest
```

`--dump-config` 只组合配置树然后退出，不启动应用。看到 `== dsh-plugin-deep-paper-reading` 这一层，就说明 patch 被正确应用了。

---

## 许可与出处

MIT（见 [LICENSE](LICENSE)）。

- 技能本体 `presets/deep-paper-reading/skills/deep-paper-reading/` 是作者自有技能（frontmatter 记为 MIT、`skill-author: user`）。**v0.2.0 起不再是上游逐字节副本**：新增 Phase 7（可视化）、V1–V8 必做图清单、可视化规范、图形模板、离线渲染器与 Word 转换标准，并同步改写了报告模板与核对清单。
- 预设的 Cordis 组合派生自本机 `scientific-evidence-en-mode` 预设：工具面（文件、shell、文件检索、网页抓取、技能、待办、目标、作业、上下文折叠、提问）原样保留，只改写了 persona 行（新增 VISUALS 段、更新 OUTPUT 段）、给 `skill-filesystem` 加了内置技能目录，并写了显示元数据。
- Mermaid 书写约定（`accTitle`/`accDescr`、只用 `classDef`、`snake_case` id、单图节点上限）参考 K-Dense `markdown-mermaid-writing` 技能的风格指南。
- 图表有助理解与记忆的**定位证据**（不是对本设计的验证）：*Infographics Improve Comprehension and Recall at the Orthopaedic Journal Club*（J Surg Educ, 2020）与 *Let Your Ideas Flow: Using Flowcharts to Convey Methods and Implications of the Results*（J Microbiol Biol Educ, 2018, PMC5969414）。
- 细节见 `presets/deep-paper-reading/SOURCE.md`。
