#!/usr/bin/env python3
"""Title banding regression test — no data, no network.

Every case is a title the rubric's Layer 1P *Title* and Layer 1I *Title/persona* bands
have an answer for. Substring matching used to put several of these in the wrong band,
so they are pinned here: change a band deliberately, or this fails.
"""
import importlib.util, os, sys

spec = importlib.util.spec_from_file_location(
    "scorer", os.path.join(os.path.dirname(__file__), '..', 'scorer', 'TG-score-batch.py'))
m = importlib.util.module_from_spec(spec)
sys.argv = ['title-bands']
try: spec.loader.exec_module(m)
except SystemExit: pass

CASES = [
    # founder / owner — the proven buyer
    ("Chief Executive Officer", 12, 10), ("Founder & CEO", 12, 10), ("Co-Founder", 12, 10),
    ("Owner", 12, 10), ("Business Owner", 12, 10), ("Managing Partner", 12, 10),
    ("Chairman", 12, 10), ("Proprietor", 12, 10),
    # a Product/Process Owner owns a deliverable, not the business
    ("Product Owner", 3, 3), ("Scrum Product Owner", 3, 3),
    # CRO and the sales-leader titles the rubric maps onto VP Sales
    ("Chief Revenue Officer", 4, 10), ("CRO", 4, 10),
    ("Vice President of Sales", 4, 10), ("VP, Sales", 4, 10), ("VP Sales", 4, 10),
    ("SVP, Revenue", 4, 10), ("Managing Director, Sales", 4, 10), ("Head of Sales", 4, 10),
    # Head of Revenue / GTM sits above CRO on Proven-Fit
    ("Head of Revenue", 6, 9), ("Head of GTM", 6, 9), ("Chief Growth Officer", 6, 9),
    # President and COO — but never "Vice President"
    ("President", 9, 8), ("COO", 9, 8), ("Chief Operating Officer", 9, 8),
    ("Vice President, Marketing", 3, 3),
    # "coordinator" contains "coo"
    ("Sales Coordinator", 3, 3),
    # sales leadership below VP
    ("Director of Sales", 3, 4), ("Sales Manager", 3, 4), ("Regional Sales Manager", 3, 4),
    # ambiguous by nature — bare MD is not assumed to be a CEO; override per run if needed
    ("Managing Director", 3, 3),
    ("Chief Information Officer", 3, 3), ("", 3, 3),
]

bad = []
for t, wp, wi in CASES:
    band, gp, gi = m.title_band(t)
    if (gp, gi) != (wp, wi):
        bad.append('  %-30s band=%-16s got %d/%d, expected %d/%d' % (repr(t), band, gp, gi, wp, wi))
if bad:
    print('TITLE BANDS FAILED (%d of %d):' % (len(bad), len(CASES)))
    print('\n'.join(bad)); sys.exit(1)
print('title bands: %d/%d correct' % (len(CASES), len(CASES)))
