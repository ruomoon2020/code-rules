# 小程序发布与回滚 Checklist

> 这是业务项目发布证据模板；规则包自身发版使用根 `RELEASE.md`。微信审核 / 灰度细节见 `shared/19-release-ops.md`。

## 发布前

- [ ] lockfile 已提交，生产构建使用固定 Node.js / pnpm 与 frozen install
- [ ] lint、type-check、test、`build:mp-weixin`、`api:check`、`size:check` 已运行；未配置项已说明
- [ ] 测试失败可凭报告和 run/test id 定位；flaky 有期限，禁止重试洗绿
- [ ] 若改支付、回调或契约：重放、竞态与 N/N-1 兼容用例已运行
- [ ] 体验版 / 审核版禁止连接生产 API；各环境 `VITE_APP_ENV` 与域名白名单已核对
- [ ] Feature Flag / 灰度 / 实验配置通过 `common-governance/docs/environment-promotion.md` 的统一生命周期清单，并验证端侧安全失败行为
- [ ] 新增页面 / 分包已更新 `pages.json`；主包体积与分包策略未超预算
- [ ] 登录、授权、隐私协议、用户信息收集路径已按微信与项目隐私规范复核
- [ ] 本次使用的支付 / 分享 / 订阅消息等开放能力已按对应 shared 规则自检；未使用的能力不作为 Level 0 阻断项
- [ ] API breaking change 有兼容窗口、消费方确认和回滚顺序
- [ ] 发布版本、Git commit、变更范围、小程序版本号和回滚版本可追溯
- [ ] 生产产物已生成 SBOM 与 provenance / attestation，且验证引用已写入发布证据
- [ ] 使用 AI 工具且属发版 / 高风险 AI 变更时，AI Tool Safety 结果为 5/5，并绑定套件摘要、模型版本和评测人
- [ ] Level 2+ 平台控制快照不超过 90 天，组织权限、主干保护与生产非自审通过校验

## 灰度与观察

- [ ] 定义灰度范围（比例 / 人群）、观察窗口、停止条件和决策 Owner
- [ ] 观察启动成功率、关键接口失败率、支付 / 登录成功率和客诉
- [ ] 审核驳回预案与二次提审材料已准备
- [ ] 高峰期、大促或重大活动的发布冻结策略已确认

## 回滚

- [ ] 上一小程序版本仍可回退或重新提审
- [ ] 旧前端可兼容当前后端契约
- [ ] CDN / 静态资源 / 远程配置的回退策略已验证
- [ ] 回滚后重新检查登录、支付和关键业务链路

发布失败、回滚或临时绕过门禁时，按 common governance 的豁免与事故流程留痕。

发布证据使用 `common-governance/scripts/validate-release-evidence.py --artifact <真实产物>` 校验；仅填写摘要但未绑定真实文件不算生产验证通过。
