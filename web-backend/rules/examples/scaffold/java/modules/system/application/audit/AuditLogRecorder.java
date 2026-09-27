package com.company.product.modules.system.application.audit;

import com.company.product.common.audit.AuditContext;
import com.company.product.modules.system.domain.AuditLog;
import com.company.product.modules.system.infrastructure.mapper.AuditLogMapper;
import org.springframework.stereotype.Component;

import java.time.Instant;

/**
 * 审计写入实现（样板）：落库 {@code sys_audit_log}。
 */
@Component
public class AuditLogRecorder implements AuditRecorder {

    private final AuditLogMapper auditLogMapper;

    public AuditLogRecorder(AuditLogMapper auditLogMapper) {
        this.auditLogMapper = auditLogMapper;
    }

    @Override
    public void record(AuditRecordCommand command) {
        AuditLog row = new AuditLog();
        row.setTenantId(AuditContext.currentTenantId());
        row.setOperatorId(AuditContext.currentOperatorId());
        row.setAction(command.action());
        row.setResourceType(command.resourceType());
        row.setResourceId(command.resourceId());
        row.setBeforeSummary(command.beforeSummary());
        row.setAfterSummary(command.afterSummary());
        row.setRequestSummary(command.requestSummary());
        row.setResult(command.result());
        row.setErrorCode(command.errorCode());
        row.setTraceId(AuditContext.currentTraceId());
        row.setOccurredAt(Instant.now());
        auditLogMapper.insert(row);
    }
}
