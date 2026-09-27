#!/usr/bin/env node
/**
 * ci-scan-views-el-tags 回归测试（零依赖）。
 * 运行：node rules/examples/run-ci-scan-fixtures.mjs
 */
import { spawnSync } from 'node:child_process';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  runCiScan,
  scanTemplate,
  scanTemplateAll,
  scanVueContent,
} from './ci-scan-views-el-tags.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const FIXTURE_ROOT = resolve(__dirname, 'fixtures/ci-scan-project');
const SCAN_SCRIPT = resolve(__dirname, 'ci-scan-views-el-tags.mjs');

let failed = 0;

function assert(condition, message) {
  if (!condition) {
    console.error(`FAIL: ${message}`);
    failed += 1;
  } else {
    console.log(`OK: ${message}`);
  }
}

const unitCases = [
  { name: 'static <el-button>', input: '<el-button />', expectCount: 1 },
  {
    name: 'HTML comment with <el-button>',
    input: '<!-- <el-button> --><BaseTable />',
    expectCount: 0,
  },
  {
    name: ':is with nested quotes',
    input: '<component :is="\'el-button\'" />',
    expectCount: 1,
  },
  { name: 'v-bind:is', input: '<component v-bind:is="\'el-button\'" />', expectCount: 1 },
  { name: 'plain is="el-button"', input: '<component is="el-button" />', expectCount: 1 },
  { name: 'Base only', input: '<BaseTable />', expectCount: 0 },
  { name: 'PascalCase ElButton', input: '<ElButton />', expectCount: 1 },
  {
    name: 'custom EligibilityCard not in denylist',
    input: '<EligibilityCard />',
    expectCount: 0,
  },
  {
    name: 'multiple violations in one template',
    input: '<el-button /><el-table />',
    expectCount: 2,
  },
];

console.log('--- unit: scanTemplateAll ---');
for (const c of unitCases) {
  const hits = scanTemplateAll(c.input);
  assert(hits.length === c.expectCount, `${c.name} (${hits.length} hits)`);
}

console.log('\n--- unit: scanTemplate first hit ---');
assert(scanTemplate('<el-button />') !== null, 'scanTemplate returns first hit');

console.log('\n--- unit: line/column ---');
const withLines = scanTemplateAll('<BaseTable />\n<el-button />');
assert(withLines.length === 1, 'one hit on second line');
assert(withLines[0].line === 2, 'el-button on line 2');

console.log('\n--- unit: scanVueContent ---');
assert(
  scanVueContent('<template><BasePage /></template>').length === 0,
  'vue with Base only',
);
assert(
  scanVueContent('<template><el-form /></template>').length >= 1,
  'vue with el-form',
);

console.log('\n--- integration: fixture project ---');
const result = runCiScan({ projectRoot: FIXTURE_ROOT });
assert(!result.ok, 'fixture project should have violations');
assert(
  result.violations.length === 8,
  `expected 8 violations, got ${result.violations.length}`,
);

const violationPaths = [...new Set(result.violations.map((v) => v.file.replace(/\\/g, '/')))];
const expectFailFiles = [
  'src/views/fail/StaticEl.vue',
  'src/views/fail/DynamicColonIs.vue',
  'src/views/fail/DynamicPlainIs.vue',
  'src/views/fail/VBindIs.vue',
  'src/views/fail/PascalCaseElButton.vue',
  'src/views/fail/MultipleInOne.vue',
  'packages/foo/src/views/fail/PkgTable.vue',
];
for (const p of expectFailFiles) {
  assert(violationPaths.includes(p), `violation file includes ${p}`);
}

const multiHits = result.violations.filter((v) =>
  v.file.replace(/\\/g, '/').endsWith('MultipleInOne.vue'),
);
assert(multiHits.length === 2, 'MultipleInOne.vue reports 2 violations');

assert(
  result.violations.every((v) => v.line && v.column && v.formatted),
  'all violations have line, column, formatted',
);

assert(
  !violationPaths.some((p) => p.includes('src/components/')),
  'src/components not scanned',
);
assert(
  !violationPaths.some((p) => p.includes('src/views/pass/')),
  'pass views not flagged',
);

console.log('\n--- cli: exit codes ---');
const noViews = spawnSync(
  process.execPath,
  [SCAN_SCRIPT, '--root', resolve(__dirname, '..')],
  { encoding: 'utf8' },
);
assert(noViews.status === 1, 'rules parent without views exits 1');

const allowEmpty = spawnSync(
  process.execPath,
  [SCAN_SCRIPT, '--root', resolve(__dirname, '..'), '--allow-empty'],
  { encoding: 'utf8' },
);
assert(allowEmpty.status === 0, '--allow-empty exits 0');

const fixtureCli = spawnSync(
  process.execPath,
  [SCAN_SCRIPT, '--root', FIXTURE_ROOT],
  { encoding: 'utf8' },
);
assert(fixtureCli.status === 1, 'fixture project CLI exits 1');
assert(
  /:\d+:\d+ \[/.test(fixtureCli.stderr || ''),
  'CLI output includes file:line:column',
);

console.log(`\n--- ${failed === 0 ? 'ALL PASSED' : `${failed} FAILED`} ---`);
process.exit(failed === 0 ? 0 : 1);
