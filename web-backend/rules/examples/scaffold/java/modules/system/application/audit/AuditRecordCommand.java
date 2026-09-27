package com.company.product.modules.system.application.audit;

/**
 * 审计写入命令，字段与 {@code sys_audit_log} / OpenAPI {@code AuditLogResponse} 对齐。
 */
public record AuditRecordCommand(
        String action,
        String resourceType,
        String resourceId,
        String beforeSummary,
        String afterSummary,
        String requestSummary,
        String result,
        String errorCode
) {
    public static AuditRecordCommand success(
            String action,
            String resourceType,
            String resourceId,
            String beforeSummary
    ) {
        return new AuditRecordCommand(
                action,
                resourceType,
                resourceId,
                beforeSummary,
                null,
                null,
                "SUCCESS",
                null
        );
    }
}
