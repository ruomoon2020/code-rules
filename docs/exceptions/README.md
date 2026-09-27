# 机器可读豁免记录

业务仓将生效中的规则或门禁豁免保存为 `docs/exceptions/EXC-YYYY-NNN.yaml`，并运行：

```text
python common-governance/scripts/validate-exceptions.py --root .
```

字段与审批口径以 [`../rule-exception-process.md`](../rule-exception-process.md) 为准。每条记录必须有明确规则、范围、Owner、风险接受人、补偿控制、审批、起止日期、复查日和关闭条件；默认有效期不得超过 90 天。已关闭记录保留 `closed_at` 和 `closure_evidence` 供审计，不要删除历史证据。

可复制 [`../../examples/rule-exception.yaml`](../../examples/rule-exception.yaml) 作为起点。目录中只有本说明文件时表示当前没有仓库内豁免；外部工单系统中的豁免仍须导出同等字段供 CI 校验。

CI 样板：[`../../examples/ci/exceptions-required.yml`](../../examples/ci/exceptions-required.yml)（PR、主干与每周定时）。注意业务仓豁免 YAML 放在仓库根 `docs/exceptions/`，与本发布包内的 `common-governance/docs/exceptions/README.md` 不是同一目录。
