-- 审计日志只追加。保留周期和归档方式写入项目配置。
CREATE TABLE IF NOT EXISTS sys_audit_log (
    id              BIGINT        PRIMARY KEY,
    tenant_id       VARCHAR(64)   NOT NULL,
    operator_id     VARCHAR(64)   NOT NULL,
    action          VARCHAR(64)   NOT NULL,
    resource_type   VARCHAR(64)   NOT NULL,
    resource_id     VARCHAR(128),
    request_summary VARCHAR(512),
    file_name       VARCHAR(256),
    before_summary  VARCHAR(1024),
    after_summary   VARCHAR(1024),
    result          VARCHAR(16)   NOT NULL,
    error_code      VARCHAR(64),
    trace_id        VARCHAR(64),
    ip              VARCHAR(64),
    user_agent      VARCHAR(512),
    occurred_at     TIMESTAMPTZ   NOT NULL,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_sys_audit_log_result CHECK (result IN ('SUCCESS', 'FAIL'))
);

CREATE INDEX IF NOT EXISTS idx_sys_audit_log_tenant_occurred
    ON sys_audit_log (tenant_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_sys_audit_log_tenant_operator
    ON sys_audit_log (tenant_id, operator_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_sys_audit_log_tenant_action
    ON sys_audit_log (tenant_id, action, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_sys_audit_log_tenant_resource
    ON sys_audit_log (tenant_id, resource_type, resource_id);

COMMENT ON TABLE sys_audit_log IS '系统审计日志；只追加。保留周期见项目配置，到期归档';
COMMENT ON COLUMN sys_audit_log.id IS '雪花 ID，由应用分配';
COMMENT ON COLUMN sys_audit_log.tenant_id IS '租户 ID';
COMMENT ON COLUMN sys_audit_log.operator_id IS '操作者用户 ID 或系统主体 ID';
COMMENT ON COLUMN sys_audit_log.action IS '操作动作编码';
COMMENT ON COLUMN sys_audit_log.resource_type IS '资源类型编码';
COMMENT ON COLUMN sys_audit_log.resource_id IS '资源 ID';
COMMENT ON COLUMN sys_audit_log.request_summary IS '请求摘要；禁止记录敏感明文';
COMMENT ON COLUMN sys_audit_log.file_name IS '文件名；导入导出场景使用';
COMMENT ON COLUMN sys_audit_log.before_summary IS '变更前摘要；禁止记录敏感明文';
COMMENT ON COLUMN sys_audit_log.after_summary IS '变更后摘要；禁止记录敏感明文';
COMMENT ON COLUMN sys_audit_log.result IS '操作结果：SUCCESS/FAIL';
COMMENT ON COLUMN sys_audit_log.error_code IS '失败错误码';
COMMENT ON COLUMN sys_audit_log.trace_id IS '链路追踪 ID';
COMMENT ON COLUMN sys_audit_log.ip IS '客户端 IP，可含 IPv6';
COMMENT ON COLUMN sys_audit_log.user_agent IS '客户端 User-Agent';
COMMENT ON COLUMN sys_audit_log.occurred_at IS '业务发生时间（UTC）';
COMMENT ON COLUMN sys_audit_log.created_at IS '记录入库时间（UTC）';
