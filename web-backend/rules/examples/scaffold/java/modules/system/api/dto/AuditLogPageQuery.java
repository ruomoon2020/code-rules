package com.company.product.modules.system.api.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import java.time.Instant;

/**
 * 审计日志分页查询，与 OpenAPI systemAuditLogPage 参数对齐。
 */
public record AuditLogPageQuery(
        @Min(1) Integer page,
        @Min(1) @Max(100) Integer pageSize,
        String action,
        String resourceType,
        String operatorId,
        String resourceId,
        String result,
        Instant occurredAtFrom,
        Instant occurredAtTo
) {
    public AuditLogPageQuery {
        page = page == null ? 1 : page;
        pageSize = pageSize == null ? 20 : pageSize;
    }
}
