package com.company.product.modules.system.api;

import com.company.product.common.observability.TraceIdFilter;
import com.company.product.common.web.ApiResult;
import com.company.product.common.web.PageResponse;
import com.company.product.modules.system.api.dto.AuditLogPageQuery;
import com.company.product.modules.system.api.dto.AuditLogResponse;
import com.company.product.modules.system.api.dto.AuditLogSummaryResponse;
import com.company.product.modules.system.application.AuditLogService;
import jakarta.validation.Valid;
import org.slf4j.MDC;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 审计日志只读 API（样板）。与 contracts/openapi.yaml 对齐；禁止注入 Mapper。
 * 权限码 {@code system:audit-log:read} 与 OpenAPI {@code x-permission} 对齐。
 */
@RestController
@RequestMapping("/api/v1/system/audit-logs")
@PreAuthorize("hasAuthority('system:audit-log:read')")
public class AuditLogController {

    private final AuditLogService auditLogService;

    public AuditLogController(AuditLogService auditLogService) {
        this.auditLogService = auditLogService;
    }

    @GetMapping
    public ApiResult<PageResponse<AuditLogSummaryResponse>> page(@Valid AuditLogPageQuery query) {
        return ApiResult.ok(auditLogService.page(query), traceId());
    }

    @GetMapping("/{id}")
    public ApiResult<AuditLogResponse> detail(@PathVariable long id) {
        return ApiResult.ok(auditLogService.detail(id), traceId());
    }

    private static String traceId() {
        return MDC.get(TraceIdFilter.MDC_KEY);
    }
}
