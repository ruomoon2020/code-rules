package com.company.product.modules.system.api.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;

/**
 * 分页查询；sortField 在 Service 内白名单映射，禁止直接进 SQL ${}。
 */
public record UserPageQuery(
        @Min(1) Integer page,
        @Min(1) @Max(100) Integer pageSize,
        String status,
        String keyword,
        String sortField,
        String sortOrder
) {
    public UserPageQuery {
        page = page == null ? 1 : page;
        pageSize = pageSize == null ? 20 : pageSize;
    }
}
