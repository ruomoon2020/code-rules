# Configuration & Secrets

1. 配置分环境：`application-{profile}.yml`；敏感项来自环境变量/配置中心。
2. 禁止提交：`application-prod.yml` 中的密码、密钥、内网地址。
3. 数据源、Redis、OSS 等连接串外部化。
4. **Feature Flag**（与前端 `00` 一致）：
   - 须有 **owner**、**默认值**、**过期/清理日期**；
   - 命名统一前缀（如 `feature.xxx.enabled`），配置来源统一（配置中心或 `application.yml`，禁止散落硬编码）。
   - **禁止**灰度/实验开关长期存在；到期须删除代码分支与配置。
5. 多库：各 profile 指定 `spring.datasource.url` 与 Flyway locations。
6. 发布与回滚相关开关策略见 `22-operability.md`。

## Type-safe Configuration

1. 业务配置优先使用 `@ConfigurationProperties` 承载，按模块设置稳定 prefix；禁止在业务代码中散落 `@Value` 读取同一组配置。
2. 配置类优先不可变：Java `record` 或构造器绑定；复杂嵌套配置须显式建模。
3. 配置必须可校验：使用 `@Validated`、Bean Validation 约束、`@Valid` 级联嵌套对象；启动期失败优先于运行期空指针。
4. 时间、容量、限额等配置使用 `Duration`、`DataSize`、枚举或值对象表达，避免裸 `String` / `long` 魔法单位。
5. 主应用或配置类按项目需要启用 `@ConfigurationPropertiesScan`；配置 prefix、默认值与 OpenAPI / 运维文档保持一致。
