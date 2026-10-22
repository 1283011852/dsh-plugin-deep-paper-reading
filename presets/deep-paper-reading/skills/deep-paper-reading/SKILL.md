---
name: deep-paper-reading
description: Use when asked to deeply read, analyze, or break down a single biomedical research paper — including when the user says "读论文", "精读", "read this paper", "analyze this paper", "journal club prep", "帮我读这篇文献", or provides a PDF/URL/DOI of a biomedical paper and wants a detailed breakdown of every figure, every experiment, and the full logic chain. Also use when the user mentions supplementary materials analysis, figure-by-figure reading, experimental protocol extraction from a paper, wants the paper's logic chain drawn as a flowchart/diagram rather than described in prose, wants the reading visualized (consistency matrices, risk maps, claim-evidence charts), or asks for the report exported to Word/DOCX. NOT for multi-paper literature reviews (use literature-review), NOT for formal peer review (use peer-review), NOT for searching for papers (use paper-lookup).
allowed-tools: Read Write Edit Bash
license: MIT
metadata: {version: "1.1", skill-author: "user"}
---

# Deep Paper Reading

## Overview

**Core principle: Read a biomedical paper as if you're preparing to present it at journal club — leave nothing unexamined, and show the structure instead of describing it.**

Every figure, every experiment, every sentence in the results section must be mapped, understood, and connected to the paper's overall logic chain. This is not skimming. This is not summarizing. This is complete structural decomposition — delivered **as diagrams plus evidence tables**, not as prose about diagrams.

A text-only logic chain is an incomplete deliverable. The reader of a close reading has to see, in one glance, which experiment followed which, why, and where the chain breaks. That is a flowchart (V1), not a paragraph.

## When to Use This Skill

Use this skill when the task is **deep single-paper analysis**:

- User asks to "read this paper" and wants more than a summary
- User says "精读" (deep read), "拆解" (break down), "逐图分析" (figure-by-figure)
- User is preparing for journal club, lab meeting, or research discussion
- User provides a paper PDF/URL and asks for experimental details
- User mentions supplementary materials / supplemental figures
- User wants to understand "how they did this experiment" or "what this figure shows"
- User asks for the logic chain **as a diagram**, or for the report **as Word**

**Do NOT use this skill for:**
- Multi-paper literature synthesis → use `literature-review`
- Formal peer review / manuscript evaluation → use `peer-review`
- Evaluating evidence quality / bias detection alone → use `scientific-critical-thinking`
- Paper search / discovery → use `paper-lookup`
- Quick one-paragraph summaries → just summarize directly

## Bundled files — read these before Phase 1

| File | What it is | When |
|---|---|---|
| `references/reading-checklist.md` | Per-phase checklist, one item per thing that must not be skipped | Before starting; tick as you go |
| `assets/report-template.md` | The report template, with every required section | Phase 8 |
| `references/visualization-spec.md` | Which diagram goes where, Mermaid constraints, rendering ladder, palette | **Phase 7 — not optional** |
| `assets/diagram-specs.md` | Copy-paste JSON/Mermaid templates for V1–V11 | Phase 7 |
| `references/docx-conversion-standard.md` | The Word export standard: page setup, style matrix, table/figure rules, 25-item acceptance list | Any DOCX request |
| `references/biomedical-tools.md` | Technique/assay quick reference | Phases 4–5 |
| `scripts/render-diagram.py` | Offline diagram renderer (spec JSON → PNG + Mermaid) | Phase 7, ladder tier C |

## Core Workflow

Follow these phases in order. Do not skip phases. The output report builds cumulatively across phases.

### Phase 1: Paper Acquisition and Initial Scan

1. **Acquire the paper** — If given a URL/DOI, use WebFetch or paper-lookup to retrieve the full text. If given a PDF filename, read it. If supplementary materials are mentioned, acquire those too.
2. **Persist the full text** — write it to `sources/paper-fulltext.txt` before analysing, so quotes stay verifiable.
3. **First-pass scan** — Read in this order:
   - Title + Abstract (understand the headline)
   - Last paragraph of Introduction (find the hypothesis / research question)
   - Figure titles and legends (get the visual story)
   - First paragraph of Discussion (author's own summary of key findings)
   - Results section headers (map the experimental structure)
4. **Identify the paper type:** original research / methods / brief communication / review.
5. **Record basic metadata** — Authors, year, journal, DOI, corresponding author affiliation, funding, competing interests, and the evidence level you actually reached (full text / abstract only).

### Phase 2: Main Text Deep Reading

Read the entire main text **line by line**. Do not skim. For each section:

**Introduction:**
- What is the background context?
- What gap in knowledge does this paper address?
- What is the explicit hypothesis or research question?
- What is the significance if the hypothesis is correct?

**Results:**
- Read paragraph by paragraph
- For each paragraph: identify which figure(s) it references
- Cross-reference: does the text accurately describe what the figure shows?
- Note any data mentioned in text but NOT shown in figures ("data not shown")
- Flag any discrepancies between text claims and figure data

**Discussion:**
- How do authors interpret each key result?
- What limitations do they acknowledge (and what do they omit)?
- How do they connect findings to the broader field?
- What future experiments do they propose?

**Methods:**
- Read alongside results — which method produced which result?
- Extract complete experimental protocols (see Phase 5)
- Note statistical tests, sample sizes, replication levels
- Identify key reagents, antibodies, cell lines, animal models

### Phase 3: Supplementary Materials Deep Reading

Treat supplementary materials with the **same rigor as main figures** — they often contain the most detailed experimental information.

1. Read every supplementary figure and its legend
2. Read every supplementary table
3. Read supplementary methods/protocols in full
4. Map supplementary figures back to main text references
5. Note any key data relegated to supplementary

Anything referenced but not obtained is recorded as **缺失（正文引用但未获取）** — never silently dropped.

### Phase 4: Figure-to-Text Mapping

This is the signature step of deep reading. For **every figure** (main + supplementary):

```
For each figure panel (e.g., Fig 1A, Fig 1B, ...):
  1. Look at the image (render the page); then read the legend
  2. Find the paragraph(s) in Results that discuss this panel
  3. Identify: what does the text ADD beyond the legend?
  4. Note: does the text interpretation match what the figure actually shows?
  5. Record the exact line/sentence mapping
```

Output: the correspondence table (section 三) **plus two diagrams** — V3 (text↔figure bipartite map) and V4 (consistency matrix). A judgement that rests on the legend rather than the image must say so in the table's note column.

### Phase 5: Experiment-by-Experiment Decomposition

For **every experiment** in the paper, extract these four elements:

| Element | Questions to answer |
|---------|-------------------|
| **目的 (Purpose)** | What question does this experiment answer? Why was it done? Where does it fit in the logic chain? |
| **设计与工具 (Design & Tools)** | What was actually done? What techniques/instruments/reagents/cell lines/animal models? What are the controls? What is the sample size? |
| **结果 (Results)** | What data was obtained? What do the figures show? Are statistics reported correctly? What are the raw numbers? |
| **解读 (Interpretation)** | How do the authors interpret it? Is the interpretation justified? What alternatives exist? What does this MEAN for the story? |

Plus one matrix across all experiments — V5 (evidence strength overview), so a reader can see which experiment is the weakest row and jump to it.

### Phase 6: Logic Chain Reconstruction

Reconstruct the paper's complete logical architecture:

1. **Background → Gap → Hypothesis** — Why was this study done?
2. **Hypothesis → Experimental Design** — How did they test it?
3. **Experiment 1 → Result 1 → Interpretation 1 → Experiment 2** — How does each result lead to the next experiment?
4. **All Results → Main Conclusion** — Do the data collectively support the conclusion?
5. **Identify missing links** — Logical leaps? Unsupported claims? Assumptions treated as facts?

**Method:**

1. List all results in order of appearance
2. For each transition (Result N → Result N+1): ask "Why was the next experiment needed?"
3. Classify each transition:
   - **排除型 (Elimination)**: "Result A ruled out explanation X, so they tested Y"
   - **扩展型 (Extension)**: "Result A showed X in system 1, so they tested system 2"
   - **机制型 (Mechanism)**: "Result A showed correlation X-Y, so they tested causation"
   - **应用型 (Application)**: "Result A showed mechanism, so they tested therapeutic relevance"
   - **验证型 (Validation)**: "Result A used method X, so they confirmed with orthogonal method Y"
4. Flag every transition where the rationale is unclear — those become **dashed edges** in V1

Drafting note (not the deliverable): sketch the chain as an indented text skeleton first if it helps you think. The **deliverable** is V1/V2 as diagrams — see Phase 7. A text skeleton pasted into the report is not an acceptable substitute.

**Red flags in logic chains:**
- Missing controls that would distinguish between hypotheses
- Causal claims without perturbation experiments
- In vitro → in vivo extrapolation without justification
- A single experiment supporting multiple conclusions (over-interpretation)
- Gaps where no experiment addresses an obvious alternative explanation

### Phase 7: Visualization Assembly (mandatory — 8 required figures)

Reading `references/visualization-spec.md` is required before this phase. Summary of the contract:

**Three hard rules**

1. **图与数据并存** — a diagram never replaces its evidence table; the table holds n, p, catalog numbers, original sentences.
2. **可溯源** — every figure carries a `来源：` line naming the figure panel / Results paragraph / supplementary item. The renderer refuses a spec without `source`.
3. **失败要标注** — a missing renderer, a missing CJK font, a supplementary item not obtained: all stated explicitly. No ASCII pretending to be a flowchart, no silent blank placeholder.

**Required figures (V1–V8), conditional (V9–V12)** — full table in `references/visualization-spec.md §2`. In short: V1 full-paper logic chain, V2 trunk-only, V3 text↔figure map, V4 consistency matrix, V5 experiment overview, V6 claim-evidence ladder, V7 limitation risk map, V8 term/mechanism map. V9 alternative-hypothesis tree (when alternatives exist), V10 cohort flow (clinical/cohort papers), V11 timeline (optional), V12 radar (**default: do not draw** — false precision).

**Rendering ladder** — try in order, stop at the first that works, and record which tier was used in each figure's caption:

| Tier | Tool | Note |
|---|---|---|
| A | `mmdc` (mermaid-cli) | best fidelity for complex graphs |
| B | `npx -y @mermaid-js/mermaid-cli` | needs Node + network |
| C | `python scripts/render-diagram.py spec.json --out fig.png --mermaid fig.mmd` | offline, Pillow only, 4 kinds: flow/matrix/scatter/timeline |
| D | not rendered | keep Mermaid source, write 「图形未渲染（原因）」 at the image position |

First use in a session: `python scripts/render-diagram.py --selftest --tmp /tmp/diagram-check`. If it reports `no CJK font found`, Chinese labels will be boxes — switch to tier A or install a font. Never ship box-glyph figures.

**Verification before moving on:** every required PNG exists, width ≥ 1200 px, Chinese renders as real glyphs, and each figure has a three-line caption (说明 / 缺口 / 来源+档位).

### Phase 8: Report Generation

Assemble the report with `assets/report-template.md`. Write in the user's preferred language (Chinese if the user communicates in Chinese; English otherwise). The report must be self-contained — someone who hasn't read the paper should understand everything, including the figures.

When the user asks for Word/DOCX:

1. Load the `docx` (or `office-docx`) skill.
2. Follow `references/docx-conversion-standard.md` **as a standard, not a suggestion** — page setup, the style matrix, table column limits, the three-line figure caption, the `○ △ × –` glyph set, and the 25-item acceptance list.
3. Convert: freeze the Markdown → render every figure → check each PNG → build styles first, then content → insert pictures inline with alt text → page numbers + TOC field → document properties.
4. Verify by looking: convert to PDF and check pages for font fallback, table overflow, blurry images, and whether the 「缺失/存疑」 callouts survived.
5. Confirm the file exists at the stated path with a real byte count before claiming delivery. State which figures were rendered and which were not.

## Output Report Structure

Every reading report must contain these sections. Use the detailed template at `assets/report-template.md` for the full structure.

**1. 论文概览 (Paper Overview)** — metadata table, one-sentence finding, research type and design, evidence level reached.

**2. 文章逻辑链条 (Logic Chain)** — **图 V1 全文逻辑链** + **图 V2 主干** (Mermaid source + rendered PNG), the transition table with each edge classified, and a separate list of leaps/unaddressed alternatives.

**3. 图注与正文对应 (Figure-Text Mapping)** — the mapping table **plus** 图 V3 (bipartite map) and 图 V4 (consistency matrix).

**4. 逐实验拆解 (Experiment-by-Experiment Breakdown)** — four elements per experiment, plus 图 V5 (evidence overview) and, where triggered, 图 V10/V11.

**5. 补充材料分析 (Supplementary Analysis)** — same structure applied to every supplementary item, with 缺失 items marked.

**6. 方法与统计评估 (Methods & Statistics Assessment)** — technique appropriateness, statistics, controls, reproducibility; verdict grid.

**7. 批判性评读 (Critical Reading)** — strengths; limitations (acknowledged + omitted); **图 V6 claim-evidence ladder**; **图 V7 limitation risk map**; 图 V9 alternative-hypothesis tree when alternatives exist; data-to-conclusion gap; unanswered questions.

**8. 关键术语表 (Key Terminology)** — terms + **图 V8 mechanism/term relation map**.

**附录** — Mermaid sources and diagram specs, so every figure is reproducible.

## Figure-Text Mapping: How To

The most common failure in paper reading is treating figures and text as separate narratives. The mapping process forces integration:

```
Step 1: Look at the figure image. Then read the legend — the legend describes WHAT is shown.
Step 2: Search the Results text for figure references — the text explains WHY it matters.
Step 3: Compare text claims to visual data: what does the reader see vs. what do the authors say?
Step 4: Record in the mapping table (and carry the verdict into V4).
```

**Example mapping entry:**

| Fig | Legend Summary | Text Location | What Text Adds | Notes |
|-----|---------------|---------------|----------------|-------|
| 1A | Western blot of Protein X in WT and KO cells | Results §2.1, para 2 | Quantifies band intensity (n=3), reports p=0.003 | Text says "significant decrease" but bands look similar — check quantification in Fig S1; judgement from legend, not densitometry |
| 1B | Immunofluorescence of Protein X localization | Results §2.1, para 3 | Describes "punctate cytoplasmic staining" not obvious from the image | Text over-reads the image → △ in V4 |

**What to flag:**
- Text describes results not visible in the figure
- Text minimizes or omits contradictory data points
- Statistics reported in text don't match figure error bars / n values
- Text makes causal claims from correlational data
- Figure legend and text give different interpretations

## Experiment Decomposition: The Four-Element Rule

Every experiment in a biomedical paper can be decomposed into exactly four elements. Never leave an experiment without answering all four.

### 1. 目的 (Purpose)
- What specific question does this experiment address?
- Is it hypothesis-testing or hypothesis-generating?
- Is it a main experiment, validation, or control?

### 2. 设计与工具 (Design & Tools)
- **Model system**: cell line (name, source, authentication status), animal model (strain, age, sex, n), patient samples (cohort, inclusion criteria, n), in vitro system
- **Technique**: Western blot, qPCR, RNA-seq, ChIP-seq, CRISPR/Cas9, ELISA, flow cytometry, microscopy (type, magnification), behavioral assay, etc.
- **Reagents**: antibodies (clone, vendor, catalog #, dilution), primers, drugs (name, concentration, vendor), plasmids/vectors
- **Controls**: positive, negative, vehicle, loading, isotype — what is the baseline being compared against?
- **Statistics**: test, n (biological vs technical), error bars (SD/SEM/CI), significance threshold, software
- **Protocol source**: methods section, supplementary, cited reference

### 3. 结果 (Results)
- What data was obtained? Quote actual numbers where possible.
- Which figure panel(s) show this data?
- Statistical outcomes: exact p-values, effect sizes, confidence intervals
- Any unexpected or negative results?
- Data quality: visible issues with blots, staining, measurements?

### 4. 解读 (Interpretation)
- **Author's interpretation**: what do they say this means?
- **Does the data support this?**: is the interpretation proportionate?
- **Alternative interpretations**: could the data mean something else?
- **What would confirm this?**: which additional experiment would nail it down?
- **Position in logic chain**: how does this connect to the next experiment?

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Summarizing the abstract instead of reading the paper | Read the full paper — the abstract is the trailer, not the movie |
| Skipping supplementary materials | Supplementary data is often more detailed and important than main figures |
| Accepting author interpretations uncritically | Distinguish what the data SHOWS from what authors SAY it shows |
| Treating figures and text separately | Map every figure to its text reference |
| Omitting experimental detail | List actual reagents, models, n values |
| Summarizing study-by-study instead of tracing the logic chain | Show how experiments connect |
| Not assessing statistical rigor | Check n, tests, error bars, missing statistics |
| **Describing the logic chain in prose (or an ASCII sketch) and calling it a diagram** | Draw V1/V2 for real; a text skeleton is a drafting note, not a deliverable |
| **Drawing a pretty diagram that hides the leap** | Dashed edges for leaps/contradictions are the point of V1 |
| **Letting a diagram replace the evidence table** | Figure indexes, table proves |
| **Numbers in a figure that appear nowhere in the paper** | Forbidden; every drawn fact traces to a panel/paragraph |
| **Shipping a figure with box-glyphs or a blank placeholder** | Check the PNG; if unrenderable, keep Mermaid + write 「未渲染（原因）」 |
| Writing the report in English when the user communicates in Chinese | Match the user's language |
| Producing a report missing required sections or figures | Use the template and the V1–V8 list |
| Claiming a DOCX was delivered without checking the path and byte count | Verify, then report; state which figures were rendered |

## Biomedical Domain Considerations

### When reading biomedical papers, pay special attention to:

1. **Model system relevance** — cell line (which? authenticated? mycoplasma-free?), animal model (strain? relation to human disease?), patient samples (how many? from where? what criteria?)
2. **Antibody validation** — validated for the application? Which controls (knockout, knockdown, peptide blocking)? An antibody without KO validation is a `major` point in V7.
3. **Blinding and randomization** — especially behavioral, histological, in vivo studies
4. **Biological vs. technical replicates** — n must be biological replicates; call out confusion explicitly
5. **Clinical relevance** — if translational claims are made, does the model recapitulate the human condition? That gap is usually a V6 `×`.
6. **Effect size vs. statistical significance** — in omics/clinical work, tiny p-values can accompany meaningless effects; look for effect sizes.

## Integration with Other Skills

- **scientific-critical-thinking** — bias detection, statistical evaluation, evidence grading
- **peer-review** — formal checklists (CONSORT, STROBE, ARRIVE)
- **experimental-design** — whether the design supports the claimed conclusions
- **literature-review** — placing the paper in the broader literature afterwards
- **paper-lookup** — retrieving papers by DOI/title/URL
- **markdown-mermaid-writing** — Mermaid syntax and style conventions
- **docx / office-docx** — producing the Word deliverable per the conversion standard

## Dependencies

- **PDF reading**: `pdf` or `markitdown` skill for text extraction; render figure pages to images before judging them
- **Diagram rendering**: tier A `mmdc` / tier B `npx @mermaid-js/mermaid-cli`; tier C needs only Pillow (`pip install pillow`) and a CJK font
- **Word export**: `docx` or `office-docx` skill
- **Supplementary data**: direct reading of Excel/CSV; image inspection for supplementary figures

## Resources

### Bundled resources
- `assets/report-template.md` — complete Chinese report template
- `assets/diagram-specs.md` — copy-paste specs and Mermaid templates for V1–V11
- `references/reading-checklist.md` — the per-phase checklist
- `references/visualization-spec.md` — diagram inventory, selection guide, Mermaid constraints, palette, anti-patterns
- `references/docx-conversion-standard.md` — the Word conversion standard
- `references/biomedical-tools.md` — technique quick reference
- `scripts/render-diagram.py` — offline renderer (spec JSON → PNG + Mermaid), with `--selftest`
