#!/usr/bin/env node
/**
 * CI 扫描：禁止业务 views 中出现 Element Plus 模板用法（el-*、EP PascalCase denylist、动态 is）。
 * 回归：node rules/examples/run-ci-scan-fixtures.mjs
 */
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { isAbsolute, relative, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { ELEMENT_PLUS_PASCAL_ALT } from './element-plus-pascal-denylist.mjs';

const SKIP_DIR_NAMES = new Set([
  'node_modules',
  'dist',
  'build',
  'coverage',
  '.output',
  '.nuxt',
  '.vite',
  'storybook-static',
]);

/** 静态标签 <el-xxx /> */
export const EL_TAG_RE = /<\/?el-[a-z][\w-]*/gi;

/** 静态标签 <ElButton /> 等（denylist） */
export const EP_PASCAL_TAG_RE = new RegExp(
  `<\\/?(?:${ELEMENT_PLUS_PASCAL_ALT})(?=[\\s/>])`,
  'g',
);

/** :is / v-bind:is → el-* */
export const DYNAMIC_BINDING_EL_PATTERNS = [
  /(?:^|\s)(?::is|v-bind:is)\s*=\s*"'(el-[a-z][\w-]*)'"/gi,
  /(?:^|\s)(?::is|v-bind:is)\s*=\s*"(el-[a-z][\w-]*)"/gi,
  /(?:^|\s)(?::is|v-bind:is)\s*=\s*'(el-[a-z][\w-]*)'/gi,
];

/** :is / v-bind:is → El*（denylist） */
export const DYNAMIC_BINDING_EP_PATTERNS = [
  new RegExp(
    `(?:^|\\s)(?::is|v-bind:is)\\s*=\\s*"'(${ELEMENT_PLUS_PASCAL_ALT})'"`,
    'gi',
  ),
  new RegExp(
    `(?:^|\\s)(?::is|v-bind:is)\\s*=\\s*"(${ELEMENT_PLUS_PASCAL_ALT})"`,
    'gi',
  ),
  new RegExp(
    `(?:^|\\s)(?::is|v-bind:is)\\s*=\\s*'(${ELEMENT_PLUS_PASCAL_ALT})'`,
    'gi',
  ),
];

/** 原生 is="el-xxx" / is="ElButton" */
export const PLAIN_IS_EL_PATTERNS = [
  /(?:^|\s)is\s*=\s*"(el-[a-z][\w-]*)"/gi,
  /(?:^|\s)is\s*=\s*'(el-[a-z][\w-]*)'/gi,
];

export const PLAIN_IS_EP_PATTERNS = [
  new RegExp(`(?:^|\\s)is\\s*=\\s*"(${ELEMENT_PLUS_PASCAL_ALT})"`, 'gi'),
  new RegExp(`(?:^|\\s)is\\s*=\\s*'(${ELEMENT_PLUS_PASCAL_ALT})'`, 'gi'),
];

export function lineColumnAt(text, index) {
  const before = text.slice(0, index);
  const lines = before.split('\n');
  return {
    line: lines.length,
    column: lines[lines.length - 1].length + 1,
  };
}

export function extractTemplateBlocks(vueContent) {
  const blocks = [];
  const re = /<template[^>]*>([\s\S]*?)<\/template>/gi;
  let m;
  while ((m = re.exec(vueContent)) !== null) {
    const inner = m[1];
    const innerOffset = m.index + m[0].indexOf(inner);
    const startLine = vueContent.slice(0, innerOffset).split('\n').length;
    blocks.push({ content: inner, startLine });
  }
  return blocks;
}

export function extractTemplateSource(vueContent) {
  return extractTemplateBlocks(vueContent)
    .map((b) => b.content)
    .join('\n');
}

export function stripHtmlComments(fragment) {
  return fragment.replace(/<!--[\s\S]*?-->/g, '');
}

function collectRegexHits(cleaned, re, kind) {
  const hits = [];
  re.lastIndex = 0;
  let m;
  while ((m = re.exec(cleaned)) !== null) {
    const { line, column } = lineColumnAt(cleaned, m.index);
    hits.push({
      kind,
      match: m[0].trim(),
      line,
      column,
      index: m.index,
    });
  }
  return hits;
}

function collectPatternHits(cleaned, patterns, kindPrefix) {
  const hits = [];
  for (const re of patterns) {
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(cleaned)) !== null) {
      const { line, column } = lineColumnAt(cleaned, m.index);
      hits.push({
        kind: kindPrefix,
        match: m[0].trim(),
        line,
        column,
        index: m.index,
      });
    }
  }
  return hits;
}

/** 返回同文件 template 内全部违规（含 line/column，相对 template 块） */
export function scanTemplateAll(fragment) {
  const cleaned = stripHtmlComments(fragment);
  const hits = [
    ...collectRegexHits(cleaned, EL_TAG_RE, 'static-tag'),
    ...collectRegexHits(cleaned, EP_PASCAL_TAG_RE, 'pascal-tag'),
    ...collectPatternHits(cleaned, DYNAMIC_BINDING_EL_PATTERNS, 'dynamic-is-binding'),
    ...collectPatternHits(cleaned, DYNAMIC_BINDING_EP_PATTERNS, 'dynamic-is-binding-ep'),
    ...collectPatternHits(cleaned, PLAIN_IS_EL_PATTERNS, 'dynamic-is-plain'),
    ...collectPatternHits(cleaned, PLAIN_IS_EP_PATTERNS, 'dynamic-is-plain-ep'),
  ];

  hits.sort((a, b) => a.index - b.index || a.column - b.column);

  const seen = new Set();
  const unique = [];
  for (const h of hits) {
    const key = `${h.line}:${h.column}:${h.kind}:${h.match}`;
    if (seen.has(key)) continue;
    seen.add(key);
    const { index, ...rest } = h;
    unique.push(rest);
  }
  return unique;
}

/** 兼容：仅返回第一条 */
export function scanTemplate(fragment) {
  const all = scanTemplateAll(fragment);
  return all[0] ?? null;
}

export function scanVueContent(vueContent) {
  const blocks = extractTemplateBlocks(vueContent);
  const all = [];
  for (const block of blocks) {
    for (const hit of scanTemplateAll(block.content)) {
      all.push({
        ...hit,
        line: hit.line + block.startLine - 1,
      });
    }
  }
  return all;
}

export function scanVueFile(filePath) {
  const content = readFileSync(filePath, 'utf8');
  return scanVueContent(content);
}

function collectVueFiles(dir, out = []) {
  let entries;
  try {
    entries = readdirSync(dir, { withFileTypes: true });
  } catch {
    return out;
  }
  for (const ent of entries) {
    const full = resolve(dir, ent.name);
    if (ent.isDirectory()) {
      if (SKIP_DIR_NAMES.has(ent.name)) continue;
      collectVueFiles(full, out);
    } else if (ent.isFile() && ent.name.endsWith('.vue')) {
      out.push(full);
    }
  }
  return out;
}

function resolveViewRoots(projectRoot, includeRoots) {
  const roots = [];
  const appViews = resolve(projectRoot, 'src/views');
  if (existsSync(appViews)) roots.push(appViews);

  const packagesDir = resolve(projectRoot, 'packages');
  try {
    for (const ent of readdirSync(packagesDir, { withFileTypes: true })) {
      if (!ent.isDirectory()) continue;
      const pkgViews = resolve(packagesDir, ent.name, 'src/views');
      if (existsSync(pkgViews)) roots.push(pkgViews);
    }
  } catch {
    // no packages/
  }

  for (const inc of includeRoots) {
    const abs = isAbsolute(inc) ? resolve(inc) : resolve(projectRoot, inc);
    if (existsSync(abs)) roots.push(abs);
    else {
      console.warn(`ci-scan-views-el-tags: skip missing --include ${inc}`);
    }
  }

  return [...new Set(roots)];
}

export function formatViolation(file, v) {
  return `${file}:${v.line}:${v.column} [${v.kind}] ${v.match}`;
}

export function runCiScan(options = {}) {
  const {
    projectRoot = process.cwd(),
    allowEmpty = false,
    includeRoots = [],
  } = options;

  const root = resolve(projectRoot);
  const viewRoots = resolveViewRoots(root, includeRoots);

  if (viewRoots.length === 0) {
    return {
      ok: allowEmpty,
      allowEmpty,
      viewRoots: [],
      candidates: [],
      violations: [],
      error: 'no view roots found',
    };
  }

  const candidates = [];
  for (const vr of viewRoots) {
    collectVueFiles(vr, candidates);
  }

  const violations = [];
  for (const file of candidates) {
    const hits = scanVueFile(file);
    const relFile = relative(root, file).replace(/\\/g, '/');
    for (const hit of hits) {
      violations.push({
        file: relFile,
        ...hit,
        formatted: formatViolation(relFile, hit),
      });
    }
  }

  return {
    ok: violations.length === 0,
    viewRoots,
    candidates,
    violations,
  };
}

function runCli() {
  const args = process.argv.slice(2);
  const allowEmpty = args.includes('--allow-empty');
  const rootIdx = args.indexOf('--root');
  const projectRoot = resolve(
    rootIdx >= 0 ? args[rootIdx + 1] : process.cwd(),
  );

  const includeRoots = [];
  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === '--include' && args[i + 1]) {
      includeRoots.push(args[i + 1]);
      i += 1;
    }
  }

  const result = runCiScan({ projectRoot, allowEmpty, includeRoots });

  if (result.error === 'no view roots found') {
    const msg =
      'ci-scan-views-el-tags: no view roots found (expected src/views or packages/*/src/views)';
    if (allowEmpty) {
      console.warn(`${msg}; --allow-empty → exit 0`);
      process.exit(0);
    }
    console.error(msg);
    console.error(
      'Fix --root / working-directory, or pass --include. Rules-only repos use --allow-empty.',
    );
    process.exit(1);
  }

  if (result.ok) {
    console.log(
      `ci-scan-views-el-tags: OK (${result.candidates.length} file(s), ${result.viewRoots.length} root(s))`,
    );
    process.exit(0);
  }

  console.error(
    `ci-scan-views-el-tags: found ${result.violations.length} violation(s):\n`,
  );
  for (const v of result.violations) {
    console.error(`  ${v.formatted}`);
  }
  console.error(
    '\nUse Base components in views. See rules/shared/00-must-follow.md §5–7.',
  );
  console.error(
    'Note: runtime :is="variable" and non-EP El* components (e.g. EligibilityCard) are not detected.',
  );
  process.exit(1);
}

function isMainModule() {
  const entry = process.argv[1];
  if (!entry) return false;
  return pathToFileURL(resolve(entry)).href === import.meta.url;
}

if (isMainModule()) {
  runCli();
}
