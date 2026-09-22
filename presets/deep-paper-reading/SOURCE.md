# Design sources

This preset packages the author's own `deep-paper-reading` skill (文献精读 / Deep Paper Reading) as a DSH agent preset, so the capability is `skill`-invocable instead of having to be read off disk by hand.

## Composition

The Cordis composition is a copy of the locally authored `scientific-evidence-en-mode` preset — that composition already supplies exactly the capability surface a close reading needs (filesystem, shell, file search, web fetch, skills, todos, goals, jobs, compaction, user questions) — with two changes:

- the persona row is rewritten as the Deep Paper Reading protocol: mandatory skill load, evidence boundary, four-element experiment decomposition, logic-chain reconstruction, output conventions;
- the `skill-filesystem` row gains a `customSkillDirs` entry pointing at this preset's bundled `skills/` directory, so `deep-paper-reading` resolves as a real skill through the skill tool rather than as a file the agent has to find.

`baseUrl` in that row's `!!js` expression is the composition's own directory, which the preset `Include` sets before the subtree is mounted — so the bundled skill root travels with the preset whether it is mounted from the user preset root, from this plugin's `presets/` directory, or from an imported `.dshpreset` archive.

## Bundled skill

`skills/deep-paper-reading/` is a verbatim copy of the author's skill (MIT, `skill-author: user`), original frontmatter included:

- `SKILL.md` — the skill body
- `references/reading-checklist.md` — the per-phase checklist
- `references/biomedical-tools.md` — technique/assay quick reference
- `assets/report-template.md` — the Chinese report template

Nothing in those files was edited for this package. The skill remains the single source of truth for the reading workflow; the preset adds only the mode-level persona, the skill mount, and the display metadata.

## Scope

Single-paper close reading. It is not a multi-paper review (`literature-review`), not a formal peer review (`peer-review`), and not paper discovery (`paper-lookup`).
