# -*- coding: utf-8 -*-
import time
import urllib2
import traceback
import logging
logging.getLogger().setLevel(logging.DEBUG)

from google.appengine.ext import ndb
from flask import Flask, render_template, request, redirect

from lib.models import User, Channel, Message
from lib.batch import get_slack_data
from lib.import_zip_log import import_zip_log
from lib.search_api import SearchApiHandler

app = Flask(__name__)

from config import APP_NAME, NUM_MASSAGES_PER_PAGE, DAYS_REQUEST_PAST_LOG, SLACK_DUMPED_LOG_URL


@app.route('/')
def index():
    """ Top Page
    """

    ch = request.args.get('ch')
    ch_data = Channel.query().filter(Channel.id == ch).get()
    if ch_data is None:
        ch_data = Channel.query().order(Channel.created).get()

    try:
        ch_name = ch_data.name
        ch = ch_data.id
    except AttributeError:
        # maybe there is no data. try to get log data.
        return redirect('/cron/job')

    ts = request.args.get('ts')
    try:
        ts = float(ts)
    except (ValueError, TypeError):
        ts = time.time()

    is_forward = request.args.get('type')
    try:
        is_forward = int(is_forward)
    except (ValueError, TypeError):
        is_forward = 1

    channels = Channel.query().order(Channel.created).iter()
    if is_forward:
        messages = Message.query().filter(Message.channel_id == ch,
                                          Message.ts < ts).order(-Message.ts).fetch(NUM_MASSAGES_PER_PAGE)
    else:
        messages = Message.query().filter(Message.channel_id == ch,
                                          Message.ts > ts).order(Message.ts).fetch(NUM_MASSAGES_PER_PAGE)
        messages = [m for m in sorted(messages, key=lambda x: x.ts, reverse=True)]

    if len(messages) > 0:
        current_ts = messages[0].ts + 0.01
        next_ts = messages[-1].ts
    else:
        current_ts = ts
        next_ts = ts

    return render_template('index.html',
                           app_name=APP_NAME,
                           current_ch_name=ch_name,
                           channels=channels,
                           messages=messages,
                           current_ch=ch,
                           current_ts=current_ts,
                           next_ts=next_ts,
                           )


@app.route('/search/')
def search():
    """ search Page
    """
    query_string = request.args.get('q')

    ch_data = Channel.query().order(Channel.created).get()

    page = request.args.get('p')
    try:
        page = int(page)
    except (ValueError, TypeError):
        page = 0

    sah = SearchApiHandler()
    list_msg = sah.search_query(query_string, page)

    #messages = [Message.query(ndb.Key('message', int(m['msg_key'][0].value))) for m in list_msg]
    messages = [ndb.Key(Message, int(m['msg_key'][0].value)).get() for m in list_msg]
    return render_template('search.html',
                           app_name=APP_NAME,
                           messages=messages,
                           page=page,
                           )


@app.route('/cron/job')
def batch():
    """ Get new messages from API
    """
    get_slack_data(days=DAYS_REQUEST_PAST_LOG)
    return 'successfully end.', 200


@app.route('/cron/create_search_index')
def create_search_index():
    """ Get new messages from API
    """
    sah = SearchApiHandler()
    sah.put_all_documents()
    return 'successfully end.', 200


@app.route('/upload/log')
def upload_log():
    """ Import messages from exported zip file.

    set your exported zip file to SLACK_DUMPED_LOG_URL
    """
    r = urllib2.urlopen(SLACK_DUMPED_LOG_URL)
    import_zip_log(r)

    return 'successfully end.', 200


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.error('An internal error occurred.' + traceback.format_exc())
    return 'An internal error occurred.', 500
