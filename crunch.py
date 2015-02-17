import sys, json, pprint
from datetime import datetime as DateTime
from datetime import timedelta as TimeDelta

def parse_date(string):
    try:
        return DateTime.strptime(string, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        # Some are exact I guess ...
        return DateTime.strptime(string, "%Y-%m-%dT%H:%M:%S")

averages = {}
records = []

def avg(key, value):
    averages.setdefault(key, [])
    averages[key].append(value)

# https://dvcs.w3.org/hg/webperf/raw-file/tip/specs/NavigationTiming/Overview.html
for line in open(sys.argv[1], 'r').readlines():
    record = json.loads(line.strip())
    records.append(record)

    # Request sent to server.  We could go connectStart but it can be the case
    # that the connection is cached (and anyway we're not measuring connect
    # speed here)
    request_start = parse_date(record['requestStart'])

    navigation_start = parse_date(record['navigationStart'])

    # First byte recieved.
    first_byte = parse_date(record['responseStart'])

    # This sort of makes sense as a start time for performance.
    render_start = parse_date(record['domLoading'])

    # Timings for the start of event firing.
    dom_ready = parse_date(record['domContentLoadedEventStart'])
    page_load = parse_date(record['loadEventStart'])

    avg('click_to_send_request', request_start - navigation_start)

    avg('first_byte', first_byte - request_start)
    avg('page_load_start', parse_date(record['loadEventStart']) - render_start)

    # I guess we can call thsi the true render time.
    avg('page_load_end', parse_date(record['loadEventEnd']) - render_start)
    avg('dom_ready_start', parse_date(record['domContentLoadedEventStart']) - render_start)

    # And this would be the time it takes before the user can start doing stuff
    # with the document?
    avg('dom_ready_end', parse_date(record['domContentLoadedEventEnd']) - render_start)

for key in sorted(averages.keys()):
    average = sum(averages[key], TimeDelta(0)) / len(averages[key])
    print key, average.total_seconds()
