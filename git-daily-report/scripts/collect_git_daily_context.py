#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import date, datetime, time, timedelta, timezone, tzinfo
from pathlib import Path
from typing import Any

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None

FALLBACK_FIXED_TIMEZONES = {
    "UTC": "+00:00",
    "Etc/UTC": "+00:00",
    "Asia/Shanghai": "+08:00",
    "Asia/Chongqing": "+08:00",
    "Asia/Harbin": "+08:00",
    "Asia/Hong_Kong": "+08:00",
    "Asia/Singapore": "+08:00",
    "Asia/Tokyo": "+09:00",
}


def run_git(repo: str, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", repo, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if check and result.returncode != 0:
        command = " ".join(["git", "-C", repo, *args])
        raise RuntimeError(f"git command failed: {command}\n{result.stderr.strip()}")
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect commit history and working tree context for a daily git report."
    )
    parser.add_argument("--repo", default=".", help="Repository path. Defaults to the current directory.")
    parser.add_argument(
        "--date",
        dest="report_date",
        help="Report date in YYYY-MM-DD. Defaults to today in the selected timezone.",
    )
    parser.add_argument(
        "--timezone",
        default="local",
        help="IANA timezone name like Asia/Shanghai, a UTC offset like +08:00, or 'local'.",
    )
    parser.add_argument(
        "--author",
        default="auto",
        help="Commit author filter. Use 'auto' for the current git user, 'all' for no filter, or a custom string.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--max-diff-lines",
        type=int,
        default=80,
        help="Maximum number of lines to keep in staged or unstaged patch previews.",
    )
    return parser.parse_args()


def parse_timezone(value: str) -> tuple[tzinfo, str]:
    if value.lower() == "local":
        local_tz = datetime.now().astimezone().tzinfo
        if local_tz is None:
            raise ValueError("Unable to determine the local timezone.")
        return local_tz, str(local_tz)

    offset_match = re.fullmatch(r"([+-])(\d{2}):(\d{2})", value)
    if offset_match:
        sign = 1 if offset_match.group(1) == "+" else -1
        hours = int(offset_match.group(2))
        minutes = int(offset_match.group(3))
        delta = timedelta(hours=hours, minutes=minutes) * sign
        return timezone(delta), value

    if ZoneInfo is None:
        fallback = FALLBACK_FIXED_TIMEZONES.get(value)
        if fallback:
            return parse_timezone(fallback)
        raise ValueError("IANA timezones require Python 3.9+ with zoneinfo support.")

    try:
        return ZoneInfo(value), value
    except Exception:
        fallback = FALLBACK_FIXED_TIMEZONES.get(value)
        if fallback:
            return parse_timezone(fallback)
        raise ValueError(f"Unsupported timezone: {value}")


def resolve_report_window(report_date: str | None, tz: tzinfo) -> tuple[datetime, datetime, date]:
    now = datetime.now(tz)
    target_date = date.fromisoformat(report_date) if report_date else now.date()
    start = datetime.combine(target_date, time.min, tzinfo=tz)
    end_of_day = datetime.combine(target_date, time(23, 59, 59), tzinfo=tz)
    end = min(now, end_of_day) if target_date == now.date() else end_of_day
    return start, end, target_date


def resolve_author(repo: str, author_arg: str) -> tuple[str | None, str]:
    lowered = author_arg.lower()
    if lowered == "all":
        return None, "all"
    if lowered != "auto":
        return author_arg, f"custom({author_arg})"

    email = run_git(repo, "config", "user.email", check=False).stdout.strip()
    name = run_git(repo, "config", "user.name", check=False).stdout.strip()
    if email:
        return email, f"auto(email={email})"
    if name:
        return name, f"auto(name={name})"
    return None, "all(no git user configured)"


def parse_name_status(output: str) -> list[dict[str, str]]:
    files: list[dict[str, str]] = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split("\t")
        status = parts[0]
        if status.startswith(("R", "C")) and len(parts) >= 3:
            path = f"{parts[1]} -> {parts[2]}"
        elif len(parts) >= 2:
            path = parts[1]
        else:
            path = ""
        files.append({"status": status, "path": path})
    return files


def parse_numstat(output: str) -> tuple[int, int, list[dict[str, Any]]]:
    insertions = 0
    deletions = 0
    files: list[dict[str, Any]] = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = raw_line.split("\t")
        if len(parts) < 3:
            continue
        added_raw, deleted_raw, path = parts[0], parts[1], parts[2]
        added = int(added_raw) if added_raw.isdigit() else None
        deleted = int(deleted_raw) if deleted_raw.isdigit() else None
        if added is not None:
            insertions += added
        if deleted is not None:
            deletions += deleted
        files.append({"path": path, "insertions": added, "deletions": deleted})
    return insertions, deletions, files


def path_to_area(path: str) -> str:
    normalized = path.split(" -> ")[-1].replace("\\", "/").strip()
    parts = [part for part in normalized.split("/") if part]
    if not parts:
        return normalized
    if parts[0] in {"src", "app", "packages", "modules", "features", "services"} and len(parts) >= 2:
        return "/".join(parts[:2])
    return "/".join(parts[: min(2, len(parts))])


def top_areas(paths: list[str], limit: int = 5) -> list[str]:
    counter = Counter(path_to_area(path) for path in paths if path)
    return [area for area, _ in counter.most_common(limit)]


def collect_commit(repo: str, commit_hash: str) -> dict[str, Any]:
    meta = run_git(
        repo,
        "show",
        "--quiet",
        "--format=%H%x00%an%x00%ae%x00%ad%x00%s%x00%b",
        "--date=iso-strict",
        commit_hash,
    ).stdout
    fields = meta.split("\x00")
    body = "\x00".join(fields[5:]).strip()
    name_status = parse_name_status(run_git(repo, "show", "--name-status", "--format=", commit_hash).stdout)
    insertions, deletions, numstat = parse_numstat(
        run_git(repo, "show", "--numstat", "--format=", commit_hash).stdout
    )
    shortstat = run_git(repo, "show", "--shortstat", "--format=", commit_hash).stdout.strip()

    return {
        "hash": fields[0].strip(),
        "short_hash": fields[0].strip()[:7],
        "author_name": fields[1].strip(),
        "author_email": fields[2].strip(),
        "authored_at": fields[3].strip(),
        "subject": fields[4].strip(),
        "body": body,
        "shortstat": shortstat,
        "insertions": insertions,
        "deletions": deletions,
        "areas": top_areas([item["path"] for item in name_status]),
        "files": name_status,
        "numstat": numstat,
    }


def truncate_lines(text: str, max_lines: int) -> tuple[str, bool]:
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text.strip(), False
    truncated = "\n".join(lines[:max_lines]).rstrip()
    return truncated, True


def collect_diff_section(repo: str, staged: bool, max_diff_lines: int) -> dict[str, Any]:
    diff_args = ["diff"]
    if staged:
        diff_args.append("--cached")

    name_status = parse_name_status(run_git(repo, *diff_args, "--name-status").stdout)
    insertions, deletions, numstat = parse_numstat(run_git(repo, *diff_args, "--numstat").stdout)
    shortstat = run_git(repo, *diff_args, "--shortstat").stdout.strip()
    patch_preview_raw = run_git(repo, *diff_args, "--unified=0", "--no-color").stdout
    patch_preview, preview_truncated = truncate_lines(patch_preview_raw, max_diff_lines)

    return {
        "has_changes": bool(name_status),
        "shortstat": shortstat,
        "insertions": insertions,
        "deletions": deletions,
        "areas": top_areas([item["path"] for item in name_status]),
        "files": name_status,
        "numstat": numstat,
        "patch_preview": patch_preview,
        "patch_preview_truncated": preview_truncated,
    }


def collect_untracked(repo: str) -> dict[str, Any]:
    output = run_git(repo, "ls-files", "--others", "--exclude-standard").stdout
    files = [line.strip() for line in output.splitlines() if line.strip()]
    return {
        "has_changes": bool(files),
        "count": len(files),
        "areas": top_areas(files),
        "files": files,
    }


def collect_today_commits(
    repo: str,
    start: datetime,
    end: datetime,
    author: str | None,
) -> list[dict[str, Any]]:
    args = [
        "rev-list",
        "--reverse",
        f"--since={start.isoformat()}",
        f"--until={end.isoformat()}",
    ]
    if author:
        args.append(f"--author={re.escape(author)}")
    args.append("HEAD")
    hashes = [line.strip() for line in run_git(repo, *args).stdout.splitlines() if line.strip()]
    return [collect_commit(repo, commit_hash) for commit_hash in hashes]


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = run_git(args.repo, "rev-parse", "--show-toplevel").stdout.strip()
    branch = run_git(repo_root, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    status_short = run_git(repo_root, "status", "--short").stdout.rstrip()

    tz, tz_label = parse_timezone(args.timezone)
    start, end, target_date = resolve_report_window(args.report_date, tz)
    author, author_label = resolve_author(repo_root, args.author)

    commits = collect_today_commits(repo_root, start, end, author)
    staged = collect_diff_section(repo_root, staged=True, max_diff_lines=args.max_diff_lines)
    unstaged = collect_diff_section(repo_root, staged=False, max_diff_lines=args.max_diff_lines)
    untracked = collect_untracked(repo_root)

    return {
        "repo_root": repo_root,
        "repo_name": Path(repo_root).name,
        "branch": branch,
        "report_date": target_date.isoformat(),
        "timezone": tz_label,
        "window_start": start.isoformat(),
        "window_end": end.isoformat(),
        "author_filter": author_label,
        "status_short": status_short,
        "today_commits": commits,
        "working_tree": {
            "staged": staged,
            "unstaged": unstaged,
            "untracked": untracked,
        },
    }


def configure_output_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def render_commit(commit: dict[str, Any], index: int) -> list[str]:
    lines = [
        f"### Commit {index}: {commit['short_hash']} {commit['subject']}",
        f"authored_at: {commit['authored_at']}",
        f"author: {commit['author_name']} <{commit['author_email']}>",
    ]
    if commit["shortstat"]:
        lines.append(f"shortstat: {commit['shortstat']}")
    if commit["areas"]:
        lines.append(f"areas: {', '.join(commit['areas'])}")
    if commit["body"]:
        lines.append("body:")
        lines.extend(f"  {line}" for line in commit["body"].splitlines())
    if commit["files"]:
        lines.append("files:")
        lines.extend(f"  - {item['status']} {item['path']}" for item in commit["files"])
    return lines


def render_diff_section(title: str, section: dict[str, Any]) -> list[str]:
    lines = [f"## {title}"]
    if not section["has_changes"]:
        lines.append("none")
        return lines
    if section["shortstat"]:
        lines.append(f"shortstat: {section['shortstat']}")
    if section["areas"]:
        lines.append(f"areas: {', '.join(section['areas'])}")
    if section["files"]:
        lines.append("files:")
        lines.extend(f"  - {item['status']} {item['path']}" for item in section["files"])
    if section["patch_preview"]:
        lines.append("patch_preview:")
        lines.extend(f"  {line}" for line in section["patch_preview"].splitlines())
        if section["patch_preview_truncated"]:
            lines.append("  [truncated]")
    return lines


def render_text(report: dict[str, Any]) -> str:
    lines = [
        "# Git Daily Context",
        f"repo: {report['repo_root']}",
        f"branch: {report['branch']}",
        f"report_date: {report['report_date']}",
        f"timezone: {report['timezone']}",
        f"window: {report['window_start']} -> {report['window_end']}",
        f"author_filter: {report['author_filter']}",
        "",
        "## Status Short",
        report["status_short"] or "clean",
        "",
        f"## Today Commits ({len(report['today_commits'])})",
    ]

    if report["today_commits"]:
        for index, commit in enumerate(report["today_commits"], start=1):
            lines.append("")
            lines.extend(render_commit(commit, index))
    else:
        lines.append("none")

    lines.extend(
        [
            "",
            "## Working Tree Overview",
            f"staged_changes: {report['working_tree']['staged']['has_changes']}",
            f"unstaged_changes: {report['working_tree']['unstaged']['has_changes']}",
            f"untracked_files: {report['working_tree']['untracked']['count']}",
            "",
        ]
    )

    lines.extend(render_diff_section("Staged Changes", report["working_tree"]["staged"]))
    lines.append("")
    lines.extend(render_diff_section("Unstaged Changes", report["working_tree"]["unstaged"]))
    lines.append("")
    lines.append("## Untracked Files")
    if report["working_tree"]["untracked"]["has_changes"]:
        if report["working_tree"]["untracked"]["areas"]:
            lines.append(f"areas: {', '.join(report['working_tree']['untracked']['areas'])}")
        lines.extend(f"  - {path}" for path in report["working_tree"]["untracked"]["files"])
    else:
        lines.append("none")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    configure_output_streams()
    args = parse_args()
    try:
        report = build_report(args)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_text(report), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
