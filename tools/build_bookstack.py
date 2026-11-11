#!/usr/bin/env python3
"""Build a BookStack Portable ZIP from the MkDocs markdown sources."""

from __future__ import annotations

import json
import posixpath
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT_DIR = ROOT / "dist"
OUT_ZIP = OUT_DIR / "ansible-wiki-bookstack.zip"

BOOK_NAME = "Ansible в администрировании и кибербезопасности"
BOOK_DESCRIPTION = (
    "<p>Практическая вики по внедрению Ansible в администрирование "
    "и кибербезопасность распределённой филиальной сети на VMware ESXi.</p>"
)

CHAPTERS: list[tuple[str, list[str]]] = [
    (
        "Старт",
        [
            "start/reading-paths.md",
            "start/quickstart.md",
            "start/glossary.md",
        ],
    ),
    (
        "Основы",
        [
            "fundamentals/01-concepts.md",
            "fundamentals/02-architecture.md",
            "fundamentals/03-install.md",
            "fundamentals/04-config.md",
            "fundamentals/05-inventory.md",
            "fundamentals/06-variables.md",
            "fundamentals/07-playbooks-roles.md",
            "fundamentals/08-templates-lookups.md",
            "fundamentals/09-modules.md",
        ],
    ),
    (
        "Безопасная разработка",
        [
            "secure-dev/10-threat-model.md",
            "secure-dev/11-secrets.md",
            "secure-dev/12-access.md",
            "secure-dev/13-safe-code.md",
            "secure-dev/14-cicd-secrets.md",
            "secure-dev/15-supply-chain.md",
            "secure-dev/16-audit-logging.md",
        ],
    ),
    (
        "Администрирование",
        [
            "admin/20-branch-fleet.md",
            "admin/21-os-management.md",
            "admin/22-config-drift.md",
            "admin/23-files-acl-selinux.md",
            "admin/24-vmware-esxi.md",
            "admin/25-network-basics.md",
            "admin/26-network-devices.md",
            "admin/27-cloud.md",
            "admin/28-containers-k8s.md",
            "admin/29-backup-dr.md",
            "admin/30-scaling.md",
            "admin/31-migration.md",
        ],
    ),
    (
        "Кибербезопасность",
        [
            "security/35-linux-hardening.md",
            "security/36-auth-ssh-pam.md",
            "security/37-firewall.md",
            "security/38-kernel-audit.md",
            "security/39-tls-pki.md",
            "security/40-vmware-hardening.md",
            "security/41-network-cloud-hardening.md",
            "security/42-logging-monitoring.md",
            "security/43-vuln-patching.md",
            "security/44-compliance.md",
            "security/45-incident-response.md",
            "security/46-eda.md",
            "security/47-zero-trust.md",
            "security/48-airgap.md",
        ],
    ),
    (
        "Качество",
        [
            "quality/50-testing.md",
            "quality/51-cicd-gitops.md",
            "quality/52-review-release.md",
            "quality/53-aap-awx.md",
            "quality/54-governance.md",
            "quality/55-training-lab.md",
        ],
    ),
    (
        "Эксплуатация",
        [
            "ops/60-troubleshooting.md",
            "ops/61-checklists.md",
            "ops/62-antipatterns.md",
            "ops/63-roadmap.md",
            "ops/64-faq.md",
            "ops/65-cheatsheet.md",
            "ops/66-sources.md",
        ],
    ),
]

LINK_RE = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)]+)\)")
FENCE_RE = re.compile(r"(```.*?```)", re.DOTALL)


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return "", text
    return parts[1], parts[2]


def fm_value(frontmatter: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", frontmatter, re.MULTILINE)
    return match.group(1).strip() if match else ""


def page_name(frontmatter: str, fallback: str) -> str:
    title = fm_value(frontmatter, "title").strip()
    return title.strip('"') if title else fallback


def tag_value(frontmatter: str, key: str) -> str:
    value = fm_value(frontmatter, key).strip().strip('"')
    return value.strip("[]").replace('"', "").replace("'", "")


def transform_outside_fences(text: str, transform) -> str:
    parts = FENCE_RE.split(text)
    return "".join(part if part.startswith("```") else transform(part) for part in parts)


def main() -> int:
    all_paths = ["index.md"] + [path for _, pages in CHAPTERS for path in pages]
    missing = [path for path in all_paths if not (DOCS / path).is_file()]
    if missing:
        print("Missing pages:")
        for path in missing:
            print(f"  - {path}")
        return 1

    records: dict[str, dict] = {}
    page_id = 1
    for rel in all_paths:
        text = (DOCS / rel).read_text(encoding="utf-8")
        frontmatter, body = split_frontmatter(text)
        body = re.sub(r"^\s*# .+\n", "", body, count=1)
        records[rel] = {
            "id": page_id,
            "name": page_name(frontmatter, Path(rel).stem),
            "markdown": body.strip() + "\n",
            "tags": [
                {"name": "audience", "value": tag_value(frontmatter, "audience")},
                {"name": "level", "value": tag_value(frontmatter, "level")},
                {
                    "name": "security-impact",
                    "value": tag_value(frontmatter, "security_impact"),
                },
            ],
        }
        page_id += 1

    id_by_path = {rel: record["id"] for rel, record in records.items()}

    def convert_links(rel: str, text: str) -> str:
        def replace(match: re.Match) -> str:
            label, target = match.group(1), match.group(2).strip()
            if target.startswith(("http://", "https://", "mailto:", "tel:", "#")):
                return match.group(0)
            target = target.strip("<>").split("#", 1)[0]
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(rel), target))
            if resolved in id_by_path:
                return f"[[bsexport:page:{id_by_path[resolved]}]]"
            return label

        return transform_outside_fences(text, lambda chunk: LINK_RE.sub(replace, chunk))

    for rel, record in records.items():
        record["markdown"] = convert_links(rel, record["markdown"])

    chapters = []
    for index, (chapter_name, paths) in enumerate(CHAPTERS, start=1):
        chapters.append(
            {
                "name": chapter_name,
                "priority": index,
                "pages": [
                    {
                        **records[path],
                        "priority": page_priority,
                    }
                    for page_priority, path in enumerate(paths, start=1)
                ],
            }
        )

    data = {
        "instance": {"id": "ansible-wiki", "version": "0.1.0"},
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "book": {
            "name": BOOK_NAME,
            "description_html": BOOK_DESCRIPTION,
            "tags": [
                {"name": "topic", "value": "ansible"},
                {"name": "audience", "value": "sysadmin, secops, soc, architect, manager"},
            ],
            "pages": [{**records["index.md"], "priority": 1}],
            "chapters": chapters,
        },
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "data.json", json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        )
        archive.writestr("files/", "")

    print(f"BookStack export: {OUT_ZIP}")
    print(f"Pages: {len(records)}; chapters: {len(chapters)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
