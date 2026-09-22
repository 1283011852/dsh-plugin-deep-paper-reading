#!/usr/bin/env python3
"""Static checks for this plugin's composition.

These verify the *shape* a DSH loader requires — the bundle manifest points at an
existing patch, the patch restates every key the row it overrides needs, a
bundled skill is discoverable and named correctly. They do not prove the harness
composes the result; that is `dsh --profile <name> --dump-config`, documented in
the README, and the only check that reads the real loader.

`!!js` is a loader-specific YAML tag and there is no schema for it here, so the
SafeLoader is extended to read it as the plain scalar it carries. A static
reader treating an expression as opaque text is correct; evaluating it is the
loader's job, not this script's.
"""

import glob
import json
import os
import sys

import yaml


class Loader(yaml.SafeLoader):
    pass


Loader.add_multi_constructor(
    "tag:yaml.org,2002:js",
    lambda loader, suffix, node: loader.construct_scalar(node),
)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ID_PATTERN = __import__("re").compile(r"^[a-z0-9][a-z0-9-]*$")

failures = []


def check(condition, message):
    if not condition:
        failures.append(message)
    return condition


def load(path):
    with open(path, encoding="utf-8") as handle:
        return yaml.load(handle, Loader=Loader)


def relative(path):
    return os.path.relpath(path, REPO).replace(os.sep, "/")


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


manifest = json.loads(read(os.path.join(REPO, "package.json")))
package_name = manifest.get("name")

# --- bundle manifest -------------------------------------------------------

patch_relative = (manifest.get("dsh") or {}).get("bundle", {}).get("patch")
if check(patch_relative, "package.json: dsh.bundle.patch is missing"):
    patch_path = os.path.join(REPO, patch_relative.lstrip("./"))
    check(os.path.isfile(patch_path), f"package.json: dsh.bundle.patch does not exist ({patch_relative})")

files = manifest.get("files") or []
for required in ("cordis.patch.yml", "presets"):
    check(required in files, f"package.json: files[] must ship {required}")

# --- every YAML file the loader reads parses -------------------------------

yaml_files = [os.path.join(REPO, "cordis.patch.yml")]
yaml_files += sorted(glob.glob(os.path.join(REPO, "presets", "*", "agent.cordis.yml")))
yaml_files += sorted(glob.glob(os.path.join(REPO, "presets", "*", "preset.yml")))

if check(yaml_files, "no composition files found"):
    for path in yaml_files:
        try:
            load(path)
        except yaml.YAMLError as error:
            check(False, f"{relative(path)}: does not parse as YAML ({error})")

# --- the row override ------------------------------------------------------

entries = load(os.path.join(REPO, "cordis.patch.yml"))
if check(isinstance(entries, list), "cordis.patch.yml: top level must be a patch-entry array"):
    inserted = [
        row
        for entry in entries
        if isinstance(entry, dict)
        for row in (entry.get("insert") or [])
    ]
    check(
        any(row.get("name") == package_name for row in inserted),
        f"cordis.patch.yml: no insert entry names this package ({package_name})",
    )

    # A patch REPLACES the whole config of the row it targets rather than
    # deep-merging keys, so a key missing here is not a fallback to the earlier
    # layer — it is an invalid row. Every key the roster requires must be present.
    overrides = [e for e in entries if isinstance(e, dict) and e.get("id") == "agent-presets"]
    if check(overrides, "cordis.patch.yml: no agent-presets override"):
        config = overrides[0].get("config") or {}
        for key in ("default", "includeShippedRoot", "includeUserRoot", "roots"):
            check(key in config, f"cordis.patch.yml: agent-presets override is missing {key}")
        roots = config.get("roots") or []
        check(roots, "cordis.patch.yml: agent-presets override declares no roots")
        for root in roots:
            check(
                isinstance(root, dict) and "path" in root and "trust" in root,
                "cordis.patch.yml: every root needs both path and trust",
            )

# --- every preset is self-describing and its bundled skills are valid ------

preset_dirs = sorted(
    path
    for path in glob.glob(os.path.join(REPO, "presets", "*"))
    if os.path.isdir(path)
)
if check(preset_dirs, "no preset directories found under presets/"):
    for preset_dir in preset_dirs:
        preset_id = os.path.basename(preset_dir)
        check(ID_PATTERN.match(preset_id), f"presets/{preset_id}: id must match [a-z0-9][a-z0-9-]*")
        check(
            os.path.isfile(os.path.join(preset_dir, "agent.cordis.yml")),
            f"presets/{preset_id}: agent.cordis.yml is missing",
        )

        metadata_path = os.path.join(preset_dir, "preset.yml")
        if check(os.path.isfile(metadata_path), f"presets/{preset_id}: preset.yml is missing"):
            metadata = load(metadata_path) or {}
            check(metadata.get("name"), f"presets/{preset_id}/preset.yml: name is missing")
            check(
                metadata.get("description"),
                f"presets/{preset_id}/preset.yml: description is missing",
            )

        skill_files = sorted(glob.glob(os.path.join(preset_dir, "skills", "*", "SKILL.md")))
        check(skill_files, f"presets/{preset_id}: no bundled skill found under skills/*/SKILL.md")
        for skill_file in skill_files:
            text = read(skill_file)
            if not check(
                text.startswith("---"),
                f"{relative(skill_file)}: frontmatter must open the file",
            ):
                continue
            front = yaml.load(text.split("---", 2)[1], Loader=Loader) or {}
            name = front.get("name")
            description = front.get("description")
            check(name, f"{relative(skill_file)}: frontmatter needs name")
            check(description, f"{relative(skill_file)}: frontmatter needs description")
            if name:
                check(
                    ID_PATTERN.match(name),
                    f"{relative(skill_file)}: skill name {name!r} is not kebab-case",
                )
                check(
                    os.path.basename(os.path.dirname(skill_file)) == name,
                    f"{relative(skill_file)}: directory name and skill name differ ({name})",
                )

if failures:
    print(f"{len(failures)} check(s) failed:\n", file=sys.stderr)
    for failure in failures:
        print(f"  - {failure}", file=sys.stderr)
    sys.exit(1)

print(f"ok: {len(yaml_files)} YAML file(s), {len(preset_dirs)} preset(s), manifest and patch shape verified")
