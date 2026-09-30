# 前端发布与回滚 Checklist

> 这是业务项目发布证据模板；规则包自身发版使用根 `RELEASE.md`。

## 发布前

- [ ] lockfile 已提交，生产构建使用固定 Node.js / pnpm 与 frozen install
- [ ] lint、type-check、test、build、api check 已运行；未配置项已说明
- [ ] 测试失败可凭报告和 run/test id 定位；flaky 有期限，禁止重试洗绿
- [ ] 若改写链路或契约：重复点击、竞态恢复与 N/N-1 兼容用例已运行
- [ ] API breaking change 有兼容窗口、消费方确认和回滚顺序
- [ ] generated client 已与 OpenAPI `x-api-style` 对齐：`RESOURCE_REST` 使用 PATCH/DELETE，`GET_POST_COMPAT` 使用显式 POST 动作端点；`201/202/204`、错误体和认证声明已同步，`204` 不再按 JSON 响应体解析
- [ ] bundle 增量未超预算，或已有 Owner、原因和复测日期
- [ ] 生产 sourcemap 不公开；错误平台上传步骤已验证
- [ ] Feature Flag / 灰度 / 实验配置通过 `common-governance/docs/environment-promotion.md` 的统一生命周期清单
- [ ] 受监管 Web 场景已验证生产响应头、第三方脚本数据流、嵌入通信来源和 Enterprise Hardening E44–E49
- [ ] 新增数据展示、复制、下载、缓存或埋点已按分级检查
- [ ] 发布版本、Git commit、变更范围和回滚版本可追溯
- [ ] 生产产物已生成 SBOM 与 provenance / attestation，且验证引用已写入发布证据
- [ ] 使用 AI 工具且属发版 / 高风险 AI 变更时，AI Tool Safety 结果为 5/5，并绑定套件摘要、模型版本和评测人
- [ ] Level 2+ 平台控制快照不超过 90 天，组织权限、主干保护与生产非自审通过校验

## 灰度与观察

- [ ] 定义灰度范围、观察窗口、停止条件和决策 Owner
- [ ] 观察 JS 错误率、白屏率、API 失败率及关键业务成功率
- [ ] 核心页面检查登录过期、路由 chunk 失败和错误恢复
- [ ] 高峰期、结算窗口或重大活动的发布冻结策略已确认

## 回滚

- [ ] 上一版本静态资源 / 镜像仍可部署
- [ ] 旧前端可兼容当前后端契约和 schema
- [ ] 缓存、service worker、CDN 入口 HTML 的回退策略已验证
- [ ] 回滚后重新检查错误率、白屏率和关键业务链路

发布失败、回滚或临时绕过门禁时，按 common governance 的豁免与事故流程留痕。

发布证据使用 `common-governance/scripts/validate-release-evidence.py --artifact <真实产物>` 校验；仅填写摘要但未绑定真实文件不算生产验证通过。
