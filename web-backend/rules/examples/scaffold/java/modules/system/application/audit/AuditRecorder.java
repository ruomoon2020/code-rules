package com.company.product.modules.system.application.audit;

/**
 * 审计写入端口。业务 Service 在敏感操作后调用，禁止仅在 Controller 打 log。
 */
public interface AuditRecorder {

    void record(AuditRecordCommand command);
}
