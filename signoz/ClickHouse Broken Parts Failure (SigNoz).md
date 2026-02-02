# ClickHouse Broken Parts Failure (SigNoz)

## Overview

The **cleanup-signoz-servers** pipeline and interactive ClickHouse access fail when querying the SigNoz ClickHouse instance because one or more MergeTree tables cannot be loaded. The server reports **Code 231 (TOO_MANY_UNEXPECTED_DATA_PARTS)**: the number of "broken" parts (0.00 B, corrupt or orphaned) exceeds the default limit `max_suspicious_broken_parts` (100). After increasing the limit to 200, a second table failed with 205 broken parts, so the limit was raised again until all tables could attach. The root cause is an unclean shutdown or disk/IO issues that left many broken parts in the data directories; the safety limit then blocks table attach to avoid silent data loss.

---

## Symptoms

- Pipeline **cleanup-signoz-servers.yml** fails with exit code 210 when running ClickHouse queries (e.g. listing partitions for cleanup).
- Interactive **clickhouse-client** (or DBeaver via SSH tunnel) fails on any query that triggers loading of affected tables (e.g. `system.parts`).
- Error message references **Code 231** and **max_suspicious_broken_parts** (e.g. "122 parts, 0.00 B in total ... maximum allowed broken parts count is 100").
- Affected tables observed: `signoz_traces.top_level_operations`, `signoz_traces.dependency_graph_minutes_v2` (others may appear with different counts).

---

## Common Errors

```
Code: 231. DB::Exception: Suspiciously many (122 parts, 0.00 B in total) broken parts to remove 
while maximum allowed broken parts count is 100. You can change the maximum value with merge tree 
setting 'max_suspicious_broken_parts' in <merge_tree> configuration section or in table settings 
in .sql file ...
(TOO_MANY_UNEXPECTED_DATA_PARTS)
```

```
Load job 'load table signoz_traces.top_level_operations' failed: Code: 231 ...
(ASYNC_LOAD_WAIT_FAILED)
```

---

## Root Cause and Context

- **When:** Container **signoz-clickhouse** (and host) last started on **2026-01-25 ~09:24 UTC**. Docker daemon had just restarted; logs show sandbox/endpoint cleanup and "Loading containers: done."
- **Why broken parts:** Unclean shutdown (reboot, OOM, or Docker restart) can leave MergeTree parts in an inconsistent state. Disk at **96.6%** and high load increase the risk of IO/space issues during writes or merges. The "0.00 B in total" broken parts are typically metadata or orphaned part directories that ClickHouse refuses to attach without an explicit higher limit.
- **Why the pipeline broke:** The workflow runs `SELECT ... FROM system.parts` (and similar) to decide which partitions to drop. Those queries require loading all tables in the database; as soon as one table fails to attach (Code 231), the whole query fails and the pipeline step exits with non-zero (e.g. 210).

---

## Solution (Increase max_suspicious_broken_parts)

### Approach

1. **Add a MergeTree config snippet** so ClickHouse allows more broken parts during attach (temporary measure to unblock the server).
2. **Place the file** in the container's config include directory. For the image used, the directory is **`/etc/clickhouse-server/config.d/`** (not `conf.d`).
3. **Restart the ClickHouse container** so the new config is loaded.
4. **Verify** with a query that touches `system.parts` (e.g. `SELECT database, sum(bytes_on_disk) ... FROM system.parts GROUP BY database`).
5. **If another table fails** with a count above the new limit (e.g. 205 > 200), increase `max_suspicious_broken_parts` again (e.g. to 250 or 300), then restart and re-test until all tables load.
6. **Optional:** After the instance is stable, run `OPTIMIZE TABLE ... FINAL` on affected tables and consider lowering `max_suspicious_broken_parts` back toward the default (e.g. 100) and restarting.

### Config file (merge_tree.xml)

On the host (e.g. `/opt/clickhouse-conf.d/merge_tree.xml`):

```xml
<clickhouse>
    <merge_tree>
        <max_suspicious_broken_parts>300</max_suspicious_broken_parts>
    </merge_tree>
</clickhouse>
```

Copy into the running container (path may differ; this image uses `config.d`):

```bash
docker cp /opt/clickhouse-conf.d/merge_tree.xml signoz-clickhouse:/etc/clickhouse-server/config.d/merge_tree.xml
docker restart signoz-clickhouse
```

If the file is already inside the container (e.g. after a previous edit), just adjust the value and restart.

### Guarantee and rollback

- **Not guaranteed:** Raising the limit only lets ClickHouse *attach* tables with many broken parts; it does not fix underlying corruption. It is a **workaround** to restore availability.
- **Rollback:** Remove or rename the custom config file in `config.d` (e.g. `merge_tree.xml`), then restart the container. The server will use the default (100) again. If tables still have more than 100 broken parts, they will fail to load again until the limit is raised or data is repaired/recreated.

---

## Summary

| Aspect | Description |
|--------|-------------|
| **Trigger** | Many broken MergeTree parts (0.00 B) in one or more tables, exceeding `max_suspicious_broken_parts` (default 100). |
| **Likely cause** | Unclean shutdown / Docker restart / disk or IO stress (e.g. disk 96.6% full). |
| **Mechanism** | Config `merge_tree.xml` in `config.d` with higher `max_suspicious_broken_parts`; restart container. |
| **Effect** | Tables attach successfully; pipeline and client queries work until another table exceeds the new limit. |
| **Rollback** | Remove custom config and restart; limit returns to default (tables may fail to load again if counts remain high). |

---

## Mitigation

- **Immediate:** Increase `max_suspicious_broken_parts` (e.g. 200, then 300 if needed) via `config.d/merge_tree.xml` and restart ClickHouse; re-run the cleanup pipeline.
- **Operational:** Free disk space and monitor usage; avoid abrupt restarts during heavy write/merge. Consider graceful shutdown of ClickHouse before host/container restarts.
- **After stability:** Run `OPTIMIZE TABLE ... FINAL` on affected tables; consider lowering `max_suspicious_broken_parts` back to default and document the incident for future similar failures.

---

## References

- ClickHouse documentation: [Merge Tree Settings](https://clickhouse.com/docs/en/operations/settings/merge-tree-settings) (e.g. `max_suspicious_broken_parts`).
- Pipeline: `.github/workflows/cleanup-signoz-servers.yml` (SigNoz EMM prod — 10.20.2.158).
