# DTO Mapping

API 层仅暴露 DTO；持久化层使用 Entity（或 DO）。转换逻辑集中，禁止散落在 Controller。

## 类型划分

| 类型 | 用途 | 命名 |
|---|---|---|
| Request | 创建/更新/查询入参 | `UserCreateRequest`、`UserUpdateRequest`、`UserPageQuery` |
| Response | 单条/列表项出参 | `UserDetailResponse`、`UserSummaryResponse` |
| PageResponse | 分页包装 | `PageResponse<UserSummaryResponse>` 或 OpenAPI 生成类型 |

禁止对外使用 `User` Entity、`UserDO`、MyBatis `Map` 作为 REST body。

## MapStruct（推荐）

1. 接口 `UserConverter` / `UserMapper`（MapStruct 命名勿与 MyBatis Mapper 混淆，团队可统一 `UserConverter`）。
2. 声明 `UserCreateRequest → User`、`User → UserDetailResponse` 等。
3. 分页转换抽取公共方法：

```java
// 形态参考；以项目 generated/Converter 为准
PageResponse<UserSummaryResponse> toPageResponse(IPage<User> page);
```

4. 生成代码在 `target/generated-sources`；**禁止手改**生成实现类。
5. 字段不一致处用 `@Mapping` 显式声明；禁止静默忽略敏感字段。

## 禁止

- `BeanUtils.copyProperties` 盲目复制（易漏字段、性能差）。
- Controller 内超过 10 行手写映射（应下沉 Converter）。
- 把数据库主键、逻辑删除、乐观锁版本号暴露到 Response（除非 OpenAPI 明确要求）。

## 与 OpenAPI

1. DTO 字段名、类型、必填与 `contracts/openapi.yaml` 一致。
2. 若使用 OpenAPI Generator 生成 DTO，业务定制通过继承或组合，不直接改 generated 目录。
3. 枚举：OpenAPI `enum` ↔ Java `enum` ↔ 库表约束三者一致。

## 脱敏

手机号、邮箱、证件号在 **Response 转换时** 脱敏；Entity 仍存完整值（按合规要求）。

## 查询对象

列表筛选参数：

- 简单场景：`UserPageQuery`（page、pageSize、status、keyword）。
- 复杂场景：独立 `UserQuery` + Service 内转 `Wrapper` 条件。

查询 DTO 不得包含 `orderBy` 原始字符串；使用 `sortField` + 白名单映射（见 `19-pagination-query.md`）。
