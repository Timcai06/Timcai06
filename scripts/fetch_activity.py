"""Fetch live GitHub activity into assets/editor/activity.json.

Public, non-fork repositories only; commits on each default branch authored by
Tim (bots excluded). Only aggregates are stored, and nothing depends on the
run date except week buckets, so the file changes only when activity does.
Locally: GH_TOKEN=$(gh auth token) python3 scripts/fetch_activity.py
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import os
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/editor/activity.json'
LOGIN = 'Timcai06'
TZ = timezone(timedelta(hours=8))  # Asia/Shanghai, no DST
FEATURED = ['EduCanvas', 'SciScope', 'TTT-I-M', 'BDI', 'PulseGraph']
CARD_WEEKS = 12


def gql(query, **variables):
    body = json.dumps({'query': query, 'variables': variables}).encode()
    req = urllib.request.Request('https://api.github.com/graphql', body,
                                 {'Authorization': f'bearer {os.environ["GH_TOKEN"]}',
                                  'Content-Type': 'application/json'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.load(resp)
            break
        except urllib.error.URLError:
            if attempt == 2:
                raise
            time.sleep(3)
    if 'errors' in data:
        raise SystemExit(data['errors'])
    return data['data']


CALENDAR = '''query($login:String!){user(login:$login){id contributionsCollection{contributionCalendar{
  totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}
  repositories(first:100, ownerAffiliations:OWNER, privacy:PUBLIC, isFork:false){nodes{name}}}}'''
HISTORY = '''query($owner:String!,$name:String!,$author:ID!,$since:GitTimestamp!,$after:String){
  repository(owner:$owner,name:$name){defaultBranchRef{target{... on Commit{
    history(first:100, after:$after, since:$since, author:{id:$author}){
      pageInfo{hasNextPage endCursor} nodes{abbreviatedOid authoredDate messageHeadline}}}}}}}'''


def commits(repo, author, since):
    out, after = [], None
    while True:
        ref = gql(HISTORY, owner=LOGIN, name=repo, author=author, since=since, after=after)['repository']['defaultBranchRef']
        if not ref:  # empty repository
            return out
        history = ref['target']['history']
        out += history['nodes']
        if not history['pageInfo']['hasNextPage']:
            return out
        after = history['pageInfo']['endCursor']


def main():
    user = gql(CALENDAR, login=LOGIN)['user']
    now = datetime.now(TZ)
    since = (now - timedelta(days=366)).isoformat()
    punch = [[0] * 24 for _ in range(7)]  # [weekday Mon=0][hour, UTC+8]
    recent, cards = [], {}
    this_monday = (now - timedelta(days=now.weekday())).date()
    for repo in sorted(r['name'] for r in user['repositories']['nodes']):
        weeks, last = [0] * CARD_WEEKS, None
        for c in commits(repo, user['id'], since):
            t = datetime.fromisoformat(c['authoredDate']).astimezone(TZ)
            punch[t.weekday()][t.hour] += 1
            recent.append({'repo': repo, 'sha': c['abbreviatedOid'], 'date': t.strftime('%Y-%m-%d'),
                           'ts': t.isoformat(), 'message': c['messageHeadline']})
            ago = (this_monday - (t.date() - timedelta(days=t.weekday()))).days // 7
            if 0 <= ago < CARD_WEEKS:
                weeks[CARD_WEEKS - 1 - ago] += 1
            last = max(last or '', t.strftime('%Y-%m-%d'))
        if repo in FEATURED:
            cards[repo] = {'weeks': weeks, 'last_commit': last}
    recent.sort(key=lambda c: c['ts'], reverse=True)
    data = {'calendar': user['contributionsCollection']['contributionCalendar'],
            'punch': punch,
            'commits_last_year': sum(map(sum, punch)),
            'recent': [{k: c[k] for k in ('repo', 'sha', 'date', 'message')} for c in recent[:5]],
            'cards': cards}
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
    print(f'Fetched activity: {data["commits_last_year"]} commits, {len(user["repositories"]["nodes"])} public repos')


main()
