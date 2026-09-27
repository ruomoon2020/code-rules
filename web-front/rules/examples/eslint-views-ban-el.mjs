/**
 * ESLint flat config 片段：禁止在 src/views 下直接 import element-plus（含子路径）。
 * 注意：不检查 Vue template 中的 <el-*> 标签，须配合 ci-scan-views-el-tags.mjs。
 */
export const viewsBanElementPlus = {
  files: [
    'src/views/**/*.{vue,ts,tsx}',
    'packages/**/src/views/**/*.{vue,ts,tsx}',
  ],
  rules: {
    'no-restricted-imports': [
      'error',
      {
        paths: [
          {
            name: 'element-plus',
            message:
              'views 禁止直接 import element-plus，请使用 Base 组件（见 rules/shared/00-must-follow.md）。',
          },
        ],
        patterns: [
          {
            group: ['element-plus', 'element-plus/*'],
            message:
              'views 禁止 import element-plus 及其子路径，请使用 Base 组件（见 rules/shared/00-must-follow.md）。',
          },
        ],
      },
    ],
  },
};
