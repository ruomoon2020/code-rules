# Production Data Fix Runbook

> 备份、恢复演练、RTO/RPO 见 `docs/backup-restore-runbook.md`。

## Before Execution

- Ticket:
- Business reason:
- Owner:
- Reviewer:
- Executor:
- Environment:
- Planned window:
- Affected tenants / users:
- Expected affected rows:
- Rollback or forward-fix plan:

## Dry-run Evidence

1. Candidate query:
2. Candidate sample:
3. Count query:
4. Expected row count:
5. Risk notes:

## Execution

1. Confirm backup / snapshot status.
2. Confirm application version and maintenance window.
3. Execute bounded batch.
4. Record actual affected rows.
5. Stop immediately if actual rows exceed expected range.

## Verification

1. Post-condition query:
2. Sample verification:
3. Business owner confirmation:
4. Audit log / change record link:

## Follow-up

- Add automated guard or test:
- Remove temporary script:
- Postmortem required: yes / no
