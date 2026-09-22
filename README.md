# dsh-plugin-deep-paper-reading

把「文献精读模式」（Deep Paper Reading）作为 **DSH 插件**分发：装好之后，预设选择器里会多出一个 `文献精读模式`，切进去就能对**单篇**生物医学文献做逐图、逐实验的结构化精读。

它打包的是作者自有的 `deep-paper-reading` 技能本体（SKILL.md + 核对清单 + 报告模板，逐字节原样），外加一个模式级 persona：强制先加载技能、守住证据边界、按四要素拆解每个实验、重建逻辑链，最后按模板产出可直接拿去 journal club 的报告。

- 关键词：`dsh-plugin` · `deepseek-harness` · `agent-preset` · 文献精读
- 许可：MIT

---

## 这个模式做什么

| 阶段 | 内容 |
|---|---|
| 1 | 论文获取与初扫（标题/摘要 → Introduction 末段 → 全部图注 → Discussion 首段 → Results 小标题） |
| 2 | 正文逐行精读（Introduction / Results / Discussion / Methods 各自要点） |
| 3 | 补充材料同等严格对待，读不到就显式标注「缺失」 |
| 4 | **图注 ↔ 正文对应表**（这是精读与复述的分界线） |
| 5 | **逐实验四要素拆解**：目的 / 设计与工具 / 结果 / 解读 |
| 6 | 逻辑链重建，并把每个转折分类为排除、延伸、机制、应用、验证 |
| 7 | 按模板产出报告；要 Word 时走 `docx` 技能导出 |

persona 里固化了两条硬约束：

- **证据边界**：不编图号、图注、数字、P 值、样本量、试剂货号；严格区分「数据实际显示了什么」与「作者说它显示了什么」；拿不到补充材料就写「缺失（正文引用但未获取）」，只读到摘要就写「证据等级：摘要级」。
- **图必须真看过**：判断若基于图注而非图像，必须写明。

**不适用**：多篇文献综述（用 `literature-review`）、正式同行评审（用 `peer-review`）、检索文献（用 `paper-lookup`）。

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

> 从 git 安装拉的是**源码**，pnpm ≥10 默认拒绝运行 git 依赖的构建脚本。本包没有任何构建步骤（纯 JS + YAML，无依赖、无 `prepare`），所以不需要 `allowBuilds` 授权。
>
> 装完重启 DSH，然后在预设选择器里就能看到 `文献精读模式`；卸载用 `dsh plugin --profile web remove dsh-plugin-deep-paper-reading`。

### 方式 2：预设包（`.dshpreset`）—— 零 CLI，推荐 Desktop 用户

到 [Releases](../../releases) 下载 `dsh-plugin-deep-paper-reading-<版本>.dshpreset`，然后在 DSH Desktop 里**导入预设**。桌面端会先校验、预览，确认后才原子写入用户预设根目录；已存在的同名预设 id 不会被覆盖。

这是 DSH Desktop 的原生预设交换格式（`manifest.json` + `preset/` 的 ZIP），不需要 `dsh` CLI，也不改动任何 profile 配置。

### 方式 3：只要技能，不要模式

把技能目录拷进任何被 DSH 扫描的技能根：

```sh
cp -r presets/deep-paper-reading/skills/deep-paper-reading ~/.agents/skills/
# 或 <DSH_HOME>/skills/
```

之后在**任何**模式下都能用 `skill` 工具调用 `deep-paper-reading`，但没有配套的模式级 persona。

> 顺带一提：这也修掉了一个常见坑——如果你的技能原本放在 `~/.claude/skills/`（Claude Code 的根），DSH 不会扫描它，`skill` 调用会报 `unknown or no longer available`。

---

## 使用

1. 新建会话，预设选 **文献精读模式**
2. 把 PDF/DOI 丢进去，说「精读这篇」即可

默认输出约定（persona 里写死）：报告落到 `paper-reading/<短标题>-精读报告.md`，原文提取物与图版渲染放 `sources/`；若工作区已有既定结构（例如 `scientific-evidence/reports/`）则跟随既有结构。

技能里假设本机有可用的 PDF 工具链（`python` + PyMuPDF 之类）。若缺失，agent 会先告诉你，而不是假装读过全文。

---

## 目录结构

```
├── package.json                    # dsh.bundle.patch → cordis.patch.yml
├── cordis.patch.yml                # 把本包的 presets/ 注册为预设 roster 的一个 root
├── index.js                        # 启动期自检行（预设目录缺失时打印原因）
├── presets/
│   └── deep-paper-reading/
│       ├── agent.cordis.yml        # 精读 persona + 内置技能目录挂载
│       ├── preset.yml              # 显示名与描述
│       ├── SOURCE.md               # 组合与技能的出处说明
│       └── skills/
│           └── deep-paper-reading/ # 技能本体（逐字节原样）
├── scripts/build-dshpreset.mjs     # 零依赖打包 .dshpreset
├── scripts/check-composition.py    # 组合静态检查（CI 每次 push 跑）
└── .github/workflows/              # ci.yml 校验，release.yml 发版附包
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
- **内置技能随预设走**：组合里 `skill-filesystem` 行的 `customSkillDirs` 用的是 `new URL('skills/', baseUrl)`；预设 `Include` 会把 `baseUrl` 设为**组合自身目录**（在 `mount.js`/`specifier.js` 里确认），所以不论预设是从用户根、本包 `presets/`，还是导入的 `.dshpreset` 挂载，技能目录都能解析到。
- **插件安装 + patch 生效**：建了一个一次性 profile，`dsh plugin add` 本包，然后在 profile 里加上 `dsh-web-app` 层再 `--dump-config`——确认注入行到位、`agent-presets` 行被覆盖且四个键（`default`/`includeShippedRoot`/`includeUserRoot`/`roots`）全部重述。
- **`!!js` 表达式可求值**：`dsh --profile <测试 profile> --help` 加载全部行并求值配置，退出码 0、无配置错误，并且插件自检行打印出 `registered from …\presets\deep-paper-reading`。表达式的路径数学另用 Node 单独跑过：解析结果正是包内的 `presets/`，其下 `agent.cordis.yml` 与 `SKILL.md` 都存在。
- **`--dump-config` 只证明 patch 应用，不证明求值**（它打印 `!!js` 原文），所以上面第 3 条才是关键那一步。
- **包格式**：打包脚本按 DSH Desktop 导入器的约束实现（`format`/`version`、id 规则、≤512 文件、单文件 ≤12 MB、解压后 ≤32 MB、压缩后 ≤16 MB），CI 里再用 `unzip` 回读校验包内布局与 manifest。
- **组合静态检查**：`python3 scripts/check-composition.py`，检查 bundle manifest、patch 覆盖键、预设与技能元数据（CI 每次 push 都跑）。

**没验的**：预设最终出现在你机器上的预设选择器里，需要你在真实 profile 装一次才能看到——那是唯一一步必须在真实环境发生的。

**你自己的机器上怎么验（不启动、不打扰现有会话）：**

```sh
dsh --profile web --dump-config | grep -n "== dsh-plugin-deep-paper-reading"
```

`--dump-config` 只组合配置树然后退出，不启动应用。看到 `== dsh-plugin-deep-paper-reading` 这一层，就说明 patch 被正确应用了。

---

## 许可与出处

MIT（见 [LICENSE](LICENSE)）。

- 技能本体 `presets/deep-paper-reading/skills/deep-paper-reading/` 是作者自有技能（frontmatter 记为 MIT、`skill-author: user`），本包**未作任何修改**。
- 预设的 Cordis 组合派生自本机 `scientific-evidence-en-mode` 预设：工具面（文件、shell、文件检索、网页抓取、技能、待办、目标、作业、上下文折叠、提问）原样保留，只改写了 persona 行、给 `skill-filesystem` 加了内置技能目录，并写了显示元数据。
- 上游组合的 `SOURCE.md`（K-Dense Scientific Agent Skills / PRISMA 相关）已被替换，因为那是另一个模式的出处；细节见 `presets/deep-paper-reading/SOURCE.md`。
