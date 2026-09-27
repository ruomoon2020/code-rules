# Code Style Rules（Java）

适用于 Spring Boot 3.x + Java 17+；Spring Boot 4.x 项目须先按依赖治理规则完成迁移评估。

## Java

1. 使用 `record` 或不可变 DTO 承载只读数据（按项目约定）。
2. 空值：对外 API 明确可选字段；内部优先 `Optional` 或显式判空，禁止随意 `@SuppressWarnings`。
3. 公共方法声明参数与返回类型；复杂逻辑拆私有方法。
4. 禁止捕获 `Exception` 后吞掉；须记录日志或转换为业务异常。
5. 命名细则以 **`02-naming.md`** 为准。

## Lombok

1. Entity 可用 `@Getter` `@Setter` 或 `@Data`（团队择一）；DTO 优先 `@Value` / record。
2. 禁止在 Entity 上使用 `@Builder` 导致 JPA/MyBatis 语义混乱（除非团队统一）。
3. `@Slf4j` 用于日志，禁止 `System.out`。

## Spring

1. 构造器注入优先，避免字段 `@Autowired`。
2. `@Transactional` 仅放在 application/service 层 public 方法。
3. Controller 使用 `@Valid` + `@RequestBody` / `@ParameterObject`。
4. HTTP API 类显式使用 `@RestController`、`@GetMapping` / `@PostMapping` 等组合注解；复杂内容协商须声明 `produces` / `consumes` 并在 OpenAPI 中同步。

## 注释

1. 注释解释**为什么**，不复述代码。
2. 复杂 SQL、权限、兼容多库逻辑必须注释。
3. `TODO` 须含负责人或任务 ID。
4. 公共 Service、Mapper 接口说明边界与事务要求。

## Import

1. 禁止 `*` 静态导入泛滥；Checkstyle 按项目配置。
2. 禁止未使用 import 提交。
