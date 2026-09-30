-- Flyway MySQL 样板。时间存 UTC。排序规则全库统一为 utf8mb4_unicode_ci。
-- 默认租户模型为 NONE。项目已有租户列或租户插件时，按项目约定显式补充 tenant_id、组合唯一约束和查询隔离。
-- 身份若在外部认证系统，不要在本表加密码列，改为外部主体标识。
CREATE TABLE IF NOT EXISTS sys_user (
    id              BIGINT       NOT NULL PRIMARY KEY COMMENT '雪花 ID，由应用分配',
    username        VARCHAR(32)  NOT NULL COMMENT '登录用户名',
    email           VARCHAR(128) NULL COMMENT '邮箱；敏感个人信息，展示和日志须脱敏',
    phone           VARCHAR(32)  NULL COMMENT '手机号；敏感个人信息，禁止明文进日志和缓存',
    status          VARCHAR(16)  NOT NULL DEFAULT 'ENABLED' COMMENT '状态：ENABLED/DISABLED',
    is_deleted      SMALLINT     NOT NULL DEFAULT 0 COMMENT '0未删除 1已删除。日常过滤只看这一列',
    delete_token    BIGINT       NOT NULL DEFAULT 0 COMMENT '未删除为 0。删除时写成该行主键，使同名用户可以多次删除',
    deleted_at      DATETIME(3)  NULL COMMENT '删除时间（UTC）。只留痕，不参与过滤，也不进入唯一键',
    deleted_by      VARCHAR(64)  NULL COMMENT '删除操作者，类型与 created_by 相同',
    version         INT          NOT NULL DEFAULT 0 COMMENT '乐观锁版本号',
    created_by      VARCHAR(64)  NULL COMMENT '创建人用户 ID；系统初始化可为空',
    updated_by      VARCHAR(64)  NULL COMMENT '最后修改人用户 ID',
    created_at      DATETIME(3)  NOT NULL DEFAULT (UTC_TIMESTAMP(3)) COMMENT '创建时间（UTC）',
    updated_at      DATETIME(3)  NOT NULL DEFAULT (UTC_TIMESTAMP(3)) COMMENT '更新时间（UTC）；由应用显式写入，禁止依赖会话时区驱动的 ON UPDATE CURRENT_TIMESTAMP',
    UNIQUE KEY uk_sys_user_username_delete_token (username, delete_token),
    KEY idx_sys_user_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统用户表';
