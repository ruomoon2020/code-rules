package com.company.product.modules.system.api.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;

/**
 * 分页查询；sortField 在 Service 内白名单映射，禁止直接进 SQL ${}。
 */
public record UserPageQuery(
        @Min(1) int page,
        @Min(1) @Max(100) int pageSize,
        String status,
        String keyword,
        String sortField,
        String sortOrder
) {
}
