package com.company.product.modules.system.application;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.company.product.common.exception.BusinessException;
import com.company.product.common.exception.ErrorCodes;
import com.company.product.common.web.PageResponse;
import com.company.product.modules.system.api.dto.AuditLogPageQuery;
import com.company.product.modules.system.api.dto.AuditLogResponse;
import com.company.product.modules.system.api.dto.AuditLogSummaryResponse;
import com.company.product.modules.system.domain.AuditLog;
import com.company.product.modules.system.infrastructure.mapper.AuditLogMapper;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

/**
 * 审计日志查询（样板）。写入见 {@link com.company.product.modules.system.application.audit.AuditRecorder}。
 */
@Service
public class AuditLogService {

    private final AuditLogMapper auditLogMapper;

    public AuditLogService(AuditLogMapper auditLogMapper) {
        this.auditLogMapper = auditLogMapper;
    }

    @Transactional(readOnly = true)
    public PageResponse<AuditLogSummaryResponse> page(AuditLogPageQuery query) {
        Page<AuditLog> page = new Page<>(query.page(), query.pageSize());
        LambdaQueryWrapper<AuditLog> wrapper = new LambdaQueryWrapper<>();
        if (StringUtils.hasText(query.action())) {
            wrapper.eq(AuditLog::getAction, query.action());
        }
        if (StringUtils.hasText(query.resourceType())) {
            wrapper.eq(AuditLog::getResourceType, query.resourceType());
        }
        if (StringUtils.hasText(query.operatorId())) {
            wrapper.eq(AuditLog::getOperatorId, query.operatorId());
        }
        if (StringUtils.hasText(query.resourceId())) {
            wrapper.eq(AuditLog::getResourceId, query.resourceId());
        }
        if (StringUtils.hasText(query.result())) {
            wrapper.eq(AuditLog::getResult, query.result());
        }
        if (query.occurredAtFrom() != null) {
            wrapper.ge(AuditLog::getOccurredAt, query.occurredAtFrom());
        }
        if (query.occurredAtTo() != null) {
            wrapper.le(AuditLog::getOccurredAt, query.occurredAtTo());
        }
        wrapper.orderByDesc(AuditLog::getOccurredAt);
        auditLogMapper.selectPage(page, wrapper);
        List<AuditLogSummaryResponse> records = page.getRecords().stream()
                .map(this::toSummary)
                .toList();
        return new PageResponse<>(query.page(), query.pageSize(), page.getTotal(), records);
    }

    @Transactional(readOnly = true)
    public AuditLogResponse detail(String id) {
        AuditLog row = auditLogMapper.selectById(Long.parseLong(id));
        if (row == null) {
            throw new BusinessException(ErrorCodes.AUDIT_LOG_NOT_FOUND, "audit log not found: " + id, HttpStatus.NOT_FOUND);
        }
        return toDetail(row);
    }

    private AuditLogSummaryResponse toSummary(AuditLog row) {
        return new AuditLogSummaryResponse(
                String.valueOf(row.getId()),
                row.getOperatorId(),
                null,
                row.getTenantId(),
                row.getAction(),
                row.getResourceType(),
                row.getResourceId(),
                row.getRequestSummary(),
                row.getFileName(),
                row.getResult(),
                row.getErrorCode(),
                row.getTraceId(),
                row.getOccurredAt()
        );
    }

    private AuditLogResponse toDetail(AuditLog row) {
        return new AuditLogResponse(
                String.valueOf(row.getId()),
                row.getOperatorId(),
                null,
                row.getTenantId(),
                row.getAction(),
                row.getResourceType(),
                row.getResourceId(),
                row.getRequestSummary(),
                row.getFileName(),
                row.getResult(),
                row.getErrorCode(),
                row.getTraceId(),
                row.getOccurredAt(),
                row.getBeforeSummary(),
                row.getAfterSummary(),
                row.getIp(),
                row.getUserAgent()
        );
    }
}
