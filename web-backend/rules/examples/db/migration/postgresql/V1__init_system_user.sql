-- Flyway PostgreSQL 样板。时间存 UTC（timestamptz）。
-- 默认租户模型为 NONE。项目已有租户列或租户插件时，按项目约定显式补充 tenant_id、组合唯一约束和查询隔离。
CREATE TABLE IF NOT EXISTS sys_user (
    id            BIGINT       PRIMARY KEY,
    username      VARCHAR(32)  NOT NULL,
    email         VARCHAR(128),
    phone         VARCHAR(32),
    status        VARCHAR(16)  NOT NULL DEFAULT 'ENABLED',
    is_deleted    SMALLINT     NOT NULL DEFAULT 0,
    delete_token  BIGINT       NOT NULL DEFAULT 0,
    deleted_at    TIMESTAMPTZ  NULL,
    deleted_by    VARCHAR(64)  NULL,
    version       INT          NOT NULL DEFAULT 0,
    created_by    VARCHAR(64),
    updated_by    VARCHAR(64),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT uk_sys_user_username_delete_token UNIQUE (username, delete_token)
);

CREATE INDEX IF NOT EXISTS idx_sys_user_status ON sys_user (status);

COMMENT ON TABLE sys_user IS '系统用户表';
COMMENT ON COLUMN sys_user.id IS '雪花 ID，由应用分配';
COMMENT ON COLUMN sys_user.username IS '登录用户名';
COMMENT ON COLUMN sys_user.email IS '邮箱；敏感个人信息，展示和日志须脱敏';
COMMENT ON COLUMN sys_user.phone IS '手机号；敏感个人信息，禁止明文进日志和缓存';
COMMENT ON COLUMN sys_user.status IS '状态：ENABLED/DISABLED';
COMMENT ON COLUMN sys_user.is_deleted IS '0未删除 1已删除。日常过滤只看这一列';
COMMENT ON COLUMN sys_user.delete_token IS '未删除为 0。删除时写成该行主键，使同名用户可以多次删除';
COMMENT ON COLUMN sys_user.deleted_at IS '删除时间（UTC）。只留痕，不参与过滤，也不进入唯一键';
COMMENT ON COLUMN sys_user.deleted_by IS '删除操作者，类型与 created_by 相同';
COMMENT ON COLUMN sys_user.version IS '乐观锁版本号';
COMMENT ON COLUMN sys_user.created_by IS '创建人用户 ID；系统初始化可为空';
COMMENT ON COLUMN sys_user.updated_by IS '最后修改人用户 ID';
COMMENT ON COLUMN sys_user.created_at IS '创建时间（UTC）';
COMMENT ON COLUMN sys_user.updated_at IS '更新时间（UTC）';
