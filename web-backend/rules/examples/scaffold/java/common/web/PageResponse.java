package com.company.product.common.web;

import java.util.List;

/**
 * 分页响应，与 OpenAPI UserPageData、前端 useTable 对齐。
 */
public record PageResponse<T>(
        int page,
        int pageSize,
        long total,
        List<T> records
) {
}
