# -*- coding: utf-8 -*-

import os

from logging import getLogger
logger = getLogger(None)

from lib.slack_dumper import SlackDumper
from lib.models import User, Channel, Message, Settings


def get_slack_data(days=None):

    try:
        _get_slack_data(days)
    except Exception as e:
        import traceback
        trc = traceback.format_exc()
        logger.error(trc)
        print(trc)
        raise e


def _get_slack_data(days):
    settings = Settings.query().get()
    try:
        api_key = settings.api_key
    except AttributeError:
        api_key = os.environ.get('SLACK_API_KEY')
        if api_key is None:
            raise Exception('please set environment variable SLACK_API_KEY')
        else:
            Settings(api_key=api_key).put()

    sd = SlackDumper(api_key)
    ents = set(dir(User))
    for user_data in sd.get_user_list():
        user_id = user_data['id']
        user_data = {k: v for k, v in user_data.items() if k in ents}
        user = User.query(User.id == user_id).get()
        if user is None:
            User(**user_data).put()
        else:
            for k, v in user_data.items():
                setattr(user, k, v)
            user.put()

    ents = set(dir(Channel))
    for channel_data in sd.get_channel_list():
        channel_id = channel_data['id']
        channel_data = {k: v for k, v in channel_data.items() if k in ents}
        channel = Channel.query(Channel.id == channel_id).get()
        if channel is None:
            Channel(**channel_data).put()
        else:
            for k, v in channel_data.items():
                setattr(channel, k, v)
            channel.put()

    ents = set(dir(Message))
    for channel_id, messages in sd.get_channels_histoey(days=days).items():
        for message in messages:
            message['channel_id'] = channel_id
            user = message.get('user', '')
            ts_raw = message['ts']
            message['ts'] = float(ts_raw)
            message['ts_raw'] = ts_raw

            message = {k: v for k, v in message.items() if k in ents}
            msg = Message.query().filter(Message.channel_id == channel_id, Message.user == user, Message.ts_raw == ts_raw).get()
            if msg is None:
                Message(**message).put()
            else:
                for k, v in message.items():
                    setattr(msg, k, v)
                msg.put()


if __name__ == '__main__':
    from logging import StreamHandler, Formatter, FileHandler
    log_fmt = Formatter('%(asctime)s %(name)s %(lineno)d [%(levelname)s][%(funcName)s] %(message)s ')

    handler = StreamHandler()
    handler.setLevel('INFO')
    handler.setFormatter(log_fmt)
    logger.setLevel('INFO')
    logger.addHandler(handler)

    get_slack_data()
