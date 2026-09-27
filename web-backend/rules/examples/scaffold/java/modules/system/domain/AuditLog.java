package com.company.product.modules.system.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import java.time.Instant;

/**
 * 审计日志实体（样板），对应 {@code sys_audit_log}。
 */
@TableName("sys_audit_log")
public class AuditLog {

    @TableId(type = IdType.ASSIGN_ID)
    private Long id;
    private String tenantId;
    private String operatorId;
    private String action;
    private String resourceType;
    private String resourceId;
    private String requestSummary;
    private String fileName;
    private String beforeSummary;
    private String afterSummary;
    private String result;
    private String errorCode;
    private String traceId;
    private String ip;
    private String userAgent;
    private Instant occurredAt;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getTenantId() { return tenantId; }
    public void setTenantId(String tenantId) { this.tenantId = tenantId; }
    public String getOperatorId() { return operatorId; }
    public void setOperatorId(String operatorId) { this.operatorId = operatorId; }
    public String getAction() { return action; }
    public void setAction(String action) { this.action = action; }
    public String getResourceType() { return resourceType; }
    public void setResourceType(String resourceType) { this.resourceType = resourceType; }
    public String getResourceId() { return resourceId; }
    public void setResourceId(String resourceId) { this.resourceId = resourceId; }
    public String getRequestSummary() { return requestSummary; }
    public void setRequestSummary(String requestSummary) { this.requestSummary = requestSummary; }
    public String getFileName() { return fileName; }
    public void setFileName(String fileName) { this.fileName = fileName; }
    public String getBeforeSummary() { return beforeSummary; }
    public void setBeforeSummary(String beforeSummary) { this.beforeSummary = beforeSummary; }
    public String getAfterSummary() { return afterSummary; }
    public void setAfterSummary(String afterSummary) { this.afterSummary = afterSummary; }
    public String getResult() { return result; }
    public void setResult(String result) { this.result = result; }
    public String getErrorCode() { return errorCode; }
    public void setErrorCode(String errorCode) { this.errorCode = errorCode; }
    public String getTraceId() { return traceId; }
    public void setTraceId(String traceId) { this.traceId = traceId; }
    public String getIp() { return ip; }
    public void setIp(String ip) { this.ip = ip; }
    public String getUserAgent() { return userAgent; }
    public void setUserAgent(String userAgent) { this.userAgent = userAgent; }
    public Instant getOccurredAt() { return occurredAt; }
    public void setOccurredAt(Instant occurredAt) { this.occurredAt = occurredAt; }
}
