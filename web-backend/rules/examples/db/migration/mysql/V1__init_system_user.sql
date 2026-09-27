-- Flyway MySQL 样板。时间存 UTC。排序规则全库统一为 utf8mb4_unicode_ci。
-- 身份若在外部认证系统，不要在本表加密码列，改为外部主体标识。
CREATE TABLE IF NOT EXISTS sys_user (
    id              BIGINT       NOT NULL PRIMARY KEY COMMENT '雪花 ID，由应用分配',
    tenant_id       VARCHAR(64)  NOT NULL COMMENT '租户 ID',
    username        VARCHAR(32)  NOT NULL COMMENT '登录用户名',
    email           VARCHAR(128) NULL COMMENT '邮箱；敏感个人信息，展示和日志须脱敏',
    phone           VARCHAR(32)  NULL COMMENT '手机号；敏感个人信息，禁止明文进日志和缓存',
    status          VARCHAR(16)  NOT NULL DEFAULT 'ENABLED' COMMENT '状态：ENABLED/DISABLED',
    deleted_at      DATETIME(3)  NOT NULL DEFAULT '1970-01-01 00:00:00.000' COMMENT '删除时间（UTC）。未删除为 1970-01-01，删除时写成实际时间。不用 NULL：MySQL 唯一索引允许多个 NULL，无法保证未删除用户名唯一',
    version         INT          NOT NULL DEFAULT 0 COMMENT '乐观锁版本号',
    created_by      VARCHAR(64)  NULL COMMENT '创建人用户 ID；系统初始化可为空',
    updated_by      VARCHAR(64)  NULL COMMENT '最后修改人用户 ID',
    created_at      DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间（UTC）',
    updated_at      DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间（UTC）',
    UNIQUE KEY uk_sys_user_tenant_username (tenant_id, username, deleted_at),
    KEY idx_sys_user_tenant_status (tenant_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统用户表';
