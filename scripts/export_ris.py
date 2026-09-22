#!/usr/bin/env python3
"""
Generate a standard RIS bibliography file directly from the canonical data/publications.yml and data/patents.yml.
Usage:
    python scripts/export_ris.py [--output proof_centre_publications.ris]
"""

import sys
import os
import re
import argparse
import yaml

def parse_family_given(author_str):
    s = str(author_str).strip().rstrip('.,;')
    if not s:
        return ""
    if s.lower().startswith('for the ') or 'consortium' in s.lower() or 'group' in s.lower() or 'team' in s.lower() or 'taskforce' in s.lower() or 'collaborators' in s.lower():
        return s
    if ',' in s:
        return s
        
    known_multiword_prefixes = [
        'le cao', 'lê cao', 'van eeden', 'de souza', 'wilson-mcmanus', 
        'sukma dewi', 'leitao filho', 'leitão filho', 'hernandez cordero', 
        'hernández cordero', 'bennike', 'bjerg bennike', 'van den berge',
        'van haren', 'van gool', 'de sanctis', 'ben-othman', 'van niewaal'
    ]
    
    s_lower = s.lower()
    for mw in known_multiword_prefixes:
        if s_lower.startswith(mw + ' '):
            fam = s[:len(mw)]
            giv = s[len(mw):].strip()
            return f"{fam}, {giv}"
            
    parts = s.split()
    if len(parts) == 1:
        return parts[0]
    
    fam = parts[0]
    giv = ' '.join(parts[1:])
    return f"{fam}, {giv}"

def main():
    parser = argparse.ArgumentParser(description="Export canonical publications to RIS format for Zotero")
    parser.add_argument('--output', '-o', default='proof_centre_publications.ris', help="Output RIS file path")
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    yaml_path = os.path.join(project_root, 'data', 'publications.yml')
    patents_path = os.path.join(project_root, 'data', 'patents.yml')

    if not os.path.exists(yaml_path):
        print(f"Error: Could not find {yaml_path}")
        sys.exit(1)

    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    if isinstance(data, dict):
        archive = data.get('archive', [])
    elif isinstance(data, list):
        archive = data
    else:
        archive = []
    print(f"Loaded {len(archive)} publications from data/publications.yml")

    records = []
    for idx, item in enumerate(archive, 1):
        year = str(item.get('year') or '')
        title = str(item.get('title') or '').strip()
        journal = str(item.get('journal') or '').strip()
        doi = str(item.get('doi') or '').strip()
        url = str(item.get('link') or '').strip()
        tag = str(item.get('tag') or '').strip()
        authors_raw = item.get('authors') or ''

        authors = []
        if isinstance(authors_raw, list):
            for a in authors_raw:
                if a:
                    authors.append(parse_family_given(a))
        elif isinstance(authors_raw, str):
            for a in re.split(r'[,;]\s*(?=[A-Z])|\sand\s', authors_raw):
                if a.strip() and len(a.strip()) > 1:
                    authors.append(parse_family_given(a.strip()))

        doc_type = 'JOUR'
        if tag == 'Book Chapter' or 'Handbook' in journal or 'Book' in journal or 'Chapter' in title or 'Chapter' in journal:
            doc_type = 'CHAP'
        elif tag == 'Preprint' or 'Preprint' in journal or 'bioRxiv' in journal or 'arXiv' in journal:
            doc_type = 'GEN'

        records.append({
            'id': f"PROOF_{year}_{idx:03d}",
            'type': doc_type,
            'title': title,
            'authors': authors,
            'journal': journal,
            'year': year,
            'doi': doi,
            'url': url,
            'tag': tag
        })

    # Load patents
    if os.path.exists(patents_path):
        with open(patents_path, 'r', encoding='utf-8') as f:
            patents = yaml.safe_load(f) or []
        for p_idx, p in enumerate(patents, 1):
            records.append({
                'id': f"PROOF_PAT_{p.get('year')}_{p_idx:02d}",
                'type': 'PAT',
                'title': str(p.get('title') or ''),
                'authors': ['PROOF Centre of Excellence'],
                'journal': str(p.get('status') or ''),
                'year': str(p.get('year') or ''),
                'doi': '',
                'url': str(p.get('link') or ''),
                'tag': 'Patent'
            })

    output_path = os.path.join(project_root, args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        for rec in records:
            f.write(f"TY  - {rec['type']}\n")
            f.write(f"ID  - {rec['id']}\n")
            f.write(f"TI  - {rec['title']}\n")
            f.write(f"T1  - {rec['title']}\n")
            for a in rec['authors']:
                if a:
                    f.write(f"AU  - {a}\n")
            if rec['journal']:
                if rec['type'] == 'PAT':
                    f.write(f"PB  - {rec['journal']}\n")
                elif rec['type'] == 'CHAP':
                    f.write(f"BT  - {rec['journal']}\n")
                else:
                    f.write(f"JO  - {rec['journal']}\n")
                    f.write(f"JF  - {rec['journal']}\n")
            if rec['year']:
                f.write(f"PY  - {rec['year']}\n")
                f.write(f"Y1  - {rec['year']}\n")
            if rec['doi']:
                f.write(f"DO  - {rec['doi']}\n")
            if rec['url']:
                f.write(f"UR  - {rec['url']}\n")
                f.write(f"L1  - {rec['url']}\n")
            if rec.get('tag'):
                f.write(f"KW  - {rec['tag']}\n")
            f.write("DB  - PROOF Centre of Excellence Publications\n")
            f.write("ER  - \n\n")

    print(f"Successfully exported {len(records)} records to {output_path}")

if __name__ == '__main__':
    main()
