-- Production data fix template.
-- Never execute directly without a ticket, owner review, dry-run evidence, and rollback / forward-fix plan.

-- Ticket:
-- Owner:
-- Reviewer:
-- Environment:
-- Planned window:
-- Expected affected rows:
-- Rollback / forward-fix:

-- 1. Dry-run: inspect candidate rows.
SELECT id, tenant_id, status, updated_at
FROM sys_user
WHERE tenant_id = :tenant_id
  AND status = :old_status
  AND updated_at < :before_time
ORDER BY id
LIMIT 100;

-- 2. Count: confirm affected rows before write.
SELECT COUNT(*) AS affected_rows
FROM sys_user
WHERE tenant_id = :tenant_id
  AND status = :old_status
  AND updated_at < :before_time;

-- 3. Backup affected primary keys for rollback / audit.
CREATE TABLE IF NOT EXISTS ops_data_fix_YYYYMMDD_ticket_id AS
SELECT id, tenant_id, status, updated_at
FROM sys_user
WHERE tenant_id = :tenant_id
  AND status = :old_status
  AND updated_at < :before_time;

-- 4. Execute in bounded batches. Replace syntax with the target database dialect.
UPDATE sys_user
SET status = :new_status,
    updated_at = CURRENT_TIMESTAMP
WHERE tenant_id = :tenant_id
  AND status = :old_status
  AND updated_at < :before_time;

-- 5. Verify post-condition.
SELECT COUNT(*) AS remaining_rows
FROM sys_user
WHERE tenant_id = :tenant_id
  AND status = :old_status
  AND updated_at < :before_time;

-- 6. Rollback draft. Validate with owner before use.
-- UPDATE sys_user u
-- SET status = b.status,
--     updated_at = b.updated_at
-- FROM ops_data_fix_YYYYMMDD_ticket_id b
-- WHERE u.id = b.id
--   AND u.tenant_id = b.tenant_id;
