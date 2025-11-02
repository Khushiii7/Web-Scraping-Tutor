
import requests
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List
from tqdm import tqdm

from .utils import ensure_dir, atomic_write_json, jitter_backoff, atomic_append_lines

BASE = "https://issues.apache.org/jira"
SEARCH_API = "/rest/api/2/search"
COMMENT_API = "/rest/api/2/issue/{key}/comment"

MAX_RESULTS = 50     
MAX_RETRIES = 6
TIMEOUT = 30
BASE_SLEEP = 0.5     
COMMENT_WORKERS = 6  

session = requests.Session()
session.headers.update({
    "Accept": "application/json",
    "User-Agent": "apache-jira-scraper/1.0 khushigoyal0706@gmail.com"
})

def safe_get(url: str, params: Dict = None, attempt: int = 0) -> requests.Response:
    try:
        r = session.get(url, params=params, timeout=TIMEOUT)
    except requests.RequestException as e:
        if attempt < MAX_RETRIES:
            jitter_backoff(attempt)
            return safe_get(url, params=params, attempt=attempt+1)
        raise
    if r.status_code == 429:
        if attempt < MAX_RETRIES:
            ra = r.headers.get("Retry-After")
            if ra and ra.isdigit():
                time.sleep(int(ra) + 1)
            else:
                jitter_backoff(attempt)
            return safe_get(url, params=params, attempt=attempt+1)
        r.raise_for_status()
    if 500 <= r.status_code < 600:
        if attempt < MAX_RETRIES:
            jitter_backoff(attempt)
            return safe_get(url, params=params, attempt=attempt+1)
        r.raise_for_status()
    r.raise_for_status()
    return r

def fetch_comment_block(issue_key: str) -> List[Dict[str, Any]]:
    url = BASE + COMMENT_API.format(key=issue_key)
    r = safe_get(url)
    payload = r.json()
    return payload.get("comments", [])

class JiraScraper:
    def __init__(self, projects: List[str], output_dir: str = "output"):
        self.projects = projects
        self.output_dir = output_dir
        ensure_dir(self.output_dir)
        self.checkpoint_file = os.path.join(self.output_dir, "checkpoint.json")
        self.raw_dir = os.path.join(self.output_dir, "raw")
        ensure_dir(self.raw_dir)
        self.checkpoint = self._load_checkpoint()

    def _load_checkpoint(self) -> Dict:
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except Exception:
                    return {"projects": {}}
        return {"projects": {}}

    def _save_checkpoint(self):
        atomic_write_json(self.checkpoint_file, self.checkpoint)

    def _write_raw_issue(self, project: str, obj: Dict):
        path = os.path.join(self.raw_dir, f"raw_{project}.jsonl")
        atomic_append_lines(path, [json.dumps(obj, ensure_ascii=False)])

    def _fetch_comments_for_batch(self, issue_keys: List[str]) -> Dict[str, List[Dict]]:
        results = {}
        with ThreadPoolExecutor(max_workers=COMMENT_WORKERS) as ex:
            futures = {ex.submit(fetch_comment_block, k): k for k in issue_keys}
            for fut in as_completed(futures):
                key = futures[fut]
                try:
                    results[key] = fut.result()
                except Exception as e:
                    # log and continue - empty comments on failure
                    print(f"[warn] comments fetch failed for {key}: {e}", file=sys.stderr)
                    results[key] = []
                    # small backoff to avoid hot loops
                    time.sleep(0.5)
        return results

    def _fetch_issues_page(self, project: str, start_at: int) -> Dict[str, Any]:
        url = BASE + SEARCH_API
        params = {
            "jql": f"project={project}",
            "startAt": start_at,
            "maxResults": MAX_RESULTS,
            "fields": "summary,description,project,reporter,assignee,status,priority,labels,created,updated"
        }
        r = safe_get(url, params=params)
        return r.json()

    def run(self):
        for project in self.projects:
            print(f"=== Project: {project} ===")
            proj_state = self.checkpoint["projects"].get(project, {"startAt": 0, "done_keys": []})
            start = proj_state.get("startAt", 0)
            done_keys = set(proj_state.get("done_keys", []))
            total_seen = 0
            while True:
                payload = self._fetch_issues_page(project, start)
                issues = payload.get("issues", [])
                total = payload.get("total", 0)
                if not issues:
                    break
                # fetch comments concurrently for these issue keys
                keys = [i.get("key") for i in issues if i.get("key")]
                comment_map = self._fetch_comments_for_batch(keys)
                # iterate and write raw issue objects (issue + comments)
                new_done = []
                lines_to_append = []
                for issue in issues:
                    key = issue.get("key")
                    if not key:
                        continue
                    if key in done_keys:
                        continue
                    comments = comment_map.get(key, [])
                    raw_obj = {"issue": issue, "comments": comments}
                    # write to raw jsonl file
                    self._write_raw_issue(project, raw_obj)
                    new_done.append(key)
                    total_seen += 1
                # update checkpoint
                start += len(issues)
                proj_state["startAt"] = start
                proj_state.setdefault("done_keys", []).extend(new_done)
                self.checkpoint["projects"][project] = proj_state
                self._save_checkpoint()
                # polite sleep
                time.sleep(BASE_SLEEP)
                # stop condition
                if start >= total:
                    break
            print(f"Finished project {project} (scraped ~{len(proj_state.get('done_keys', []))} issues).")
        print("Scraping complete.")
