# 分页与查询规则

与前端 `19-list-pagination.md` 语义对齐。

## 入参

- `page`：从 1 开始。字段名固定为 `page`，禁止 `pageNo`、`pageNum`，禁止把第一页写成 0。
- `pageSize`：上限由配置限制（如 max 100）。
- 筛选字段与 OpenAPI query 参数一致。

## 出参

- `records`、`total`、`page`、`pageSize`（或 `data` 包装内同等字段）。

## MyBatis-Plus

```java
int page = query.page();
Page<User> mpPage = new Page<>(page, query.pageSize());
mapper.selectPage(mpPage, wrapper);
```

禁止各接口手写 `LIMIT offset, size` 三套。

## 排序白名单

1. 请求字段为 `sortField`、`sortOrder`。`sortOrder` 只允许 `asc`、`desc`。组件事件里的 `ascending` / `descending` 由前端在发请求前映射，后端不接受。
2. 使用方法引用或 Wrapper 列表达式建立排序白名单，例如 `Map<String, SFunction<User, ?>>`；未命中白名单，或 `sortOrder` 不是 `asc` / `desc`，返回明确错误码，禁止当成默认降序。
3. 排序调用 Wrapper 的 `orderBy` / `orderByAsc` / `orderByDesc`。禁止 `order by ${sortField}`，也不要把白名单列名再拼成 `last("ORDER BY ...")`。
4. 未传排序时，默认排序在 Service 或 XML 写死。

## 筛选

1. 动态条件用 `LambdaQueryWrapper` 或 XML `<if>` + `#{}`。
2. 模糊查询注意索引；禁止 leading `%` 滥用（性能见 `16-performance.md`）。

## 全文检索（命中场景时）

1. 引入搜索引擎或全文索引前必须定义可检索字段白名单、数据权限过滤、查询深度、结果窗口和单请求成本上限。租户模型不是 `NONE` 时同时过滤租户；`NONE` 不追加租户条件。
2. 禁止允许客户端透传任意 DSL、索引名、排序脚本或无界聚合；复杂查询必须由服务端受控模板生成。
3. 搜索结果必须服从与数据库详情接口相同的对象级权限；索引延迟、删除传播和回源校验策略必须写清。
4. 新增搜索基础设施同时触发 `20-dependency-governance.md`、`42-cost-governance.md` 和架构 / 运维评审，不因本文件存在而默认允许引入。
