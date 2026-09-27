# Pagination & Query

与前端 `19-list-pagination.md` 语义对齐。

## 入参

- `page`：从 1 开始（或 OpenAPI 约定，全项目统一）。
- `pageSize`：上限由配置限制（如 max 100）。
- 筛选字段与 OpenAPI query 参数一致。

## 出参

- `records`、`total`、`page`、`pageSize`（或 `data` 包装内同等字段）。

## MyBatis-Plus

```java
Page<User> page = new Page<>(pageNo, pageSize);
mapper.selectPage(page, wrapper);
```

禁止各接口手写 `LIMIT offset, size` 三套。

## 排序白名单

1. 前端传 `sortField`、`sortOrder` 时，后端 **Map 白名单** 到列名。
2. 禁止 `order by ${sortField}` 直接拼接用户输入。
3. 默认排序在 Service 或 XML 写死。

## 筛选

1. 动态条件用 `LambdaQueryWrapper` 或 XML `<if>` + `#{}`。
2. 模糊查询注意索引；禁止 leading `%` 滥用（性能见 `16`）。
