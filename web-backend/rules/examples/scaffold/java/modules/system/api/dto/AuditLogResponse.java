package com.company.product.modules.system.api.dto;

import java.time.Instant;

/**
 * 审计日志详情，与 OpenAPI AuditLogResponse 对齐。
 */
public record AuditLogResponse(
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
        Instant occurredAt,
        String beforeSummary,
        String afterSummary,
        String ip,
        String userAgent
) {
}
