package com.company.product.modules.system.api.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import java.time.Instant;

/**
 * 审计日志分页查询，与 OpenAPI systemAuditLogPage 参数对齐。
 */
public record AuditLogPageQuery(
        @Min(1) int page,
        @Min(1) @Max(100) int pageSize,
        String action,
        String resourceType,
        String operatorId,
        String resourceId,
        String result,
        Instant occurredAtFrom,
        Instant occurredAtTo
) {
}
