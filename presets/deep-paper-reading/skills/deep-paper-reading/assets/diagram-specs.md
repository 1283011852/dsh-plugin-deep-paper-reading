# 图形模板库（Diagram Specs）

> 可直接改写的最小模板，与 `references/visualization-spec.md` 的 V1–V11 一一对应。
> `【】` 是必须替换的占位符；替换后仍含 `【` 的 spec 不算完成。
> 每份 spec 的 `source` 必须写实：指到具体图号、正文小节、补充表号。

渲染（档 C，离线）：

```bash
python scripts/render-diagram.py figures/V1.json --out figures/V1-logic-chain.png \
       --mermaid figures/V1-logic-chain.mmd
```

渲染（档 A，有 mermaid-cli）：

```bash
mmdc -i figures/V1-logic-chain.mmd -o figures/V1-logic-chain.png -b white -w 2000 --scale 2
```

---

## 0. Mermaid 配色块（所有 flow 图共用）

把这段粘到任何 `flowchart` 末尾，颜色才与 PNG 一致：

```
    classDef context fill:#F1F5F9,stroke:#64748B,color:#1F2937
    classDef gap fill:#FEF3C7,stroke:#B45309,color:#7C2D12
    classDef hypothesis fill:#DBEAFE,stroke:#1D4ED8,color:#1E3A5F
    classDef experiment fill:#CCFBF1,stroke:#0F766E,color:#134E4A
    classDef result fill:#EDE9FE,stroke:#6D28D9,color:#3B0764
    classDef interpretation fill:#FCE7F3,stroke:#BE185D,color:#831843
    classDef conclusion fill:#DCFCE7,stroke:#16A34A,color:#14532D
    classDef implication fill:#E0F2FE,stroke:#0284C7,color:#0C4A6E
    classDef risk fill:#FEE2E2,stroke:#DC2626,color:#7F1D1D
    classDef supplementary fill:#F5F5F4,stroke:#78716C,color:#292524
```

---

## V1　全文逻辑链主图（必做）

```json
{
  "kind": "flow",
  "lang": "zh",
  "title": "图 V1｜全文逻辑链",
  "subtitle": "分层：背景→空白→假说→实验→结果→结论；虚线=作者未补的缺口",
  "source": "Fig 【1–5】；Results §【2.1–2.5】；Table 【S1】",
  "layers": [
    {"name": "背景", "nodes": ["bg_1", "bg_2"]},
    {"name": "空白", "nodes": ["gap"]},
    {"name": "假说", "nodes": ["hyp"]},
    {"name": "实验", "nodes": ["exp_1", "exp_2", "exp_3"]},
    {"name": "结果", "nodes": ["res_1", "res_2", "res_3"]},
    {"name": "解读", "nodes": ["int_1"]},
    {"name": "结论", "nodes": ["con"]},
    {"name": "意义", "nodes": ["imp"]}
  ],
  "nodes": {
    "bg_1": {"label": "【已知事实 1】", "role": "context", "tag": "已知"},
    "bg_2": {"label": "【已知事实 2】", "role": "context", "tag": "已知"},
    "gap": {"label": "【前人未解决的问题】", "role": "gap", "tag": "Gap"},
    "hyp": {"label": "【核心假说】", "role": "hypothesis", "tag": "Hypothesis"},
    "exp_1": {"label": "【实验 1 及其方法】", "role": "experiment", "tag": "Fig 1"},
    "exp_2": {"label": "【实验 2 及其方法】", "role": "experiment", "tag": "Fig 2"},
    "exp_3": {"label": "【实验 3 及其方法】", "role": "experiment", "tag": "Fig 3"},
    "res_1": {"label": "【结果 1，带方向与幅度】", "role": "result", "tag": "Fig 1"},
    "res_2": {"label": "【结果 2】", "role": "result", "tag": "Fig 2"},
    "res_3": {"label": "【结果 3】", "role": "result", "tag": "Fig 3"},
    "int_1": {"label": "【作者对该结果的解读】", "role": "interpretation"},
    "con": {"label": "【核心结论】", "role": "conclusion"},
    "imp": {"label": "【领域意义/治疗指向】", "role": "implication"}
  },
  "edges": [
    {"from": "bg_1", "to": "gap", "type": "neutral"},
    {"from": "bg_2", "to": "gap", "type": "neutral"},
    {"from": "gap", "to": "hyp", "type": "neutral"},
    {"from": "hyp", "to": "exp_1", "type": "mechanism", "label": "机制型"},
    {"from": "exp_1", "to": "res_1", "type": "support"},
    {"from": "res_1", "to": "exp_2", "type": "extension", "label": "扩展型"},
    {"from": "res_1", "to": "exp_3", "type": "validation", "label": "验证型"},
    {"from": "exp_2", "to": "res_2", "type": "support"},
    {"from": "exp_3", "to": "res_3", "type": "support"},
    {"from": "res_2", "to": "int_1", "type": "support"},
    {"from": "int_1", "to": "con", "type": "leap", "label": "跳跃：【缺什么证据】"},
    {"from": "res_3", "to": "con", "type": "support"},
    {"from": "con", "to": "imp", "type": "application", "label": "应用型"}
  ]
}
```

对应的 Mermaid（同一结构，id 为 `snake_case`）：

```
flowchart TD
    accTitle: 全文逻辑链
    accDescr: 从已知背景到核心结论的分层推进，虚线标出作者未补的证据缺口。

    bg_1["已知：【事实 1】"]
    gap["空白：【问题】"]
    hyp["假说：【核心假说】"]
    exp_1["Fig 1｜【实验 1】"]
    res_1["【结果 1】"]
    exp_2["Fig 2｜【实验 2】"]
    res_2["【结果 2】"]
    con["结论：【核心结论】"]

    bg_1 --> gap
    gap --> hyp
    hyp -->|机制型| exp_1
    exp_1 --> res_1
    res_1 -->|扩展型| exp_2
    exp_2 --> res_2
    res_2 -.->|跳跃：缺【人体样本】证据| con
```

---

## V2　主干与分叉（必做）

把 V1 压到「读者记不住就说不出论文」的程度：假说 + 2–3 个关键实验 + 结论。侧枝实验合并成一个节点。

```json
{
  "kind": "flow",
  "lang": "zh",
  "title": "图 V2｜主干三步",
  "subtitle": "侧枝实验已折叠；只保留支撑结论不可省略的那几步",
  "source": "Fig 【1–3】；Results §【2.1–2.3】",
  "layers": [
    {"name": "起点", "nodes": ["hyp"]},
    {"name": "关键实验", "nodes": ["key_1", "key_2"]},
    {"name": "关键结果", "nodes": ["kres_1", "kres_2"]},
    {"name": "其余实验", "nodes": ["rest"]},
    {"name": "结论", "nodes": ["con"]}
  ],
  "nodes": {
    "hyp": {"label": "【假说】", "role": "hypothesis"},
    "key_1": {"label": "【不可省略的实验 A】", "role": "experiment", "tag": "Fig 1"},
    "key_2": {"label": "【不可省略的实验 B】", "role": "experiment", "tag": "Fig 2"},
    "kres_1": {"label": "【A 的结果】", "role": "result"},
    "kres_2": {"label": "【B 的结果】", "role": "result"},
    "rest": {"label": "支持性实验：【Fig 3–5 一句话概括】", "role": "supplementary"},
    "con": {"label": "【结论】", "role": "conclusion"}
  },
  "edges": [
    {"from": "hyp", "to": "key_1", "type": "mechanism"},
    {"from": "key_1", "to": "kres_1", "type": "support"},
    {"from": "kres_1", "to": "key_2", "type": "extension"},
    {"from": "key_2", "to": "kres_2", "type": "support"},
    {"from": "kres_1", "to": "con", "type": "support"},
    {"from": "kres_2", "to": "con", "type": "support"},
    {"from": "rest", "to": "con", "type": "support", "label": "支撑"}
  ]
}
```

---

## V3　正文↔图 映射二分图（必做）

```json
{
  "kind": "flow",
  "lang": "zh",
  "title": "图 V3｜正文段落与图的对应关系",
  "subtitle": "左=Results 小节/段落，右=图；无边的段落=正文没讲的图，无边的图=图没被正文解释",
  "source": "Results 全文；Fig 【1–5】；Fig 【S1–S6】",
  "layers": [
    {"name": "正文", "nodes": ["p1", "p2", "p3", "p4", "p5"]},
    {"name": "图", "nodes": ["f1", "f2", "f3", "f4", "fs1"]}
  ],
  "nodes": {
    "p1": {"label": "§2.1 第 1 段", "role": "context"},
    "p2": {"label": "§2.1 第 2 段", "role": "context"},
    "p3": {"label": "§2.2 第 1 段", "role": "context"},
    "p4": {"label": "§2.3 第 1 段", "role": "context"},
    "p5": {"label": "§2.4 第 1 段", "role": "context"},
    "f1": {"label": "Fig 1A–C", "role": "supplementary"},
    "f2": {"label": "Fig 2A–F", "role": "supplementary"},
    "f3": {"label": "Fig 3A–D", "role": "supplementary"},
    "f4": {"label": "Fig 4A–G", "role": "supplementary"},
    "fs1": {"label": "Fig S1", "role": "supplementary"}
  },
  "edges": [
    {"from": "p1", "to": "f1", "type": "support", "label": "对应"},
    {"from": "p2", "to": "f1", "type": "support", "label": "补充引用"},
    {"from": "p3", "to": "f2", "type": "support", "label": "对应"},
    {"from": "p3", "to": "f3", "type": "support", "label": "跨段引用"},
    {"from": "p4", "to": "f4", "type": "support", "label": "对应"},
    {"from": "p5", "to": "fs1", "type": "support", "label": "仅补充材料"},
    {"from": "p2", "to": "f2", "type": "contradiction", "label": "正文与图不符"}
  ]
}
```

在 `subtitle` 里显式统计：`共 X 段 / Y 图；未配对：…`——这个数字本身就是结论。

---

## V4　图注-正文一致性矩阵（必做）

行=图（建议主图逐张；小图按图合并），列固定四项，判定必须能指回原文。

```json
{
  "kind": "matrix",
  "lang": "zh",
  "title": "图 V4｜图注-正文一致性矩阵",
  "subtitle": "○ 一致　△ 正文超出图注　× 矛盾　– 不适用",
  "source": "各图图注与 Results 对应段落逐条比对，见附表 3.1",
  "rows": ["Fig 1A–C", "Fig 2A–F", "Fig 3A–D", "Fig 4A–G", "Fig S1"],
  "cols": ["图注自洽", "正文一致", "统计可查", "图像可辨"],
  "cells": [
    ["ok",   "ok",   "ok",   "ok"],
    ["ok",   "warn", "ok",   "ok"],
    ["warn", "bad",  "na",   "ok"],
    ["ok",   "ok",   "ok",   "warn"],
    ["ok",   "na",   "warn", "ok"]
  ],
  "legend": {"ok": "一致", "warn": "存疑/超出", "bad": "矛盾", "na": "不适用"}
}
```

判定口径（写清楚才不会变成主观打分）：

| 列 | ○ 一致 | △ 存疑 | × 矛盾 |
|---|---|---|---|
| 图注自洽 | 图注交代了 n、统计、误差线 | 缺其中一项 | 图注与图中标号/单位不符 |
| 正文一致 | 正文只说了图上看得见的 | 正文说了图上看不出的（如「punctate」） | 正文与图趋势相反 |
| 统计可查 | p 值/n/检验在正文或图注可查 | 部分缺失 | 文字数值与图不符 |
| 图像可辨 | 本条判断基于看图本身 | 判断基于图注而非图像（须注明） | 图不可辨/缺图 |

---

## V5　实验总览矩阵（必做）

```json
{
  "kind": "matrix",
  "lang": "zh",
  "title": "图 V5｜实验证据强度总览",
  "subtitle": "○ 有　△ 部分　× 缺　– 不适用",
  "source": "逐实验四要素拆解（第四节）；图号为对应数据来源",
  "rows": ["Exp 1 【名称】(Fig 1)", "Exp 2 【名称】(Fig 2)", "Exp 3 【名称】(Fig 4)"],
  "cols": ["在体证据", "正交验证", "剂量/时间梯度", "对照完备", "效应量可估"],
  "cells": [
    ["bad",  "warn", "ok",   "ok",   "ok"],
    ["ok",   "ok",   "warn", "ok",   "ok"],
    ["ok",   "na",   "bad",  "warn", "warn"]
  ],
  "legend": {"ok": "具备", "warn": "部分", "bad": "缺失", "na": "不适用"}
}
```

**这张图不能替代四要素拆解**，它只是让读者一眼看到「哪一行最虚」，然后翻到对应小节看证据。

---

## V6　论证强度阶梯（必做）

把 7.4 的数据→结论差距压成一张可扫视的格子。

```json
{
  "kind": "matrix",
  "lang": "zh",
  "title": "图 V6｜核心主张的证据充分性",
  "subtitle": "○ 充分　△ 部分　× 不足；括号内为支持该主张的图号",
  "source": "Discussion 首段核心主张逐条比对 Results 与图",
  "rows": ["主张 1【原文】", "主张 2【原文】", "主张 3【原文】"],
  "cols": ["主张在原文的位置", "直接证据 (Fig)", "因果性证据", "跨系统复现", "效应量"],
  "cells": [
    ["ok", "ok",   "warn", "bad",  "ok"],
    ["ok", "warn", "bad",  "bad",  "warn"],
    ["ok", "bad",  "na",   "na",   "bad"]
  ],
  "legend": {"ok": "充分", "warn": "部分", "bad": "不足", "na": "无此类证据"}
}
```

---

## V7　局限风险矩阵（必做）

x = 对**核心结论**的影响，y = 方法学严重程度。两轴都必须给出锚点，否则格子位置就是主观的。

```json
{
  "kind": "scatter",
  "lang": "zh",
  "title": "图 V7｜局限风险矩阵",
  "subtitle": "x=对核心结论的影响；y=方法学严重程度；锚点见 7.2 表",
  "source": "7.2 方法学局限表；每条局限对应到具体实验编号",
  "x_label": "对核心结论的影响 →", "y_label": "方法学严重程度 →",
  "quadrants": {"tl": "需正面回应", "tr": "致命", "bl": "可接受", "br": "应写进 limitation"},
  "points": [
    {"x": 0.30, "y": 0.25, "label": "单一细胞系", "status": "minor"},
    {"x": 0.55, "y": 0.45, "label": "抗体未经 KO 验证", "status": "moderate"},
    {"x": 0.78, "y": 0.35, "label": "多重比较未校正", "status": "major"},
    {"x": 0.88, "y": 0.85, "label": "无原位敲除", "status": "fatal"}
  ]
}
```

`status` 会改变点的配色：`fatal`/`major`/`moderate`/`minor`，另有 `strength` 供「优势」使用。

---

## V8　术语/机制关系图（必做）

```json
{
  "kind": "flow",
  "lang": "zh",
  "title": "图 V8｜本文用到的分子关系",
  "subtitle": "只画论文实际涉及的关系；每条边的证据强度在术语表中注明",
  "source": "Introduction 与 Discussion 的机制描述；Figure 【X】",
  "layers": [
    {"name": "配体/受体", "nodes": ["upar"]},
    {"name": "通路", "nodes": ["path_1", "path_2"]},
    {"name": "效应分子", "nodes": ["eff_1"]},
    {"name": "表型", "nodes": ["pheno"]},
    {"name": "干预", "nodes": ["drug"]}
  ],
  "nodes": {
    "upar": {"label": "uPAR (PLAUR)", "role": "context"},
    "path_1": {"label": "【通路 1】", "role": "hypothesis"},
    "path_2": {"label": "【通路 2】", "role": "hypothesis"},
    "eff_1": {"label": "【效应分子】", "role": "experiment"},
    "pheno": {"label": "【表型：侵袭/转移】", "role": "result"},
    "drug": {"label": "【干预手段】", "role": "implication"}
  },
  "edges": [
    {"from": "upar", "to": "path_1", "type": "mechanism", "label": "本文证据"},
    {"from": "upar", "to": "path_2", "type": "leap", "label": "文献推断，本文未验"},
    {"from": "path_1", "to": "eff_1", "type": "mechanism"},
    {"from": "eff_1", "to": "pheno", "type": "support"},
    {"from": "drug", "to": "upar", "type": "application", "label": "靶向"}
  ]
}
```

本文没验证、只是引用的关系**必须画成虚线**，否则这张图会替作者说出他没说的话。

---

## V9　替代假说判别树（条件）

```json
{
  "kind": "tree",
  "lang": "zh",
  "title": "图 V9｜替代解释与判别实验",
  "subtitle": "每个分支给出一个能判别的实验；作者未排除的分支用虚线连回结论",
  "source": "7.5 替代假说；对应图号的现有数据",
  "layers": [
    {"name": "观察", "nodes": ["obs"]},
    {"name": "解释", "nodes": ["h_auth", "h_alt1", "h_alt2"]},
    {"name": "预测", "nodes": ["p_auth", "p_alt1", "p_alt2"]},
    {"name": "判别", "nodes": ["t_1", "t_2"]},
    {"name": "状态", "nodes": ["open"]}
  ],
  "nodes": {
    "obs": {"label": "【观察到的现象】", "role": "result"},
    "h_auth": {"label": "作者解释：【…】", "role": "hypothesis"},
    "h_alt1": {"label": "替代 1：【…】", "role": "risk"},
    "h_alt2": {"label": "替代 2：【…】", "role": "risk"},
    "p_auth": {"label": "预测：【…】", "role": "interpretation"},
    "p_alt1": {"label": "预测：【…】", "role": "interpretation"},
    "p_alt2": {"label": "预测：【…】", "role": "interpretation"},
    "t_1": {"label": "判别实验 1：【…】", "role": "experiment"},
    "t_2": {"label": "判别实验 2：【…】", "role": "experiment"},
    "open": {"label": "现状：【已有数据是否已排除】", "role": "gap"}
  },
  "edges": [
    {"from": "obs", "to": "h_auth", "type": "support"},
    {"from": "obs", "to": "h_alt1", "type": "leap", "label": "未被讨论"},
    {"from": "obs", "to": "h_alt2", "type": "leap", "label": "未被讨论"},
    {"from": "h_auth", "to": "p_auth", "type": "support"},
    {"from": "h_alt1", "to": "p_alt1", "type": "support"},
    {"from": "h_alt2", "to": "p_alt2", "type": "support"},
    {"from": "p_auth", "to": "t_1", "type": "validation"},
    {"from": "p_alt1", "to": "t_2", "type": "validation"},
    {"from": "t_1", "to": "open", "type": "neutral"},
    {"from": "t_2", "to": "open", "type": "neutral"}
  ]
}
```

---

## V10　入组/队列流程图（条件：临床、队列、患者样本）

人数必须闭合：每个节点的 n 与其上游一致，排除原因写在节点里。

```json
{
  "kind": "flow",
  "lang": "zh",
  "title": "图 V10｜样本入组与分组",
  "subtitle": "每个节点人数闭合；排除原因来自论文原文",
  "source": "Methods 患者队列；Fig 【1A】流程图；Table 【S2】",
  "layers": [
    {"name": "筛查", "nodes": ["screen"]},
    {"name": "排除", "nodes": ["excl"]},
    {"name": "入组", "nodes": ["enrol"]},
    {"name": "分组", "nodes": ["grp_1", "grp_2"]},
    {"name": "分析", "nodes": ["ana"]}
  ],
  "nodes": {
    "screen": {"label": "筛查 n=【N】", "role": "context"},
    "excl": {"label": "排除 n=【n】：【原因】", "role": "gap"},
    "enrol": {"label": "入组 n=【N】", "role": "hypothesis"},
    "grp_1": {"label": "【组 1】 n=【n】", "role": "experiment"},
    "grp_2": {"label": "【组 2】 n=【n】", "role": "experiment"},
    "ana": {"label": "纳入分析 n=【N】", "role": "result"}
  },
  "edges": [
    {"from": "screen", "to": "excl", "type": "elimination", "label": "排除型"},
    {"from": "screen", "to": "enrol", "type": "support"},
    {"from": "enrol", "to": "grp_1", "type": "support"},
    {"from": "enrol", "to": "grp_2", "type": "support"},
    {"from": "grp_1", "to": "ana", "type": "support"},
    {"from": "grp_2", "to": "ana", "type": "support"}
  ]
}
```

---

## V11　实验推进时间线（可选）

```json
{
  "kind": "timeline",
  "lang": "zh",
  "title": "图 V11｜实验推进阶段",
  "subtitle": "条形只表示推进顺序与跨度，不代表真实耗时",
  "source": "Results 小节顺序；各阶段对应图号",
  "x_label": "推进顺序 →",
  "phases": [
    {"label": "发现", "start": 0, "end": 2, "status": "experiment", "note": "表达谱/临床相关性", "ref": "Fig 1"},
    {"label": "功能", "start": 2, "end": 4.5, "status": "result", "note": "敲除 + 回复", "ref": "Fig 2–3"},
    {"label": "在体", "start": 4.5, "end": 6.5, "status": "experiment", "note": "原位模型/生存", "ref": "Fig 4"},
    {"label": "转化", "start": 6.5, "end": 8, "status": "application", "note": "靶向/联合", "ref": "Fig 5"}
  ]
}
```

`subtitle` 里那句「不代表真实耗时」必须在报告里保留——否则读者会把它当时间轴读。

---

## 生成命令一览

```bash
# 首次使用先自检（四类样图 + source 规则）
python scripts/render-diagram.py --selftest --tmp /tmp/diagram-check

# 一张一张渲染；--mermaid 同时落一份文本真源
python scripts/render-diagram.py figures/V1.json --out figures/V1-logic-chain.png --mermaid figures/V1-logic-chain.mmd
python scripts/render-diagram.py figures/V4.json --out figures/V4-consistency-matrix.png
python scripts/render-diagram.py figures/V5.json --out figures/V5-experiment-overview.png
python scripts/render-diagram.py figures/V6.json --out figures/V6-claim-evidence.png
python scripts/render-diagram.py figures/V7.json --out figures/V7-risk-map.png
python scripts/render-diagram.py figures/V8.json --out figures/V8-mechanism-map.png
```
