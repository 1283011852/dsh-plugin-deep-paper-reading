# Design sources

This preset packages the author's own `deep-paper-reading` skill (文献精读 / Deep Paper Reading) as a DSH agent preset, so the capability is `skill`-invocable instead of having to be read off disk by hand.

## Composition

The Cordis composition is a copy of the locally authored `scientific-evidence-en-mode` preset — that composition already supplies exactly the capability surface a close reading needs (filesystem, shell, file search, web fetch, skills, todos, goals, jobs, compaction, user questions) — with three changes:

- the persona row is rewritten as the Deep Paper Reading protocol: mandatory skill load, evidence boundary, four-element experiment decomposition, logic-chain reconstruction, **a VISUALS clause mandating eight drawn figures**, and output conventions (report in `paper-reading/`, figures in `paper-reading/figures/`, DOCX per the bundled standard);
- the `skill-filesystem` row gains a `customSkillDirs` entry pointing at this preset's bundled `skills/` directory, so `deep-paper-reading` resolves as a real skill through the skill tool rather than as a file the agent has to find;
- nothing else is touched.

`baseUrl` in that row's `!!js` expression is the composition's own directory, which the preset `Include` sets before the subtree is mounted — so the bundled skill root travels with the preset whether it is mounted from the user preset root, from this plugin's `presets/` directory, or from an imported `.dshpreset` archive.

## Bundled skill

`skills/deep-paper-reading/` is the author's own skill (MIT, `skill-author: user`).

**Status change in v0.2.0: this is no longer a verbatim copy.** It was one up to v0.1.0, and the README said so; the current version is edited by the author. What changed and why:

| File | Change | Reason |
|---|---|---|
| `SKILL.md` | 7 → 8 phases; new **Phase 7 Visualization Assembly**; Phase 6 keeps its method but no longer accepts a text/ASCII chain as the deliverable | The logic chain is the spine of a close reading, and a reader cannot see a spine in prose. The text skeleton is now explicitly a *drafting note*. |
| `SKILL.md` | V1–V8 required-figure contract; V9/V10 conditional; V12 discouraged | Journals club readers need *judgement* views too, not only structure: consistency, strength, gap, risk. V12 is discouraged because a radar score over heterogeneous evidence manufactures precision. |
| `references/visualization-spec.md` | new | One place that decides which figure belongs to which section, the Mermaid constraints, the rendering ladder, the palette, and the anti-patterns. Without it "add a diagram" produces decorative diagrams. |
| `assets/diagram-specs.md` | new | Copy-paste specs so eight figures per report stays cheap enough to actually happen. |
| `scripts/render-diagram.py` | new | The honest failure mode of "add diagrams" is that the environment has no `mmdc`, no Chromium, no network — and the agent then ships an ASCII sketch. This renderer is the offline floor: Pillow only, four topologies, and a hard refusal when a spec has no traceable `source` line. |
| `assets/report-template.md` | rewritten | Each section now names its figure, its three-line caption (what it shows / where it breaks / source + tier), and keeps the evidence table beside it. |
| `references/reading-checklist.md` | rewritten | Phase 7 and Phase 8 are now gates: an unticked figure check means the report is not finished. |
| `references/docx-conversion-standard.md` | new | Word is where markdown reports go to lose their structure. The standard pins page setup, the style matrix with `eastAsia` fonts set separately, a six-column table cap, table-title-above / figure-title-below, and a 25-item acceptance list — plus the limitations (TOC page numbers, font fallback, SVG) stated rather than glossed. |

What did **not** change: the four-element experiment rule, the figure-text mapping method, the transition classification, the evidence-boundary rules, and the "figures must actually be looked at" requirement. Those were right already.

## Checks that enforce the above

`scripts/check-composition.py` (run on every push) verifies the manifest and patch shape as before, and additionally:

- every path SKILL.md names in backticks under `references/`, `assets/` or `scripts/` is really bundled with the skill;
- V1–V8 are mentioned in SKILL.md and defined in `visualization-spec.md`;
- the `source` rule is stated in the spec.

`ci.yml` additionally renders the four sample diagrams and asserts each PNG is at least 1200 px wide — a renderer that silently emits blank images would let every report claim figures it never drew.

## Scope

Single-paper close reading. It is not a multi-paper review (`literature-review`), not a formal peer review (`peer-review`), and not paper discovery (`paper-lookup`).

## Orientation evidence (not validation)

Two pieces of literature were used to justify *"diagrams beat prose for comprehension/recall in a journal-club setting"*: *Infographics Improve Comprehension and Recall at the Orthopaedic Journal Club* (J Surg Educ, 2020) and *Let Your Ideas Flow: Using Flowcharts to Convey Methods and Implications of the Results* (J Microbiol Biol Educ, 2018, PMC5969414). They support the premise; they do not show that this particular set of eight figures improves a reading report. That would need its own evaluation.
