#!/usr/bin/env python3
"""
Sync live data from Google Sheets into local YAML fallback files:
- data/publications.yml
- data/team.yml
- data/patents.yml

Features:
- Validates and normalizes types (e.g. pillar '01'-'04', citations as int, lead as bool).
- Change detection: Compares incoming data with existing YAML; only writes when changes exist.
- Emits 'has_changes=true/false' to $GITHUB_OUTPUT for smart GitHub Actions conditional builds.
- Safe: Aborts cleanly without touching local files if Google Sheets is unreachable or empty.
"""

import csv
import io
import os
import sys
import urllib.request
import yaml

# Ensure multiline strings use YAML block scalar style (|)
def str_presenter(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_presenter, Dumper=yaml.SafeDumper)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Default Google Sheet ID for PROOF Centre Web Content
SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "1WabgRo9nsUT75jzaVqyDrfWLEXBrzX8CYhdTB2cT4o8")

def fetch_csv(tab_name):
    """Fetch CSV rows from Google Sheets export URL."""
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={tab_name}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (PROOF-Sync/1.0)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode("utf-8")
        reader = list(csv.reader(io.StringIO(content)))
        return reader
    except Exception as e:
        print(f"Error fetching '{tab_name}' from Google Sheets: {e}", file=sys.stderr)
        return None

def process_publications(rows):
    if not rows or len(rows) < 2:
        return None
    headers = [h.strip() for h in rows[0]]
    pubs = []
    for r in rows[1:]:
        if not any(cell.strip() for cell in r):
            continue
        d = {headers[i]: r[i].strip() for i in range(min(len(headers), len(r))) if headers[i]}
        if not d.get("title"):
            continue
        
        # Pillar normalization: supports '1'-'4' -> '01'-'04'
        raw_pillar = d.get("pillar", "").strip()
        pillar_val = ""
        if raw_pillar:
            try:
                p_int = int(raw_pillar)
                pillar_val = f"{p_int:02d}" if p_int > 0 else raw_pillar
            except ValueError:
                pillar_val = raw_pillar
        
        # Type casting
        try:
            year_val = int(d.get("year", 0))
        except (ValueError, TypeError):
            year_val = 0
            
        try:
            cit_val = int(d.get("citations", 0))
        except (ValueError, TypeError):
            cit_val = 0
            
        lead_val = d.get("lead", "").strip().lower() in ["true", "1", "yes"]
        
        item = {
            "year": year_val,
            "title": d.get("title", ""),
            "journal": d.get("journal", ""),
            "doi": d.get("doi", ""),
            "link": d.get("link", ""),
            "authors": d.get("authors", ""),
            "display_authors": d.get("display_authors", ""),
            "tag": d.get("tag", ""),
            "lead": lead_val,
            "citations": cit_val,
            "date": d.get("date", ""),
            "pillar": pillar_val
        }
        pubs.append(item)
    return pubs

def process_team(rows):
    if not rows or len(rows) < 2:
        return None
    headers = [h.strip() for h in rows[0]]
    team = []
    for r in rows[1:]:
        if not any(cell.strip() for cell in r):
            continue
        d = {headers[i]: r[i].strip() for i in range(min(len(headers), len(r))) if headers[i]}
        if not d.get("name"):
            continue
        item = {
            "name": d.get("name", ""),
            "role": d.get("role", ""),
            "mini_bio": d.get("mini_bio", ""),
            "bio": d.get("bio", ""),
            "orcid": d.get("orcid", ""),
            "image": d.get("image", ""),
            "img_position": d.get("img_position", "") or "50% 50%"
        }
        team.append(item)
    return team

def process_patents(rows):
    if not rows or len(rows) < 2:
        return None
    headers = [h.strip() for h in rows[0]]
    patents = []
    for r in rows[1:]:
        if not any(cell.strip() for cell in r):
            continue
        d = {headers[i]: r[i].strip() for i in range(min(len(headers), len(r))) if headers[i]}
        if not d.get("title"):
            continue
        try:
            year_val = int(d.get("year", 0))
        except (ValueError, TypeError):
            year_val = 0
        item = {
            "year": year_val,
            "title": d.get("title", ""),
            "jurisdiction": d.get("jurisdiction", ""),
            "status": d.get("status", ""),
            "link": d.get("link", "")
        }
        patents.append(item)
    return patents

def load_existing_yaml(filepath):
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: unable to load existing {filepath}: {e}", file=sys.stderr)
        return None

def write_yaml(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

def main():
    print(f"Connecting to Google Sheets (ID: {SHEET_ID})...")
    
    # 1. Fetch
    pub_rows = fetch_csv("Publications")
    team_rows = fetch_csv("Team")
    pat_rows = fetch_csv("Patents")
    
    if pub_rows is None or team_rows is None or pat_rows is None:
        print("Error: Failed to fetch one or more tabs from Google Sheets. Aborting sync.", file=sys.stderr)
        sys.exit(1)
        
    new_pubs = process_publications(pub_rows)
    new_team = process_team(team_rows)
    new_patents = process_patents(pat_rows)
    
    if new_pubs is None or len(new_pubs) == 0:
        print("Error: Parsed publications dataset is empty. Aborting sync.", file=sys.stderr)
        sys.exit(1)
    if new_team is None or len(new_team) == 0:
        print("Error: Parsed team dataset is empty. Aborting sync.", file=sys.stderr)
        sys.exit(1)
    if new_patents is None or len(new_patents) == 0:
        print("Error: Parsed patents dataset is empty. Aborting sync.", file=sys.stderr)
        sys.exit(1)
        
    # 2. Compare against existing data
    pubs_path = os.path.join(DATA_DIR, "publications.yml")
    team_path = os.path.join(DATA_DIR, "team.yml")
    patents_path = os.path.join(DATA_DIR, "patents.yml")
    
    old_pubs = load_existing_yaml(pubs_path)
    old_team = load_existing_yaml(team_path)
    old_patents = load_existing_yaml(patents_path)
    
    # Check if changes exist
    # Normalize comparison by stripping unused legacy fields (like original_bio) if present in old_team
    cleaned_old_team = None
    if old_team:
        cleaned_old_team = []
        for m in old_team:
            item = {
                "name": m.get("name", ""),
                "role": m.get("role", ""),
                "mini_bio": m.get("mini_bio", ""),
                "bio": m.get("bio", ""),
                "orcid": m.get("orcid", ""),
                "image": m.get("image", ""),
                "img_position": m.get("img_position", "") or "50% 50%"
            }
            cleaned_old_team.append(item)
    
    pubs_changed = (old_pubs != new_pubs)
    team_changed = (cleaned_old_team != new_team)
    patents_changed = (old_patents != new_patents)
    
    has_changes = pubs_changed or team_changed or patents_changed
    
    print(f"Publications: {len(new_pubs)} rows (Changed: {pubs_changed})")
    print(f"Team: {len(new_team)} members (Changed: {team_changed})")
    print(f"Patents: {len(new_patents)} patents (Changed: {patents_changed})")
    
    if has_changes:
        print("Detected updates in Google Sheets. Writing updated YAML files...")
        if pubs_changed:
            write_yaml(pubs_path, new_pubs)
            print(f"Updated {pubs_path}")
        if team_changed:
            write_yaml(team_path, new_team)
            print(f"Updated {team_path}")
        if patents_changed:
            write_yaml(patents_path, new_patents)
            print(f"Updated {patents_path}")
        print("Sync completed successfully with changes.")
    else:
        print("No changes detected between Google Sheets and local data/*.yml files.")
        
    # Output for GitHub Actions
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as gh_out:
            gh_out.write(f"has_changes={'true' if has_changes else 'false'}\n")
            gh_out.write(f"pubs_count={len(new_pubs)}\n")

if __name__ == "__main__":
    main()
