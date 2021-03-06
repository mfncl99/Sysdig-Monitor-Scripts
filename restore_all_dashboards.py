#!/usr/bin/env python
#
# Save/restore dashboards
#

import os
import sys
import zipfile
import json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), '..'))
from sdcclient import SdcClient

#
# Parse arguments
#
if len(sys.argv) != 2:
    print 'usage: %s <sysdig-token/token-json-file>' % sys.argv[0]
    print 'You can find your token at https://app.sysdigcloud.com/#/settings/user'
    sys.exit(1)

sdc_token = sys.argv[1]
sdc_tokens = []
if not '.json' in sdc_token:
    sdc_tokens.append(sdc_token)
else:
    with open(sdc_token) as f:
        data = json.load(f)
        for apikey in data['apikeys']:
            sdc_tokens.append(apikey)


for token in sdc_tokens:
    #
    # Instantiate the SDC client
    # For on-pmreises, add ssl_verify=False
    #
    sdclient = SdcClient(token, sdc_url='https://app.sysdigcloud.com')
    print token

    dashboard_state_file = token
    print dashboard_state_file
    zipf = zipfile.ZipFile(dashboard_state_file, 'r')


    dashboard_conf_items = ['showAsType', 'filterRoot', 'linkMetrics',
                            'singleTimeNavigation', 'gridConfiguration', 'responsive',
                            'nodesNoiseFilter', 'compareWith', 'format', 'linksNoiseFilter',
                            'filterProcesses', 'isLegendExpanded', 'inhertitTimeNavigation',
                            'schema', 'sortAscending', 'mapDataLimit', 'metrics', 'filterExtNodes',
                            'sorting', 'name', 'sourceExploreView', 'items', 'showAs', 'eventsFilter',
                            'timeMode', 'isShared', 'sourceDrilldownView', 'filterExpression']

    for info in zipf.infolist():
        data = zipf.read(info.filename)
        try:
            j = json.loads(data)
        except ValueError:
            print 'Non-JSON item found in ZIP: ' + info.filename + ' (skipping)'
            continue
        k = {}
        for item in j.keys():
            if item in dashboard_conf_items:
                k[item] = j[item]

        res = sdclient.create_dashboard_with_configuration(k)
        if res[0]:
            print 'Restored Dashboard named: ' + j['name']
        else:
            print "Dashboard creation failed for dashboard name %s with error %s" % (j['name'], res[1])
