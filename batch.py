# -*- coding: utf-8 -*-

import os

from logging import getLogger
logger = getLogger(None)

from lib.slack_dumper import SlackDumper
from lib.models import User, Channel, Message


def main():
    api_key = os.environ.get('KAGGLER_SLACK_API_KEY')
    if api_key is None:
        raise Exception('please set environment variable KAGGLER_SLACK_API_KEY')

    sd = SlackDumper(api_key)

    for user_data in sd.get_user_list():
        user_id = user_data[id]
        if User.get_by_key_name(user_id) is None:
            User(**user_data).put()

    for channel_data in sd.get_channel_list():
        channel_id = channel_data[id]
        if Channel.get_by_key_name(channel_id) is None:
            Channel(**channel_data).put()

    for message in sd.get_channels_histoey():
        channel_id = message['id']
        user_id = Message['user_id']
        ts = message['ts']
        if Message.get(channel_id=message, user_id=user_id, ts=ts).fetch() is None:
            Message(**message).put()


if __name__ == '__main__':
    from logging import StreamHandler, Formatter, FileHandler

    log_fmt = Formatter('%(asctime)s %(name)s %(lineno)d [%(levelname)s][%(funcName)s] %(message)s ')

    handler = StreamHandler()
    handler.setLevel('INFO')
    handler.setFormatter(log_fmt)
    logger.setLevel('INFO')
    logger.addHandler(handler)

    main()
