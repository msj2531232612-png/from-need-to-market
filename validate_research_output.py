#!/usr/bin/env python3
"""Check a from-need-to-market research directory for structural problems.

Covers what can be judged mechanically: required files, research status,
card order and unique IDs, field counts, dangling card/action references,
evidence traceability, action fields, relative links and anchors, and
leftover template placeholders. Exit code 1 means at least one error.
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

REQUIRED_FILES = [
    "00-start-here.md",
    "01-market-cards.md",
    "02-evidence-log.md",
    "03-action-plan.md",
]
RESULTS_FILE = "04-action-results.md"
CARD_ORDER = "RMPEVC"
# Minimum number of "- **field**" lines per card type (the card name is the bold title line).
MIN_FIELDS = {"R": 6, "M": 5, "P": 6, "E": 6, "V": 6, "C": 6}
RESEARCH_STATUSES = [
    "部分完成", "等待材料", "完成", "离线",
    "partially complete", "partial", "waiting for input", "waiting", "complete", "offline",
]
ACTION_STATUSES = [
    "待执行", "进行中", "等待材料", "已完成",
    "pending", "in progress", "waiting for input", "waiting", "done", "completed",
]
ACTION_FIELDS = [
    ("要回答的问题", ("问题", "question")),
    ("状态", ("状态", "status")),
    ("输入和前置条件", ("输入", "前置", "input", "prerequisite")),
    ("操作步骤", ("步骤", "steps")),
    ("产出", ("产出", "output", "deliverable")),
    ("验收条件", ("验收", "acceptance")),
    ("结果分支", ("分支", "branch")),
    ("依据", ("依据", "basis", "based on")),
]

CARD_HEADING = re.compile(r"^###\s+([RMPEVC])(\d{2})\s*$", re.M)
ANY_HEADING = re.compile(r"^#{1,6}\s+.*$", re.M)
# Two digits only, so prices such as "R799" are not read as card IDs.
CARD_REF = re.compile(r"(?<![A-Za-z0-9])([RMPEVC])(\d{2})(?![A-Za-z0-9])")
CARD_RANGE = re.compile(
    r"(?<![A-Za-z0-9])([RMPEVC])(\d{2})\s*[–—~～-]\s*\1(\d{2})(?![A-Za-z0-9])"
)
ACTION_HEADING = re.compile(r"^#{2,3}\s+(A\d{2,3})\s*[｜|:：]", re.M)
ACTION_REF = re.compile(r"(?<![A-Za-z0-9])(A\d{2,3})(?![A-Za-z0-9])")
RESULT_HEADING = re.compile(
    r"^###\s+(\d{4}-\d{2}-\d{2})\s*[｜|]\s*(A\d{2,3})\s*[｜|]\s*(.+?)\s*$", re.M
)
FIELD_LINE = re.compile(r"^\s*[-*]\s+\*\*(.+?)\*\*", re.M)
LINK = re.compile(r"\]\(([^)\s]+)\)")
FENCE = re.compile(r"^(```|~~~)", re.M)


class Report:
    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def error(self, where: str, message: str) -> None:
        self.errors.append(f"[错误] {where}: {message}")

    def warn(self, where: str, message: str) -> None:
        self.warnings.append(f"[提醒] {where}: {message}")


def strip_code_and_urls(text: str) -> str:
    """Remove fenced blocks and link targets so IDs inside them are not counted."""
    text = re.sub(r"^(```|~~~+).*?^\1[~`]*\s*$", "", text, flags=re.M | re.S)
    text = re.sub(r"\]\([^)]*\)", "]", text)
    return re.sub(r"https?://\S+", "", text)


def anchors_in(text: str) -> Set[str]:
    found: Set[str] = set()
    for match in ANY_HEADING.finditer(text):
        heading = re.sub(r"^#{1,6}\s+", "", match.group(0)).strip().lower()
        heading = re.sub(r"[^\w\- ]", "", heading).replace(" ", "-")
        found.add(heading)
    found.update(re.findall(r"<a\s+(?:id|name)=\"([^\"]+)\"", text))
    return found


def split_cards(text: str) -> List[Tuple[str, str]]:
    """Return (card_id, body) for each '### X01' section in file order."""
    cards: List[Tuple[str, str]] = []
    matches = list(CARD_HEADING.finditer(text))
    for index, match in enumerate(matches):
        end = len(text)
        following = ANY_HEADING.search(text, match.end())
        if following:
            end = following.start()
        if index + 1 < len(matches):
            end = min(end, matches[index + 1].start())
        cards.append((match.group(1) + match.group(2), text[match.end():end]))
    return cards


def referenced_cards(text: str) -> Set[str]:
    clean = strip_code_and_urls(text)
    refs: Set[str] = set()
    for match in CARD_RANGE.finditer(clean):
        letter, start, stop = match.group(1), int(match.group(2)), int(match.group(3))
        width = len(match.group(2))
        if start <= stop and stop - start < 100:
            refs.update(f"{letter}{n:0{width}d}" for n in range(start, stop + 1))
    refs.update(m.group(1) + m.group(2) for m in CARD_REF.finditer(clean))
    return refs


def find_status(text: str, labels: Tuple[str, ...], allowed: List[str]) -> Tuple[bool, Optional[str]]:
    """Look for '**label**: value' and match value against allowed (longest first)."""
    pattern = re.compile(
        r"\*\*\s*(?:%s)\s*[:：]?\s*\*\*\s*[:：]?\s*(.+)" % "|".join(map(re.escape, labels)), re.I
    )
    match = pattern.search(text)
    if not match:
        return False, None
    value = match.group(1).strip().lower()
    for status in sorted(allowed, key=len, reverse=True):
        if value.startswith(status):
            return True, status
    return True, None


def check_start_here(text: str, present: Set[str], report: Report) -> None:
    name = "00-start-here.md"
    found, status = find_status(text, ("调研状态", "结果状态", "research status"), RESEARCH_STATUSES)
    if not found:
        report.error(name, "缺少“**调研状态**：…”一行")
    elif status is None:
        report.error(name, "调研状态必须以 完成、部分完成、离线、等待材料 之一开头")
    for other in REQUIRED_FILES[1:]:
        if other in present and f"({other}" not in text:
            report.error(name, f"没有链接到 {other}")


def check_cards(text: str, offline: bool, report: Report) -> Set[str]:
    name = "01-market-cards.md"
    cards = split_cards(text)
    ids = [card_id for card_id, _ in cards]
    seen: Set[str] = set()
    for card_id in ids:
        if card_id in seen:
            report.error(name, f"卡片编号重复: {card_id}")
        seen.add(card_id)

    order = [CARD_ORDER.index(card_id[0]) for card_id in ids]
    if order != sorted(order):
        report.error(name, "卡片顺序应为 R、M、P、E、V、C")
    for letter in "RVC":
        count = sum(1 for card_id in ids if card_id[0] == letter)
        if count != 1:
            report.error(name, f"应有且仅有一张 {letter}01 卡，实际 {count} 张")
    if not any(card_id[0] == "M" for card_id in ids):
        report.error(name, "至少需要一张 M 卡")
    if not offline and not any(card_id[0] == "P" for card_id in ids):
        report.warn(name, "没有 P 卡；若未找到任何产品或替代做法，请在 C01 说明")

    titles: Dict[str, str] = {}
    for card_id, body in cards:
        stripped = body.strip()
        first_line = stripped.splitlines()[0].strip() if stripped else ""
        if not (first_line.startswith("**") and first_line.endswith("**") and len(first_line) > 4):
            report.error(name, f"{card_id} 标题下一行应为粗体卡名")
        elif card_id[0] == "P":
            key = first_line.strip("*").strip().lower()
            if key in titles:
                report.error(name, f"{card_id} 与 {titles[key]} 是同一产品，应合并为一张产品卡")
            titles[key] = card_id
        fields = len(FIELD_LINE.findall(body))
        if fields < MIN_FIELDS[card_id[0]]:
            report.error(
                name, f"{card_id} 只有 {fields} 个字段，{card_id[0]} 卡至少需要 {MIN_FIELDS[card_id[0]]} 个"
            )
        if card_id[0] == "E" and not re.search(r"\d{4}-\d{2}-\d{2}", body):
            report.warn(name, f"{card_id} 没有核验日期（YYYY-MM-DD）")
        if card_id[0] == "P" and not re.search(r"https?://|S\d{2}|用户提供|provided by", body):
            report.warn(name, f"{card_id} 没有可追溯的来源（链接、S 编号或用户提供材料）")
        if card_id[0] == "V" and not (referenced_cards(body) - {card_id}):
            report.error(name, f"{card_id} 没有引用任何支持它的卡片")
    return seen


def check_evidence_log(text: str, card_ids: Set[str], offline: bool, report: Report) -> None:
    name = "02-evidence-log.md"
    for card_id in sorted(card_ids):
        if card_id[0] == "E" and card_id not in referenced_cards(text):
            report.error(name, f"证据台账中找不到 {card_id}，无法追溯到来源")
    has_queries = re.search(r"(?<![A-Za-z0-9])Q\d{2,3}(?![A-Za-z0-9])", strip_code_and_urls(text))
    if not has_queries and not offline:
        report.error(name, "没有任何 Q 编号的实际查询；离线成果请加 --offline 并写明未执行联网查询")
    if has_queries and offline:
        report.warn(name, "离线成果中出现了 Q 编号，请确认它们没有被写成实际执行的查询")
    if any(card_id[0] == "E" for card_id in card_ids) and not re.search(
        r"(?<![A-Za-z0-9])S\d{2,3}(?![A-Za-z0-9])", text
    ):
        report.warn(name, "有 E 卡但没有 S 编号的来源记录")


def check_action_plan(text: str, report: Report) -> Set[str]:
    name = "03-action-plan.md"
    matches = list(ACTION_HEADING.finditer(text))
    ids = [match.group(1) for match in matches]
    if not ids:
        report.error(name, "没有找到“## A01｜…”形式的行动")
        return set()
    if len(ids) != len(set(ids)):
        report.error(name, "行动编号重复")
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        following = re.compile(r"^##\s+", re.M).search(text, match.end())
        if following:
            end = min(end, following.start())
        body = text[match.end():end]
        labels = [label.lower() for label in FIELD_LINE.findall(body)]
        for field, keywords in ACTION_FIELDS:
            if not any(keyword in label for label in labels for keyword in keywords):
                report.error(name, f"{match.group(1)} 缺少字段：{field}")
        found, status = find_status(body, ("状态", "status"), ACTION_STATUSES)
        if found and status is None:
            report.error(name, f"{match.group(1)} 的状态应以 待执行、进行中、等待材料、已完成 之一开头")
    tail = text[matches[-1].end():]
    if len(FENCE.findall(tail)) < 2:
        report.warn(name, "文件末尾没有找到代码块形式的交接指令")
    return set(ids)


def check_action_results(text: str, action_ids: Set[str], report: Report) -> None:
    name = RESULTS_FILE
    entries = RESULT_HEADING.findall(text)
    if not entries:
        report.error(name, "没有“### YYYY-MM-DD｜A01｜状态”形式的记录")
    for _date, action_id, status in entries:
        if not any(status.lower().startswith(allowed) for allowed in ACTION_STATUSES):
            report.error(name, f"{action_id} 的记录状态“{status}”不在允许取值内")
    for action_id in sorted(set(ACTION_REF.findall(strip_code_and_urls(text))) - action_ids):
        report.error(name, f"引用了行动方案中不存在的 {action_id}")


def check_links(root: Path, texts: Dict[str, str], report: Report) -> None:
    anchor_cache: Dict[Path, Set[str]] = {}
    for name, text in texts.items():
        for target in LINK.findall(text):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            path_part, _, fragment = target.partition("#")
            destination = (root / urllib.parse.unquote(path_part)).resolve() if path_part else root / name
            if not destination.exists():
                report.error(name, f"链接目标不存在: {target}")
                continue
            if fragment and destination.suffix.lower() == ".md":
                if destination not in anchor_cache:
                    anchor_cache[destination] = anchors_in(destination.read_text(encoding="utf-8"))
                if urllib.parse.unquote(fragment).lower() not in anchor_cache[destination]:
                    report.error(name, f"锚点不存在: {target}")


def validate(root: Path, offline: bool = False) -> Report:
    report = Report()
    if not root.is_dir():
        report.error(str(root), "不是目录")
        return report

    texts: Dict[str, str] = {}
    for name in REQUIRED_FILES + [RESULTS_FILE]:
        path = root / name
        if path.is_file():
            content = path.read_text(encoding="utf-8")
            if content.strip():
                texts[name] = content
            else:
                report.error(name, "文件为空")
        elif name != RESULTS_FILE:
            report.error(name, "文件缺失")

    for name, text in texts.items():
        if "{{" in text or "}}" in text:
            report.error(name, "残留模板占位符 {{…}}")

    if "00-start-here.md" in texts:
        check_start_here(texts["00-start-here.md"], set(texts), report)
    card_ids: Set[str] = set()
    if "01-market-cards.md" in texts:
        card_ids = check_cards(texts["01-market-cards.md"], offline, report)
        for name, text in texts.items():
            for missing in sorted(referenced_cards(text) - card_ids):
                report.error(name, f"引用了不存在的卡片 {missing}")
    if "02-evidence-log.md" in texts:
        check_evidence_log(texts["02-evidence-log.md"], card_ids, offline, report)
    action_ids: Set[str] = set()
    if "03-action-plan.md" in texts:
        action_ids = check_action_plan(texts["03-action-plan.md"], report)
        for name in ("00-start-here.md", "01-market-cards.md"):
            for missing in sorted(set(ACTION_REF.findall(strip_code_and_urls(texts.get(name, "")))) - action_ids):
                report.error(name, f"引用了行动方案中不存在的 {missing}")
    if RESULTS_FILE in texts:
        check_action_results(texts[RESULTS_FILE], action_ids, report)
    check_links(root, texts, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="Research output directory to check")
    parser.add_argument("--offline", action="store_true", help="The research ran without web access")
    args = parser.parse_args()

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    report = validate(args.directory.expanduser(), offline=args.offline)
    for line in report.errors + report.warnings:
        print(line)
    print(f"校验结束：{len(report.errors)} 个错误，{len(report.warnings)} 条提醒。")
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
