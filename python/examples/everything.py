#!/usr/bin/python3
"""
An example for using the python SDK that includes recommendations for local caching

This script should be used as an example and modified to export the indicators to any SIEM or TIP as needed.
Dragos recommends a run frequency of once every 6 hours, using a random minute to prevent API rate limiting.
API rate limit information is available on the User Profile page of portal.dragos.com in the same section
where API credentials can be found. Please contact support@dragos.com (and include Customer Portal in the subject)
with any questions or feedback.
"""

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import sqlite3
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dragos_portal import DragosPortalAPI

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--api-config', help='config file with Dragos API credentials and options', default='dragos.cfg')
parser.add_argument('-r', '--reset', help='truncate data and start over', action='store_true', default=False)
parser.add_argument('-s', '--save-dir', help='path to directory to save outputs', default='.')
parser.add_argument('-d', '--debug', help='print debugging information', action='store_true', default=False)
args = parser.parse_args()

last_run = None
sqlclient = sqlite3.connect('dragos.sqlite3')
sqlcursor = sqlclient.cursor()
portalclient = DragosPortalAPI(args.api_config)

INDICATOR_FIELDS = ['id', 'value', 'indicator_type', 'comment', 'first_seen', 'last_seen', 'updated_at', 'confidence', 'kill_chain', 'activity_groups', 'attack_techniques', 'pre_attack_techniques']
REPORT_FIELDS = ['serial', 'type', 'tlp_level', 'updated_at', 'release_date', 'threat_level', 'ioc_count', 'title', 'executive_summary', 'tags']

# Initialize a sqlite3 database
if args.debug:
    print("Initializing SQLite3 Database")
sqlclient.execute('CREATE TABLE IF NOT EXISTS logs (date datetime, count integer);')
sqlclient.execute('CREATE TABLE IF NOT EXISTS reports (' \
    'serial varchar(255),' \
    'type varchar(255),' \
    'tlp_level varchar(255),' \
    'updated_at datetime,' \
    'release_date datetime,' \
    'threat_level integer,' \
    'ioc_count integer,' \
    'title text,' \
    'executive_summary text,' \
    'tags text' \
');')
sqlclient.execute('CREATE TABLE IF NOT EXISTS indicators (' \
    'id integer primary key,' \
    'value varchar(255),' \
    'indicator_type varchar(255),' \
    'comment varchar(255),' \
    'first_seen datetime,' \
    'last_seen datetime,' \
    'updated_at datetime,' \
    'confidence varchar(255),' \
    'kill_chain varchar(255),' \
    'activity_groups varchar(255),' \
    'attack_techniques varchar(255),' \
    'pre_attack_techniques varchar(255)' \
');')

# the --reset flag will purge the indicators and leave the last_run variable as None
if args.reset:
    if args.debug:
        print('Purging Indicators')
    sqlcursor.execute('DELETE FROM indicators;')
    sqlclient.commit()
else:
    last_run = sqlcursor.execute('SELECT date FROM logs ORDER BY date DESC LIMIT 1;').fetchone()
    if last_run:
        last_run = last_run[0]
        if args.debug:
            print('Last run was: %s', last_run)
    elif args.debug:
        print('No previous run found')

# indicators = portalclient.get_indicators(updated_after=last_run, debug=args.debug)
indicators = []
count = len(indicators)
if args.debug:
    print("Found %i indicators" % count)

# --save-dir will dump the indicator payload to a file with an EPOCH timestamp
if args.save_dir:
    filename = Path(str(args.save_dir) + "/dragos_indicators_%i.json" % datetime.utcnow().timestamp())
    if args.debug:
        print("Saving ", filename)
    with open(filename, 'w') as f:
        json.dump(indicators, f)

# write all the indicators into sqlite db as a local cache
for i in indicators:
    sqlcursor.execute(
        'INSERT OR REPLACE INTO indicators (%s) VALUES (%s)' % (
            ','.join(INDICATOR_FIELDS),
            ','.join(['?'] * len(INDICATOR_FIELDS))
        ), (
            i['id'],
            i['value'],
            i['indicator_type'],
            i['comment'],
            i['first_seen'],
            i['last_seen'],
            i['updated_at'],
            i['confidence'],
            i['kill_chain'],
            ';'.join(i['activity_groups']),
            ';'.join(i['attack_techniques']),
            ';'.join(i['pre_attack_techniques'])
        )
    )

reports = portalclient.get_intel_reports(updated_after=last_run, debug=args.debug)
count = len(reports)
if args.debug:
    print("Found %i reports" % count)

for r in reports:
    tags = []
    for t in r['tags']:
        tag = t['text']
        if t['tag_type']:
            tag += " (%s)" % t['tag_type']
        tags.append(tag)

    sqlcursor.execute(
        'INSERT OR REPLACE INTO reports (%s) VALUES (%s)' % (
            ','.join(REPORT_FIELDS),
            ','.join(['?'] * len(REPORT_FIELDS))
        ), (
            r['serial'],
            r['type'],
            r['tlp_level'],
            r['updated_at'],
            r['release_date'],
            r['threat_level'],
            r['ioc_count'],
            r['title'],
            r['executive_summary'],
            ';'.join(tags)
        )
    )
    if 'report_link' in r:
        portalclient.get_intel_report_pdf(r['report_link'], save_dir=args.save_dir, debug=args.debug)

# save the successful run into the log so the timestamp can be used to only fetch the delta next time
sqlcursor.execute('INSERT INTO logs (date, count) VALUES (?, ?);', (datetime.utcnow(), count))
sqlclient.commit()
