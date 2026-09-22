import yaml
import urllib.request
import urllib.parse
import json
import time
import sys

def fetch_date_and_citations(doi, title, fallback_year):
    """Fetch exact publication_date and citation count from OpenAlex."""
    headers = {
        'User-Agent': 'PROOF-Centre/1.0 (mailto:info@proofcentre.ca)'
    }
    
    pub_date = None
    citations = None

    # 1. Try DOI lookup
    if doi:
        clean_doi = doi.strip()
        if clean_doi.startswith('http'):
            url = f"https://api.openalex.org/works/{clean_doi}?select=id,publication_date,cited_by_count"
        else:
            url = f"https://api.openalex.org/works/https://doi.org/{urllib.parse.quote(clean_doi)}?select=id,publication_date,cited_by_count"
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                pub_date = data.get('publication_date')
                citations = data.get('cited_by_count')
        except Exception:
            pass

    # 2. Try Title search fallback if not found
    if not pub_date and title:
        try:
            clean_title = urllib.parse.quote(title.strip())
            url = f"https://api.openalex.org/works?filter=title.search:{clean_title}&select=id,title,publication_date,cited_by_count&per-page=1"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                results = data.get('results', [])
                if results:
                    pub_date = results[0].get('publication_date')
                    citations = results[0].get('cited_by_count')
        except Exception:
            pass

    if not pub_date:
        pub_date = f"{fallback_year}-01-01"

    return pub_date, citations

def update_all_dates_and_citations(yaml_path='data/publications.yml'):
    print(f"Loading publications from {yaml_path}...")
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    pubs = data.get('archive', [])
    total = len(pubs)
    print(f"Updating full publication dates and citations for {total} entries...\n")

    for i, p in enumerate(pubs, 1):
        doi = p.get('doi', '')
        title = p.get('title', '')
        year = p.get('year', 2026)

        pub_date, citations = fetch_date_and_citations(doi, title, year)
        p['date'] = str(pub_date)
        if citations is not None:
            p['citations'] = int(citations)
        elif 'citations' not in p:
            p['citations'] = 0

        title_preview = (title[:40] + '...') if len(title) > 40 else title
        print(f"[{i:3d}/{total:3d}] Date: {p['date']} | Cites: {p['citations']:4d} | {title_preview}")
        sys.stdout.flush()
        
        # Rate limit
        time.sleep(0.08)

    # Also sort the archive list initially by date descending
    pubs.sort(key=lambda x: x.get('date', f"{x.get('year', 2000)}-01-01"), reverse=True)
    data['archive'] = pubs

    print("\nSaving updated publications.yml...")
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True, width=1000)

    print("Done! All publications updated and sorted chronologically by full date.")

if __name__ == '__main__':
    update_all_dates_and_citations()
