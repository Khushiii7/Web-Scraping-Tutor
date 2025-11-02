
import os
import sys
from pathlib import Path

PROJECT_KEYS = ["HDFS", "SPARK", "HADOOP"] 
OUTPUT_DIR = "output"

def run_scrape():
    from .scraper import JiraScraper
    s = JiraScraper(PROJECT_KEYS, output_dir=OUTPUT_DIR)
    s.run()

def run_transform():
    from .transformer import transform_raw_project
    raw_dir = os.path.join(OUTPUT_DIR, "raw")
    clean_dir = os.path.join(OUTPUT_DIR, "clean")
    os.makedirs(clean_dir, exist_ok=True)
    # find raw files
    for f in Path(raw_dir).glob("raw_*.jsonl"):
        project = f.stem.replace("raw_", "")
        out_path = os.path.join(clean_dir, f"clean_{project}.jsonl")
        print(f"[transform] {f} -> {out_path}")
        transform_raw_project(str(f), out_path)
    print("[transform] done.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m src.run [scrape|transform|all]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "scrape":
        run_scrape()
    elif cmd == "transform":
        run_transform()
    elif cmd == "all":
        run_scrape()
        run_transform()
    else:
        print("Unknown command", cmd)
        sys.exit(2)

if __name__ == "__main__":
    main()
