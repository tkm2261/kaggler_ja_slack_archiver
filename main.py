# -*- coding: utf-8 -*-
import time
import traceback
import logging
logging.getLogger().setLevel(logging.DEBUG)

from flask import Flask, render_template, request, redirect

from lib.models import User, Channel, Message
from lib.batch import get_slack_data

app = Flask(__name__)

CH_GENERAL_KEY = 'C0M91A5FX'

NUM_MASSAGES_PER_PAGE = 50

DAYS_REQUEST_PAST_LOG = 1


@app.route('/')
def index():
    ch = request.args.get('ch')
    if ch is None:
        ch = CH_GENERAL_KEY
    try:
        ch_name = Channel.query().filter(Channel.id == ch).get().name
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
    if is_forward > 0:
        messages = Message.query().filter(Message.channel_id == ch,
                                          Message.ts < ts).order(-Message.ts).fetch(NUM_MASSAGES_PER_PAGE)
    else:
        messages = Message.query().filter(Message.channel_id == ch,
                                          Message.ts > ts).order(-Message.ts).fetch(NUM_MASSAGES_PER_PAGE)
    if len(messages) > 0:
        next_ts = messages[-1].ts
    else:
        next_ts = ts
    return render_template('index.html',
                           current_ch_name=ch_name,
                           channels=channels,
                           messages=messages,
                           current_ch=ch,
                           current_ts=ts,
                           next_ts=next_ts,
                           )


@app.route('/cron/job')
def batch():
    get_slack_data(days=DAYS_REQUEST_PAST_LOG)
    return redirect('/')


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.error('An internal error occurred.' + traceback.format_exc())
    return 'An internal error occurred.', 500
