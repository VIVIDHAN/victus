"""BlastShield CloudOps tools: AWS infrastructure health diagnostics and safe remediation actions.

Diagnostic tools provide read-only observability. Remediation tools modify infrastructure state
and are safeguarded by the Strands Decider 2B BlastRadiusGuard before execution.
"""

from __future__ import annotations

import json
from pathlib import Path
from strands import tool

DATA_FILE = Path(__file__).resolve().parent / "data" / "services.json"


def _load_data() -> dict:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return {"services": {}, "cloudwatch_logs": {}}


ACTIONS: list[dict] = []


@tool
def check_service_health(service_name: str, environment: str = "production") -> dict:
    """Check the health status, CPU, memory, and error rates of an AWS cloud service."""
    data = _load_data()
    svc = data.get("services", {}).get(service_name.lower().strip())
    if not svc:
        available = list(data.get("services", {}).keys())
        return {"error": f"Service '{service_name}' not found. Available services: {available}"}
    return {
        "service_name": service_name,
        "environment": environment,
        **svc,
    }


@tool
def inspect_cloudwatch_logs(service_name: str, limit: int = 5) -> dict:
    """Inspect recent CloudWatch logs and error events for an AWS service."""
    data = _load_data()
    logs = data.get("cloudwatch_logs", {}).get(service_name.lower().strip())
    if logs is None:
        return {"error": f"No CloudWatch log stream found for service '{service_name}'"}
    return {
        "service_name": service_name,
        "log_events": logs[:limit],
        "total_lines": len(logs),
    }


@tool
def scale_service(service_name: str, desired_count: int, environment: str = "production") -> dict:
    """Scale the desired task or instance count of an AWS service (state-changing)."""
    data = _load_data()
    svc = data.get("services", {}).get(service_name.lower().strip())
    if not svc:
        return {"error": f"Cannot scale: service '{service_name}' does not exist"}
    old_count = svc.get("tasks_desired", 0)
    svc["tasks_desired"] = desired_count
    ACTIONS.append({
        "action": "scale_service",
        "service": service_name,
        "old_count": old_count,
        "new_count": desired_count,
        "environment": environment,
    })
    return {
        "action": "scale_service",
        "service_name": service_name,
        "environment": environment,
        "previous_desired_count": old_count,
        "new_desired_count": desired_count,
        "status": "scaling_in_progress",
    }


@tool
def reboot_resource(resource_type: str, resource_id: str, environment: str = "production") -> dict:
    """Reboot or restart a cloud resource, container task, or node (destructive/disruptive)."""
    ACTIONS.append({
        "action": "reboot_resource",
        "resource_type": resource_type,
        "resource_id": resource_id,
        "environment": environment,
    })
    return {
        "action": "reboot_resource",
        "resource_type": resource_type,
        "resource_id": resource_id,
        "environment": environment,
        "status": "reboot_initiated",
    }


@tool
def flush_cache(cache_name: str, environment: str = "production") -> dict:
    """Flush an in-memory cache cluster or drop volatile keys (destructive/data-loss)."""
    ACTIONS.append({
        "action": "flush_cache",
        "cache_name": cache_name,
        "environment": environment,
    })
    return {
        "action": "flush_cache",
        "cache_name": cache_name,
        "environment": environment,
        "status": "cache_flushed_successfully",
    }


TOOLS = [check_service_health, inspect_cloudwatch_logs, scale_service, reboot_resource, flush_cache]
