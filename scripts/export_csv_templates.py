#!/usr/bin/env python3
"""
Export current YAML data files into starter CSV files for Google Sheets.
Generates:
- data/starter_publications.csv
- data/starter_team.csv
- data/starter_patents.csv
"""

import csv
import os
import sys
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'starter_csv')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def export_publications():
    input_path = os.path.join(DATA_DIR, 'publications.yml')
    output_path = os.path.join(OUTPUT_DIR, 'starter_publications.csv')
    
    with open(input_path, 'r', encoding='utf-8') as f:
        pubs = yaml.safe_load(f)
    
    # Handle if root is list or dict
    if isinstance(pubs, dict):
        pubs = pubs.get('archive', [])
    
    fieldnames = [
        'year',
        'date',
        'title',
        'journal',
        'citations',
        'doi',
        'link',
        'lead',
        'tag',
        'authors',
        'display_authors'
    ]
    
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for p in pubs:
            row = {
                'year': p.get('year', ''),
                'date': p.get('date', ''),
                'title': p.get('title', ''),
                'journal': p.get('journal', ''),
                'citations': p.get('citations', 0),
                'doi': p.get('doi', ''),
                'link': p.get('link', ''),
                'lead': 'TRUE' if p.get('lead') is True else 'FALSE',
                'tag': p.get('tag', ''),
                'authors': p.get('authors', ''),
                'display_authors': p.get('display_authors', '')
            }
            writer.writerow(row)
    
    print(f"Exported {len(pubs)} publications -> {output_path}")

def export_team():
    input_path = os.path.join(DATA_DIR, 'team.yml')
    output_path = os.path.join(OUTPUT_DIR, 'starter_team.csv')
    
    with open(input_path, 'r', encoding='utf-8') as f:
        members = yaml.safe_load(f)
    
    if isinstance(members, dict):
        members = members.get('core', [])
        
    fieldnames = [
        'name',
        'role',
        'mini_bio',
        'bio',
        'orcid',
        'image',
        'img_position'
    ]
    
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for m in members:
            row = {
                'name': m.get('name', ''),
                'role': m.get('role', ''),
                'mini_bio': m.get('mini_bio', ''),
                'bio': m.get('bio', ''),
                'orcid': m.get('orcid', ''),
                'image': m.get('image', ''),
                'img_position': m.get('img_position', '50% 50%')
            }
            writer.writerow(row)
            
    print(f"Exported {len(members)} team members -> {output_path}")

def export_patents():
    input_path = os.path.join(DATA_DIR, 'patents.yml')
    output_path = os.path.join(OUTPUT_DIR, 'starter_patents.csv')
    
    with open(input_path, 'r', encoding='utf-8') as f:
        patents = yaml.safe_load(f)
        
    fieldnames = [
        'year',
        'title',
        'jurisdiction',
        'status',
        'link'
    ]
    
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for pat in patents:
            row = {
                'year': pat.get('year', ''),
                'title': pat.get('title', ''),
                'jurisdiction': pat.get('jurisdiction', ''),
                'status': pat.get('status', ''),
                'link': pat.get('link', '')
            }
            writer.writerow(row)
            
    print(f"Exported {len(patents)} patents -> {output_path}")

if __name__ == '__main__':
    export_publications()
    export_team()
    export_patents()
    print("All CSV templates successfully exported to data/ directory.")
