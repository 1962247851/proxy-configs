#!/usr/bin/env python3
"""Fetch ACL4SSR NoAuto and inject repository-local Mihomo classical rule providers."""
from pathlib import Path
from urllib.request import urlopen
import os
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/config/ACL4SSR_Online_Full_NoAuto.ini"
OUTPUT = ROOT / "subconverter" / "ACL4SSR_Online_Full_NoAuto.ini"
REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "1962247851/proxy-configs")
REF = "main"
INTERVAL = 3600
GROUPS = {"DIRECT": "DIRECT", "REJECT": "REJECT", "PROXY": "🚀 节点选择"}
RULE_TYPES = ("DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "DOMAIN-REGEX", "IP-CIDR", "IP-CIDR6", "GEOIP", "PROCESS-NAME", "PROCESS-PATH", "DST-PORT", "SRC-IP-CIDR", "SRC-PORT", "NETWORK")


LIST_GROUPS = {"DIRECT": "🎯 全球直连", "REJECT": "🛑 全球拦截", "PROXY": "🚀 节点选择"}


def add_manual_groups(content):
    groups = [
        "🚀 手动切换1",
        "🚀 手动切换2",
        "🚀 手动切换3",
    ]

    lines = content.splitlines()
    result = []

    for line in lines:
        if line.startswith("custom_proxy_group="):
            name = line.split("=", 1)[1].split("`", 1)[0]

            # 不修改手动切换组自身，避免循环引用
            if name not in groups and name != "🚀 手动切换":
                if "`select`" in line:
                    for group in groups:
                        reference = f"`[]{group}"
                        if reference not in line:
                            line += reference

        result.append(line)

    # 在现有策略组末尾添加三个新组
    definitions = [
        f"custom_proxy_group={group}`select`.*"
        for group in groups
    ]

    # 插入最后一个 custom_proxy_group 后面
    last_index = max(
        i for i, line in enumerate(result)
        if line.startswith("custom_proxy_group=")
    )

    for definition in reversed(definitions):
        if definition not in result:
            result.insert(last_index + 1, definition)

    return "\n".join(result) + "\n"


def normalize_list_filenames():
    """Rename local .list files to Or + UpperCamelCase; fail on collisions."""
    for folder in LIST_GROUPS:
        directory = ROOT / "rulesets" / folder
        if not directory.is_dir():
            continue
        for file in sorted(directory.rglob("*.list")):
            if file.is_symlink() or not file.is_file():
                continue
            # Only add prefix when absent. Capitalize first char to match UpperCamelCase.
            stem = file.stem
            renamed = stem if stem.startswith("Or") else "Or" + stem[:1].upper() + stem[1:]
            target = file.with_name(renamed + ".list")
            if target != file:
                if target.exists():
                    raise FileExistsError(f"Ruleset filename collision: {file} -> {target}")
                file.rename(target)
                print(f"Renamed {file.relative_to(ROOT)} -> {target.relative_to(ROOT)}")


def rulesets():
    entries = []
    for folder, group in GROUPS.items():
        directory = ROOT / "rules" / folder
        if not directory.exists():
            continue
        for file in sorted(directory.rglob("*.yaml")) + sorted(directory.rglob("*.yml")):
            if file.is_symlink() or not file.is_file():
                continue
            content = file.read_text(encoding="utf-8")
            if not re.search(r"(?m)^payload:\s*$", content):
                raise ValueError(f"Invalid rule-provider payload: {file}")
            if not re.search(r"(?m)^\s+-\s+\S", content):
                raise ValueError(f"Rule-provider is empty: {file}")
            relative = file.relative_to(ROOT).as_posix()
            url = f"https://raw.githubusercontent.com/{REPOSITORY}/{REF}/{relative}"
            entries.append(f"ruleset={group},clash-classic:{url},{INTERVAL}")
    for folder, group in LIST_GROUPS.items():
        directory = ROOT / "rulesets" / folder
        if not directory.is_dir():
            continue
        for file in sorted(directory.rglob("*.list")):
            if file.is_symlink() or not file.is_file():
                continue
            if not any(line.strip() and not line.lstrip().startswith("#") for line in file.read_text(encoding="utf-8").splitlines()):
                raise ValueError(f"Empty .list ruleset: {file}")
            relative = file.relative_to(ROOT).as_posix()
            url = f"https://raw.githubusercontent.com/{REPOSITORY}/{REF}/{relative}"
            entries.append(f"ruleset={group},{url}")
    if not entries:
        raise ValueError("No rulesets under rules/ or rulesets/")
    return entries


def merge(upstream):
    lines = upstream.lstrip("\ufeff").splitlines()
    if not any(line.strip() == "[custom]" for line in lines):
        raise ValueError("Upstream lacks [custom] section")
    match_indices = [i for i, line in enumerate(lines) if line.strip().startswith("ruleset=")]
    if not match_indices:
        raise ValueError("Upstream lacks ruleset= entries")
    first = match_indices[0]
    # Only inject inside [custom] before upstream rules; preserve the rest untouched.
    if lines.index("[custom]") > first:
        raise ValueError("Unexpected upstream section order")
    custom = ["; >>> LOCAL REMOTE RULE PROVIDERS >>>", *rulesets(), "; <<< LOCAL REMOTE RULE PROVIDERS <<<", ""]
    lines[first:first] = custom
    return "\n".join(lines) + "\n"


def main():
    normalize_list_filenames()
    with urlopen(SOURCE, timeout=40) as response:
        upstream = response.read().decode("utf-8-sig")
    entries = rulesets()
    # 合并自定义远程规则集
    generated = merge(upstream)
    # 新增三个手动切换策略组
    generated = add_manual_groups(generated)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != generated:
        OUTPUT.write_text(generated, encoding="utf-8")
        print(f"Updated {OUTPUT.relative_to(ROOT)} with {len(entries)} remote rulesets")
    else:
        print("No changes")


if __name__ == "__main__":
    main()
