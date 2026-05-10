#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple DNS resolver utilities.

Features:
- Resolve domains from a text file (one per line)
- Optional comment support (# comment)
- Optional ports in input (example.com:443)
- Structured per-domain results and summary statistics
- Small CLI for direct terminal usage
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import socket
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple


@dataclass(frozen=True)
class DnsResult:
    """Per-domain DNS query result."""

    domain: str
    ips: Tuple[str, ...]
    success: bool
    error: str = ""


@dataclass(frozen=True)
class DnsSummary:
    """Aggregate summary for a DNS batch query."""

    total_domains: int
    succeeded: int
    failed: int
    unique_ips: int


def _normalize_domain(raw: str) -> str:
    """Normalize a domain string from user/file input."""
    line = raw.split("#", 1)[0].strip()
    if not line:
        return ""

    if "://" in line:
        line = line.split("://", 1)[1]

    # Trim path/query fragments if someone pasted full URLs
    line = line.split("/", 1)[0].split("?", 1)[0].strip()

    # Handle "example.com:443" but not IPv6 literals.
    if ":" in line and line.count(":") == 1:
        host, port = line.rsplit(":", 1)
        if port.isdigit():
            line = host

    return line.lower().strip(".")


def _is_ip_address(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
    except ValueError:
        return False
    return True


def read_domains(file_path: str) -> List[str]:
    """Read, normalize, and deduplicate domains while preserving order."""
    raw_lines = Path(file_path).read_text(encoding="utf-8").splitlines()
    normalized = [_normalize_domain(line) for line in raw_lines]
    filtered = [domain for domain in normalized if domain]

    unique_domains: List[str] = []
    seen: Set[str] = set()
    for domain in filtered:
        if domain not in seen:
            unique_domains.append(domain)
            seen.add(domain)
    return unique_domains


def dns_detailed(file_path: str) -> Tuple[Set[str], List[str], List[DnsResult], DnsSummary]:
    """Detailed DNS query for each domain listed in a file."""
    domains = read_domains(file_path)
    resolved_ips: Set[str] = set()
    failed_domains: List[str] = []
    results: List[DnsResult] = []

    for domain in domains:
        try:
            if _is_ip_address(domain):
                ips = (domain,)
            else:
                _, _, ip_addresses = socket.gethostbyname_ex(domain)
                ips = tuple(sorted(set(ip_addresses)))
        except (socket.gaierror, socket.herror) as error:
            failed_domains.append(domain)
            results.append(
                DnsResult(domain=domain, ips=tuple(), success=False, error=str(error))
            )
        else:
            resolved_ips.update(ips)
            results.append(DnsResult(domain=domain, ips=ips, success=True))

    summary = DnsSummary(
        total_domains=len(domains),
        succeeded=sum(1 for item in results if item.success),
        failed=len(failed_domains),
        unique_ips=len(resolved_ips),
    )
    return resolved_ips, failed_domains, results, summary


def dns(file_path: str) -> Tuple[Set[str], List[str]]:
    """Backward-compatible API: returns (resolved_ips, failed_domains)."""
    resolved_ips, failed_domains, _, _ = dns_detailed(file_path)
    return resolved_ips, failed_domains


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve domains from a file.")
    parser.add_argument("file", help="Input file containing domains/hosts")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print detailed result as JSON",
    )
    return parser.parse_args()


def _render_text(results: Iterable[DnsResult], summary: DnsSummary) -> str:
    lines = []
    for result in results:
        if result.success:
            lines.append(f"[OK]   {result.domain} -> {', '.join(result.ips)}")
        else:
            lines.append(f"[FAIL] {result.domain} ({result.error})")

    lines.append("")
    lines.append(
        (
            f"Summary: total={summary.total_domains}, "
            f"succeeded={summary.succeeded}, failed={summary.failed}, "
            f"unique_ips={summary.unique_ips}"
        )
    )
    return "\n".join(lines)


def main() -> None:
    args = _parse_args()
    _, _, results, summary = dns_detailed(args.file)

    if args.json:
        payload = {
            "results": [asdict(item) for item in results],
            "summary": asdict(summary),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print(_render_text(results, summary))


if __name__ == "__main__":
    main()
