import json
import os
from typing import Any, Dict, List
from .utils import ensure_dir, atomic_append_lines

def extract_plain_text(field_value) -> str:
    if field_value is None:
        return ""
    if isinstance(field_value, str):
        return field_value.strip()
    def walk(node):
        if node is None:
            return ""
        if isinstance(node, str):
            return node
        if isinstance(node, dict):
            out = ""
            if node.get("text"):
                out += node.get("text")
            for v in node.values():
                if isinstance(v, list):
                    for c in v:
                        out += walk(c)
            return out
        if isinstance(node, list):
            return " ".join(walk(x) for x in node)
        return ""
    return walk(field_value).strip()

def simple_summary(text: str, max_chars: int = 300) -> str:
    if not text:
        return ""
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    candidate = paras[0] if paras else text
    if len(candidate) > max_chars:
        return candidate[:max_chars].rsplit(" ",1)[0] + "..."
    return candidate

def generate_qna_seeds(title: str, description: str, comments: List[Dict]) -> List[Dict]:
    seeds = []
    if description:
        first_sentence = description.split(".")[0].strip()
        if first_sentence:
            seeds.append({"q": "What is the issue about?", "a": first_sentence})
    if comments:
        last_body = comments[-1].get("body") or ""
        last_body_text = last_body.strip()
        if last_body_text:
            seeds.append({"q": "What does the last comment mention?", "a": last_body_text[:250]})
    return seeds

def transform_raw_project(raw_path: str, out_path: str):
    ensure_dir(os.path.dirname(out_path))
    lines_to_write = []
    with open(raw_path, "r", encoding="utf-8") as fin:
        for line in fin:
            try:
                raw = json.loads(line)
            except Exception:
                continue
            issue = raw.get("issue", {})
            comments = raw.get("comments", [])
            fields = issue.get("fields", {})
            issue_key = issue.get("key")
            title = fields.get("summary") or ""
            description = extract_plain_text(fields.get("description"))
            comment_texts = []
            for c in comments:
                body = c.get("body") or c.get("renderedBody") or ""
                body_text = extract_plain_text(body)
                comment_texts.append({
                    "author": c.get("author", {}).get("displayName"),
                    "created": c.get("created"),
                    "body": body_text
                })
            obj = {
                "issue_key": issue_key,
                "title": title,
                "project": fields.get("project", {}).get("key"),
                "reporter": fields.get("reporter", {}).get("displayName") if fields.get("reporter") else None,
                "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
                "status": fields.get("status", {}).get("name") if fields.get("status") else None,
                "priority": fields.get("priority", {}).get("name") if fields.get("priority") else None,
                "labels": fields.get("labels", []),
                "created": fields.get("created"),
                "updated": fields.get("updated"),
                "description": description,
                "comments": comment_texts,
                "derived": {
                    "summary": simple_summary(description + "\n\n" + " ".join(c["body"] for c in comment_texts)),
                    "classification": None,
                    "qna_seeds": generate_qna_seeds(title, description, comment_texts)
                }
            }
            lines_to_write.append(json.dumps(obj, ensure_ascii=False))
            if len(lines_to_write) >= 100:
                atomic_append_lines(out_path, lines_to_write)
                lines_to_write = []
    if lines_to_write:
        atomic_append_lines(out_path, lines_to_write)
