# 规则与门禁豁免记录

本目录用于保存业务仓中仍然生效或已经关闭的规则豁免。豁免不是绕过质量门禁的快捷方式，而是一份可审计、会到期、必须落实补偿控制的风险决定。

## 什么时候使用

只有在规则或门禁暂时无法满足，并且业务确实不能等待常规整改时，才创建豁免。普通缺陷、缺少测试、时间紧张或“先合并再说”都不能作为豁免理由。

## 建立记录

1. 复制 [`../../examples/rule-exception.yaml`](../../examples/rule-exception.yaml)。
2. 命名为 `docs/exceptions/EXC-YYYY-NNN.yaml`。
3. 填写规则、适用范围、Owner、风险接受人、补偿控制、审批、起止日期、复查日和关闭条件。
4. 提交前运行：

```text
python common-governance/scripts/validate-exceptions.py --root .
```

字段与审批口径以 [`../rule-exception-process.md`](../rule-exception-process.md) 为准。默认有效期不得超过 90 天；临近到期时必须关闭、续期或升级处理，不能静默失效。

## 关闭与审计

整改完成后填写 `closed_at` 和 `closure_evidence`，保留原记录供审计，不要删除历史证据。目录中只有本说明文件时，表示当前没有仓库内豁免；外部工单系统中的豁免仍须导出同等字段供 CI 校验。

CI 样板见 [`../../examples/ci/exceptions-required.yml`](../../examples/ci/exceptions-required.yml)，覆盖 PR、主干与每周定时检查。业务仓的豁免 YAML 应放在仓库根 `docs/exceptions/`；`common-governance/docs/exceptions/` 是发布包说明目录，不用于存放业务豁免。
