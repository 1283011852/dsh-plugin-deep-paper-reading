#!/usr/bin/env node
/**
 * Builds a `.dshpreset` package from ./presets/deep-paper-reading.
 *
 * `.dshpreset` is DSH Desktop's preset exchange format: a ZIP archive holding
 * `manifest.json` at the root plus the preset directory under `preset/`. DSH
 * Desktop validates the archive, checks that the composition mounts, and moves
 * it into the user preset root atomically.
 *
 * This script is dependency-free on purpose: the plugin itself ships no runtime
 * dependencies, and a build step that needs a package manager to produce a
 * 30 KB archive would be the only reason to run one. The ZIP writer below is a
 * plain stored/deflate implementation.
 *
 * The archive layout, manifest fields, id rule, and the four size caps mirror
 * the DSH Desktop importer/exporter, so a package built here is one the importer
 * accepts rather than merely one that looks right.
 *
 * Usage: node scripts/build-dshpreset.mjs [--out <file>]
 */

import { deflateRawSync } from 'node:zlib'
import { mkdirSync, readdirSync, readFileSync, lstatSync, writeFileSync } from 'node:fs'
import { dirname, join, relative, resolve, sep } from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const PRESET_ID = 'deep-paper-reading'
const PRESET_DIR = join(ROOT, 'presets', PRESET_ID)

/** Archive contract — mirrors the DSH Desktop preset-transfer plugin. */
const ARCHIVE_FORMAT = 'dsh-preset'
const ARCHIVE_VERSION = 1
const ID_PATTERN = /^[a-z0-9][a-z0-9-]*$/
const IGNORED_NAMES = new Set(['.DS_Store', 'Thumbs.db', 'desktop.ini'])
const MAX_FILES = 512
const MAX_FILE_BYTES = 12 * 1024 * 1024
const MAX_UNCOMPRESSED_BYTES = 32 * 1024 * 1024
const MAX_COMPRESSED_BYTES = 16 * 1024 * 1024

/**
 * Stamped into the manifest as `sourceDshVersion`. The importer uses it only to
 * warn about a version gap, so an approximate value is honest as long as it is
 * not fabricated: bump this when the preset is re-verified against a newer
 * harness.
 */
const SOURCE_DSH_VERSION = '0.1.5-rc.2'

/** Fixed stamp keeps the archive byte-identical across rebuilds. */
const BUILD_EPOCH = new Date('2026-01-01T00:00:00Z')

const CRC_TABLE = (() => {
  const table = new Int32Array(256)
  for (let index = 0; index < 256; index += 1) {
    let value = index
    for (let bit = 0; bit < 8; bit += 1) {
      value = value & 1 ? 0xedb88320 ^ (value >>> 1) : value >>> 1
    }
    table[index] = value
  }
  return table
})()

function crc32(buffer) {
  let value = 0xffffffff
  for (let index = 0; index < buffer.length; index += 1) {
    value = CRC_TABLE[(value ^ buffer[index]) & 0xff] ^ (value >>> 8)
  }
  return (value ^ 0xffffffff) >>> 0
}

function dosStamp(date) {
  const year = Math.max(1980, date.getUTCFullYear())
  const time =
    (date.getUTCHours() << 11) | (date.getUTCMinutes() << 5) | (date.getUTCSeconds() >> 1)
  const day = ((year - 1980) << 9) | ((date.getUTCMonth() + 1) << 5) | date.getUTCDate()
  return { time, day }
}

function buildZip(entries) {
  const { time, day } = dosStamp(BUILD_EPOCH)
  const local = []
  const central = []
  let offset = 0

  for (const [name, data] of entries) {
    const nameBytes = Buffer.from(name, 'utf8')
    const deflated = deflateRawSync(data, { level: 9 })
    const useDeflate = deflated.length < data.length
    const payload = useDeflate ? deflated : data
    const method = useDeflate ? 8 : 0
    const checksum = crc32(data)

    const localHeader = Buffer.alloc(30)
    localHeader.writeUInt32LE(0x04034b50, 0)
    localHeader.writeUInt16LE(20, 4)
    localHeader.writeUInt16LE(0x0800, 6)
    localHeader.writeUInt16LE(method, 8)
    localHeader.writeUInt16LE(time, 10)
    localHeader.writeUInt16LE(day, 12)
    localHeader.writeUInt32LE(checksum, 14)
    localHeader.writeUInt32LE(payload.length, 18)
    localHeader.writeUInt32LE(data.length, 22)
    localHeader.writeUInt16LE(nameBytes.length, 26)
    localHeader.writeUInt16LE(0, 28)
    local.push(localHeader, nameBytes, payload)

    const centralHeader = Buffer.alloc(46)
    centralHeader.writeUInt32LE(0x02014b50, 0)
    centralHeader.writeUInt16LE(20, 4)
    centralHeader.writeUInt16LE(20, 6)
    centralHeader.writeUInt16LE(0x0800, 8)
    centralHeader.writeUInt16LE(method, 10)
    centralHeader.writeUInt16LE(time, 12)
    centralHeader.writeUInt16LE(day, 14)
    centralHeader.writeUInt32LE(checksum, 16)
    centralHeader.writeUInt32LE(payload.length, 20)
    centralHeader.writeUInt32LE(data.length, 24)
    centralHeader.writeUInt16LE(nameBytes.length, 28)
    centralHeader.writeUInt16LE(0, 30)
    centralHeader.writeUInt16LE(0, 32)
    centralHeader.writeUInt16LE(0, 34)
    centralHeader.writeUInt16LE(0, 36)
    centralHeader.writeUInt32LE(0, 38)
    centralHeader.writeUInt32LE(offset, 42)
    central.push(centralHeader, nameBytes)

    offset += localHeader.length + nameBytes.length + payload.length
  }

  const centralBytes = Buffer.concat(central)
  const end = Buffer.alloc(22)
  end.writeUInt32LE(0x06054b50, 0)
  end.writeUInt16LE(0, 4)
  end.writeUInt16LE(0, 6)
  end.writeUInt16LE(entries.length, 8)
  end.writeUInt16LE(entries.length, 10)
  end.writeUInt32LE(centralBytes.length, 12)
  end.writeUInt32LE(offset, 16)
  end.writeUInt16LE(0, 20)

  return Buffer.concat([...local, centralBytes, end])
}

function collectPresetFiles(dir, prefix = 'preset') {
  const collected = []
  let total = 0

  const visit = (current, relativePrefix) => {
    for (const entry of readdirSync(current, { withFileTypes: true })) {
      if (IGNORED_NAMES.has(entry.name) || entry.name.startsWith('._') || entry.name === '__MACOSX') {
        continue
      }
      const full = join(current, entry.name)
      const archivePath = relativePrefix ? `${relativePrefix}/${entry.name}` : entry.name

      if (entry.isDirectory()) {
        visit(full, archivePath)
        continue
      }
      if (entry.isSymbolicLink()) {
        throw new Error(`Preset contains a symbolic link, which cannot be exported safely: ${archivePath}`)
      }
      if (!entry.isFile()) {
        throw new Error(`Preset contains an unsupported filesystem entry: ${archivePath}`)
      }

      const info = lstatSync(full)
      if (collected.length + 1 > MAX_FILES) {
        throw new Error(`Preset contains more than ${MAX_FILES} files`)
      }
      if (info.size > MAX_FILE_BYTES) {
        throw new Error(`Preset file is too large to export: ${archivePath}`)
      }
      total += info.size
      if (total > MAX_UNCOMPRESSED_BYTES) {
        throw new Error('Preset is too large to export')
      }
      collected.push([`${prefix}/${archivePath}`, readFileSync(full)])
    }
  }

  visit(dir, '')
  return { collected, total }
}

function readPresetMetadata() {
  const presetYml = readFileSync(join(PRESET_DIR, 'preset.yml'), 'utf8')
  const read = (key) => {
    const match = new RegExp(`^${key}:\\s*(.+)$`, 'm').exec(presetYml)
    return match ? match[1].trim().replace(/^["']|["']$/g, '') : undefined
  }
  return { name: read('name'), description: read('description') }
}

function main() {
  const outFlagIndex = process.argv.indexOf('--out')
  const packageJson = JSON.parse(readFileSync(join(ROOT, 'package.json'), 'utf8'))
  const version = packageJson.version
  const outputPath =
    outFlagIndex !== -1 && process.argv[outFlagIndex + 1]
      ? resolve(process.argv[outFlagIndex + 1])
      : join(ROOT, 'dist', `dsh-plugin-deep-paper-reading-${version}.dshpreset`)

  if (!ID_PATTERN.test(PRESET_ID)) {
    throw new Error(`Invalid preset id "${PRESET_ID}"`)
  }
  if (!lstatSync(PRESET_DIR).isDirectory()) {
    throw new Error(`Preset directory not found: ${PRESET_DIR}`)
  }

  const { collected, total } = collectPresetFiles(PRESET_DIR)
  const meta = readPresetMetadata()

  const manifest = {
    format: ARCHIVE_FORMAT,
    version: ARCHIVE_VERSION,
    id: PRESET_ID,
    name: meta.name,
    description: meta.description,
    icon: 'sparkle',
    sourceDshVersion: SOURCE_DSH_VERSION,
    exportedAt: BUILD_EPOCH.toISOString(),
  }

  const entries = [
    ['manifest.json', Buffer.from(`${JSON.stringify(manifest, null, 2)}\n`, 'utf8')],
    ...collected,
  ]

  const archive = buildZip(entries)
  if (archive.length > MAX_COMPRESSED_BYTES) {
    throw new Error('The compressed preset package is larger than 16 MB.')
  }

  mkdirSync(dirname(outputPath), { recursive: true })
  writeFileSync(outputPath, archive)

  const relativeOutput = relative(ROOT, outputPath).split(sep).join('/')
  console.log(
    `built ${relativeOutput} — ${entries.length} files, ` +
      `${(total / 1024).toFixed(1)} KiB uncompressed, ` +
      `${(archive.length / 1024).toFixed(1)} KiB packaged`,
  )
  for (const [name] of entries) console.log(`  ${name}`)
}

main()
