#!/usr/bin/env python3
"""Founder one-shot: apply sibling patches in measured order. Do not push.

    python3 scripts/apply_product_patches.py --dry-run
    python3 scripts/apply_product_patches.py --product pointer --repo /path/to/Pointer
    python3 scripts/apply_product_patches.py --all

Clones SIBLING_PINS (the SHAs the patches were cut against), not live HEAD.
Live product HEAD moved 2026-10-30; push 403 so we cannot refresh patches.
Order matches sibling `scripts/test_sibling_patches.py`, not the README
"independent" crew-gate placement (crew-gate must land before crew-netie).
Constructor extras `constructor-*-4896ddd.patch` stay out of the 26-stack.
Does not push. Does not vendor OpenWork or Grok Bot. Cortex never
`uv add` Netie.git.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCHES = ROOT / "docs" / "patches"
_LOCAL_BIN = str(Path.home() / ".local" / "bin")
os.environ["PATH"] = _LOCAL_BIN + os.pathsep + os.environ.get("PATH", "")

CONSTRUCTOR_26: tuple[str, ...] = (
    "constructor-compiler-tests.patch",
    "constructor-empty-graph.patch",
    "constructor-ir-refuse.patch",
    "constructor-ir-ids.patch",
    "constructor-ghost-refuse.patch",
    "constructor-ir-emit.patch",
    "constructor-tool-action.patch",
    "constructor-inspect-action.patch",
    "constructor-inspect-object.patch",
    "constructor-inspect-tier.patch",
    "constructor-chat-object.patch",
    "constructor-topo-leftover.patch",
    "constructor-ir-entry.patch",
    "constructor-ir-output.patch",
    "constructor-ir-object.patch",
    "constructor-ir-bind.patch",
    "constructor-ir-action-allow.patch",
    "constructor-ir-intake.patch",
    "constructor-ir-hitl.patch",
    "constructor-ir-connected.patch",
    "constructor-ir-note.patch",
    "constructor-ir-cortex-post.patch",
    "constructor-object-pick.patch",
    "constructor-engine-order.patch",
    "constructor-ir-post.patch",
    "constructor-ir-kahn-nodes.patch",
)

CONSTRUCTOR_EXTRAS: tuple[str, ...] = (
    "constructor-ir-4896ddd.patch",
    "constructor-inspect-4896ddd.patch",
)

# Sibling measured order: crew-gate after lkgp, before context-headroom, so
# crew-netie has a gate to wrap. README lists crew-gate last; do not copy that.
OPENVAULT_STACK: tuple[str, ...] = (
    "openvault-detect-stacks.patch",
    "openvault-strict-random.patch",
    "openvault-lkgp.patch",
    "openvault-crew-gate.patch",
    "openvault-context-headroom.patch",
    "openvault-reset-window.patch",
    "openvault-reset-aware.patch",
    "openvault-cache-optimized.patch",
    "openvault-execution-shapes.patch",
    "openvault-chat-dispatch.patch",
    "openvault-hop-walk.patch",
    "openvault-hop-failover.patch",
    "openvault-hop-park.patch",
    "openvault-hop-stream.patch",
    "openvault-hop-relay.patch",
    "openvault-hop-trace.patch",
    "openvault-hop-usage.patch",
    "openvault-hop-persist.patch",
    "openvault-hop-anthropic.patch",
    "openvault-hop-scope.patch",
    "openvault-hop-serve.patch",
    "openvault-hop-bound.patch",
    "openvault-hop-catalog.patch",
    "openvault-quota-share.patch",
    "openvault-hop-strip.patch",
    "openvault-hop-sidecar.patch",
    "openvault-ship-netie.patch",
    "openvault-crew-netie.patch",
    "openvault-crew-skill-ids.patch",
    "openvault-free-pool.patch",
    "openvault-free-pool-route.patch",
    "openvault-ship-claim-ov.patch",
)

# Measured SHAs the patches were cut against (2026-08-28 / 2026-09-02).
# Live product HEAD moved 2026-10-30. Push 403, so --all clones these pins.
SIBLING_PINS: dict[str, str] = {
    "constructor": "4896ddd5edd46b6ccfdcfc2ec7fbe42d413a96fd",
    "openvault": "62bb1c7b056aeb2429f6ecdd073c1a24f9c4ad44",
    "cortex": "bf4eceea5595f426a613477cb36f1899e4842a78",
    "dms": "3f9a9be48ede43c506fd86bd819c700abf355277",
    "pointer": "8c0e6c21079d6cb4051cede7353cf23f04d4b3e9",
    "control": "82ab1aefc6d320f9dc0dc5a329b66f2d0f36cb28",
    "kb": "10356e58d1606b9b6bc2131edebc84bd0e42ab50",
}


@dataclass(frozen=True)
class Stack:
    repo: str
    branch: str
    pin: str
    patches: tuple[str, ...]
    cwd: str = "."
    uv_add_netie: bool = False
    verify: tuple[list[str], ...] = field(default_factory=tuple)
    min_passed: int | None = None


STACKS: dict[str, Stack] = {
    "constructor": Stack(
        repo="https://github.com/Netie-AI/constructor.git",
        branch="landing-9-first-path",
        pin=SIBLING_PINS["constructor"],
        patches=CONSTRUCTOR_26,
        verify=(["node", "--test", "tests/compiler.test.cjs"],),
        min_passed=62,
    ),
    "openvault": Stack(
        repo="https://github.com/Netie-AI/OpenVault.git",
        branch="main",
        pin=SIBLING_PINS["openvault"],
        patches=OPENVAULT_STACK,
        cwd="OpenMW",
        uv_add_netie=True,
        verify=(
            [
                "uv",
                "run",
                "pytest",
                "tests/test_route_strategies.py",
                "tests/test_execution_shapes.py",
                "tests/test_execution_chat.py",
                "tests/test_freeroute_acceptance.py",
                "tests/test_freeroute_metering.py",
                "tests/test_crew_gate.py",
                "tests/test_crew_netie_gate.py",
                "tests/test_ship_netie_claim.py",
                "tests/test_free_pool.py",
                "tests/test_free_pool_route.py",
                "-q",
                "--tb=line",
            ],
        ),
        min_passed=90,
    ),
    "cortex": Stack(
        repo="https://github.com/Netie-AI/Cortex.git",
        branch="main",
        pin=SIBLING_PINS["cortex"],
        patches=(
            "cortex-netie-path.patch",
            "cortex-web-via-runner.patch",
            "cortex-role-execute.patch",
            "cortex-observe-guard.patch",
        ),
        uv_add_netie=False,
        verify=(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/dms/test_constitution_path.py",
                "tests/dms/test_broker_no_skip.py",
                "tests/dms/test_f7_rbac.py",
                "-k",
                "not tool_runner",
                "-q",
            ],
        ),
    ),
    "dms": Stack(
        repo="https://github.com/Netie-AI/dms.git",
        branch="main",
        pin=SIBLING_PINS["dms"],
        patches=("dms-netie-acl.patch", "dms-demo-acl-resolve.patch"),
        uv_add_netie=True,
        verify=(
            [
                "pytest",
                "tests/test_netie_acl.py",
                "tests/test_space_acl_boundary.py",
                "tests/test_live_ask.py",
                "-q",
            ],
        ),
    ),
    "pointer": Stack(
        repo="https://github.com/Netie-AI/Pointer.git",
        branch="main",
        pin=SIBLING_PINS["pointer"],
        patches=("pointer-netie-hands.patch", "pointer-observe-guard.patch"),
        uv_add_netie=True,
        verify=(
            ["node", "test/netie-hands.test.js"],
            ["node", "test/netie-observe.test.js"],
            ["node", "test/uacc.test.js"],
        ),
    ),
    "control": Stack(
        repo="https://github.com/Netie-AI/netie-control.git",
        branch="main",
        pin=SIBLING_PINS["control"],
        patches=("control-netie-board.patch",),
        uv_add_netie=True,
        verify=(
            [
                "pytest",
                "tests/test_netie_board.py",
                "tests/test_control_stays_plane_4.py",
                "-q",
            ],
        ),
        min_passed=51,
    ),
    "kb": Stack(
        repo="https://github.com/Netie-AI/Netie-KB.git",
        branch="main",
        pin=SIBLING_PINS["kb"],
        patches=("kb-netie-index.patch",),
        uv_add_netie=True,
        verify=(["python3", "tests/test_netie_index.py"],),
    ),
}


def _run(
    cmd: list[str],
    cwd: Path,
    *,
    timeout: int = 180,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def apply_stack(name: str, dest: Path) -> None:
    """git apply each patch. Never push. Never mix constructor extras."""
    stack = STACKS[name]
    for extra in CONSTRUCTOR_EXTRAS:
        if extra in stack.patches:
            raise SystemExit(f"refuse mix {extra}")
    for patch_name in stack.patches:
        path = PATCHES / patch_name
        if not path.is_file():
            raise SystemExit(f"missing {patch_name}")
        applied = _run(["git", "apply", str(path)], cwd=dest)
        if applied.returncode != 0:
            raise SystemExit(f"{patch_name} failed: {applied.stderr or applied.stdout}")
        print(f"applied {patch_name}")


def verify_stack(name: str, dest: Path, *, netie: Path) -> None:
    stack = STACKS[name]
    work = dest / stack.cwd
    env_extra: list[str] = []
    if stack.uv_add_netie and name == "openvault":
        env_extra = ["--with-editable", str(netie)]
    for cmd in stack.verify:
        run_cmd = list(cmd)
        if run_cmd[:2] == ["uv", "run"] and env_extra:
            run_cmd = ["uv", "run", *env_extra, *run_cmd[2:]]
        print("verify", " ".join(run_cmd))
        probed = _run(run_cmd, cwd=work, timeout=180)
        blob = probed.stdout + probed.stderr
        if probed.returncode != 0:
            raise SystemExit(blob[-4000:] or f"{run_cmd} failed")
        if stack.min_passed is not None:
            import re

            found = re.search(r"(\d+) passed", blob)
            if found is None:
                raise SystemExit(f"no passed count: {blob[-500:]}")
            if int(found.group(1)) < stack.min_passed:
                raise SystemExit(
                    f"{name} passed {found.group(1)} < {stack.min_passed}"
                )
        print(blob[-500:] if len(blob) > 500 else blob)


def _clone_pinned(
    url: str, dest: Path, sha: str, *, timeout: int = 180
) -> subprocess.CompletedProcess[str]:
    dest.mkdir(parents=True, exist_ok=True)
    probed = _run(["git", "init"], cwd=dest, timeout=timeout)
    if probed.returncode != 0:
        return probed
    probed = _run(
        ["git", "remote", "add", "origin", url], cwd=dest, timeout=timeout
    )
    if probed.returncode != 0:
        return probed
    probed = _run(
        ["git", "fetch", "--depth", "1", "origin", sha], cwd=dest, timeout=timeout
    )
    if probed.returncode != 0:
        return probed
    return _run(
        ["git", "-c", "advice.detachedHead=false", "checkout", "FETCH_HEAD"],
        cwd=dest,
        timeout=timeout,
    )


def _clone(stack: Stack, dest: Path) -> None:
    cloned = _clone_pinned(stack.repo, dest, stack.pin)
    if cloned.returncode != 0:
        raise SystemExit(cloned.stderr or cloned.stdout)


def _print_dry_run(names: list[str]) -> None:
    for name in names:
        stack = STACKS[name]
        print(
            f"# {name} {stack.branch} pin={stack.pin} uv_add={stack.uv_add_netie}"
        )
        for patch_name in stack.patches:
            print(f"git apply docs/patches/{patch_name}")
        print("do not push")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Apply Netie product patches. Does not push."
    )
    parser.add_argument("--product", choices=sorted(STACKS), action="append")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--repo", type=Path, help="existing checkout (one product)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-tests", action="store_true")
    parser.add_argument("--push", action="store_true", help="refused")
    parser.add_argument("--netie", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    if args.push:
        print("do not push", file=sys.stderr)
        return 2
    names = list(args.product or [])
    if args.all:
        names = list(STACKS)
    if not names:
        names = list(STACKS)
        args.dry_run = True
    if args.repo is not None and len(names) != 1:
        print("--repo needs exactly one --product", file=sys.stderr)
        return 2
    if args.dry_run:
        _print_dry_run(names)
        return 0
    for name in names:
        stack = STACKS[name]
        if args.repo is not None:
            dest = args.repo.resolve()
            apply_stack(name, dest)
            if not args.skip_tests:
                verify_stack(name, dest, netie=args.netie.resolve())
            print(f"{name} applied. do not push.")
            continue
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / name
            _clone(stack, dest)
            apply_stack(name, dest)
            if not args.skip_tests:
                verify_stack(name, dest, netie=args.netie.resolve())
            print(f"{name} applied in a temp clone. do not push.")
    return 0


if __name__ == "__main__":
    if shutil.which("git") is None:
        raise SystemExit("git required")
    raise SystemExit(main())
