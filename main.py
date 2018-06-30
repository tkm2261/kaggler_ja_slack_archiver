# -*- coding: utf-8 -*-

from flask import Flask, render_template, request
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor
from lib.models import User, Channel, Message


app = Flask(__name__)

ch_general_key = Channel.query().filter(name='_general').get().id()

NUM_MASSAGES_PER_PAGE = 100


@app.route('/')
def index():
    ch = request.args.get('ch')
    if ch is None:
        ch = ch_general_key

    channels = Channel.query().iter()

    curs = Cursor(urlsafe=request.get('cursor'))
    messages, next_curs, page_more = Message.query().filter(
        channel_id=ch).order(-Message.ts).fetch_page(NUM_MASSAGES_PER_PAGE, start_cursor=curs)

    return render_template('index.html'
                           channels=channels,
                           messages=mesasges,
                           page_more=page_more,
                           next_curs=next_curs,
                           )
