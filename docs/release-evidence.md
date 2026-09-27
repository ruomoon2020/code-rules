# 发布证据规范

> 发布清单必须产生可定位、可复核、可机器校验的证据，而不是只勾选复选框。

## 标准文件

每次生产发布生成一份 `release-evidence.yaml`，推荐按版本归档到 `releases/<version>/release-evidence.yaml`，并在 Release / 工单中链接。样板见 `common-governance/examples/release-evidence.yaml`。

必填内容：

- 发布 ID、语义化版本、`staging` / `production` 环境、Owner、变更引用和带时区的批准时间；
- 7–40 位 Git commit SHA、`sha256:` 产物摘要和本次使用的规则包版本（必须包含 `common-governance`）；
- SBOM、build provenance、签名 / attestation、builder 身份、验签命令和带时区的验签时间；
- 至少一个需求 / Issue 及其验收证据；
- 风险等级与摘要；
- 已验证的回滚命令或 Runbook 与回滚 Owner；
- Dashboard、告警和观察窗口；
- 代码、契约、安全、数据、可观测和发布门禁状态；
- 结构化豁免记录（门禁、Owner、到期日、补偿控制），没有豁免时使用空数组。

## 机器校验

```bash
python common-governance/scripts/validate-release-evidence.py --file releases/1.8.0/release-evidence.yaml

# 生产发布 CI 必须把实际产物交给校验器，避免只填一个格式正确的摘要
python common-governance/scripts/validate-release-evidence.py --file releases/1.8.0/release-evidence.yaml --artifact dist/app.tgz --require-artifact
```

校验器会拒绝：

- 空值和 `TODO`、`TBD`、`N/A` 等占位内容；
- 非语义化版本、无时区批准时间、无效 commit SHA 或产物摘要；
- 缺少 SBOM、provenance、签名 / attestation、builder 或验签证据；
- 使用 `--artifact` 时，YAML 摘要与实际产物字节不一致；
- 无需求或无验收证据；
- 回滚未测试或没有可执行命令 / Runbook；
- 观察窗口小于 60 分钟；
- 任一门禁不是 `passed` 或经批准的 `exception`；
- `exception` 门禁缺少对应的未过期结构化豁免，或豁免引用未处于 exception 的门禁；
- `high` / `critical` 风险没有灰度 / 金丝雀证据。

## 责任边界

不传 `--artifact` 时，文件通过校验只证明证据结构完整；生产发布必须使用 `--artifact --require-artifact`。发布 Owner 仍须确认远程 attestation 可验证、业务验收有效、回滚在目标环境可执行。

相关文档：[`definition-of-done.md`](definition-of-done.md)、[`requirements-traceability.md`](requirements-traceability.md)、[`slo-alerting-template.md`](slo-alerting-template.md)。
