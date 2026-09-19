---
name: kubernetes-patterns
description: Kubernetes workload patterns, resource management, RBAC, probes, autoscaling, ConfigMap/Secret handling, and kubectl debugging for production-grade deployments.
triggers:
  - kubernetes
  - k8s
  - kubectl
  - deployment
  - pod
  - ingress
  - configmap
  - secret
  - rbac
  - serviceaccount
  - hpa
  - pdb
  - cronjob
  - crashloopbackoff
  - oomkilled
  - imagepullbackoff
metadata:
  origin: ECC
---

# Kubernetes Patterns

**Use when:** writing/reviewing K8s manifests · configuring probes, resources, RBAC, secrets · debugging pod errors · HPA/PDB/autoscaling

## Deployment — Critical Fields
```yaml
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxSurge: 1, maxUnavailable: 0 }
  template:
    spec:
      securityContext: { runAsNonRoot: true, runAsUser: 1001 }
      terminationGracePeriodSeconds: 30
      containers:
        - name: my-app
          image: ghcr.io/org/my-app:1.0.0  # Never :latest
          resources:
            requests: { cpu: "100m", memory: "128Mi" }
            limits:   { cpu: "500m", memory: "256Mi" }
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities: { drop: [ALL] }
          startupProbe:
            httpGet: { path: /health, port: 8080 }
            failureThreshold: 30   # 30×5s = 150s max startup; replaces initialDelaySeconds
            periodSeconds: 5
          livenessProbe:
            httpGet: { path: /health, port: 8080 }
            periodSeconds: 30
            failureThreshold: 3
          readinessProbe:
            httpGet: { path: /ready, port: 8080 }  # separate endpoint from liveness
            periodSeconds: 10
            failureThreshold: 2
          envFrom: [{ configMapRef: { name: my-app-config } }]
          env: [{ name: DB_PASSWORD, valueFrom: { secretKeyRef: { name: my-app-secrets, key: db-password } } }]
          volumeMounts: [{ name: tmp, mountPath: /tmp }]  # required when readOnlyRootFilesystem: true
      volumes: [{ name: tmp, emptyDir: {} }]
```

## Probes
| Probe | On failure | Use for |
|---|---|---|
| `startupProbe` | Kills container | Slow-starting apps (JVM, Python) |
| `livenessProbe` | Restarts container | Deadlock / hung process |
| `readinessProbe` | Removes from Service | Temporary unavailability (DB reconnect) |

> **Never** use `initialDelaySeconds` as a substitute for `startupProbe` — it's a race condition.

## Resource Sizing
| Workload | CPU req | Memory req | Notes |
|---|---|---|---|
| Web API | 100–250m | 128–256Mi | Limits 2–4× requests |
| Worker | 250–500m | 256–512Mi | Memory limit = request |
| JVM | 500m–1 | 512Mi–2Gi | Headroom above `-Xmx` |
| Sidecar | 10–50m | 32–64Mi | Keep minimal |

## RBAC — Least Privilege
```yaml
# Most apps: disable token entirely
apiVersion: v1
kind: ServiceAccount
metadata: { name: my-app-sa, namespace: my-namespace }
automountServiceAccountToken: false
---
# Apps that call the K8s API: grant only what's needed
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: { name: my-app-role, namespace: my-namespace }
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["secrets"]
    resourceNames: ["my-app-secrets"]  # name-scoped
    verbs: ["get"]
```

> Use `Role` (namespace-scoped), not `ClusterRole`, unless cluster-wide access is required.

## HPA & PDB
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: my-app }
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource: { name: cpu, target: { type: Utilization, averageUtilization: 70 } }
---
apiVersion: policy/v1
kind: PodDisruptionBudget
spec:
  minAvailable: 2
  selector: { matchLabels: { app: my-app } }
```

## kubectl Debugging
```bash
kubectl describe pod <pod> -n <ns>            # events, exit codes, OOMKilled
kubectl logs <pod> -n <ns> --previous         # logs from crashed container
kubectl get events -n <ns> --sort-by='.lastTimestamp'
# CrashLoopBackOff → --previous logs + exit code; ImagePullBackOff → Events section
# Pending → insufficient resources / taint mismatch; OOMKilled → raise memory limit
kubectl rollout undo deployment/my-app -n <ns>    # rollback
kubectl top pods -n <ns>                           # live resource use
kubectl apply -f manifest.yaml --dry-run=server   # validate before apply
```

## Anti-Patterns
| ❌ Bad | ✅ Good |
|---|---|
| `image: myapp:latest` | `image: myapp:1.4.2` or `@sha256:…` |
| No `resources` block | Always set requests **and** limits |
| `initialDelaySeconds` in liveness | Use `startupProbe` |
| Secrets in ConfigMap | `kind: Secret` + Sealed Secrets / ESO |
| `cluster-admin` ServiceAccount | Namespace `Role` + least-privilege verbs |
| `restartPolicy: Always` in a Job | `OnFailure` or `Never` |
| `minAvailable: 0` in PDB | `minAvailable: 1+` |

## Related Skills
- `docker-patterns` — Multi-stage Dockerfiles and image security
- `security-review` — Broader security hardening
- `git-workflow` — GitOps with ArgoCD / Flux
