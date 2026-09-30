package com.company.product.common.audit;

import com.company.product.common.observability.TraceIdFilter;
import org.slf4j.MDC;

/**
 * 审计上下文（单租户样板）。接入 Spring Security 后从 Authentication 解析 operatorId / ip。
 * 项目已有租户机制时，在项目适配层增加可信 tenantId，并在所有数据入口统一恢复租户上下文。
 */
public final class AuditContext {

    private AuditContext() {}

    public static String currentOperatorId() {
        return "0";
    }

    public static String currentTraceId() {
        return MDC.get(TraceIdFilter.MDC_KEY);
    }
}
