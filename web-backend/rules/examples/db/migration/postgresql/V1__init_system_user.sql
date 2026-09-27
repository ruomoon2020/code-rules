-- Flyway PostgreSQL 样板。时间存 UTC（timestamptz）。
CREATE TABLE IF NOT EXISTS sys_user (
    id           BIGINT       PRIMARY KEY,
    tenant_id    VARCHAR(64)  NOT NULL,
    username     VARCHAR(32)  NOT NULL,
    email        VARCHAR(128),
    phone        VARCHAR(32),
    status       VARCHAR(16)  NOT NULL DEFAULT 'ENABLED',
    deleted_at   TIMESTAMPTZ  NOT NULL DEFAULT TIMESTAMPTZ '1970-01-01 00:00:00+00',
    version      INT          NOT NULL DEFAULT 0,
    created_by   VARCHAR(64),
    updated_by   VARCHAR(64),
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT uk_sys_user_tenant_username UNIQUE (tenant_id, username, deleted_at)
);

CREATE INDEX IF NOT EXISTS idx_sys_user_tenant_status ON sys_user (tenant_id, status);

COMMENT ON TABLE sys_user IS '系统用户表';
COMMENT ON COLUMN sys_user.id IS '雪花 ID，由应用分配';
COMMENT ON COLUMN sys_user.tenant_id IS '租户 ID';
COMMENT ON COLUMN sys_user.username IS '登录用户名';
COMMENT ON COLUMN sys_user.email IS '邮箱；敏感个人信息，展示和日志须脱敏';
COMMENT ON COLUMN sys_user.phone IS '手机号；敏感个人信息，禁止明文进日志和缓存';
COMMENT ON COLUMN sys_user.status IS '状态：ENABLED/DISABLED';
COMMENT ON COLUMN sys_user.deleted_at IS '删除时间（UTC）。未删除为 1970-01-01，删除时写成实际时间，以便 (tenant_id, username, deleted_at) 唯一';
COMMENT ON COLUMN sys_user.version IS '乐观锁版本号';
COMMENT ON COLUMN sys_user.created_by IS '创建人用户 ID；系统初始化可为空';
COMMENT ON COLUMN sys_user.updated_by IS '最后修改人用户 ID';
COMMENT ON COLUMN sys_user.created_at IS '创建时间（UTC）';
COMMENT ON COLUMN sys_user.updated_at IS '更新时间（UTC）';
