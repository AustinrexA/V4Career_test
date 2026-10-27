#!/usr/bin/env python3
"""Run JobSpy for Indeed + Naukri and save completed results to V4Career's DB.

Run from the V4Career project root:
  python scripts/run_jobspy.py --minutes 5 --results-per-site 100

Database writes are enabled by default. Use --dry-run to collect and report without
writing to the database. The script uses the existing .env, normalize_job(), and
save_jobs() functions; it does not need a separate CSV import step.
"""
from __future__ import annotations

import argparse
import csv
import multiprocessing as mp
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from collectors.normalization import normalize_job
from collectors.repository import save_jobs

ROLES = [
    "Software Engineer", "Python Developer", "Java Developer", "Full Stack Developer",
    "Frontend Developer", "Backend Developer", "Data Analyst", "Data Engineer",
    "Machine Learning Engineer", "DevOps Engineer", "QA Engineer", "Cloud Engineer",
    "Android Developer", "React Developer", "Graduate Engineer Trainee",
]
LOCATIONS = ["Chennai", "Bengaluru", "Hyderabad", "Pune", "Mumbai", "Delhi NCR"]
SOURCE_INFO = {
    "indeed": ("Indeed", "https://in.indeed.com/"),
    "naukri": ("Naukri", "https://www.naukri.com/"),
}


def scrape_one(role, location, results_wanted, hours_old, output_path, queue):
    """Worker runs one combined site query and writes only its completed result to CSV."""
    try:
        from jobspy import scrape_jobs
        jobs = scrape_jobs(
            site_name=["indeed", "naukri"],
            search_term=role,
            location=location,
            results_wanted=results_wanted,
            country_indeed="India",
            description_format="plain",
            hours_old=hours_old,
            verbose=0,
        )
        jobs.to_csv(output_path, index=False, encoding="utf-8-sig")
        queue.put({"ok": True, "count": int(len(jobs)), "errors": getattr(jobs, "attrs", {}).get("errors", {})})
    except Exception as exc:
        queue.put({"ok": False, "error": f"{type(exc).__name__}: {exc}"})


def nonempty(value):
    if value is None:
        return None
    value = str(value).strip()
    if not value or value.casefold() in {"nan", "none", "nat"}:
        return None
    return value


def row_to_job(row):
    site = (nonempty(row.get("site")) or "").casefold()
    if site not in SOURCE_INFO:
        raise ValueError(f"Unsupported JobSpy site: {site!r}")
    raw = {
        "external_id": nonempty(row.get("id") or row.get("job_id")),
        "title": nonempty(row.get("title")),
        "company": nonempty(row.get("company")),
        "location": nonempty(row.get("location")),
        "experience": nonempty(row.get("experience_range") or row.get("experience")),
        "salary_min": nonempty(row.get("min_amount")),
        "salary_max": nonempty(row.get("max_amount")),
        "salary_currency": nonempty(row.get("currency")) or "INR",
        "salary_period": nonempty(row.get("interval")) or "year",
        "skills": nonempty(row.get("skills")),
        "description": nonempty(row.get("description")),
        "job_url": nonempty(row.get("job_url") or row.get("url")),
        "posted_at": nonempty(row.get("date_posted") or row.get("posted_at")),
        "status": "active",
    }
    return site, normalize_job(raw)


def save_completed_csv(csv_path, dry_run, seen_hashes, totals):
    grouped = defaultdict(list)
    row_errors = 0
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            try:
                site, job = row_to_job(row)
                if job["url_hash"] in seen_hashes[site]:
                    totals["duplicates_in_run"] += 1
                    continue
                seen_hashes[site].add(job["url_hash"])
                grouped[site].append(job)
            except (ValueError, TypeError, AttributeError) as exc:
                row_errors += 1
                if row_errors <= 5:
                    print(f"  Skipped invalid CSV row: {exc}")
    totals["invalid_rows"] += row_errors

    for site, jobs in grouped.items():
        source_name, base_url = SOURCE_INFO[site]
        if dry_run:
            print(f"  DRY RUN {source_name}: {len(jobs)} validated unique jobs; database unchanged")
            totals["validated"] += len(jobs)
            continue
        try:
            result = save_jobs(source_name, base_url, jobs, source_type="job_website")
            totals["validated"] += len(jobs)
            totals["inserted"] += int(result.get("inserted", 0))
            totals["updated"] += int(result.get("updated", 0))
            print(
                f"  DB saved {source_name}: found={result.get('found', 0)}, "
                f"inserted={result.get('inserted', 0)}, updated={result.get('updated', 0)}"
            )
        except Exception as exc:
            totals["db_errors"] += 1
            print(f"  DATABASE SAVE FAILED for {source_name}: {type(exc).__name__}: {exc}")


def main():
    parser = argparse.ArgumentParser(description="Collect Indeed + Naukri jobs and save directly to V4Career DB.")
    parser.add_argument("--minutes", type=float, default=5.0, help="Run budget (maximum 5 minutes; default 5)")
    parser.add_argument("--results-per-site", type=int, default=100, help="Requested results per site/search (default 100)")
    parser.add_argument("--output-dir", default=str(ROOT / "jobspy_results"), help="Directory for run CSVs")
    parser.add_argument("--roles", nargs="*", help="Optional role list")
    parser.add_argument("--locations", nargs="*", help="Optional location list")
    parser.add_argument("--hours-old", type=int, default=None, help="Optional posting-age filter in hours, if supported by installed JobSpy")
    parser.add_argument("--dry-run", action="store_true", help="Collect and validate without database writes")
    args = parser.parse_args()
    if not 0 < args.minutes <= 5:
        parser.error("--minutes must be greater than 0 and no more than 5")
    if not 1 <= args.results_per_site <= 1000:
        parser.error("--results-per-site must be between 1 and 1000")
    if args.hours_old is not None and args.hours_old < 1:
        parser.error("--hours-old must be at least 1")

    roles = args.roles or ROLES
    locations = args.locations or LOCATIONS
    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = out_dir / "completed_searches"
    temp_dir.mkdir(exist_ok=True)
    combinations = [(role, location) for location in locations for role in roles]
    deadline = time.monotonic() + args.minutes * 60
    ctx = mp.get_context("spawn")
    completed_files = []
    seen_hashes = defaultdict(set)
    totals = Counter()
    start = time.monotonic()
    interrupted = None

    print("Starting JobSpy: Indeed + Naukri")
    print(f"Time budget: {args.minutes:g} minutes | requested per site/search: {args.results_per_site}")
    print(f"Database mode: {'DRY RUN (no writes)' if args.dry_run else 'LIVE WRITE using V4Career .env database'}")
    print(f"Search combinations available: {len(combinations)}")

    for index, (role, location) in enumerate(combinations, start=1):
        remaining = deadline - time.monotonic()
        if remaining <= 2:
            break
        safe_role = "".join(c if c.isalnum() else "_" for c in role).strip("_")
        safe_location = "".join(c if c.isalnum() else "_" for c in location).strip("_")
        result_file = temp_dir / f"{index:03d}_{safe_role}_{safe_location}.csv"
        queue = ctx.Queue()
        process = ctx.Process(target=scrape_one, args=(role, location, args.results_per_site, args.hours_old, str(result_file), queue))
        query_started = time.monotonic()
        process.start()
        process.join(timeout=min(40.0, max(0, deadline - time.monotonic())))
        if process.is_alive():
            process.terminate()
            process.join(timeout=2)
            if deadline - time.monotonic() <= 2:
                interrupted = (role, location)
                print(f"Time limit reached while searching {role} | {location}.")
                break
            totals["timed_out_searches"] += 1
            print(f"[timeout] {role} | {location}; moving to next search")
            continue
        result = None
        try:
            if not queue.empty():
                result = queue.get_nowait()
        except Exception:
            pass
        finally:
            queue.close()
        elapsed = time.monotonic() - query_started
        if not result or not result.get("ok") or not result_file.exists():
            totals["failed_searches"] += 1
            print(f"[failed] {role} | {location}: {(result or {}).get('error', 'worker returned no result')}")
            continue
        completed_files.append(result_file)
        totals["completed_searches"] += 1
        totals["raw_rows"] += result.get("count", 0)
        print(f"[{totals['completed_searches']}] {role} | {location}: {result.get('count', 0)} raw rows in {elapsed:.1f}s")
        # Crucial: save each completed search immediately, so a later timeout does not lose prior results.
        save_completed_csv(result_file, args.dry_run, seen_hashes, totals)

    # Combined CSV is retained as an audit/export artifact, not required for DB saving.
    import pandas as pd
    frames = []
    for file_path in completed_files:
        try:
            frame = pd.read_csv(file_path)
            if not frame.empty:
                frames.append(frame)
        except Exception as exc:
            print(f"Warning: unable to read {file_path.name} for combined CSV: {exc}")
    combined_path = out_dir / "jobspy_combined_latest.csv"
    if frames:
        combined = pd.concat(frames, ignore_index=True)
        if "job_url" in combined.columns:
            combined = combined.drop_duplicates(subset=["job_url"], keep="first")
        combined.to_csv(combined_path, index=False, encoding="utf-8-sig")
        totals["combined_unique_rows"] = len(combined)
    else:
        combined_path.write_text("", encoding="utf-8")
        totals["combined_unique_rows"] = 0

    print("\n--- JOBSPY RUN SUMMARY ---")
    print(f"Elapsed seconds: {min(time.monotonic() - start, args.minutes * 60):.1f}")
    for key in ("completed_searches", "raw_rows", "combined_unique_rows", "validated", "inserted", "updated", "duplicates_in_run", "invalid_rows", "timed_out_searches", "failed_searches", "db_errors"):
        print(f"{key.replace('_', ' ').title()}: {totals.get(key, 0)}")
    print(f"Combined CSV: {combined_path}")
    if interrupted:
        print(f"Interrupted search at deadline: {interrupted[0]} | {interrupted[1]}")
    if args.dry_run:
        print("DRY RUN finished: no database writes were performed.")
    elif totals.get("db_errors", 0):
        print("WARNING: one or more database saves failed; see messages above.")
    else:
        print("Completed results were saved through V4Career's existing repository to the configured database.")


if __name__ == "__main__":
    mp.freeze_support()
    main()
