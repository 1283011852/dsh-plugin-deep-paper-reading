---
name: deep-paper-reading
description: Use when asked to deeply read, analyze, or break down a single biomedical research paper — including when the user says "读论文", "精读", "read this paper", "analyze this paper", "journal club prep", "帮我读这篇文献", or provides a PDF/URL/DOI of a biomedical paper and wants a detailed breakdown of every figure, every experiment, and the full logic chain. Also use when the user mentions supplementary materials analysis, figure-by-figure reading, or experimental protocol extraction from a paper. NOT for multi-paper literature reviews (use literature-review), NOT for formal peer review (use peer-review), NOT for searching for papers (use paper-lookup).
allowed-tools: Read Write Edit Bash
license: MIT
metadata: {version: "1.0", skill-author: "user"}
---

# Deep Paper Reading

## Overview

**Core principle: Read a biomedical paper as if you're preparing to present it at journal club — leave nothing unexamined.** Every figure, every experiment, every sentence in the results section must be mapped, understood, and connected to the paper's overall logic chain. This is not skimming. This is not summarizing. This is complete structural decomposition.

## When to Use This Skill

Use this skill when the task is **deep single-paper analysis**:

- User asks to "read this paper" and wants more than a summary
- User says "精读" (deep read), "拆解" (break down), "逐图分析" (figure-by-figure)
- User is preparing for journal club, lab meeting, or research discussion
- User provides a paper PDF/URL and asks for experimental details
- User mentions supplementary materials / supplemental figures
- User wants to understand "how they did this experiment" or "what this figure shows"

**Do NOT use this skill for:**
- Multi-paper literature synthesis → use `literature-review`
- Formal peer review / manuscript evaluation → use `peer-review`
- Evaluating evidence quality / bias detection alone → use `scientific-critical-thinking`
- Paper search / discovery → use `paper-lookup`
- Quick one-paragraph summaries → just summarize directly

## Core Workflow

Follow these phases in order. Do not skip phases. The output report builds cumulatively across phases.

### Phase 1: Paper Acquisition and Initial Scan

1. **Acquire the paper** — If given a URL/DOI, use WebFetch or paper-lookup to retrieve the full text. If given a PDF filename, read it. If supplementary materials are mentioned, acquire those too.

2. **First-pass scan** — Read in this order:
   - Title + Abstract (understand the headline)
   - Last paragraph of Introduction (find the hypothesis / research question)
   - Figure titles and legends (get the visual story)
   - First paragraph of Discussion (author's own summary of key findings)
   - Results section headers (map the experimental structure)

3. **Identify the paper type:**
   - Original research article (most common)
   - Methods/protocol paper
   - Brief communication / letter
   - Review (if review: note this is NOT the primary target, but can still be read)

4. **Record basic metadata** — Authors, year, journal, DOI, corresponding author affiliation, funding sources, competing interests.

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
- Extract complete experimental protocols (see Phase 4)
- Note statistical tests used, sample sizes, replication levels
- Identify key reagents, antibodies, cell lines, animal models

### Phase 3: Supplementary Materials Deep Reading

Treat supplementary materials with the **same rigor as main figures** — they often contain the most detailed experimental information.

1. Read every supplementary figure and its legend
2. Read every supplementary table
3. Read supplementary methods/protocols in full
4. Map supplementary figures back to main text references
5. Note any key data relegated to supplementary (often the most controlled/technical experiments)

### Phase 4: Figure-to-Text Mapping

This is the signature step of deep reading. For **every figure** (main + supplementary):

```
For each figure panel (e.g., Fig 1A, Fig 1B, ...):
  1. Read the figure legend description
  2. Find the paragraph(s) in Results that discuss this panel
  3. Identify: what does the text ADD beyond the legend?
  4. Note: does the text interpretation match what the figure actually shows?
  5. Record the exact line/sentence mapping
```

Build a complete correspondence table (see Output Report Structure).

### Phase 5: Experiment-by-Experiment Decomposition

For **every experiment** in the paper, extract these four elements:

| Element | Questions to answer |
|---------|-------------------|
| **Purpose** | What question does this experiment answer? Why was it done? Where does it fit in the logic chain? |
| **Design & Tools** | What was actually done? What techniques/instruments/reagents/cell lines/animal models? What are the controls? What is the sample size? |
| **Results** | What data was obtained? What do the figures show? Are statistics reported correctly? What are the raw numbers? |
| **Interpretation** | How do the authors interpret the result? Is the interpretation justified by the data? What alternative interpretations exist? What does this result MEAN for the overall story? |

### Phase 6: Logic Chain Reconstruction

Reconstruct the paper's complete logical architecture:

1. **Background → Gap → Hypothesis** — Why was this study done?
2. **Hypothesis → Experimental Design** — How did they test it?
3. **Experiment 1 → Result 1 → Interpretation 1 → Experiment 2** — How does each result lead to the next experiment?
4. **All Results → Main Conclusion** — Do the data collectively support the conclusion?
5. **Identify missing links** — Are there logical leaps? Unsupported claims? Assumptions treated as facts?

Draw the logic chain as a flow:

```
Background knowledge
   ↓
Knowledge gap identified
   ↓
Hypothesis / Research question
   ↓
Experimental approach chosen (why this approach?)
   ↓
Experiment 1 ──→ Result 1 ──→ Interpretation 1
   ↓                              ↓
Experiment 2 ──→ Result 2 ──→ Interpretation 2
   ↓                              ↓
   ...                            ...
   ↓
Synthesis of all results
   ↓
Main conclusion(s)
   ↓
Broader implications / Future directions
```

### Phase 7: Report Generation

Assemble the complete reading report using the template structure below. Write in the user's preferred language (Chinese if the user communicates in Chinese; English otherwise). The report must be self-contained — someone who hasn't read the paper should understand everything.

## Output Report Structure

Every reading report must contain these sections. Use the detailed template at `assets/report-template.md` for the full structure.

### Required sections:

**1. 论文概览 (Paper Overview)**
- Title, authors, year, journal, DOI
- One-sentence core finding
- Research type and design
- Overall significance assessment

**2. 文章逻辑链条 (Logic Chain)**
- Complete logical flow from background to conclusion
- Visual flow diagram (text-based)
- Key decision points: why each experiment was done

**3. 图注与正文对应表 (Figure-Text Mapping)**
- Table: Figure | Legend Summary | Main Text Reference (section/paragraph) | What Text Adds | Discrepancies (if any)

**4. 逐实验拆解 (Experiment-by-Experiment Breakdown)**
For each experiment/result section:
- Purpose and hypothesis
- Experimental design: what, how, controls, sample size
- Tools/techniques/reagents used (full detail)
- Results obtained (data, statistics, figure reference)
- Author's interpretation
- Critical assessment: is the interpretation justified?
- Position in logic chain

**5. 补充材料分析 (Supplementary Materials Analysis)**
- Same structure as main text, applied to all supplementary items

**6. 方法与统计评估 (Methods & Statistics Assessment)**
- Key techniques used and their appropriateness
- Statistical methods evaluation
- Controls and validation quality
- Reproducibility assessment

**7. 批判性评读 (Critical Reading)**
- Strengths of the study
- Limitations (acknowledged and unacknowledged)
- Data-to-conclusion gap analysis
- Alternative interpretations
- Unanswered questions
- Relationship to other work in the field

**8. 关键术语表 (Key Terminology)**
- Domain-specific terms and abbreviations
- Techniques requiring background knowledge
- Pathway/gene/protein names and their relationships

## Figure-Text Mapping: How To

The most common failure in paper reading is treating figures and text as separate narratives. The mapping process forces integration:

**For each figure in the paper:**

```
Step 1: Read the figure legend carefully.
        The legend describes WHAT is shown.

Step 2: Search the Results text for figure references.
        The text explains WHY it matters and HOW to interpret it.

Step 3: Compare text claims to visual data.
        What does the reader see vs. what the authors say?

Step 4: Record in the mapping table.
```

**Example mapping entry:**

| Fig | Legend Summary | Text Location | What Text Adds | Notes |
|-----|---------------|---------------|----------------|-------|
| 1A | Western blot of Protein X in WT and KO cells | Results §2.1, para 2 | Quantifies band intensity (n=3), reports p=0.003 | Text mentions "significant decrease" but bands appear similar — check quantification in supp. fig S1 |
| 1B | Immunofluorescence of Protein X localization | Results §2.1, para 3 | Describes "punctate cytoplasmic staining" not obvious from image | Text interpretation consistent with figure |

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
- **Reagents**: antibodies (clone, vendor, catalog #, dilution), primers (sequences if given), drugs (name, concentration, vendor), plasmids/vectors
- **Controls**: positive control, negative control, vehicle control, loading control, isotype control — what is the baseline being compared against?
- **Statistics**: test used, n (biological vs technical replicates), error bars (SD/SEM/CI), significance threshold, software used
- **Protocol source**: from methods section, from supplementary, from cited reference

### 3. 结果 (Results)
- What data was obtained? Quote actual numbers where possible.
- Which figure panel(s) show this data?
- Statistical outcomes: exact p-values, effect sizes, confidence intervals
- Any unexpected or negative results?
- Data quality: any visible issues with blots, staining, or measurements?

### 4. 解读 (Interpretation)
- **Author's interpretation**: what do they say this result means?
- **Does the data support this?**: Is the interpretation proportionate to the data?
- **Alternative interpretations**: could the data mean something else?
- **What would confirm this?**: what additional experiment would nail down the conclusion?
- **Position in logic chain**: how does this result connect to the next experiment?

## Logic Chain Reconstruction: How To

The logic chain is the **narrative spine** of the paper. It answers: "Why did they do experiment B after experiment A?"

**Method:**

1. List all the results in order of appearance
2. For each transition (Result N → Result N+1): ask "Why was the next experiment needed?"
3. Classify each transition:
   - **Elimination**: "Result A ruled out explanation X, so they tested explanation Y"
   - **Extension**: "Result A showed X in system 1, so they tested whether X also happens in system 2"
   - **Mechanism**: "Result A showed correlation X-Y, so they tested whether X causes Y"
   - **Application**: "Result A showed mechanism, so they tested therapeutic relevance"
   - **Validation**: "Result A used method X, so they confirmed with orthogonal method Y"
4. Flag any transition where the rationale is unclear

**Red flags in logic chains:**
- Missing controls that would distinguish between hypotheses
- Causal claims without perturbation experiments
- In vitro → in vivo extrapolation without justification
- A single experiment supporting multiple conclusions (over-interpretation)
- Gaps where no experiment addresses an obvious alternative explanation

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Summarizing the abstract instead of reading the paper | Read the full paper — the abstract is the trailer, not the movie |
| Skipping supplementary materials | Supplementary data is often more detailed and important than main figures |
| Accepting author interpretations uncritically | Distinguish between what the data SHOWS and what authors SAY it shows |
| Treating figures and text separately | Map every figure to its text reference — they tell different parts of the same story |
| Omitting experimental detail | List actual reagents, models, n values — these determine whether results are believable |
| Summarizing study-by-study instead of tracing the logic chain | Show how experiments connect, not just what each one found |
| Not assessing statistical rigor | Check n values, test appropriateness, error bar definitions, missing statistics |
| Writing report in English when user communicates in Chinese | Match the user's language for readability |
| Producing a report missing required sections | Use the template — every section matters |

## Biomedical Domain Considerations

### When reading biomedical papers, pay special attention to:

1. **Model system relevance**: Is it a cell line (which one? authenticated? mycoplasma-free?), animal model (which strain? how does it relate to human disease?), or patient sample (how many? from where? what criteria?)

2. **Antibody validation**: Are antibodies validated for the application? What controls were used (knockout, knockdown, peptide blocking)?

3. **Blinding and randomization**: Were experiments blinded? Were animals/samples randomized to groups? This is especially important for behavioral, histological, and in vivo studies.

4. **Biological vs. technical replicates**: Are the n values biological replicates (independent experiments/samples) or technical replicates (same sample measured multiple times)? Biological replicates are what matter.

5. **Clinical relevance**: If the paper claims clinical/translational relevance, does the model actually recapitulate the human condition? What is the gap between the model and the clinic?

6. **Effect size vs. statistical significance**: In large-scale omics or clinical studies, p-values can be tiny even for biologically meaningless effects. Look for effect sizes and clinical significance, not just statistical significance.

## Integration with Other Skills

Use related skills for deeper analysis of specific aspects:

- **scientific-critical-thinking** — For rigorous bias detection, statistical evaluation, and evidence quality grading
- **peer-review** — For formal evaluation checklists (CONSORT, STROBE, ARRIVE compliance)
- **experimental-design** — For evaluating whether the experimental design supports the claimed conclusions
- **literature-review** — When the user wants to follow up by placing this paper in the broader literature context
- **paper-lookup** — For retrieving papers by DOI, title, or URL

## Dependencies

### For PDF reading:
- **pdf** skill or `markitdown` skill for extracting text from PDF files
- WebFetch for retrieving papers from URLs

### For supplementary data:
- Direct reading of Excel/CSV supplementary tables (use Read tool)
- Image inspection of supplementary figures (Read tool handles PNG/JPG)

## Resources

### Bundled resources:
- `assets/report-template.md` — Complete report template in Chinese, with all sections and guiding prompts
- `references/reading-checklist.md` — Checklist to ensure no element is missed during deep reading
- `references/biomedical-tools.md` — Quick reference of common biomedical techniques and what to look for when evaluating them
