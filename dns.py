#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
from typing import List, Set, Tuple


def dns(file_path: str) -> Tuple[Set[str], List[str]]:
    """Query DNS for each URL listed in a file.

    Args:
        file_path: Path to a file containing one URL per line.

    Returns:
        A tuple of (resolved_ips, failed_urls).
    """
    resolved_ips: Set[str] = set()
    failed_urls: List[str] = []
    with open(file_path, "r", encoding="utf-8") as file_handle:
        for line in file_handle:
            url = line.strip()
            if not url:
                continue
            try:
                _, _, ip_addresses = socket.gethostbyname_ex(url)
            except (socket.gaierror, socket.herror):
                failed_urls.append(url)
            else:
                resolved_ips.update(ip_addresses)
    return resolved_ips, failed_urls
