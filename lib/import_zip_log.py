# -*- coding: utf-8 -*-

import re
import json
import zipfile
from io import BytesIO
from logging import getLogger
logger = getLogger()

from lib.models import User, Channel, Message, Settings


def import_zip_log(io_buffer):

    try:
        _import_zip_log(io_buffer)
    except Exception as e:
        import traceback
        trc = traceback.format_exc()
        logger.error(trc)
        print(trc)
        raise e


def _import_zip_log(io_buffer):
    logger.debug('start')

    szd = SlackZipDumpedLog(zipfile.ZipFile(BytesIO(io_buffer.read())))

    ents = set(dir(User))
    for user_data in szd.users_data:
        user_id = user_data['id']
        user_data = {k: v for k, v in user_data.items() if k in ents}
        user = User.query(User.id == user_id).get()
        if user is None:
            User(**user_data).put()
        else:
            for k, v in user_data.items():
                setattr(user, k, v)
            user.put()
    logger.debug('user end')

    ents = set(dir(Channel))
    for channel_data in szd.channels_data:
        channel_id = channel_data['id']
        channel_data['created'] = int(channel_data['created'])

        channel_data = {k: v for k, v in channel_data.items() if k in ents}
        channel = Channel.query(Channel.id == channel_id).get()
        if channel is None:
            Channel(**channel_data).put()
        else:
            for k, v in channel_data.items():
                setattr(channel, k, v)
            channel.put()

    logger.debug('channel end')
    ents = set(dir(Message))
    for channel_id, messages in szd.map_message_data.items():
        for message in messages.values():
            message['channel_id'] = channel_id
            user = message.get('user', '')
            ts_raw = str(message['ts'])
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
    logger.debug('exit')


class SlackZipDumpedLog(object):

    CHANNELS_DATA_NAME = 'channels.json'
    USERS_DATA_NAME = 'users.json'

    def __init__(self, zipfile_buffer):
        self.zipfile_buffer = zipfile_buffer

        # print(self.zipfile_buffer.namelist())
        self.channels_data = self._extract_channels_data()
        self.users_data = self._extract_users_data()
        self.map_message_data = self._extract_message_data()

    def _extract_channels_data(self):
        data = json.loads(self.zipfile_buffer.read(self.CHANNELS_DATA_NAME))
        logger.info('channel num: %s' % len(data))
        return data

    def _extract_users_data(self):
        data = json.loads(self.zipfile_buffer.read(self.USERS_DATA_NAME))
        logger.info('user num: %s' % len(data))
        return data

    def _extract_message_data(self):
        map_message_data = {}
        cnt = 0
        for ch_data in self.channels_data:
            map_messages = {}
            ch_name = ch_data['name']
            channel_id = ch_data['id']

            list_ch_logs = sorted([p for p in self.zipfile_buffer.namelist()
                                   if re.match('^' + ch_name + '/.*.json', p) is not None])
            for path in list_ch_logs:
                msgs = json.loads(self.zipfile_buffer.read(path))
                for msg in msgs:
                    msg['channel_id'] = channel_id
                    ts_raw = msg['ts']
                    msg['ts'] = float(ts_raw)
                    msg['ts_raw'] = ts_raw
                    user = msg.get('user', '')

                    map_messages[ts_raw, user] = msg  # overwrite by newdata
            cnt += len(map_messages)
            map_message_data[channel_id] = map_messages
        logger.info('message channel num: %s, total messeage num: %s' % (len(map_message_data), cnt))
        return map_message_data


if __name__ == '__main__':
    from logging import StreamHandler, Formatter, FileHandler
    log_fmt = Formatter('%(asctime)s %(name)s %(lineno)d [%(levelname)s][%(funcName)s] %(message)s ')

    logger = getLogger(None)
    handler = StreamHandler()
    handler.setLevel('DEBUG')
    handler.setFormatter(log_fmt)
    logger.setLevel('DEBUG')
    logger.addHandler(handler)

    import zipfile
    with zipfile.ZipFile('test.zip') as zipfile_buffer:
        szd = SlackZipDumpedLog(zipfile_buffer)
