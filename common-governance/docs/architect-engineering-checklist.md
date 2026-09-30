# 架构师代码与工程规范 Checklist

> 适用场景：新项目立项评审、技术方案评审、上线前检查、对照团队规范做评审。
> 使用方式：先按「适用端」「最低 Level」「评审时机」过滤，再在评审记录中填写「通过 / 豁免 / 不适用」。最低 Level 表示常规采纳门槛；安全、权限、契约或数据风险命中时须提前触发。豁免须走 [`rule-exception-process.md`](rule-exception-process.md)。
> 合并与发布的强制门禁以 [`definition-of-done.md`](definition-of-done.md) 为准。本清单是评审提问单，不替代各端 `rules/shared/`。

规则列一律写仓库内完整路径，不使用跨端裸编号。业务仓未安装对应规则包时，仍按检查点判断，忽略缺失的文件路径。

---

## 一、架构与设计

| # | 适用端 | 最低 Level | 评审时机 | 检查项 | 检查点 | 具体要求 | 规则 |
|---|---|---|---|---|---|---|---|
| 1.1 | 后端 | L0 | 立项 / 方案 | 分层架构 | 新项目是否用轻量分层；如果不用，有没有写明原因 | 新项目默认轻量分层，接口对象用 Request / Response（`CRUD_LITE`、`ENTITY_REQUEST_RESPONSE`），不用先做三选一。已经使用 Web / Service / Manager / DAO 的旧项目可以继续。聚合复杂、入口多或存储方式多时，才升级到六边形并写 ADR。禁止跨层调用，也不要为了层次看起来完整再加一层只做转发的类 | `web-backend/rules/shared/01-project-structure.md`、`web-backend/rules/shared/15-testing.md`；[`definition-of-done.md`](definition-of-done.md) |
| 1.2 | 后端 | L0 | 立项 / 方案 | 模块边界和表的写入方 | 模块职责是否单一，代码和 SQL 是否只访问本模块的表 | 按业务模块划分。禁止导入其他模块的内部类型；本模块的 Mapper 和 XML 不得关联、查询或更新其他模块的表。跨模块只保存对方 ID，并通过公开接口或消息协作。报表模块只读，不得回写业务数据 | `web-backend/rules/shared/01-project-structure.md`、`web-backend/rules/shared/43-business-module-extension.md` |
| 1.2a | 后端 | L0 | 立项 / 方案 | 单写方 | 一个聚合或业务事实是否只有一个写入模块 | 为聚合、业务表和状态列声明唯一写入 Owner；其他模块只保存 ID 或维护事件驱动读模型，禁止回写源状态 | `web-backend/rules/shared/01-project-structure.md`、`web-backend/rules/shared/43-business-module-extension.md` |
| 1.3 | 后端 | L0 | 立项 / 方案 | 依赖方向 | 是否存在循环依赖、反向依赖 | 依赖只能指向更稳定的内侧。已接入架构测试或依赖检查时用它卡住方向；未接入须说明，不能把某个工具当成所有仓库的必做项 | `web-backend/rules/shared/01-project-structure.md`、`web-backend/rules/shared/15-testing.md` |
| 1.4 | 全端 | L0 | 立项 / 方案 | 接口契约 | 是否有版本、入参出参、错误码和破坏性变更策略 | OpenAPI 为单一来源。入参和出参用传输对象，禁止把持久化实体直接当接口。消费端生成代码，禁止手改 `generated/**` | `web-backend/rules/shared/04-rest-api-design.md`、`web-backend/rules/shared/05-openapi-contract.md`、`web-backend/rules/shared/12-dto-mapping.md`；[`definition-of-done.md`](definition-of-done.md) §契约 |
| 1.5 | 后端 | L0 | 立项 / 方案 | 幂等与并发 | 支付、导入、批量变更是否有幂等键；更新是否防丢失；分布式锁是否会拖住业务 | 重复请求返回同一业务结果或明确冲突码；唯一索引 + 乐观锁，禁止先查再插。分布式锁只锁短临界区，必须有过期时间，释放时校验持有者 | `web-backend/rules/shared/18-idempotency-concurrency.md` |
| 1.6 | 后端 | L0 | 立项 / 方案 | 领域模型 | 当前架构档的业务规则应放在哪里 | 默认 `CRUD_LITE` 由应用服务编排业务规则，Entity 可保持轻量但不得直接出 API；只有显式声明 `DOMAIN_HEXAGONAL` 时，才要求不变量进入实体 / 值对象 / 领域服务，并由应用服务调用聚合 | `web-backend/rules/shared/01-project-structure.md`、`web-backend/rules/shared/11-domain-model.md` |
| 1.7 | 后端 | L0 | 立项 / 方案 | 扩展点 | 多实现、多租户差异、渠道差异是否有稳定扩展点 | 只有确有多个实现时才预留 SPI / 插件；写明负责人和删除条件。单条业务不要为扩展而抽象 | `web-backend/rules/shared/43-business-module-extension.md` |
| 1.8 | 后端 | L0 | 立项 / 方案 | 配置与认证材料 | 多环境是否隔离；生产认证材料是否进仓库 | 生产认证材料不得进入 Git；从环境变量或项目配置中心注入，并按环境隔离。集中托管、轮换和吊销按 L3 的 2.15a 评审 | `web-backend/rules/shared/21-configuration-secrets.md` |
| 1.9 | 后端 | L0 | 立项 / 方案 | 事务边界 | 本地事务是否越过模块 / 外部系统边界 | 模块内同一聚合使用本地事务；禁止一个 `@Transactional` 写两个业务模块的表，也禁止事务内同步 HTTP / RPC 或发送不可回滚消息；跨模块 / 跨服务用公开接口、Outbox、事件或补偿 | `web-backend/rules/shared/01-project-structure.md`、`web-backend/rules/shared/18-idempotency-concurrency.md`、`web-backend/rules/shared/17-messaging-async.md` |
| 1.10 | 全端 | L0 | 方案 | 金额与时间基础 | 是否避免浮点金额，以及把自然日当成带时区时刻 | 金额不得用浮点数计算，并写明币种、精度和舍入。时刻携带时区或明确 UTC；自然日用日期类型并写明业务时区与闭开区间，不得用设备或服务器本地时区猜测业务日 | `web-backend/rules/shared/00-must-follow.md`、`web-front/rules/shared/23-i18n-locale.md`、`miniapp/rules/shared/12-list-form-pagination.md` |
| 1.10a | 后端 | L3 | 方案 / 上线 | 复杂账期与显式状态机 | 账期关闭、跨期调整或受控状态流转是否集中治理 | 复杂账期定义关闭、补记 / 重开与审计规则；存在显式生命周期的聚合定义合法迁移、权限、并发和审计 | `web-backend/rules/shared/40-money-time-precision.md`、`web-backend/rules/shared/41-dictionary-state-machine.md` |
| 1.11 | 后端 | L0 | 立项 / 方案 | 接口形态 | 是否返回持久化实体；排序和筛选是否白名单 | 入参和出参用传输对象。排序、筛选字段白名单。引入图查询、远程调用或长连接时再写决策记录，并读取 9.14 与 `web-backend/rules/shared/33-alternate-api-paradigms.md` | `web-backend/rules/shared/12-dto-mapping.md`、`web-backend/rules/shared/19-pagination-query.md` |
| 1.12 | 后端 | L0 | 立项 / 方案 | 定时与批处理 | 任务是否防重、可恢复、可关闭 | 多实例不得重复执行。重试不得重复扣款或重复发消息。分批提交，禁止一批事务包住海量数据。任务有负责人、超时、告警和关闭开关。任务不能绕过权限、租户、审计和脱敏 | `web-backend/rules/shared/25-jobs-scheduling.md` |
| 1.13 | 后端 | L0 | 立项 / 方案 | 租户和异步写入 | 做多租户或异步写入时，能否识别发起人和所属租户 | 未发现租户设计时按单租户（`NONE`）处理，按资源 ID 访问不增加租户条件。已有 `tenant_id`、租户插件或拦截器时，沿用共享表加租户列（`SHARED_COLUMN`）。事件、任务和 Outbox 必须包含 actorId、traceId；多租户项目还须包含 tenantId。消费端不得使用无数据范围限制的系统账号扩大权限 | `web-backend/rules/shared/00-must-follow.md`、`web-backend/rules/shared/25-jobs-scheduling.md`、`web-backend/rules/shared/39-event-contracts.md`、`web-backend/rules/shared/43-business-module-extension.md` |
| 1.14 | 后端 | L2 | 方案 | 长流程补偿 | 跨模块 / 外部系统流程失败后能否定位和接管 | 实现前定义步骤顺序、每步幂等键、终态、补偿顺序和人工入口；状态可查询，不能用互调任务代替流程定义 | `web-backend/rules/shared/25-jobs-scheduling.md`、`web-backend/rules/shared/17-messaging-async.md` |

---

## 二、非功能需求

| # | 适用端 | 最低 Level | 评审时机 | 检查项 | 检查点 | 具体要求 | 规则 |
|---|---|---|---|---|---|---|---|
| 2.1 | 后端 | L2 | 方案 / 上线 | 性能指标 | 核心接口是否有延迟和吞吐预算 | 上线前有压测基线；超预算进入发布风险评审，禁止只把超时调大 | `web-backend/rules/shared/16-performance.md`、`web-backend/rules/shared/32-service-reliability.md` |
| 2.2 | 后端 | L1 | 方案 / 上线 | 依赖韧性 | 关键外部依赖是否有超时、熔断、限流、降级 | 降级返回可理解的错误码。按能力选型，不绑定已停止维护的具体库 | `web-backend/rules/shared/28-external-integration.md`、`web-backend/rules/shared/32-service-reliability.md` |
| 2.3 | 后端 | L1 | 方案 / 上线 | 限流隔离 | 是否有接口级、租户级限流和舱壁 | 按接口、租户或连接池隔离。具体算法由网关或限流组件实现。失败时拒绝，而不是拖垮进程 | `web-backend/rules/shared/32-service-reliability.md`、`web-backend/rules/shared/28-external-integration.md` |
| 2.3a | 后端 | L1 | 方案 / 上线 | 请求截止时间 | 核心请求及内部同步调用是否共享端到端时间预算 | 核心链路声明截止时间；模块间调用继承剩余预算，不逐层重置超时；高扇出 / 批量转异步任务，不占在线请求线程 | `web-backend/rules/shared/28-external-integration.md`、`web-backend/rules/shared/32-service-reliability.md` |
| 2.4 | 后端 | L1 | 方案 / 上线 | 可观测性 | 日志、追踪、指标是否齐全 | `traceId` 贯穿全链路。核心接口至少看请求速率、错误率和延迟。日志无令牌和个人信息明文 | `web-backend/rules/shared/09-logging-observability.md` |
| 2.5 | 后端 | L2 | 方案 / 上线 | 告警与值班 | 是否分级，是否有人负责 | P0 核心不可用、P1 核心降级、P2 非核心；告警带追踪号、服务、版本；有值班表 | `web-backend/rules/shared/32-service-reliability.md`；`docs/slo-alerting-template.md` |
| 2.6 | 后端 | L0 | 方案 / 上线 | 认证、授权与越权 | 是否同时覆盖登录、功能权限、数据范围和对象级越权 | 前端隐藏按钮不能代替后端鉴权。列表、详情、导出、批量操作使用同一套数据权限。必测未登录、无权限、拿他人 ID 访问。租户模型不是 `NONE` 时另测跨租户 | `web-backend/rules/shared/06-security-authz.md`、`web-backend/rules/shared/24-data-access-cache.md` |
| 2.7 | 全端 | L1 | 方案 / 上线 | 数据分级与脱敏 | 新字段是否分级；日志、缓存、导出、消息是否按级处理 | 对照分级矩阵。脱敏组件不能只加在列表页 | `docs/data-classification-matrix.md`、`web-backend/rules/shared/29-data-privacy-lifecycle.md` |
| 2.8 | 后端 | L1 | 方案 / 上线 | 一致性 | 跨服务写操作的一致性方案是否写明 | 优先本地事务 + Outbox 和补偿；跨库禁止用一个本地事务假装分布式事务 | `web-backend/rules/shared/17-messaging-async.md`、`web-backend/rules/shared/18-idempotency-concurrency.md` |
| 2.9 | 后端 | L2 | 方案 | 威胁建模 | 登录、支付、权限、导入导出、Webhook、个人信息变更是否做了轻量威胁建模 | 记录资产、信任边界、入口、滥用场景、缓解和剩余风险负责人 | `web-backend/rules/shared/35-threat-modeling.md` |
| 2.10 | 后端 | L1 | 方案 / 上线 | 审计 | 敏感操作能否回答谁在何时做了什么 | 审计含操作者、追踪号、对象和前后状态；禁止只打一条「操作成功」 | `web-backend/rules/shared/27-audit-log.md` |
| 2.11 | 后端 | L1 | 方案 / 上线 | 服务间认证基础 | 内部调用是否证明调用方身份 | 不信任内网地址；调用身份、租户和数据权限不得丢失 | `web-backend/rules/shared/00-must-follow.md`、`web-backend/rules/shared/06-security-authz.md` |
| 2.11a | 后端 | L3 | 方案 / 上线 | 服务调用身份 | 调用方凭证是否统一管理、轮换和吊销 | 服务之间用受控签名、令牌或双向 TLS。凭证要能轮换、吊销和审计，不能用“在内网”代替身份 | `web-backend/rules/shared/37-service-to-service-auth.md` |
| 2.12 | 后端 | L2 | 方案 / 上线 | 恢复目标 | 是否声明可接受的数据丢失窗口和恢复时间 | 数据库、消息、对象存储的备份与目标一致；没做过恢复演练，不得声称可随时恢复 | `web-backend/rules/shared/32-service-reliability.md`、`web-backend/rules/shared/31-production-data-ops.md` |
| 2.13 | 后端 | L2 | 上线 | 错误预算 | 可用性未达标时是否会停掉无关发布 | 对外承诺不得高于内部目标；错误预算烧完优先修稳定性和观测 | `web-backend/rules/shared/32-service-reliability.md` |
| 2.14 | 后端 | L1 | 方案 / 上线 | 功能开关 | 开关是否有负责人和到期日 | 灰度开关到期删除代码和配置，禁止长期留在主干 | `web-backend/rules/shared/21-configuration-secrets.md` |
| 2.15 | 后端 | L0 | 方案 / 上线 | 密码与令牌基础 | 密码如何存储；令牌是否完整校验 | 密码只用带盐慢哈希；禁止自研算法和硬编码认证材料。令牌校验签名、过期、签发方和受众，旧会话可失效 | `web-backend/rules/shared/00-must-follow.md`、`web-backend/rules/shared/06-security-authz.md` |
| 2.15a | 后端 | L3 | 方案 / 上线 | 密钥托管与轮换 | 密钥是否集中托管、轮换和吊销 | 声明密钥 Owner、托管位置、轮换周期、吊销和审计，不把应用配置当密钥生命周期系统 | `web-backend/rules/shared/36-crypto-key-management.md` |
| 2.16 | 后端 | L0 | 方案 / 上线 | 回调与重放基础 | Webhook 和外部回调能否被伪造或重放 | 校验调用身份、签名或等价认证，并使用时间窗、随机数或幂等键防重放 | `web-backend/rules/shared/00-must-follow.md`、`web-backend/rules/shared/18-idempotency-concurrency.md` |
| 2.17 | 后端 | L0 | 方案 / 上线 | 出站请求 | 用户能否指定服务端去访问的地址 | 出站地址走白名单，禁止把用户输入直接当作请求目标 | `web-backend/rules/shared/28-external-integration.md` |
| 2.18 | 后端 | L0 | 方案 / 上线 | 会话与暴露面 | 跨域、Cookie、管理端点在生产是否收口 | 生产禁止任意源带凭据。Cookie 会话启用跨站防护。接口文档和除健康检查外的管理端点不对公网开放 | `web-backend/rules/shared/06-security-authz.md`、`web-backend/rules/shared/22-operability.md` |
| 2.19 | 后端 | L0 | 方案 / 上线 | 登录防刷 | 登录、验证码、重置密码是否限流 | 按 IP、账号或租户限流；错误提示不暴露账号是否存在 | `web-backend/rules/shared/06-security-authz.md` |

---

## 三、数据与存储

| # | 适用端 | 最低 Level | 评审时机 | 检查项 | 检查点 | 具体要求 | 规则 |
|---|---|---|---|---|---|---|---|
| 3.1 | 后端 | L0 | 方案 | 数据库规范 | 命名、索引、字段类型是否统一 | 建表模板 + 评审；金额列写明精度，多租户唯一约束带租户键 | `web-backend/rules/shared/07-persistence-mybatis.md`、`web-backend/rules/shared/02-naming.md` |
| 3.2 | 后端 | L0 | 方案 | 索引与查询 | 是否避免全表扫描、深分页，以及把用户输入拼进排序 | 慢查询监控 + 执行计划审查；排序和筛选走白名单 | `web-backend/rules/shared/07-persistence-mybatis.md`、`web-backend/rules/shared/19-pagination-query.md` |
| 3.3 | 后端 | L2 | 立项 / 方案 | 分片 | 是否要分库分表；分片键是否写进决策记录 | 分库分表、索引重构和跨库迁移须先有决策记录，写明容量、分片键、迁移和回滚。分片键要能覆盖主要查询 | `web-backend/rules/shared/30-ownership-adr.md` |
| 3.4 | 后端 | L2 | 方案 | 读写分离 | 写完立刻读的路径是否会读到从库旧数据 | 创建后立即详情、支付后查单等路径必须写明是否读主库。从库延迟要监控，超过阈值告警或改读主库。事务内读写走同一连接 | `web-backend/rules/shared/07-persistence-mybatis.md` |
| 3.5 | 后端 | L1 | 方案 / 上线 | 缓存防护 | 穿透、击穿、雪崩是否有对策 | 空值缓存、互斥、随机过期按场景选用，不默认三件套全上 | `web-backend/rules/shared/24-data-access-cache.md` |
| 3.6 | 后端 | L1 | 方案 / 上线 | 缓存一致性 | 更新策略、失效和租户维度是否写明 | 写明是旁路缓存还是其他策略，以及 TTL。缓存键和值不得带明文个人信息 | `web-backend/rules/shared/24-data-access-cache.md`、`web-backend/rules/shared/29-data-privacy-lifecycle.md` |
| 3.7 | 后端 | L1 | 方案 / 上线 | 结构迁移 | 是否版本化，新旧版本能否同时运行 | Flyway / Liquibase；先扩展再收缩，保证滚动发布期间新旧代码都能读写；禁止手工改表 | `web-backend/rules/shared/07-persistence-mybatis.md`；`docs/definition-of-done.md` §数据 |
| 3.8 | 后端 | L3 | 方案 / 上线 | 事件契约治理 | 顺序、重复、死信和契约版本是否处理 | 幂等消费 + 死信 + 有界重试；事件像接口一样管理版本、兼容和上下文 | `web-backend/rules/shared/17-messaging-async.md`、`web-backend/rules/shared/39-event-contracts.md` |
| 3.9 | 后端 | L1 | 方案 / 上线 | 保留与删除 | 是否有保留周期、注销和个人信息删除 | 软删除要说明何时物理清理；注销后对外接口不得再返回可识别个人信息 | `web-backend/rules/shared/29-data-privacy-lifecycle.md`、`web-backend/rules/shared/34-data-archival.md` |
| 3.10 | 后端 | L1 | 方案 / 上线 | 生产数据操作 | 手工 SQL、回填、从生产复制数据是否可审批 | 工单、影响范围、预演、回滚、审计；条件必须带主键、租户或时间窗 | `web-backend/rules/shared/31-production-data-ops.md` |
| 3.11 | 后端 | L2 | 上线 | 备份恢复 | 备份是否加密、限权，并做过恢复演练 | 证明「能恢复」，而不是只证明「有备份」 | `web-backend/rules/shared/31-production-data-ops.md`、`web-backend/rules/shared/32-service-reliability.md` |
| 3.12 | 后端 | L2 | 方案 / 上线 | 多数据库 | 若同时支持多种数据库，迁移和核心 SQL 是否都跑过 | 每种目标库都做迁移校验和核心用例，禁止只在一种库上通过 | `web-backend/rules/shared/07-persistence-mybatis.md`、`web-backend/rules/shared/15-testing.md` |
| 3.13 | 全端 | L0 | 方案 | 字典与主数据基础 | 枚举和主数据是否只有一处契约来源 | 前后端共用 OpenAPI 枚举或平台字典；禁止各端各写一套魔法值或静默改变已有取值语义 | `web-backend/rules/shared/00-must-follow.md`、`web-backend/rules/shared/05-openapi-contract.md` |
| 3.14 | 后端 | L2 | 方案 / 上线 | 租户配额 | 多租户是否限制单租户的请求、存储或批处理量 | 配额超限有明确错误码，不能靠把线程池打满来限流 | `web-backend/rules/shared/24-data-access-cache.md` |
| 3.15 | 后端 | L3 | 方案 / 上线 | 冷热数据 | 在线接口是否会把归档数据一起扫进来 | 在线接口默认只查仍在主路径上的热数据，避免历史大表拖慢主库。查归档走单独接口和权限，并写清是否异步导出。禁止对大表做无分批的全表删除。归档存储必须鉴权，不能公开访问 | `web-backend/rules/shared/34-data-archival.md` |

---

## 四、代码质量与工程化

| # | 适用端 | 最低 Level | 评审时机 | 检查项 | 检查点 | 具体要求 | 规则 |
|---|---|---|---|---|---|---|---|
| 4.1 | 后端 | L0 | 方案 | 项目结构 | 目录是否与脚手架一致 | 统一脚手架；新模块走扩展规则，不另起一套目录 | `web-backend/rules/shared/01-project-structure.md` |
| 4.2 | 后端 | L0 | 方案 | 命名 | 类、方法、变量、表和字段是否可读 | 检查器强制。金额字段带语义和单位，禁止 `money`、`price1` 这类名字 | `web-backend/rules/shared/02-naming.md` |
| 4.3 | 后端 | L0 | 方案 | 注释 | 是否解释为什么，而不是复述代码 | 复杂 SQL、权限、多库兼容、金额和时区语义必须写清。公开契约写在 OpenAPI，不靠类注释堆历史 | `web-backend/rules/shared/03-code-style.md` |
| 4.4 | 后端 | L0 | 方案 | 变更记录 | 作者、日期、版本从哪里查 | 以 Git 历史和变更日志为准。不要求文件头再写作者、日期、版本 | `docs/git-pr-governance.md` |
| 4.5 | 后端 | L0 | 方案 | 异常与错误码 | 响应壳数字状态与稳定业务错误码是否分清 | 既有响应壳可保留数字 `code`；稳定业务契约字段是字符串 `errorCode`，建议使用 `DOMAIN_REASON`，例如 `USER_NOT_FOUND`。客户端不得按 `message` 分支；未知异常映射为 `INTERNAL_ERROR` 且不返回堆栈 | `web-backend/rules/shared/08-exception-errorcodes.md` |
| 4.6 | 后端 | L0 | 方案 | 输入校验 | 是否防批量赋值和越权字段 | 更新请求只含允许修改的字段；角色、租户、状态不能从普通更新接口写入 | `web-backend/rules/shared/13-validation.md` |
| 4.7 | 后端 | L1 | 方案 / 上线 | 静态扫描 | 严重问题是否阻断合并 | 质量门禁阻断严重缺陷；跳过须记录豁免 | `web-backend/rules/shared/23-quality-gates.md` |
| 4.8 | 全端 | L1 | 方案 / 上线 | 依赖 | 版本是否锁定；漏洞和许可证是否扫描 | 用父 POM 或 BOM 对齐版本，禁止无回归地升级主版本。高危漏洞按处置时限。GPL / AGPL / 未知许可证须评审。发布制品的软件物料清单见 7.5 | `web-backend/rules/shared/20-dependency-governance.md`；[`supply-chain-baseline.md`](supply-chain-baseline.md) |
| 4.9 | 全端 | L1 | 方案 | 代码审查 | 谁必须看哪类变更 | 受保护分支只走拉取请求。契约、数据库、安全、持续集成按所有者矩阵审查，不能只数人数 | `docs/codeowners-matrix.md`、`docs/git-pr-governance.md` |
| 4.10 | 后端 | L0 | 方案 | 文件导入导出 | 上传、导入、下载是否有边界 | 校验类型和大小。导入有行数上限、幂等和行列级失败明细。下载链接鉴权并设有效期，禁止永久公开地址 | `web-backend/rules/shared/14-file-import-export.md` |

---

## 五、测试

| # | 适用端 | 最低 Level | 评审时机 | 检查项 | 检查点 | 具体要求 | 规则 |
|---|---|---|---|---|---|---|---|
| 5.1 | 全端 | L1 | 方案 / 上线 | 单元与分支 | 核心逻辑的分支、异常和权限失败是否覆盖 | 项目覆盖层定义阈值并关注新增代码与趋势；生成代码等排除项须显式配置。覆盖率不能代替有效断言，核心域可条件启用变异测试 | `web-backend/rules/shared/15-testing.md` |
| 5.2 | 全端 | L1 | 方案 / 上线 | 边界 | 空值、极值、金额、时区、编码和超量输入是否覆盖 | 参数化测试；覆盖金额舍入、月末/年末、Unicode、超长文本、大文件和大分页。解析器、规则引擎等高风险模块可用属性测试或模糊测试 | `web-backend/rules/shared/15-testing.md`、`web-backend/rules/shared/00-must-follow.md`、`web-front/rules/shared/15-testing.md`、`miniapp/rules/shared/16-testing-quality-gates.md` |
| 5.3 | 全端 | L1 | 方案 / 上线 | 集成 | 数据库、缓存、消息和外部依赖是否在隔离环境联调 | 使用与生产行为一致的容器、嵌入式依赖或等价临时环境；禁止连生产和预发。异步与跨线程用例显式清理，不能只依赖测试事务回滚 | `web-backend/rules/shared/15-testing.md` |
| 5.4 | 全端 | L1 | 方案 / 上线 | API 与文件契约 | 接口和文件契约是否兼容消费者 | 固定版本 `oasdiff breaking --fail-on WARN` + 消费端生成代码校验；批量文件声明版本和兼容策略；独立部署服务按风险启用消费者驱动契约 | `web-backend/rules/shared/05-openapi-contract.md`、`web-backend/rules/shared/15-testing.md` |
| 5.4a | 后端 | L3 | 方案 / 上线 | 事件契约 | MQ、Webhook 和 Outbox 事件是否可演进 | 事件名称、版本、生产方、上下文和兼容策略进入契约；验证重复、乱序和旧消费者 | `web-backend/rules/shared/39-event-contracts.md` |
| 5.5 | 全端 | L0 | 方案 / 上线 | 回归 | 合并请求和发布是否运行匹配风险的回归集 | PR 跑快速确定性回归；发布分支跑集成、端到端、安全和迁移回归；定时跑跨平台或长时间测试。Required 失败禁止合并 | `web-backend/rules/shared/23-quality-gates.md`；`docs/branch-protection.md` |
| 5.6 | 后端 | L2 | 上线 | 性能 | 是否有可复现的压测基线，并纳入高风险发布 | 记录数据量、并发/QPS、预热与时长、P50/P95/P99、错误率、资源水位和基线差异；预算超标进入风险评审 | `web-backend/rules/shared/16-performance.md` |
| 5.7 | 全端 | L1 | 方案 / 上线 | 安全测试 | 越权、注入、依赖和敏感凭据是否在流水线里 | PR 跑静态、依赖、凭据及鉴权回归；租户模型不是 `NONE` 时含跨租户回归。有可部署环境时跑 DAST/API 模糊测试；人工渗透按风险或大版本启用 | `web-backend/rules/shared/06-security-authz.md`、`web-backend/rules/shared/15-testing.md`、`web-backend/rules/shared/23-quality-gates.md` |
| 5.8 | 后端 | L2 | 上线 | 故障演练 | 是否验证过依赖失败、降级和数据恢复 | 演练声明稳态、影响半径、中止条件和恢复目标，并记录 RTO/RPO 与改进行动。Chaos Mesh 等只是可选注入手段 | `web-backend/rules/shared/32-service-reliability.md`、`web-backend/rules/shared/31-production-data-ops.md` |
| 5.9 | 全端 | L1 | 方案 / 上线 | 测试数据 | 是否可重复、可隔离、可清理且无生产个人信息 | 优先 synthetic fixture；生产数据须脱敏与审批。按用例/租户隔离，失败后可清理；性能数据达到目标数量级 | `web-backend/rules/shared/15-testing.md`、`web-backend/rules/shared/29-data-privacy-lifecycle.md` |
| 5.10 | 全端 | L1 | 方案 / 上线 | 测试稳定性 | 用例是否可重复，是否靠重试掩盖偶发失败 | 固定时钟、随机种子、网络响应和运行版本；监控 flaky rate。隔离用例须有 Owner、原因和到期日，禁止无限重试把红灯洗绿 | `web-backend/rules/shared/15-testing.md`、`web-front/rules/shared/15-testing.md`、`miniapp/rules/shared/16-testing-quality-gates.md`；`docs/rule-exception-process.md` |
| 5.11 | 全端 | L2 | 方案 / 上线 | 并发与幂等 | 重复提交、并发更新、重复消费和乱序到达是否验证 | 覆盖幂等键、唯一约束、乐观锁冲突、任务多实例防重、消息重复投递和重放 | `web-backend/rules/shared/18-idempotency-concurrency.md`、`web-backend/rules/shared/25-jobs-scheduling.md`、`web-backend/rules/shared/15-testing.md`、`web-front/rules/shared/15-testing.md`、`miniapp/rules/shared/16-testing-quality-gates.md` |
| 5.12 | 全端 | L2 | 方案 / 上线 | 兼容与迁移 | 新旧应用版本和数据库迁移是否可用 | 覆盖 N/N-1、滚动升级和 expand/migrate/contract；验证可重入迁移及前滚/回滚策略 | `web-backend/rules/shared/05-openapi-contract.md`、`web-backend/rules/shared/07-persistence-mybatis.md`；[`environment-promotion.md`](environment-promotion.md) |
| 5.12a | 后端 | L3 | 方案 / 上线 | 事件升级 | 新旧事件生产者和消费者能否并存 | 覆盖事件 Schema 版本、兼容窗口、重放及前滚/回滚策略 | `web-backend/rules/shared/39-event-contracts.md` |
| 5.13 | 全端 | L1 | 方案 / 上线 | 失败诊断证据 | CI 失败后能否直接定位原因 | 保留测试报告、原始输出和 run/test id；有请求上下文时再关联 traceId。端侧按需保留截图、视频、网络记录。证据须脱敏并按期限保存 | `web-backend/rules/shared/15-testing.md`、`web-backend/rules/shared/09-logging-observability.md`、`web-front/rules/shared/15-testing.md`、`web-front/rules/shared/18-logging-observability.md`、`miniapp/rules/shared/16-testing-quality-gates.md`、`miniapp/rules/shared/15-logging-observability.md`；[`requirements-traceability.md`](requirements-traceability.md) |

---

## 六、文档与协作

| # | 适用端 | 最低 Level | 评审时机 | 检查项 | 检查点 | 具体要求 | 规则 |
|---|---|---|---|---|---|---|---|
| 6.1 | 全端 | L0 | 立项 / 方案 / 上线 | 架构决策 | 关键选型是否有记录 | 每个重大决策一篇决策记录：背景、选项、后果 | `web-backend/rules/shared/30-ownership-adr.md` |
| 6.2 | 全端 | L0 | 立项 / 方案 / 上线 | 架构图 | 若项目已有架构图，图是否还和当前边界一致 | 有图就和代码一起更新。仓库不强制某一种画法。重大边界变化记在决策记录里 | `web-backend/rules/shared/30-ownership-adr.md` |
| 6.3 | 全端 | L0 | 立项 / 方案 / 上线 | 接口文档 | 是否由契约生成并在合并时检查差异 | OpenAPI + 流水线发布；破坏性变更写兼容、迁移和回滚 | `web-backend/rules/shared/05-openapi-contract.md` |
| 6.4 | 全端 | L0 | 立项 / 方案 / 上线 | 需求追踪 | 需求、验收条件、实现和验证是否能对上 | 拉取请求写明需求编号、验收条件和证据 | `docs/requirements-traceability.md` |
| 6.5 | 全端 | L0 | 立项 / 方案 / 上线 | 业务正确性 | 行为变更是否经过人工业务评审 | 流程、数据、权限、契约和回归由人看过，不把测试通过当成业务正确 | `docs/business-correctness-review.md` |
| 6.6 | 全端 | L0 | 立项 / 方案 / 上线 | README 与运维手册 | 是否能按文档启动、部署、回滚和排障 | 后端数据与基础设施恢复写入 `web-backend/rules/docs/backup-restore-runbook.md` 或项目后端运维手册；管理端静态资源 / CDN 回滚、小程序版本回退分别写入本端发布文档或项目级运行手册，禁止塞进后端备份手册 | `web-backend/rules/docs/backup-restore-runbook.md`、`web-front/rules/docs/release-checklist.md`、`miniapp/rules/docs/release-checklist.md` |
| 6.7 | 全端 | L0 | 立项 / 方案 / 上线 | 技术债 | 存量债务是否只减不增 | 机器基线记录当前债务；新代码按目标规则，禁止为了迁就存量去改共享规则 | `docs/migration-baseline.md` |
| 6.8 | 全端 | L0 | 立项 / 方案 / 上线 | 豁免 | 跳过门禁是否有期限和补偿 | 写明负责人、到期日、补偿措施和关闭证据 | `docs/rule-exception-process.md` |
| 6.9 | 全端 | L2 | 上线 | 事故 | 是否有响应路径和复盘 | 分级、沟通、证据保全；复盘含时间线、根因、行动项和关闭人 | `docs/incident-response.md`、`docs/incident-postmortem-template.md` |
| 6.10 | 全端 | L2 | 方案 / 上线 | 合规留痕 | 金融或政务是否留下可审计证据 | 使用合规证据日志，不能只凭安全测试通过 | `docs/compliance-evidence-log.md` |

---

## 七、持续集成与发布

| # | 适用端 | 最低 Level | 评审时机 | 检查项 | 检查点 | 具体要求 | 规则 |
|---|---|---|---|---|---|---|---|
| 7.1 | 全端 | L0 | 方案 / 上线 | 流水线 | 构建、测试、扫描是否自动执行 | 必需检查失败不能合并；流水线权限最小化，动作版本钉死 | `web-backend/rules/shared/23-quality-gates.md`；`docs/branch-protection.md` |
| 7.2 | 全端 | L1 | 立项 / 方案 | 分支策略 | 是否统一，主干是否受保护 | 选定一种分支模型后全仓遵守；受保护分支禁止直推 | `docs/git-pr-governance.md`、`docs/branch-protection.md` |
| 7.3 | 全端 | L0 | 方案 | 提交说明 | 是否能看出变更意图 | Conventional Commits；破坏性变更写迁移和回滚 | `docs/git-pr-governance.md` |
| 7.4 | 全端 | L1 | 方案 / 上线 | 版本 | 是否语义化，变更日志是否经人看过 | SemVer。自动生成的变更日志仍由发布负责人审阅破坏性变更 | `docs/git-pr-governance.md` |
| 7.5 | 全端 | L3 | 方案 / 上线 | 镜像与云原生运行时 | 是否最小、非 root，并有物料清单和资源边界 | 多阶段构建；禁止 `latest`；镜像内不带密钥。CPU 和内存有请求值与上限；生产制品生成物料清单和构建证明 | `web-backend/rules/shared/38-cloud-native-runtime.md`；`docs/supply-chain-baseline.md`、`docs/release-evidence.md` |
| 7.6 | 全端 | L2 | 方案 / 上线 | 发布策略 | 核心域是否灰度或金丝雀 | 按业务风险选择；开关有负责人和到期日 | `web-backend/rules/shared/32-service-reliability.md`、`web-backend/rules/shared/21-configuration-secrets.md`；`docs/environment-promotion.md` |
| 7.7 | 全端 | L2 | 上线 | 回滚 | 是否能退回上一制品和配置 | 回滚路径可执行，并在等价环境演练过。数据结构在滚动期间兼容。只有「可以回滚」的描述、没有演练证据，不能进入生产 | [`environment-promotion.md`](environment-promotion.md)、[`release-evidence.md`](release-evidence.md) |
| 7.8 | 全端 | L3 | 上线 | 环境晋级 | 开发、测试、预发、生产是否隔离 | 同一不可变制品晋级；配置漂移有证据；禁止用本机直连生产库发布 | `docs/environment-promotion.md` |
| 7.9 | 全端 | L0 | 方案 / 上线 | 密钥扫描 | 提交和流水线是否扫描凭据 | 发现即阻断，并按安全策略轮换 | `docs/supply-chain-baseline.md` |
| 7.10 | 全端 | L2 | 上线 | 发布证据 | 生产发布是否留下可校验记录 | 范围、风险、制品摘要、回滚验证、负责人 | `docs/release-evidence.md` |
| 7.11 | 后端 | L1 | 方案 / 上线 | 运行探针 | 进程是否能被判定为存活、就绪，并优雅停机 | 提供存活和就绪检查。停机前处理完进行中的请求。连接池和线程池有监控。探针以外的管理端点不对公网开放 | `web-backend/rules/shared/22-operability.md` |

---

## 八、团队与流程

| # | 适用端 | 最低 Level | 评审时机 | 检查项 | 检查点 | 具体要求 | 规则 |
|---|---|---|---|---|---|---|---|
| 8.1 | 全端 | L0 | 立项 / 方案 / 上线 | 技术选型 | 新语言、框架、中间件是否有评审 | 选型写入决策记录，含维护状态、许可证和退出方案 | `web-backend/rules/shared/30-ownership-adr.md` |
| 8.2 | 全端 | L1 | 方案 / 上线 | 规范落地 | 能自动检查的是否已经进流水线 | 工具能挡住的不靠人口头提醒；例外走豁免单 | `web-backend/rules/shared/23-quality-gates.md`；`docs/rule-exception-process.md` |
| 8.3 | 全端 | L0 | 立项 / 方案 / 上线 | 新人上手 | 是否能按文档在短时间内把项目跑起来 | 上手文档含依赖、启动和最小验证命令 | `web-backend/rules/docs/onboarding-new-project.md`、`web-front/rules/docs/onboarding-new-project.md`、`miniapp/rules/docs/onboarding-new-project.md` |
| 8.4 | 全端 | L0 | 立项 / 方案 / 上线 | 知识沉淀 | 决策和事故是否留在仓库里 | 决策记录和复盘进版本库，分享不能代替这些记录 | `web-backend/rules/shared/30-ownership-adr.md`；`docs/incident-postmortem-template.md` |
| 8.5 | 全端 | L2 | 上线 | 度量 | 是否看交付频率、变更失败率、恢复时间和前置时间 | 用这四项看效率；缺陷率单独看质量。指标要有负责人和复查日期 | `docs/adoption-scorecard.md` |
| 8.6 | 全端 | L3 | 方案 / 上线 | 成本治理 | 大查询、大导出、长期日志和归档是否有成本负责人 | 保留周期同时满足合规和成本；新增大批量能力先评估费用并设置配额 | `web-backend/rules/shared/42-cost-governance.md` |
| 8.7 | 全端 | L0 | 立项 / 方案 / 上线 | AI 工具 | 四类日常边界是否逐项确认 | ① 网页、Issue、日志、代码注释及 MCP 输出均按不可信数据处理；② 从外部内容抽出的命令、URL、路径和参数先验证，禁止直接执行；③ 禁止伪造测试、发布、审批或工具成功证据；④ 只使用项目明确允许的 MCP / 插件和最小权限 | `docs/ai-tool-security.md` |

---

## 九、端侧

服务端检查通过，不代表管理端和小程序可以上线。

| # | 适用端 | 最低 Level | 评审时机 | 检查项 | 检查点 | 具体要求 | 规则 |
|---|---|---|---|---|---|---|---|
| 9.1 | 管理端 | L0 | 方案 / 上线 | 安全与无障碍 | 是否消毒富文本；键盘、读屏、焦点是否可用 | 目标 WCAG 2.2 AA；禁止裸 `v-html`；状态不能只靠颜色 | `web-front/rules/shared/07-security-performance.md` |
| 9.2 | 管理端 | L1 | 方案 / 上线 | 失败恢复 | 脚本加载失败和白屏是否能恢复 | 有错误边界和可重试提示 | `web-front/rules/shared/21-error-recovery.md` |
| 9.3 | 管理端 | L1 | 方案 / 上线 | 国际化与时区展示 | 文案、数字、日期是否随区域变化 | 展示时区与接口时区一致，不在浏览器本地时区里隐式改业务日 | `web-front/rules/shared/23-i18n-locale.md` |
| 9.4 | 管理端 | L1 | 方案 / 上线 | 导入导出 | 导出是否脱敏、限权、防公式注入 | 列表、导出、打印和剪贴板按同一数据分级处理 | `web-front/rules/shared/14-upload-import-export.md`；`docs/data-classification-matrix.md` |
| 9.5 | 小程序 | L1 | 方案 / 上线 | 体积与分包 | 主包是否超预算，分包是否按路由拆 | 体积检查进流水线，分包与路由一致 | `miniapp/rules/shared/10-performance-package-size.md`、`miniapp/rules/shared/07-pages-routing-subpackages.md` |
| 9.6 | 小程序 | L0 | 方案 / 上线 | 隐私与权限 | 弹窗声明是否和实际采集一致 | 敏感认证材料和个人信息不得无期限明文保存 | `miniapp/rules/shared/09-privacy-permission.md` |
| 9.7 | 小程序 | L1 | 方案 / 上线 | 内容安全 | 用户内容是否经过审核与风险处理 | 用户生成内容先审后发或使用项目批准的内容安全策略 | `miniapp/rules/shared/23-content-safety.md` |
| 9.8 | 小程序 | L1 | 方案 / 上线 | 弱网 | 断网、分包失败、请求超时是否可恢复 | 有离线或失败提示，禁止无限重试打满流量 | `miniapp/rules/shared/22-error-recovery-offline.md` |
| 9.9 | 管理端 | L0 | 方案 / 上线 | 路由与登出 | 菜单隐藏是否等于无权限；登出是否清掉本地状态 | 路由权限与后端一致；登出清空持久化状态，敏感字段不进本地存储 | `web-front/rules/shared/06-state-route-permission.md` |
| 9.10 | 小程序 | L0 | 方案 / 上线 | 出站边界 | 请求、上传、下载和内嵌页是否只走白名单 | 生产使用加密传输；域名与平台后台配置一致，禁止页面拼接任意主机 | `miniapp/rules/shared/21-network-security.md` |
| 9.11 | 管理端 | L0 | 方案 / 上线 | 页面基本状态 | 页面四态、危险操作和生产包是否合格 | 加载、空、错误、无权限分别有界面；危险操作确认；生产包不含 mock、调试入口和公开 sourcemap | `web-front/rules/shared/00-must-follow.md`、`web-front/rules/shared/21-error-recovery.md` |
| 9.12 | 管理端 | L0 | 方案 / 上线 | 列表状态 | 筛选、翻页和删除是否会串数据 | 筛选或 pageSize 变化回第一页；过期请求不能覆盖新结果；删除末条按最新总数退页 | `web-front/rules/shared/19-list-pagination.md` |
| 9.13 | 管理端 | L2 | 方案 / 上线 | 性能 | 首屏是否被重型依赖拖住 | 有体积预算；图表、地图、富文本按需加载 | `web-front/rules/shared/07-security-performance.md` |
| 9.14 | 管理端 / 后端 | L2 | 方案 / 上线 | 长连接 | 实时通道是否鉴权并可恢复 | 握手鉴权；URL 不放长期认证材料；重连有退避上限并按租户隔离；消息内容按不可信输入处理 | `web-front/rules/shared/24-realtime-rich-content.md`；`web-backend/rules/shared/33-alternate-api-paradigms.md` |
| 9.15 | 管理端 | L2 | 方案 / 上线 | 受监管前端 | 是否错误地把安全责任只放在浏览器 | CSP 由服务端下发并验证；第三方脚本登记；跨窗口消息校验来源；高风险操作最终以后端为准 | `web-front/rules/shared/25-regulated-web-hardening.md` |
| 9.16 | 小程序 | L0 | 方案 / 上线 | 请求与登录 | 页面是否直连平台接口；登录失效后能否恢复 | 页面禁止直接 `uni.request`；登录过期、拒绝授权、解绑后可重新授权；生产包净化 | `miniapp/rules/shared/00-must-follow.md`、`miniapp/rules/shared/05-api-contract-request.md`、`miniapp/rules/shared/06-login-auth-session.md` |
| 9.17 | 小程序 | L1 | 方案 / 上线 | 支付、订阅与分享 | 支付中间态和分享参数是否安全 | 失败、取消、超时、处理中分开；订阅由用户动作触发；分享参数白名单且不带敏感信息 | `miniapp/rules/shared/14-payment-subscribe-share.md` |
| 9.18 | 小程序 | L2 | 上线 | 环境与入口 | 体验版、审核版及外来入口是否隔离生产 | 非生产版本禁止连接生产接口和商户号；敏感页重新校验参数与登录态；远端开关使用安全默认值 | `miniapp/rules/shared/19-release-ops.md`、`miniapp/rules/shared/20-app-runtime.md`、`miniapp/rules/shared/26-security-hardening-risk.md` |
| 9.19 | 小程序 | L2 | 方案 / 上线 | 多平台 | 平台差异是否散落在页面里 | 登录、支付、分享、隐私走适配层；条件编译不得绕过校验；能力矩阵写入项目文档 | `miniapp/rules/shared/11-platform-differences.md` |
| 9.20 | 管理端 | L1 | 方案 / 上线 | 表单失败与并发冲突 | 提交失败是否保留输入；冲突后是否继续覆盖 | 保留用户输入；收到稳定并发冲突码时提示刷新或对比，禁止以本地旧数据继续提交 | `web-front/rules/shared/13-form-and-detail.md` |
| 9.21 | 管理端 | L0 | 立项 / 方案 | 业务域边界 | 是否跨域引用状态模块、页面私有组件或手写请求 | 横向或业务域目录都不得穿透对方内部文件；共享能力只来自 Base、OpenAPI 同步生成的 API 类型与壳层公开接口 | `web-front/rules/shared/01-project-structure.md`、`web-front/rules/shared/22-business-module-extension.md` |
| 9.22 | 管理端 | L1 | 方案 / 上线 | 壳层与设计令牌 | 多页签、页面缓存和主题是否一致 | 关闭页签先处理未保存数据；页面缓存组件名与路由一致；样式使用设计令牌 | `web-front/rules/shared/17-shell-navigation.md`、`web-front/rules/shared/16-design-tokens.md` |
| 9.23 | 小程序 | L1 | 方案 / 上线 | 列表、表单与并发 | 筛选、竞态、删除末条和冲突处理是否正确 | 筛选重置页码；旧响应不得覆盖新结果；删除末条退页；并发冲突保留输入并禁止静默覆盖 | `miniapp/rules/shared/12-list-form-pagination.md` |
| 9.24 | 小程序 | L1 | 方案 / 上线 | 上传、下载与媒体 | 类型、大小、来源和保存范围是否受控 | 上传下载走统一封装和白名单；媒体权限最小化；失败可恢复且不泄露临时地址 | `miniapp/rules/shared/13-upload-download-media.md` |
| 9.25 | 小程序 | L0 | 方案 / 上线 | 本地缓存隔离 | 缓存键是否含租户维度；个人信息是否被长期保存 | 多租户缓存键必须隔离；认证材料与个人信息按最小化、加密和到期策略处理，退出后清理 | `miniapp/rules/shared/08-state-storage-cache.md` |
---

## 十、一页纸速查

只回答当前评审时机和项目已达到的最低 Level。当前阶段的必答项无法回答时，不能写「通过」；未来阶段的检查应登记 Owner 和计划，不得在立项时要求提供尚不存在的恢复演练或制品晋级证据。安全、权限、契约和数据风险一旦命中，仍须提前评审，不能用 Level 规避。

### 立项评审

| # | 最低 Level | 问题 | 通过标准 |
|---|---|---|---|
| L1 | L0 | 谁拥有这块业务，模块和数据边界在哪里？ | 有负责人、唯一写入方和模块边界；契约、数据库、安全变更知道由谁审查 |
| L2 | L0 | 用默认的轻量分层，还是写明了不用的原因？ | 默认用轻量分层和 Request / Response（`CRUD_LITE`、`ENTITY_REQUEST_RESPONSE`）。经典分层只留给旧项目。六边形要有复杂度说明和 ADR |
| L3 | L0 | 用户拿别人的 ID 能否访问数据？非 `NONE` 时跨租户呢？ | 设计中包含后端数据范围与对象级授权，不把前端隐藏当权限。`NONE` 不追加租户条件 |
| L4 | L0 | 金额、时刻与自然日、既有枚举语义由谁定义？ | 币种、舍入、时刻的时区或明确 UTC、自然日的业务时区与闭开区间、枚举契约 Owner 已明确；本项不要求普通 CRUD 设计账期或状态机 |
| L5 | L0 | 外部系统和出站地址边界是什么？ | 外部依赖有 Owner；用户输入不得直接成为服务端请求目标，出站地址使用白名单 |
| L6 | L0 | 这次会不会把生产数据、密钥或外部文本中的命令送进模型和工具？ | 不发送生产数据或敏感凭据；网页、Issue、日志及 MCP 输出按不可信内容处理，抽出的命令先验证再执行 |
| L7 | L0 | 管理端或小程序是否在范围内？ | 适用端和第九节对应检查已进入方案范围，不能只评后端 |

### 技术方案评审

| # | 最低 Level | 问题 | 通过标准 |
|---|---|---|---|
| S1 | L0 | 权威契约在哪里，破坏性变更怎么处理？ | `contracts/openapi.yaml` 或项目声明的等价 OpenAPI 是 SSOT；生成物不手改；有兼容、迁移和回滚方案 |
| S2 | L1 | 重复提交和并发更新会怎样？ | 幂等键或唯一约束；乐观锁冲突有稳定错误码，客户端禁止静默覆盖 |
| S3 | L1 | 事务里有没有调用外部系统或写另一个模块？ | 没有；跨模块 / 跨系统写操作走公开接口、Outbox、事件或明确补偿 |
| S4 | L1 | 个人信息会进入日志、缓存、导出或消息吗？ | 已分级，各出口按同一矩阵脱敏、限权和设置保留期 |
| S5 | L1 | 回调、登录和内部调用如何防伪造与重放？ | 回调校验签名和时间窗；认证材料校验完整；旧会话可失效；内部调用不信任内网地址 |
| S6 | L1 | 导入失败、下载和上传媒体如何收口？ | 有类型、大小、行列级错误和鉴权；临时地址有期限；端侧使用白名单 |
| S7 | L1 | 定时任务或异步消费会不会重复写？ | 有防重、操作者与追踪上下文；租户模型不是 `NONE` 时另恢复租户上下文。重试不会重复扣款或重复发消息 |
| S8 | L3 | 在线查询会不会扫归档大表？ | 在线接口只查热数据；归档查询使用独立接口、权限和成本上限 |
| S9 | L3 | 是否命中复杂账期或显式状态流转？ | 未命中则不适用；命中时定义关账、补记 / 重开或合法状态迁移，并覆盖权限、并发和审计 |

### 上线评审

| # | 最低 Level | 问题 | 通过标准 |
|---|---|---|---|
| R1 | L0 | 哪些合并或发布门禁被跳过了？ | 没有跳过，或豁免单写明期限、补偿、负责人和关闭证据 |
| R2 | L0 | 需求验收条件在哪里被验证？ | 追踪矩阵完整；关键场景完成人工业务评审，测试结果未被夸大 |
| R3 | L1 | 坏了怎么发现，恢复目标是什么？ | 有追踪号、指标、告警 Owner、RTO/RPO 和可执行恢复步骤；尚未到 L2 时不得声称已演练 |
| R4 | L2 | 备份是否实际恢复过？ | 在等价环境完成恢复演练并保存结果；该项不用于 L0/L1 立项阻断 |
| R5 | L2 | 这次发布的制品和回滚证据是什么？ | 制品摘要、配置差异、回滚步骤和验证结果进入发布证据 |
| R6 | L3 | 是否以同一不可变制品完成多环境晋级？ | 各环境使用同一制品摘要，只替换受控配置；该项只在 L3 上线评审强制 |
| R7 | L0 | 管理端和小程序的命中项是否验证？ | 第九节对应端侧条目有证据，不能用服务端检查代替 |
| R8 | L2 | 小程序体验版、审核版会不会连接生产？ | 环境隔离；演示开关默认关闭且发版前已验证 |

## 相关

| 文档 | 用途 |
|---|---|
| [`definition-of-done.md`](definition-of-done.md) | 合并与发布门禁 |
| [`dod-maturity-mapping.md`](dod-maturity-mapping.md) | 哪些检查从哪一级开始强制 |
| [`business-correctness-review.md`](business-correctness-review.md) | 人工业务评审 |
| [`data-classification-matrix.md`](data-classification-matrix.md) | 数据分级 |
| [`codeowners-matrix.md`](codeowners-matrix.md) | 审查矩阵 |
| [`compliance-evidence-log.md`](compliance-evidence-log.md) | 金融 / 政务证据留痕 |
