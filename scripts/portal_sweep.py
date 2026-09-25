#!/usr/bin/env python3
"""Portal sweep: new-grad software postings on account-gated career portals (no login needed to LIST).

    python3 scripts/portal_sweep.py            # since state/last_portal_sweep.txt, then advance it
    python3 scripts/portal_sweep.py --dry      # do not advance the cutoff
    python3 scripts/portal_sweep.py --since 2026-09-10T00:00Z

Covers: Amazon (search API), the Workday tenants in WORKDAY (Nvidia, Salesforce, Intel, Arrowstreet,
G-Research), Google Careers (HTML cards), D. E. Shaw (campus JSON), Two Sigma and Bloomberg (Avature HTML),
Microsoft and Qualcomm (Eightfold pcsx API), Netflix and Millennium (Eightfold v2 API), AMD (careers.amd.com
API, applies via iCIMS), Uber (Oracle Recruiting REST), Apple (student-team search HTML) and Renaissance
(static page). Portals without a posting date use seen-ids, so their first run lists everything.
Not covered, check in the browser: Meta, Tesla, Citadel, Citadel Securities (scripts get "Access Denied" or
a JS shell) and Balyasny (Salesforce site). The agent never creates an account. A row is the agent's when its
host is in config/settings.json -> channels.signed_in_portals (the user signed in) or in OPEN_PORTALS (no account
needed); every other row is printed under "FOR YOU, BY HAND" for the run summary.
Output: state/sweep/portal_cands.json and tab-separated rows on stdout. Run in the FOREGROUND.
"""
import json, re, os, sys, ssl, time, datetime, urllib.request, urllib.parse

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUT_FILE = os.path.join(R, 'state', 'last_portal_sweep.txt')
OUT = os.path.join(R, 'state', 'sweep', 'portal_cands.json')
UTC = datetime.timezone.utc

WORKDAY = [  # (label, tenant, wd-host, site, host for signed_in_portals)
    ('Nvidia', 'nvidia', 'wd5', 'NVIDIAExternalCareerSite', 'nvidia.wd5.myworkdayjobs.com'),
    ('Salesforce', 'salesforce', 'wd12', 'External_Career_Site', 'salesforce.wd12.myworkdayjobs.com'),
    ('Intel', 'intel', 'wd1', 'External', 'intel.wd1.myworkdayjobs.com'),
    ('Arrowstreet', 'arrowstreetcapital', 'wd5', 'Campus_Careers', 'arrowstreetcapital.wd5.myworkdayjobs.com'),
    ('G-Research', 'gresearch', 'wd103', 'G-Research', 'gresearch.wd103.myworkdayjobs.com'),
]
# Portals whose apply form needs NO account (checked 2026-09-24, data/manual-portals.md): rows here are the
# agent's to apply to, same as a signed-in portal.
OPEN_PORTALS = {'www.deshaw.com', 'explore.jobs.netflix.net', 'career.mlp.com', 'jobs.uber.com', 'www.rentec.com'}
AMAZON_QUERIES = ['software development engineer', 'software engineer university', 'sde 2027']
WORKDAY_QUERIES = ['new college grad software', 'new college graduate software engineer', 'software engineer intern 2027']

NEWGRAD = re.compile(r'\b(I|1)\b|university|grad|2027|entry|early career|campus|new college|intern', re.I)
BAD = re.compile(r'senior|\bsr\b|principal|\blead\b|manager|director|architect|\bII\b|\bIII\b|hardware|asic|fpga|verification|\bqa\b|quality assurance|test engineer|sales|support', re.I)
SOFT = re.compile(r'software|developer|engineer|machine learning|\bml\b|\bai\b', re.I)
US = re.compile(r'\bUS\b|United States|, (WA|CA|NY|IL|TX|MA|VA|AZ|CO)\b', re.I)

def parse_ts(s):
    try:
        d = datetime.datetime.fromisoformat(s.strip().replace('Z', '+00:00'))
        return d if d.tzinfo else d.replace(tzinfo=UTC)
    except Exception: return None

args = sys.argv[1:]; dry = '--dry' in args
since = args[args.index('--since') + 1] if '--since' in args else None
CUT = parse_ts(since) if since else (parse_ts(open(CUT_FILE).read()) if os.path.exists(CUT_FILE) else datetime.datetime.now(UTC) - datetime.timedelta(days=7))
if not CUT: sys.exit('bad cutoff')
START = datetime.datetime.now(UTC)

def _ctx():
    for cafile in ['/etc/ssl/cert.pem']:
        if os.path.exists(cafile): return ssl.create_default_context(cafile=cafile)
    return ssl.create_default_context()
CTX = _ctx()

def get(u, data=None, retry=True):
    req = urllib.request.Request(u, data=json.dumps(data).encode() if data is not None else None,
                                 headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json', 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=25, context=CTX) as r: return json.load(r)
    except urllib.error.HTTPError as e:
        if retry and (e.code == 429 or e.code >= 500):  # Eightfold rate-limits bursts; one slow retry clears it
            time.sleep(5); return get(u, data, retry=False)
        print(f'  ! HTTPError {e.code} on {u[:80]}', file=sys.stderr); return None
    except Exception as e:
        print(f'  ! {type(e).__name__} on {u[:80]}', file=sys.stderr); return None

SEEN_FILE = os.path.join(R, 'state', 'sweep', 'portal_seen.json')
try: SEEN = json.load(open(SEEN_FILE))
except Exception: SEEN = {}
def get_text(u):
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128 Safari/537.36'})
    try:
        with urllib.request.urlopen(req, timeout=25, context=CTX) as r: return r.read().decode('utf-8', 'ignore')
    except Exception as e:
        print(f'  ! {type(e).__name__} on {u[:80]}', file=sys.stderr); return ''
def new_id(portal, jid):
    """Portals with no posting date: a row is new if its id was not seen before. Updated on a non-dry run."""
    s = SEEN.setdefault(portal, [])
    if jid in s: return False
    s.append(jid); return True

try:
    signed = set(json.load(open(os.path.join(R, 'config', 'settings.json'))).get('channels', {}).get('signed_in_portals', []))
except Exception: signed = set()

rows = []  # [portal, host, posted, title, location, url]

# ---- Amazon ----
seen = set()
for q in AMAZON_QUERIES:
    for offset in (0, 100, 200):
        u = ('https://www.amazon.jobs/en/search.json?' + urllib.parse.urlencode({'base_query': q, 'country[]': 'USA',
             'result_limit': 100, 'offset': offset, 'sort': 'recent', 'category[]': 'software-development'}))
        d = get(u)
        if not d or not d.get('jobs'): break
        stop = False
        for j in d['jobs']:
            try: posted = datetime.datetime.strptime(j.get('posted_date', ''), '%B %d, %Y').replace(tzinfo=UTC)
            except Exception: continue
            if posted < CUT: stop = True; continue
            if j['id_icims'] in seen: continue
            seen.add(j['id_icims'])
            t = j.get('title', '')
            if NEWGRAD.search(t) and not BAD.search(t) and US.search(j.get('location', '') or ''):
                rows.append(['Amazon', 'amazon.jobs', posted.isoformat()[:10], t, j.get('location', ''), 'https://www.amazon.jobs' + j.get('job_path', '')])
        if stop: break
        time.sleep(1)

# ---- Workday tenants ----
REL = re.compile(r'Posted (Today|Yesterday|(\d+)\+? Days? Ago)', re.I)
def wd_date(s):
    m = REL.search(s or '')
    if not m: return None
    if m.group(1).lower() == 'today': days = 0
    elif m.group(1).lower() == 'yesterday': days = 1
    else: days = int(m.group(2))
    return START - datetime.timedelta(days=days)
for label, tenant, wd, site, host in WORKDAY:
    seen = set()
    for q in WORKDAY_QUERIES:
        for offset in (0, 20, 40):
            d = get(f'https://{tenant}.{wd}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs', {'appliedFacets': {}, 'limit': 20, 'offset': offset, 'searchText': q})
            if not d or not d.get('jobPostings'): break
            for j in d['jobPostings']:
                posted = wd_date(j.get('postedOn'))
                if not posted or posted < CUT: continue
                path = j.get('externalPath', '')
                if path in seen: continue
                seen.add(path)
                t = j.get('title', ''); loc = j.get('locationsText', '') or ''
                # 'N Locations' hides the list; the primary location leads the path (/job/US-CA-... vs /job/China-...).
                if NEWGRAD.search(t) and not BAD.search(t) and SOFT.search(t) and (US.search(loc) or ('Locations' in loc and path.startswith('/job/US'))):
                    rows.append([label, host, posted.isoformat()[:10], t, loc, f'https://{tenant}.{wd}.myworkdayjobs.com/en-US/{site}{path}'])
            time.sleep(1)

# ---- Google Careers (listings embedded in the HTML; no date, so seen-ids) ----
import html as _html
GOOGLE_QUERIES = ['"software engineer" "university graduate"', '"software engineer" "early career"', '"software engineer" "new grad"']
for q in GOOGLE_QUERIES:
    u = 'https://www.google.com/about/careers/applications/jobs/results/?' + urllib.parse.urlencode({'q': q, 'location': 'United States', 'sort_by': 'date'})
    page = get_text(u)
    for c in re.split(r'<li class="lLd3Je"', page)[1:]:
        jid = re.search(r"ssk='\d+:(\d+)'", c); title = re.search(r'<h3 class="QJPWVe">([^<]+)</h3>', c)
        if not jid or not title: continue
        tt = _html.unescape(title.group(1)); loc = '; '.join(_html.unescape(re.sub(r'<[^>]+>', '', s)) for s in re.findall(r'<span class="r0wTof">(.*?)</span>', c))
        if NEWGRAD.search(tt) and not BAD.search(tt) and new_id('google', jid.group(1)):
            rows.append(['Google', 'www.google.com', 'new', tt, loc or 'United States', f'https://www.google.com/about/careers/applications/jobs/results/{jid.group(1)}'])
    time.sleep(1)

# ---- D. E. Shaw campus page (positions embedded as JSON; no date, so seen-ids; own form, no account) ----
page = get_text('https://www.deshaw.com/careers/choose-your-path/campus-candidates')
for m in re.finditer(r'"id":(\d+),"displayName":"([^"]+)","jobUrl":"([^"]+)"', page):
    jid, tt, slug = m.group(1), _html.unescape(m.group(2)), m.group(3)
    tail = page[m.end():m.end() + 6000]
    offices = ', '.join(re.findall(r'"name":"([^"]+)"', tail.split('"header"')[0])) if '"office"' in tail else ''
    # The campus page embeds EVERY position. Campus-track ones carry "Student" in jobSeekerCategoriesString.
    nxt = tail.find('"displayName"'); seg = tail[:nxt] if nxt > 0 else tail
    js = re.search(r'"jobSeekerCategoriesString":"([^"]*)"', seg)
    campus = bool(js and 'Student' in js.group(1))
    if campus and re.search(r'software|developer|engineer', tt, re.I) and not re.search(r'intern|ph\.?d|senior|lead|london|all positions', tt, re.I) and (not offices or 'New York' in offices):
        if new_id('deshaw', jid):
            rows.append(['D. E. Shaw', 'www.deshaw.com', 'new', tt, offices or 'New York', f'https://www.deshaw.com/careers/{slug.lower()}'])

# ---- Two Sigma (Avature portal; early-careers page lists JobDetail links; no date, seen-ids) ----
page = get_text('https://careers.twosigma.com/careers/InternshipsAndEarlyCareers')
for u, slug, jid in sorted(set(re.findall(r'href="(https://careers\.twosigma\.com/careers/JobDetail/([^"/]+)/(\d+))"', page))):
    tt = slug.replace('-', ' ')
    if re.search(r'software|engineer|developer', tt, re.I) and not re.search(r'intern|hardware|ph ?d', tt, re.I) and re.search(r'united states', tt, re.I):
        if new_id('twosigma', jid):
            rows.append(['Two Sigma', 'careers.twosigma.com', 'new', tt, 'see title', u])

US_STATES = re.compile(r'United States|\bUSA?\b|California|Washington|New York|Texas|Massachusetts|Illinois|Oregon|Colorado|Georgia|North Carolina|Virginia|Arizona|Florida|Remote', re.I)
def keep(t, loc):
    return NEWGRAD.search(t) and not BAD.search(t) and SOFT.search(t) and (US.search(loc or '') or US_STATES.search(loc or ''))
def ts_date(ts):
    try: return datetime.datetime.fromtimestamp(int(ts), UTC)
    except Exception: return None

# ---- Eightfold, newer pcsx API (Microsoft, Qualcomm; both need the signed-in account to apply) ----
for label, host, domain in [('Microsoft', 'apply.careers.microsoft.com', 'microsoft.com'), ('Qualcomm', 'careers.qualcomm.com', 'qualcomm.com')]:
    # Relevance order, not timestamp: sorted by timestamp the API ignores the query words.
    for q in ['university', 'intern', 'college graduate', 'new grad']:
        d = get(f'https://{host}/api/pcsx/search?' + urllib.parse.urlencode({'domain': domain, 'query': q, 'location': 'United States', 'start': 0}))
        for p in ((d or {}).get('data') or {}).get('positions') or []:
            posted = ts_date(p.get('postedTs')); loc = '; '.join(p.get('locations') or [])
            if posted and posted >= CUT and keep(p.get('name', ''), loc) and new_id(label.lower(), str(p['id'])):
                rows.append([label, host, posted.isoformat()[:10], p['name'].lstrip('#'), loc, f"https://{host}{p.get('positionUrl') or '/careers/job/' + str(p['id'])}"])
        time.sleep(3)

# ---- Eightfold, v2 API (Netflix, Millennium; no account) ----
for label, host, domain in [('Netflix', 'explore.jobs.netflix.net', 'netflix.com'), ('Millennium', 'career.mlp.com', 'mlp.com')]:
    d = get(f'https://{host}/api/apply/v2/jobs?' + urllib.parse.urlencode({'domain': domain, 'query': 'software engineer', 'location': 'United States', 'num': 100, 'sort_by': 'timestamp'}))
    for p in (d or {}).get('positions') or []:
        posted = ts_date(p.get('t_create')); t = p.get('name', ''); loc = p.get('location', '')
        # Millennium titles rarely say "grad"; keep its non-senior software roles for the agent to vet.
        ok = keep(t, loc) if label == 'Netflix' else (re.search(r'software|developer', t, re.I) and not BAD.search(t) and US.search(loc))
        if posted and posted >= CUT and ok and new_id(label.lower(), str(p['id'])):
            rows.append([label, host, posted.isoformat()[:10], t, loc, f'https://{host}/careers/apply?pid={p["id"]}&domain={domain}'])

# ---- AMD (careers.amd.com search API, dated; applying goes through iCIMS, signed in) ----
for q in ['software engineer new college grad', 'software engineer intern', 'software engineer university']:
    d = get('https://careers.amd.com/api/jobs?' + urllib.parse.urlencode({'keywords': q, 'location': 'United States', 'limit': 50, 'sortBy': 'posted_date', 'descending': 'true'}))
    for j in (d or {}).get('jobs') or []:
        j = j.get('data', {}); posted = parse_ts(re.sub(r'([+-]\d\d)(\d\d)$', r'\1:\2', j.get('posted_date', '') or ''))  # '+0000' -> '+00:00' for py3.9
        if posted and posted >= CUT and keep(j.get('title', ''), j.get('full_location', '')) and new_id('amd', str(j.get('req_id'))):
            rows.append(['AMD', 'careers-amd.icims.com', posted.isoformat()[:10], j['title'], j.get('full_location', ''), f"https://careers.amd.com/careers-home/jobs/{j['req_id']}"])
    time.sleep(1)

# ---- Uber (Oracle Recruiting Cloud REST, dated; no account) ----
for q in ['software engineer', 'new grad', 'intern']:
    u = ('https://iaziqy.fa.ocs.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList'
         f'&finder=findReqs;siteNumber=UberCareers,keyword=%22{urllib.parse.quote(q)}%22,limit=50,sortBy=POSTING_DATES_DESC')
    d = get(u)
    for x in (((d or {}).get('items') or [{}])[0].get('requisitionList') or []):
        posted = parse_ts((x.get('PostedDate') or '') + 'T00:00:00Z')
        if posted and posted >= CUT and keep(x.get('Title', ''), x.get('PrimaryLocation', '')) and new_id('uber', str(x['Id'])):
            rows.append(['Uber', 'jobs.uber.com', posted.isoformat()[:10], x['Title'], x.get('PrimaryLocation', ''), f"https://jobs.uber.com/en/jobs/{x['Id']}/"])
    time.sleep(1)

# ---- Apple (search page HTML carries details/<id>/<slug> links; no date, seen-ids; Apple ID signed in) ----
# The page ignores free-text search when fetched without JS, so filter by the student team instead.
for team in ['internships-STDNT-INTRN']:
    page = get_text('https://jobs.apple.com/en-us/search?' + urllib.parse.urlencode({'team': team, 'sort': 'newest', 'location': 'united-states-USA'}))
    for jid, slug in sorted(set(re.findall(r'details/([0-9A-Z-]+)/([a-z0-9-]+)', page))):
        tt = slug.replace('-', ' ')
        if NEWGRAD.search(tt) and not BAD.search(tt) and SOFT.search(tt) and new_id('apple', jid):
            rows.append(['Apple', 'jobs.apple.com', 'new', tt, 'United States', f'https://jobs.apple.com/en-us/details/{jid}/{slug}'])
    time.sleep(1)

# ---- Bloomberg (Avature search HTML; no date, seen-ids; signed in) ----
for q in ['software engineer', 'internship', '2027']:
    page = get_text('https://bloomberg.avature.net/careers/SearchJobs/' + urllib.parse.quote(q) + '?listFilterMode=1&jobRecordsPerPage=50')
    for slug, jid in sorted(set(re.findall(r'JobDetail/([^"/?]+)/(\d+)', page))):
        tt = slug.replace('-', ' ')
        if NEWGRAD.search(tt) and not BAD.search(tt) and SOFT.search(tt) and not re.search(r'london|singapore|tokyo|hong kong|frankfurt', tt, re.I) and new_id('bloomberg', jid):
            rows.append(['Bloomberg', 'bloomberg.avature.net', 'new', tt, 'see posting', f'https://bloomberg.avature.net/careers/JobDetail/{slug}/{jid}'])
    time.sleep(1)

# ---- Renaissance (one static page of positions; no date, seen-ids; no account). Titles never say "grad". ----
page = get_text('https://www.rentec.com/Careers.action?jobs=true')
for pos in sorted(set(re.findall(r'selectedPosition=([A-Za-z]+)', page))):
    tt = re.sub(r'(?<!^)([A-Z])', r' \1', pos).title()
    if re.search(r'programmer|engineer', tt, re.I) and not re.search(r'network|security|systems|devops|data center', tt, re.I) and new_id('rentec', pos):
        rows.append(['Renaissance', 'www.rentec.com', 'new', tt, 'East Setauket / New York', f'https://www.rentec.com/Careers.action?jobs=true&selectedPosition={pos}'])

# ---- start window: a season named in the title ("Summer 2027") must fall inside eligibility's window ----
SEASON = {'winter': 1, 'spring': 1, 'summer': 5, 'fall': 8, 'autumn': 8}
try: _E = json.load(open(os.path.join(R, 'config', 'settings.json'))).get('eligibility', {})
except Exception: _E = {}
def _ym(s):
    m = re.match(r'(\d{4})-(\d{2})', s or ''); return (int(m.group(1)), int(m.group(2))) if m else None
WIN = (_ym(_E.get('earliest_start')), _ym(_E.get('latest_start')))
def in_window(title):
    m = re.search(r'(winter|spring|summer|fall|autumn)\s*(\d{4})', title or '', re.I)
    return not (m and all(WIN)) or WIN[0] <= (int(m.group(2)), SEASON[m.group(1).lower()]) <= WIN[1]
dropped = [r for r in rows if not in_window(r[3])]
rows = [r for r in rows if in_window(r[3])]

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(rows, open(OUT, 'w'))
print(f'cutoff {CUT.isoformat()[:16]}Z  candidates {len(rows)} ({len(dropped)} dropped: season outside the start window)  signed-in portals: {sorted(signed) or "none"}')
ok_hosts = signed | OPEN_PORTALS
agent = [r for r in rows if r[1] in ok_hosts]; alex = [r for r in rows if r[1] not in ok_hosts]
if agent:
    print('--- AGENT MAY APPLY (signed-in portal, or a no-account portal in OPEN_PORTALS):')
    for r in sorted(agent): print('\t'.join(r))
if alex:
    print('--- FOR YOU, BY HAND (no signed-in account; put these in the run summary):')
    for r in sorted(alex): print('\t'.join(r))
if not dry:
    json.dump(SEEN, open(SEEN_FILE, 'w'))
    open(CUT_FILE, 'w').write(START.isoformat(timespec='minutes').replace('+00:00', 'Z') + '\n')
