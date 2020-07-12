from flask import Flask
from flask import request as flask_request
import sys, os
import blinker as _

import json
import requests

from logging.config import dictConfig


## Have flask use stdout as the logger
FORMAT = ('%(asctime)s level=%(levelname)s name=%(name)s source=%(filename)s:%(lineno)d '
          'message="%(message)s"')

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': FORMAT,
    }},
    'handlers': {'console': {
        'class': 'logging.StreamHandler',
        'level': 'INFO',
        'formatter': 'default',
        'stream': 'ext://sys.stdout'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['console']
    }
})

## Flask
app = Flask(__name__)


@app.route('/webhook/splunk', methods=['POST'])
def post_endpoint():
    app.logger.info('circleci webhook triggered splunk http event collector')
    app.logger.info(json.dumps(flask_request.json))
    
    splunk_hec_protocol = os.environ.get('SPLUNK_HEC_PROTOCOL', 'https')
    splunk_hec_host = os.environ.get('SPLUNK_HEC_HOST', 'localhost:8088')
    splunk_hec_token = os.environ.get('SPLUNK_HEC_TOKEN', 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX')

    splunk_hec_endpoint = '%s://%s/services/collector/raw' % (splunk_hec_protocol, splunk_hec_host)

    headers = {
        'Authorization': 'Splunk %s' % splunk_hec_token,
        'Conten-Type': 'application/json'
    }

    # POST Splunk HEC Endpoint
    r = requests.post(splunk_hec_endpoint, data=json.dumps(flask_request.json), headers=headers)

    dict_r = json.loads(r.text)
    if dict_r['code'] != 0:
        app.logger.error('failed to post splunk; message=' + dict_r['text'])
    else:
        app.logger.info('success to post splunk hec')

    return dict_r['text']

if __name__ == '__main__':
    app.logger.info('%(message)s This is __main__ log')
    app.run(host='0.0.0.0', port='5050')
