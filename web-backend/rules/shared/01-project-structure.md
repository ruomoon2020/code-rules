# Project Structure Rules

## 推荐包结构（单模块）

```text
src/main/java/com/company/product/
├─ ProductApplication.java
├─ common/
│  ├─ exception/
│  ├─ web/              # GlobalExceptionHandler、统一响应
│  ├─ observability/    # TraceIdFilter、MDC
│  └─ util/
├─ config/              # Security、MyBatis、OpenAPI
└─ modules/
   └─ system/
      ├─ api/           # Controller、*Request、*Response
      ├─ application/   # *Service（@Transactional）
      ├─ domain/        # Entity、领域服务（可选）
      └─ infrastructure/
         └─ mapper/     # Mapper 接口

src/main/resources/
├─ application.yml
├─ mapper/
│  ├─ common/           # 可移植 SQL
│  └─ dialect/
│     ├─ mysql/
│     └─ postgresql/
└─ db/migration/        # Flyway
   ├─ mysql/            # 可选：按库分子目录
   └─ postgresql/
```

## 多模块（可选）

```text
product-api          # Controller + DTO（仅依赖 application 接口）
product-application  # Service、用例
product-domain       # Entity、仓储接口
product-infrastructure # Mapper、XML、外部适配
```

依赖：`api → application → domain`；`infrastructure` 实现 domain 接口并依赖 MyBatis。

## 依赖方向

允许：

```text
Controller -> ApplicationService -> Mapper
ApplicationService -> Domain Entity / Domain Service
Mapper XML -> 数据库
```

禁止：

```text
Controller -> Mapper
domain -> infrastructure 具体实现（应依赖接口）
common -> modules 业务包
```

## 放置规则

1. 一个业务域一个 `modules/{name}`，避免巨型 `service` 包。
2. Mapper 接口与 XML 同名：`UserMapper.java` ↔ `UserMapper.xml`。
3. 跨模块复用 DTO 放 `api` 或独立 `contract` 模块，禁止复制粘贴。
4. 命名与路径见 **`02-naming.md`**；持久化见 **`07-persistence-mybatis.md`**。
5. 首个业务域可复制 **`docs/scaffold-module-system.md`**。
