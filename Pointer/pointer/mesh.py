"""Independent probes of Cortex TAS, OpenVault mesh Cortex, and OpenVault.

OpenVault (public, cloneable) hard-codes Cortex at :8000.
TAS-CORTEX in this meta repo starts uvicorn at :8010.
Pointer's gate uses CORTEX_URL (default :8010) only.

A silent remap 8010 -> 8000 is a lie. If the laptop runs Cortex the OpenVault
way, the founder must set CORTEX_URL=http://127.0.0.1:8000 before `pointer serve`.
This module never copies secrets. Gemini keys live in OpenVault provider `google`
as GOOGLE_API_KEY (see OpenVault airgpt_keyvault.PROVIDER_TO_ENV).
"""

from __future__ import annotations

import os
import urllib.error
import urllib.request
from typing import Any

from . import DEFAULT_PORT

TAS_CORTEX_DEFAULT = "http://127.0.0.1:8010"
OPENVAULT_MESH_CORTEX_DEFAULT = "http://127.0.0.1:8000"
OPENVAULT_DEFAULT = "http://127.0.0.1:5000"

# Measured 2026-08-22 from clone https://github.com/Netie-AI/OpenVault
OPENVAULT_HEALTH = "/api/healthz"
OPENVAULT_GOOGLE_PROVIDER = "google"
OPENVAULT_GOOGLE_ENV = "GOOGLE_API_KEY"
OPENVAULT_GOOGLE_REGISTER = "https://aistudio.google.com/apikey"


def tas_cortex_base() -> str:
    return os.environ.get("CORTEX_URL", TAS_CORTEX_DEFAULT).rstrip("/")


def openvault_mesh_cortex_base() -> str:
    return os.environ.get(
        "OPENVAULT_CORTEX_URL", OPENVAULT_MESH_CORTEX_DEFAULT
    ).rstrip("/")


def openvault_base() -> str:
    return os.environ.get("OPENVAULT_URL", OPENVAULT_DEFAULT).rstrip("/")


def probe_url(url: str, timeout: float = 1.0) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            code = int(resp.status)
            return {"ok": 200 <= code < 300, "http": code, "error": None}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "http": int(exc.code), "error": f"HTTP {exc.code}"}
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        return {"ok": False, "http": None, "error": str(exc)}


def probe_cortex(base: str) -> dict[str, Any]:
    health = probe_url(base + "/health")
    if health["ok"]:
        return {"reachable": True, "path": "/health", **health}
    healthz = probe_url(base + "/healthz")
    if healthz["ok"]:
        return {"reachable": True, "path": "/healthz", **healthz}
    return {
        "reachable": False,
        "path": "/health",
        "ok": False,
        "http": health.get("http") or healthz.get("http"),
        "error": health.get("error") or healthz.get("error"),
    }


def probe_openvault(base: str) -> dict[str, Any]:
    hz = probe_url(base + OPENVAULT_HEALTH)
    if hz["ok"]:
        return {"reachable": True, "path": OPENVAULT_HEALTH, **hz}
    alt = probe_url(base + "/healthz")
    if alt["ok"]:
        return {"reachable": True, "path": "/healthz", **alt}
    return {
        "reachable": False,
        "path": OPENVAULT_HEALTH,
        "ok": False,
        "http": hz.get("http") or alt.get("http"),
        "error": hz.get("error") or alt.get("error"),
    }


def report() -> dict[str, Any]:
    tas = probe_cortex(tas_cortex_base())
    mesh_cx = probe_cortex(openvault_mesh_cortex_base())
    vault = probe_openvault(openvault_base())
    same_url = tas_cortex_base() == openvault_mesh_cortex_base()
    degraded: list[str] = []
    if not tas["reachable"]:
        degraded.append("cortex_tas_unreachable")
    if not mesh_cx["reachable"]:
        degraded.append("cortex_openvault_mesh_unreachable")
    if not vault["reachable"]:
        degraded.append("openvault_unreachable")
    if not same_url and tas["reachable"] is False and mesh_cx["reachable"] is True:
        degraded.append("cortex_on_openvault_port_set_CORTEX_URL")
    return {
        "pointer_listen": f"127.0.0.1:{DEFAULT_PORT}",
        "silent_port_remap": False,
        "cortex_auto_ingests_pointer_intent": False,
        "cortex_tas": {
            "url": tas_cortex_base(),
            "default": TAS_CORTEX_DEFAULT,
            "source": "TAS-CORTEX uvicorn --port 8010; Pointer gate uses CORTEX_URL",
            **tas,
        },
        "cortex_openvault_mesh": {
            "url": openvault_mesh_cortex_base(),
            "default": OPENVAULT_MESH_CORTEX_DEFAULT,
            "source": "cloneable Netie-AI/OpenVault mesh contract (not used by the gate)",
            **mesh_cx,
        },
        "openvault": {
            "url": openvault_base(),
            "default": OPENVAULT_DEFAULT,
            "clone": "https://github.com/Netie-AI/OpenVault",
            "google_provider": OPENVAULT_GOOGLE_PROVIDER,
            "google_env": OPENVAULT_GOOGLE_ENV,
            "register": OPENVAULT_GOOGLE_REGISTER,
            "key_policy": (
                "OpenVault is the only key vault. Upsert GOOGLE_API_KEY for provider "
                "google (POST /api/keyvault/upsert). Export that env into the hackathon "
                "process. Pointer does not copy secrets from OpenVault."
            ),
            **vault,
        },
        "degraded": degraded,
    }
