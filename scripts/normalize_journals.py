import yaml

with open('data/publications.yml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

# Explicit canonical Title Case mappings for journals with special casing or acronyms
CANONICAL_JOURNALS = {
    # Lowercase fixes
    'the new england journal of medicine': 'The New England Journal of Medicine',
    'the canadian journal of cardiology': 'The Canadian Journal of Cardiology',
    'canadian journal of cardiology': 'Canadian Journal of Cardiology',
    'kidney international': 'Kidney International',
    'european journal of heart failure': 'European Journal of Heart Failure',
    'clinics in laboratory medicine': 'Clinics in Laboratory Medicine',
    'environmental health perspectives': 'Environmental Health Perspectives',
    'frontiers in cellular and infection microbiology': 'Frontiers in Cellular and Infection Microbiology',
    'blood. red cells & iron': 'Blood: Red Cells & Iron',
    
    # Acronym and capitalization standardization
    'bmc bioinformatics': 'BMC Bioinformatics',
    'jhlt open': 'JHLT Open',
    'plos one': 'PLOS ONE',
    'plos computational biology': 'PLOS Computational Biology',
    'chest': 'CHEST',
    'ebiomedicine': 'eBioMedicine',
    'eclinicalmedicine': 'eClinicalMedicine',
    'arxiv [cs.lg]': 'arXiv [cs.LG]',
    'openrxiv': 'openRxiv',
    'mbio': 'mBio',
    'imeta': 'iMeta',
    'iscience': 'iScience',
    
    # HTML entities
    'allergy, asthma &amp; clinical immunology': 'Allergy, Asthma & Clinical Immunology',
    'molecular &amp; cellular proteomics': 'Molecular & Cellular Proteomics',
    'nicotine &amp; tobacco research': 'Nicotine & Tobacco Research',
    'proteomics – clinical applications': 'Proteomics – Clinical Applications',
}

LOWERCASE_WORDS = {'and', 'of', 'in', 'for', 'the', 'a', 'an', 'to', 'at', 'by', 'with', 'from', 'as'}

def clean_journal(name):
    if not name:
        return name
    raw = name.strip().replace('&amp;', '&')
    k = raw.lower()
    if k in CANONICAL_JOURNALS:
        return CANONICAL_JOURNALS[k]
    
    # Otherwise standard title case while preserving acronyms
    words = raw.split(' ')
    result = []
    for i, w in enumerate(words):
        # If after a colon (e.g. "Title: A Subtitle"), capitalize
        prev_has_colon = (i > 0 and words[i-1].endswith(':'))
        lw = w.lower()
        if w.isupper() and len(w) > 1:
            result.append(w)
        elif i > 0 and lw in LOWERCASE_WORDS and not prev_has_colon:
            result.append(lw)
        else:
            result.append(w.capitalize())
    return ' '.join(result)

count = 0
for section in ['highlighted', 'archive']:
    for p in data.get(section, []):
        old_j = p.get('journal', '')
        new_j = clean_journal(old_j)
        if old_j != new_j:
            p['journal'] = new_j
            count += 1

print(f"Updated {count} publication records to canonical Title Case.")

with open('data/publications.yml', 'w', encoding='utf-8') as f:
    yaml.dump(data, f, sort_keys=False, allow_unicode=True, width=1000)

print("Saved clean data/publications.yml!")
