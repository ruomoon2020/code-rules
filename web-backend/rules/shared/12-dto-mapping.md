# DTO 映射规则

API 层仅暴露 DTO；持久化层使用 Entity（或 DO）。转换逻辑集中，禁止散落在 Controller。

## 类型划分

| 类型 | 用途 | 命名 |
|---|---|---|
| Request | 创建/更新/查询入参 | `UserCreateRequest`、`UserUpdateRequest`、`UserPageQuery` |
| Response | 单条/列表项出参 | `UserDetailResponse`、`UserSummaryResponse` |
| PageResponse | 分页包装 | `PageResponse<UserSummaryResponse>` 或 OpenAPI 生成类型 |

存量项目已采用经典分层命名时，可继续映射为：持久化对象 `*DO`、跨层/跨模块传输 `*DTO`、业务内部 `*BO`、展示输出 `*VO`、查询条件 `*Query`。这不是新项目默认，也不得把 DTO 当成所有接口、所有方向通用的数据袋。

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
- 把数据库主键和逻辑删除字段暴露到 Response。

## 与 OpenAPI

1. DTO 字段名、类型、必填与 `contracts/openapi.yaml` 一致。
2. 若使用 OpenAPI Generator 生成 DTO，业务定制通过继承或组合，不直接改 generated 目录。
3. 枚举：OpenAPI `enum` ↔ Java `enum` ↔ 库表约束三者一致。
4. 会被并发修改的资源，详情响应、更新请求和删除请求必须包含 `version`。创建响应返回初始 `version`；更新成功后，响应返回递增后的 `version`，供客户端下次提交使用。列表响应无需重复返回该字段。逻辑删除字段不得进入 Response。

## 脱敏

手机号、邮箱、证件号在 **Response 转换时** 脱敏；Entity 仍存完整值（按合规要求）。

## 查询对象

列表筛选参数：

- 简单场景：`UserPageQuery`（page、pageSize、status、keyword）。
- 复杂场景：独立 `UserQuery` + Service 内转 `Wrapper` 条件。

查询参数超过 2 个时必须封装为 `*Query`（或项目统一的 `*Param`），禁止使用 `Map<String, Object>`、`JSONObject` 作为跨层参数袋。即使只有 1–2 个参数，若存在分页、排序、权限范围或后续扩展预期，也应优先使用查询对象。

查询 DTO 不得包含 `orderBy` 原始字符串；使用 `sortField` + 白名单映射（见 `19-pagination-query.md`）。
