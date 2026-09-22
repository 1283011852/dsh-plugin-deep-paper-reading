/**
 * Boot row for dsh-plugin-deep-paper-reading.
 *
 * The capability this bundle actually contributes is declarative: the
 * `agent-presets` override in ./cordis.patch.yml adds the bundled
 * ./presets directory as a roster root. This module contributes no service and
 * no tool — it exists so the plugin is visible in the plugin inventory and so a
 * broken install says why, in one line, instead of surfacing as a preset that
 * silently never appears in the picker.
 *
 * The two ways this install goes wrong are both packaging mistakes rather than
 * configuration ones:
 *   - `presets/` missing from the tarball (a `files` field that dropped it);
 *   - the package resolvable in the profile's node_modules under a different
 *     name than the one cordis.patch.yml resolves.
 * Both are reported here at boot.
 */

import { existsSync, readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

export const name = 'deep-paper-reading-preset'

const PRESET_ID = 'deep-paper-reading'

function presetDir() {
  return join(dirname(fileURLToPath(import.meta.url)), 'presets', PRESET_ID)
}

export function apply() {
  const dir = presetDir()
  const composition = join(dir, 'agent.cordis.yml')

  if (!existsSync(composition)) {
    console.warn(
      `[${name}] preset composition not found at ${composition}. ` +
        'The bundled presets/ directory is missing from this install, so the ' +
        `${PRESET_ID} agent preset will not appear in the picker.`,
    )
    return
  }

  let label = PRESET_ID
  try {
    const presetYml = readFileSync(join(dir, 'preset.yml'), 'utf8')
    const match = /^name:\s*(.+)$/m.exec(presetYml)
    if (match) label = match[1].trim()
  } catch {
    // preset.yml is optional display metadata; the preset still mounts without it.
  }

  console.log(
    `[${name}] agent preset "${PRESET_ID}" (${label}) registered from ${dir}`,
  )
}
