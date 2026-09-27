package com.company.product.modules.system.api.dto;

import java.time.Instant;

/**
 * 审计日志列表项，与 OpenAPI AuditLogSummaryResponse 对齐。
 */
public record AuditLogSummaryResponse(
        String id,
        String operatorId,
        String operatorName,
        String tenantId,
        String action,
        String resourceType,
        String resourceId,
        String requestSummary,
        String fileName,
        String result,
        String errorCode,
        String traceId,
        Instant occurredAt
) {
}
