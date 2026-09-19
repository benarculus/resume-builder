#!/usr/bin/env python3
"""Render an approved resume intermediate JSON payload as a portable .docx file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH


def load_payload(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("resume input must be a JSON object")
    if not isinstance(payload.get("basics"), dict):
        raise ValueError("resume input must include a basics object")
    return payload


def add_bullets(document: Document, values: list[str]) -> None:
    for value in values:
        document.add_paragraph(str(value), style="List Bullet")


def build_document(payload: dict[str, Any]) -> Document:
    document = Document()
    basics = payload["basics"]
    name = str(basics.get("name", ""))
    heading = document.add_heading(name or "Resume", level=0)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

    contact = " | ".join(
        str(value)
        for key in ("email", "phone", "location", "url")
        if (value := basics.get(key))
    )
    if contact:
        paragraph = document.add_paragraph(contact)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    if payload.get("summary"):
        document.add_heading("Summary", level=1)
        document.add_paragraph(str(payload["summary"]))

    if payload.get("experience"):
        document.add_heading("Experience", level=1)
        for role in payload["experience"]:
            title = " — ".join(
                str(value)
                for key in ("title", "company")
                if (value := role.get(key))
            )
            dates = str(role.get("dates", ""))
            document.add_paragraph(f"{title} {dates}".strip())
            add_bullets(document, [str(item) for item in role.get("bullets", [])])

    if payload.get("education"):
        document.add_heading("Education", level=1)
        for item in payload["education"]:
            details = " — ".join(
                str(value)
                for key in ("degree", "institution", "dates")
                if (value := item.get(key))
            )
            document.add_paragraph(details)

    if payload.get("skills"):
        document.add_heading("Skills", level=1)
        document.add_paragraph(", ".join(str(item) for item in payload["skills"]))

    if payload.get("awards"):
        document.add_heading("Awards", level=1)
        for item in payload["awards"]:
            details = item.get("details") or item.get("title") or ""
            document.add_paragraph(str(details))

    if payload.get("unmetRequirements"):
        document.add_heading("Requirements not addressed", level=1)
        add_bullets(document, [str(item) for item in payload["unmetRequirements"]])

    return document


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    document = build_document(load_payload(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    document.save(args.output)


if __name__ == "__main__":
    main()
