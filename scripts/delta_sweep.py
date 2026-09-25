#!/usr/bin/env python3
"""Delta sweep: list every req published since the last sweep across every known Ashby, Greenhouse,
Lever and SmartRecruiters board (Workable only via --ats wk, it rate-limits), then apply the title and location filters.

    python3 scripts/delta_sweep.py              # since state/last_sweep.txt, then advance it
    python3 scripts/delta_sweep.py --dry        # same, but do not advance the cutoff
    python3 scripts/delta_sweep.py --since 2026-09-15T04:00Z

RUN IT IN THE FOREGROUND. A headless run that backgrounds this and "waits for the notification"
ends its turn, and the session ends with it (runs 165-168, 2026-09-14). It finishes in 2-6 minutes
on ~2,000 live boards and stops itself at DEADLINE (7 minutes) no matter what. Run it ONCE per run:
back-to-back sweeps get throttled by the boards and read as dead.
Testing flags: --ats sr,wk (only those ATSs, no phase 2) and --limit 300 (first N slugs); neither advances the cutoff.

Outputs: state/sweep/allnew.json (every new req), state/sweep/cands.json (after title+location),
and a tab-separated list of candidates on stdout. A row ending in ★FLYOUT promises an in-person
final round in its description (a plus for users who like being flown out); mention it, it is not a gate. The cutoff lives in state/last_sweep.txt (UTC ISO).
Boards come from data/boards.md (backticked slugs in column 2) plus data/slug-candidates.txt.
"""
import json, re, sys, os, time, datetime, urllib.request, concurrent.futures as cf

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUT_FILE = os.path.join(R, 'state', 'last_sweep.txt')
OUT = os.path.join(R, 'state', 'sweep')
DEADLINE = 420          # seconds, hard stop for the whole sweep (Bash tool timeout must exceed this)
THREADS = 24
UTC = datetime.timezone.utc

def parse_ts(s):
    try: return datetime.datetime.fromisoformat(s.strip().replace('Z', '+00:00')).astimezone(UTC)
    except Exception: return None

args = sys.argv[1:]
dry = '--dry' in args
since = args[args.index('--since') + 1] if '--since' in args else None
ONLY = args[args.index('--ats') + 1].split(',') if '--ats' in args else None      # e.g. --ats sr,wk (testing)
LIMIT = int(args[args.index('--limit') + 1]) if '--limit' in args else None      # probe only the first N slugs (testing)
if since:
    CUT = parse_ts(since)
elif os.path.exists(CUT_FILE):
    CUT = parse_ts(open(CUT_FILE).read())
else:
    CUT = datetime.datetime.now(UTC) - datetime.timedelta(hours=24)
if not CUT:
    sys.exit(f'bad cutoff (want ISO UTC like 2026-09-15T04:00Z): {since or open(CUT_FILE).read()!r}')
START = datetime.datetime.now(UTC)

slugs = set()
for l in open(os.path.join(R, 'data', 'slug-candidates.txt')):
    l = l.strip()
    if l and not l.startswith('#') and '/' not in l and ' ' not in l: slugs.add(l)
for l in open(os.path.join(R, 'data', 'boards.md')):
    if l.startswith('|'):
        c = l.split('|')
        if len(c) > 3:
            for s in re.findall(r'`([A-Za-z0-9._-]+)`', c[2]): slugs.add(s)
slugs = sorted(slugs)
if LIMIT: slugs = slugs[:LIMIT]

LOC = re.compile(r'san francisco|\bsf\b|bay area|palo alto|mountain view|menlo park|sunnyvale|san jose|redwood city|oakland|berkeley|san mateo|burlingame|foster city|santa clara|cupertino|emeryville|new york|\bnyc\b|brooklyn|manhattan|chicago|seattle|bellevue|kirkland|redmond|remote|united states|\busa?\b|north america|americas|\bhq\b', re.I)
BADLOC = re.compile(r'london|toronto|canada|india|bangalore|bengaluru|berlin|paris|singapore|sydney|melbourne|tokyo|europe|emea|apac|mexico|brazil|israel|tel aviv|dublin|amsterdam|zurich|poland|warsaw|hong kong', re.I)
USLOC = re.compile(r'new york|san francisco|seattle|chicago|united states|\bus\b|\busa\b', re.I)
TIT = re.compile(r'engineer|developer|technical staff|\bmts\b|\bswe\b|programmer|\bintern\b|internship', re.I)
# "staff" is a seniority word, but "Member of Technical Staff" is a title we want: strip that phrase first.
BAD = re.compile(r'senior|\bsr\b|\bsr\.|principal|\blead\b|manager|director|head of|\bvp\b|architect|recruit|sales|account exec|designer|marketing|counsel|legal|finance|hardware|mechanical|electrical|firmware|\brf\b|analog|asic|fpga|verification|manufactur|technician|solutions engineer|support engineer|customer success|\biii\b|\biv\b|\bstaff\b', re.I)
# Postings that promise an in-person final round. A plus for users who like being flown out, not a gate.
FLY = re.compile(r"fly (you )?(out|in)|flown (out|in)|on-?site (final|round|interview|loop)|in-?person (final|round|interview|loop)|final (round|interview).{0,30}(on-?site|in-?person|in our office)|visit (our|the) (office|team)", re.I)
titleok = lambda t: TIT.search(t) and not BAD.search(re.sub(r'technical staff', '', t, flags=re.I))
locok = lambda loc: LOC.search(loc) and not (BADLOC.search(loc) and not USLOC.search(loc))

import ssl
def _ctx():
    """A verifying SSL context that works under launchd, in a sandbox, and with a bare python."""
    for cafile in ([__import__('certifi').where()] if _has('certifi') else []) + ['/etc/ssl/cert.pem']:
        try:
            if os.path.exists(cafile): return ssl.create_default_context(cafile=cafile)
        except Exception: pass
    return ssl.create_default_context()
def _has(m):
    try: __import__(m); return True
    except Exception: return False
CTX = _ctx()

def get(u, tag=''):
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=20, context=CTX) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:      # 404 = no board; 429 = rate limited (retry once)
            k = f'{tag}:HTTP{e.code}'; get.errors[k] = get.errors.get(k, 0) + 1
            if e.code != 429 or attempt == 2: return None
            time.sleep(2)
        except Exception as e:                   # connection reset / DNS / timeout: retry once
            k = f'{tag}:{type(e).__name__}'; get.errors[k] = get.errors.get(k, 0) + 1
            if attempt == 2: return None
            time.sleep(1)
get.errors = {}

def ts(s):
    try:
        d = datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))
        return d if d.tzinfo else d.replace(tzinfo=UTC)
    except Exception: return None

def probe(a):
    ats, s = a; out = []
    if ats == 'ash':
        d = get(f'https://api.ashbyhq.com/posting-api/job-board/{s}?includeCompensation=true', 'ash')
        if not isinstance(d, dict) or not d.get('jobs'): return ats, s, 0, out
        for j in d['jobs']:
            t = ts(j.get('publishedAt') or '')
            if not t or t < CUT or not j.get('isListed', True): continue
            loc = ' | '.join([j.get('location') or ''] + [x.get('location', '') for x in (j.get('secondaryLocations') or [])])
            comp = ((j.get('compensation') or {}).get('compensationTierSummary') or '')
            out.append([ats, s, t.isoformat()[:16], j.get('title', ''), loc, comp, j.get('jobUrl', ''), j.get('descriptionPlain') or ''])
    elif ats == 'gh':
        d = get(f'https://boards-api.greenhouse.io/v1/boards/{s}/jobs', 'gh')
        if not isinstance(d, dict) or not d.get('jobs'): return ats, s, 0, out
        for j in d['jobs']:
            t = ts(j.get('first_published') or '')
            if not t or t < CUT: continue
            out.append([ats, s, t.astimezone(UTC).isoformat()[:16], j.get('title', ''), (j.get('location') or {}).get('name', ''), '', j.get('absolute_url', ''), str(j.get('id'))])
    elif ats == 'sr':
        # SmartRecruiters. Public apply forms, no account. Company ids are case-sensitive, so lowercase
        # slugs miss some; still worth the call. No description in the list call (hand-read later).
        d = get(f'https://api.smartrecruiters.com/v1/companies/{s}/postings?limit=100', 'sr')
        if not isinstance(d, dict) or not d.get('content'): return ats, s, 0, out
        for j in d['content']:
            t = ts(j.get('releasedDate') or '')
            if not t or t < CUT: continue
            loc = j.get('location') or {}
            locs = ' | '.join(x for x in [loc.get('city'), loc.get('region'), loc.get('country'), 'remote' if loc.get('remote') else ''] if x)
            out.append([ats, s, t.astimezone(UTC).isoformat()[:16], j.get('name', ''), locs, '', f"https://jobs.smartrecruiters.com/{s}/{j.get('id')}", ''])
    elif ats == 'wk':
        # Workable. Public apply forms, no account.
        d = get(f'https://apply.workable.com/api/v1/widget/accounts/{s}?details=true', 'wk')
        if not isinstance(d, dict) or not d.get('jobs'): return ats, s, 0, out
        for j in d['jobs']:
            t = ts(j.get('published_on') or j.get('created_at') or '')
            if not t or t < CUT: continue
            locs = ' | '.join(x for x in [j.get('city'), j.get('state'), j.get('country'), 'remote' if j.get('telecommuting') else ''] if x)
            desc = re.sub(r'<[^>]+>', ' ', (j.get('description') or '') + ' ' + (j.get('requirements') or ''))
            out.append([ats, s, t.isoformat()[:16], j.get('title', ''), locs, '', j.get('url') or j.get('application_url') or '', desc])
    else:
        d = get(f'https://api.lever.co/v0/postings/{s}?mode=json', 'lv')
        if not isinstance(d, list) or not d: return ats, s, 0, out
        for j in d:
            t = datetime.datetime.fromtimestamp((j.get('createdAt') or 0) / 1000, UTC)
            if t < CUT: continue
            c = j.get('categories') or {}
            loc = ' | '.join([c.get('location') or ''] + (c.get('allLocations') or []))
            sr = j.get('salaryRange') or {}
            comp = f"{sr.get('min')}-{sr.get('max')} {sr.get('interval')}" if sr else ''
            desc = (j.get('descriptionPlain') or '') + ' ' + ' '.join(x.get('content', '') for x in j.get('lists') or [])
            out.append([ats, s, t.isoformat()[:16], j.get('text', ''), loc, comp, j.get('hostedUrl', ''), desc])
    return ats, s, 1, out

live = {'ash': 0, 'gh': 0, 'lv': 0, 'sr': 0, 'wk': 0}; allnew = []; done = 0; timed_out = False
t0 = time.time()

def run(pairs, seconds):
    """Probe pairs with a thread pool; stop at `seconds`. Returns (results, hit_deadline)."""
    ex = cf.ThreadPoolExecutor(THREADS); futs = [ex.submit(probe, j) for j in pairs]; res = []; hit = False
    try:
        for f in cf.as_completed(futs, timeout=max(1, seconds)): res.append(f.result())
    except cf.TimeoutError:
        hit = True
    ex.shutdown(wait=False, cancel_futures=True)
    return res, hit

# Phase 1: the big three. This is the part that must finish for the cutoff to advance.
pairs1 = [(a, s) for s in slugs for a in (ONLY or ('ash', 'gh', 'lv'))]
res1, timed_out = run(pairs1, DEADLINE)
live_slugs = set()
for ats, s, ok, out in res1:
    live[ats] += ok; allnew += out; done += 1
    if ok: live_slugs.add(s)
# Phase 2, only with time left: SmartRecruiters and Workable for slugs that have no board on the big three.
# A company uses one ATS, so this halves the extra load. Partial results here never block the cutoff.
pairs2 = []
left = DEADLINE - (time.time() - t0)
if not ONLY and not timed_out and left > 30:
    # Workable is NOT in phase 2: it answers HTTP 429 to almost every probe at this volume (1,302 of 1,400
    # on 2026-09-16). Its probe stays for --ats wk testing and for a future curated list.
    pairs2 = [(a, s) for s in slugs if s not in live_slugs for a in ('sr',)]
    res2, hit2 = run(pairs2, left)
    for ats, s, ok, out in res2:
        live[ats] += ok; allnew += out; done += 1
    if hit2: print(f'(phase 2 stopped at the deadline after {len(res2)} of {len(pairs2)} SmartRecruiters/Workable probes)')
jobs = pairs1 + pairs2

os.makedirs(OUT, exist_ok=True)
json.dump(allnew, open(os.path.join(OUT, 'allnew.json'), 'w'))
c = [o for o in allnew if o[1] != 'jobgether' and titleok(o[3]) and locok(o[4])]
json.dump(c, open(os.path.join(OUT, 'cands.json'), 'w'))
print(f'cutoff {CUT.isoformat()[:16]}Z  pairs {len(jobs)}  probed {done}  live {live}  new reqs {len(allnew)}  after title+loc {len(c)}  {time.time()-t0:.0f}s'
      + ('  ★ TIMED OUT at DEADLINE, results partial; cutoff NOT advanced' if timed_out else ''))
for o in sorted(c, key=lambda o: (o[1], o[3])): print('\t'.join(o[:7]) + ('\t★FLYOUT' if FLY.search(o[7] or '') else ''))
if get.errors: print('--- request errors by type:', get.errors)
testing = bool(ONLY or LIMIT)
if not testing and sum(live.values()) < 500: print('★ FEWER THAN 500 LIVE BOARDS: the network or TLS is broken, not the boards. Results are NOT trustworthy; cutoff NOT advanced.')
print('--- new-req slugs dropped by title/loc:', sorted({o[1] for o in allnew} - {o[1] for o in c}))
if not dry and not testing and not timed_out and sum(live.values()) >= 500:
    open(CUT_FILE, 'w').write(START.isoformat(timespec='minutes').replace('+00:00', 'Z') + '\n')
    print('cutoff advanced to', START.isoformat(timespec='minutes'))
