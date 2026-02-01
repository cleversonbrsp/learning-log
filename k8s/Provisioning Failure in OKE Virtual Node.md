# Provisioning Failure in OKE Virtual Node

## Overview

Intermittent provisioning failures occur during deployments when workloads run on **Oracle Kubernetes Engine (OKE)** using **Virtual Nodes**. When a Deployment is updated (e.g., new image revision), the new Pod may fail to provision due to temporary lack of capacity in the underlying OCI infrastructure (region or availability domain, such as AD).

In these cases, the Pod does not start correctly and the Deployment rollout can block, leading to a **progress deadline exceeded** error. The root cause is not the application but the dynamic capacity provisioning of the Virtual Node.

---

## Symptoms

- New Pods fail to start after a Deployment revision.
- Rollout remains stuck; progress deadline may be exceeded.
- Errors indicate insufficient capacity rather than application or image issues.

---

## Common Errors

```
Error creating pod: [cannot provision pod due to insufficient capacity]
```

---

## Pipeline workaround

Because this issue is caused by temporary capacity limits in the infrastructure backing Virtual Nodes, a **workaround** was added to our pipelines.

### Approach

1. **Cordon and isolate to a single node**  
   Before or during the rollout, the pipeline cordons and isolates the workload to a single node. This reduces scheduling spread and makes retries more predictable.

2. **Retry for transient failures only**  
   In the pipelines, **retry does not fix application or configuration errors**; it is used only to **mitigate transient provisioning failures**. Each restart starts a new scheduling cycle, which may place the Pod on different available infrastructure and succeed when capacity was temporarily unavailable elsewhere.

3. **Resilience vs. root cause**  
   This approach improves the resilience of the deploy process while the root cause—cloud capacity—cannot be controlled directly.

### Summary

| Aspect | Description |
|--------|-------------|
| **Trigger** | Temporary lack of capacity in OCI/Virtual Node infrastructure |
| **Mechanism** | Cordon + isolate to one node; retry on provisioning failure |
| **Retry purpose** | Transient provisioning only (not app/config fixes) |
| **Effect** | New scheduling cycle per restart; Pod may land on available capacity |

---

## Oracle Guidance on Virtual Node Shapes

During meetings with Oracle, the recommendation was to use **shape A6** instead of **A4**, as A4 is no longer supported.

When creating an OKE Virtual Node, the UI currently offers only shapes **A1** and **A4**. If A6 is required for support and capacity, this may need to be requested or configured via Oracle support or updated OKE/OCI APIs.

---

## Mitigation

- **Pipeline workaround:** Use cordon + isolate to a single node and retry on provisioning failure (see [Pipeline workaround](#pipeline-workaround)). Retries target transient capacity issues only, not application or configuration errors.
- Prefer supported shapes (e.g., A6) where available; avoid deprecated shapes (e.g., A4).
- Retry the rollout after a short delay when capacity errors occur; they are often transient.
- Consider spreading workloads across availability domains or regions if capacity is frequently constrained in one location.
- Escalate to Oracle support if A6 (or other required shapes) are not available in the OKE Virtual Node creation flow.

---

## References

- OKE Virtual Nodes documentation
- OCI compute shapes (A1, A4, A6) and regional capacity
