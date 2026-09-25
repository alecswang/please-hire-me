#!/usr/bin/env python3
"""List sweep: new postings from the curated job lists and VC portfolio boards in data/sources.md.

    python3 scripts/list_sweep.py            # since state/last_list_sweep.txt, then advance it
    python3 scripts/list_sweep.py --dry      # do not advance the cutoff or touch slug-candidates.txt
    python3 scripts/list_sweep.py --since 2026-09-20T00:00Z

Sources:
- SimplifyJobs New-Grad-Positions and Summer2027-Internships, via their machine-readable
  .github/scripts/listings.json (company, title, locations, sponsorship, degrees, terms, direct ATS url).
- VC portfolio boards on Consider (a16z, Sequoia, Lightspeed, Kleiner Perkins, GV, Bessemer), via the
  board's own search API (needs the page's CSRF token and cookie). Jobs carry minYearsExp and salary.
Not covered: Getro boards (General Catalyst, Khosla, Accel; the API returned nothing), YC Work at a Startup
and Wellfound (both need an account).

Every row links to the company's own ATS. Filters come from config/settings.json: targets.locations,
eligibility (sponsorship, start window), max_years_experience_required, the comp floors, skip_companies and
the interview tracker. The prestige gate stays with the agent: read each posting and judge it against
targets.prestige_note. Greenhouse/Ashby/Lever slugs seen here that no sweep knows yet are appended to
data/slug-candidates.txt, so delta_sweep.py reads those boards in full (comp, description) from then on.
Output: state/sweep/list_cands.json and tab-separated rows on stdout. Run in the FOREGROUND.
"""
import json, re, os, sys, ssl, time, datetime, subprocess, http.cookiejar, urllib.request, urllib.parse

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUT_FILE = os.path.join(R, 'state', 'last_list_sweep.txt')
OUT = os.path.join(R, 'state', 'sweep', 'list_cands.json')
SLUGS = os.path.join(R, 'data', 'slug-candidates.txt')
UTC = datetime.timezone.utc
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128 Safari/537.36'

SIMPLIFY = [('Simplify new-grad', 'SimplifyJobs/New-Grad-Positions'), ('Simplify intern', 'SimplifyJobs/Summer2027-Internships')]
CONSIDER = [  # (label, board host, board id)
    ('a16z', 'portfoliojobs.a16z.com', 'andreessen-horowitz'),
    ('Sequoia', 'jobs.sequoiacap.com', 'sequoia-capital'),
    ('Lightspeed', 'jobs.lsvp.com', 'lightspeed'),
    ('Kleiner Perkins', 'jobs.kleinerperkins.com', 'kleiner-perkins'),
    ('GV', 'jobs.gv.com', 'gv'),
    ('Bessemer', 'jobs.bvp.com', 'bessemer-ventures'),
]

S = json.load(open(os.path.join(R, 'config', 'settings.json')))
T, E = S['targets'], S['eligibility']
MAX_YEARS = T.get('max_years_experience_required', 1)
FLOOR = T.get('min_annual_comp_usd', 0)

BAD = re.compile(r'senior|\bsr\b|staff|principal|\blead\b|manager|director|head of|architect|\bII\b|\bIII\b|\bIV\b|sales|account exec|recruit|marketing|support|legal|counsel|finance|accountant|designer'
                 r'|solutions? engineer|value engineer|\bgtm\b|\bit engineer|customer|optical|electrical|solar|mechanical|hardware|design verification|\bpcb\b|\brf\b|ph\.?d|technician|test equipment|\[template\]', re.I)
SOFT = re.compile(r'software|developer|engineer|machine learning|\bml\b|\bai\b|research|quant|infrastructure|platform|backend|full.?stack|forward.?deployed', re.I)
LOC_RULES = {  # targets.locations entry -> pattern over a posting location
    'San Francisco Bay Area': r'San Francisco|\bSF\b|Bay Area|Palo Alto|Mountain View|Menlo Park|Redwood City|San Mateo|Sunnyvale|Santa Clara|San Jose|Oakland|Berkeley|Cupertino|Foster City|Emeryville|Burlingame|San Bruno',
    'New York': r'New York|\bNYC\b|Brooklyn|Manhattan',
    'Chicago': r'Chicago',
    'Seattle': r'Seattle|Bellevue|Redmond|Kirkland',
    'Remote (US)': r'Remote.{0,20}(US|U\.S\.|United States|USA)|(US|USA|United States).{0,5}Remote|^Remote$',
}
LOC = re.compile('|'.join(LOC_RULES[l] for l in T.get('locations', []) if l in LOC_RULES), re.I)

def parse_ts(s):
    try:
        d = datetime.datetime.fromisoformat(s.strip().replace('Z', '+00:00'))
        return d if d.tzinfo else d.replace(tzinfo=UTC)
    except Exception: return None

args = sys.argv[1:]; dry = '--dry' in args
since = args[args.index('--since') + 1] if '--since' in args else None
CUT = parse_ts(since) if since else (parse_ts(open(CUT_FILE).read()) if os.path.exists(CUT_FILE) else datetime.datetime.now(UTC) - datetime.timedelta(days=3))
if not CUT: sys.exit('bad cutoff')
START = datetime.datetime.now(UTC)

CTX = ssl.create_default_context(cafile='/etc/ssl/cert.pem') if os.path.exists('/etc/ssl/cert.pem') else ssl.create_default_context()
def fetch(u, data=None, headers=None, opener=None):
    req = urllib.request.Request(u, data=json.dumps(data).encode() if data is not None else None,
                                 headers={'User-Agent': UA, **({'Content-Type': 'application/json'} if data is not None else {}), **(headers or {})})
    try:
        with (opener.open(req, timeout=30) if opener else urllib.request.urlopen(req, timeout=30, context=CTX)) as r:
            return r.read().decode('utf-8', 'ignore')
    except Exception as e:
        print(f'  ! {type(e).__name__} on {u[:80]}', file=sys.stderr); return ''

# ---- companies that are never a target ----
def norm(c): return re.sub(r'[^a-z0-9]', '', (c or '').lower())
blocked = {norm(c) for c in T.get('skip_companies', [])}
try:
    tr = subprocess.run([sys.executable, os.path.join(R, 'scripts', 'tracker_companies.py')], capture_output=True, text=True, timeout=60)
    blocked |= {norm(l) for l in tr.stdout.splitlines() if l.strip()}
except Exception: pass
def is_blocked(company):
    n = norm(company)
    return any(b and (n == b or n.startswith(b) or b.startswith(n)) for b in blocked)

# ---- internship terms vs. the start window (Winter/Spring start in January, Summer in May, Fall in August) ----
SEASON = {'winter': 1, 'spring': 1, 'summer': 5, 'fall': 8, 'autumn': 8}
def ym(s):
    m = re.match(r'(\d{4})-(\d{2})', s or ''); return (int(m.group(1)), int(m.group(2))) if m else None
WIN = (ym(E.get('earliest_start')), ym(E.get('latest_start')))
def title_term_ok(t):
    """A season named in the title ('Summer 2027') must fall inside the start window too."""
    m = re.search(r'(winter|spring|summer|fall|autumn)\s*(\d{4})', t or '', re.I)
    return term_ok([m.group(0)]) if m else True
def term_ok(terms):
    if not terms or not all(WIN): return True
    for t in terms:
        m = re.search(r'(winter|spring|summer|fall|autumn)\s*(\d{4})', t, re.I)
        if not m: return True  # "N/A", "Off-cycle" or unparsed: let the agent read it
        if WIN[0] <= (int(m.group(2)), SEASON[m.group(1).lower()]) <= WIN[1]: return True
    return False

rows, slugs_seen = [], set()
ATS_SLUG = re.compile(r'(?:job-boards|boards)(?:\.eu)?\.greenhouse\.io/([A-Za-z0-9_-]+)|jobs\.ashbyhq\.com/([A-Za-z0-9._-]+)|jobs\.lever\.co/([A-Za-z0-9._-]+)')
def harvest(url):
    m = ATS_SLUG.search(url or '')
    if m: slugs_seen.add(next(g for g in m.groups() if g))
def clean(url): return re.sub(r'[?&](utm_[^&]+|lever-source[^&]*|gh_src=[^&]+|ref=[^&]+)', '', url or '').rstrip('?&')

# ---- SimplifyJobs listings.json ----
for label, repo in SIMPLIFY:
    try: listings = json.loads(fetch(f'https://raw.githubusercontent.com/{repo}/dev/.github/scripts/listings.json') or '[]')
    except Exception: listings = []
    if not listings: print(f'  ! {label}: empty feed', file=sys.stderr)
    for x in listings:
        if not x.get('active') or not x.get('is_visible', True): continue
        posted = datetime.datetime.fromtimestamp(x.get('date_posted', 0), UTC)
        if posted < CUT: continue
        url, t, co, locs = x.get('url', ''), x.get('title', ''), x.get('company_name', ''), '; '.join(x.get('locations') or [])
        harvest(url)
        sp = x.get('sponsorship', '') or ''
        if E.get('needs_visa_sponsorship') and re.search(r'does not offer|citizenship', sp, re.I): continue
        if not E.get('us_person_only_roles_ok', True) and re.search(r'citizenship', sp, re.I): continue
        degrees = x.get('degrees') or []
        if degrees and not any('bachelor' in d.lower() for d in degrees): continue
        if not SOFT.search(t) or BAD.search(t) or not LOC.search(locs) or is_blocked(co): continue
        if ('intern' in label and not term_ok(x.get('terms'))) or not title_term_ok(t): continue
        # Simplify marks ~all rows "Other"; only its explicit values carry information.
        rows.append([label, co, posted.isoformat()[:10], t, locs[:80], '' if sp == 'Other' else sp, '', clean(url)])

# ---- Consider VC boards ----
for label, host, board in CONSIDER:
    jar = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar), urllib.request.HTTPSHandler(context=CTX))
    page = fetch(f'https://{host}/jobs', opener=op)
    tok = re.search(r'"csrfToken":"([^"]+)"', page)
    if not tok: print(f'  ! {label}: no CSRF token', file=sys.stderr); continue
    seq, pages = None, 0
    while pages < 20:
        body = {'meta': {'size': 100, **({'sequence': seq} if seq else {})}, 'board': {'id': board, 'isParent': True}, 'query': {}, 'grouped': False}
        raw = fetch(f'https://{host}/api-boards/search-jobs', body, {'x-csrf-token': tok.group(1)}, op)
        try: d = json.loads(raw)
        except Exception: break
        jobs = d.get('jobs') or []
        if not jobs: break
        old = 0
        for j in jobs:
            posted = parse_ts(j.get('timeStamp', ''))
            if not posted or posted < CUT: old += 1; continue
            url, t, co = j.get('applyUrl') or j.get('url', ''), j.get('title', ''), j.get('companyName', '')
            harvest(url)
            locs = '; '.join(j.get('locations') or [])
            if j.get('remote') and re.search(r'United States|\bUSA?\b|North America', json.dumps([j.get('regions'), j.get('normalizedLocations')])):
                locs += '; Remote (US)'
            yrs = j.get('minYearsExp')
            sal = j.get('salary') or {}
            mx = sal.get('maxValue') if (sal.get('period') or {}).get('value') == 'year' else None
            if yrs is not None and yrs > MAX_YEARS: continue
            if not SOFT.search(t) or BAD.search(t) or not LOC.search(locs) or is_blocked(co) or not title_term_ok(t): continue
            if mx and FLOOR and mx < FLOOR and not re.search(r'intern', t, re.I): continue
            band = f"${sal.get('minValue', 0) // 1000}K-${mx // 1000}K" if mx else ''
            rows.append([label, co, posted.isoformat()[:10], t, locs[:80], '', band, clean(url)])
        if old == len(jobs): break  # a whole page older than the cutoff: done
        seq = (d.get('meta') or {}).get('sequence'); pages += 1
        if not seq: break
        time.sleep(1)

# ---- de-duplicate (the same req often sits on several lists), newest first ----
seen, uniq = set(), []
for r in sorted(rows, key=lambda r: r[2], reverse=True):
    k = r[7].split('?')[0].rstrip('/').lower()
    if k in seen: continue
    seen.add(k); uniq.append(r)

# ---- new ATS slugs feed delta_sweep.py ----
known = set()
for f in (SLUGS, os.path.join(R, 'data', 'boards.md')):
    try: known |= set(re.findall(r'[A-Za-z0-9._-]+', open(f).read()))
    except Exception: pass
new_slugs = sorted(s for s in slugs_seen if s not in known)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(uniq, open(OUT, 'w'))
print(f'cutoff {CUT.isoformat()[:16]}Z  candidates {len(uniq)}  new ATS slugs {len(new_slugs)}  '
      f'(columns: source, company, posted, title, location, sponsorship, band, url)')
print('--- JUDGE EACH AGAINST targets.prestige_note, THEN APPLY THE USUAL DUPLICATE AND ELIGIBILITY CHECKS:')
for r in uniq: print('\t'.join(r))
if not dry:
    if new_slugs:
        with open(SLUGS, 'a') as f: f.write('\n'.join(new_slugs) + '\n')
    open(CUT_FILE, 'w').write(START.isoformat(timespec='minutes').replace('+00:00', 'Z') + '\n')
