# dsh-plugin-deep-paper-reading

A **DeepSeek Harness plugin** that ships the *文献精读模式* (Deep Paper Reading) agent preset: install it and the preset picker gains a mode for figure-by-figure, experiment-by-experiment close reading of a **single** biomedical paper.

It packages the author's own `deep-paper-reading` skill verbatim (SKILL.md, reading checklist, report template) plus a mode-level persona that mandates loading that skill first, enforces an evidence boundary, decomposes every experiment into four elements, and reconstructs the paper's logic chain into a journal-club-ready report.

- Keywords: `dsh-plugin` · `deepseek-harness` · `agent-preset` · paper reading
- License: MIT

---

## What the mode does

1. Acquire and first-pass scan the paper (title/abstract → last Introduction paragraph → all figure legends → first Discussion paragraph → Results headers)
2. Read the main text line by line
3. Treat supplementary material with the same rigor; label anything unobtainable as missing
4. Build a **figure-legend ↔ main-text correspondence table** — the step that separates close reading from paraphrase
5. Decompose **every** experiment into purpose / design & tools / results / interpretation
6. Reconstruct the logic chain, classifying each transition as elimination, extension, mechanism, application, or validation
7. Assemble the report from the template; export to Word through the `docx` skill when asked

Two hard constraints live in the persona:

- **Evidence boundary** — never invent figure panels, legends, numbers, p-values, sample sizes, catalog numbers, or a claim of full-text access; distinguish what the data *shows* from what the authors *say*; label every access failure explicitly.
- **Figures must actually be looked at** — if a judgement rests on a legend rather than the image, say so.

Not for: multi-paper reviews (`literature-review`), formal peer review (`peer-review`), or paper discovery (`paper-lookup`).

---

## Install

### 1. As a bundle (needs the `dsh` CLI)

```sh
dsh plugin --profile web add github:1283011852/dsh-plugin-deep-paper-reading
# DSH Desktop: pnpm dsh plugin --profile web add github:1283011852/dsh-plugin-deep-paper-reading
```

No `prepare` script and no dependencies, so pnpm's git-build permission prompt does not apply. Restart DSH, then pick `文献精读模式` in the preset picker. Remove with `dsh plugin --profile web remove dsh-plugin-deep-paper-reading`.

### 2. As a preset package (`.dshpreset`) — no CLI

Download `dsh-plugin-deep-paper-reading-<version>.dshpreset` from [Releases](../../releases) and import it in DSH Desktop. The desktop validates, previews, and atomically installs into the user preset root; an existing preset id is never overwritten. This path does not touch any profile configuration.

### 3. Skill only

```sh
cp -r presets/deep-paper-reading/skills/deep-paper-reading ~/.agents/skills/
```

Then `deep-paper-reading` is callable through the `skill` tool in any mode, without the mode persona. (Note: DSH does not scan `~/.claude/skills/`, so a skill kept there reports `unknown or no longer available`.)

---

## Usage

Start a session on **文献精读模式** and point it at a PDF or DOI. The report lands in `paper-reading/<short-slug>-精读报告.md` with extracted text and figure renders under `sources/`, unless the workspace already has an established layout.

The skill assumes a working PDF toolchain (`python` + PyMuPDF). If it is missing the agent says so rather than pretending it read the full text.

---

## Layout

```
├── package.json                    # dsh.bundle.patch → cordis.patch.yml
├── cordis.patch.yml                # registers this package's presets/ as a roster root
├── index.js                        # boot-time self-check row
├── presets/deep-paper-reading/     # the agent preset (composition, metadata, bundled skill)
├── scripts/build-dshpreset.mjs     # dependency-free .dshpreset packer
└── .github/workflows/              # ci.yml checks, release.yml attaches the package
```

---

## ⚠️ Known impact

This plugin's patch **replaces the whole `config` of the `agent-presets` row**, because DSH patches replace a targeted row's config value rather than deep-merging its keys. Every key that row requires is therefore restated in `cordis.patch.yml`, which means:

1. **The `roots` list belongs to this plugin.** If another bundle or your own `cordis.patch.yml` also configures `agent-presets`, the later layer wins outright and the earlier roots disappear. To keep both, merge the two `roots` arrays by hand in your profile patch instead of mounting both bundles.
2. **`default` is restated as `standard`.** Your `agent-presets.default` in `$DSH_HOME/settings.yaml` lives in the settings layer, outranks the config, and is unaffected.

Prefer the `.dshpreset` install if you would rather not take either consequence — it changes no profile configuration.

---

## Verification

- The preset was mount-validated through the roster (`standingKeyFor` → `mounted OK`), which composes the plugin subtree for real.
- The composition's `skill-filesystem` row points `customSkillDirs` at `new URL('skills/', baseUrl)`; the preset `Include` sets `baseUrl` to the composition's own directory, so the bundled skill travels with the preset whether it is mounted from the user root, from this package's `presets/`, or from an imported `.dshpreset`.
- The packer mirrors the DSH Desktop importer's constraints (manifest `format`/`version`, id rule, ≤512 files, ≤12 MB per file, ≤32 MB uncompressed, ≤16 MB compressed), and CI re-reads the archive with `unzip` to check its layout.

On your own machine, without booting anything:

```sh
dsh --profile web --dump-config | grep -n "== dsh-plugin-deep-paper-reading"
```

---

## License and provenance

MIT — see [LICENSE](LICENSE). The bundled skill is the author's own (frontmatter records MIT and `skill-author: user`) and is included unmodified. The Cordis composition derives from a locally authored `scientific-evidence-en-mode` preset: its tool surface is kept as-is, with the persona row rewritten, the bundled skill directory added, and display metadata written. See `presets/deep-paper-reading/SOURCE.md`.
