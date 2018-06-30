# -*- coding: utf-8 -*-

import time
import json

import requests

from logging import getLogger
logger = getLogger(__name__)


class SlackDumper(object):
    USERS_LIST_URL_FORMAT = 'https://slack.com/api/users.list?token={token}&cursor={cursor}&limit=1000'
    CHANNELS_LIST_URL_FORMAT = 'https://slack.com/api/channels.list?token={token}&cursor={cursor}&limit=1000'
    CHANNELS_HISTORY_URL_FORMAT = ('https://slack.com/api/channels.history?' +
                                   'token={token}&channel={channel}&latest={latest}&oldest={oldest}&count=100')

    def __init__(self,
                 api_key):
        self.api_key = api_key

        self.list_users = None
        self.list_channels = None

    def get_user_list(self):
        logger.debug('enter')
        if self.list_users is not None:
            logger.debug('return cached user list')
            return self.list_users

        list_users = []
        cursor = ''
        while 1:
            url = self.USERS_LIST_URL_FORMAT.format(token=self.api_key, cursor=cursor)
            r = requests.get(url, headers={"content-type": "application/json"})
            data = r.json()
            if not data['ok']:
                raise Exception('fail to get users.list data')
            list_users += data['members']
            cursor = data['response_metadata']['next_cursor']
            if cursor == '':
                break

        self.list_users = list_users

        logger.info('get %s members' % len(list_users))
        logger.debug('exit')
        return list_users

    def get_channel_list(self):
        logger.debug('enter')
        if self.list_channels is not None:
            logger.debug('return cached channel list')
            return self.list_channels

        list_channels = []
        cursor = ''
        while 1:
            url = self.CHANNELS_LIST_URL_FORMAT.format(token=self.api_key, cursor=cursor)
            r = requests.get(url, headers={"content-type": "application/json"})
            data = r.json()
            if not data['ok']:
                raise Exception('fail to get channels.list data')
            list_channels += data['channels']
            cursor = data['response_metadata']['next_cursor']
            if cursor == '':
                break

        self.list_channels = list_channels
        logger.info('get %s channels' % len(list_channels))
        logger.debug('exit')
        return list_channels

    def get_channels_histoey(self, days=None):
        logger.debug('enter')
        latest = time.time()
        oldest = time.time() - (3600 * 24 * days) if days is not None else 0
        cursor = ''
        map_channles_hist = {}
        for ch_data in self.get_channel_list():
            channel_id = ch_data['id']
            list_channel_hist = self.get_channel_hist(channel_id, latest, oldest)
            map_channles_hist[channel_id] = list_channel_hist
        logger.debug('exit')

        return map_channles_hist

    def get_channel_hist(self, channel_id, latest, oldest):
        list_channel_hist = []
        while 1:
            url = self.CHANNELS_HISTORY_URL_FORMAT.format(token=self.api_key,
                                                          channel=channel_id,
                                                          latest=latest,
                                                          oldest=oldest)
            r = requests.get(url, headers={"content-type": "application/x-www-form-urlencoded"})

            data = r.json()
            if not data['ok']:
                raise Exception('fail to get %s channel history  data' % ch)
            list_channel_hist += data['messages']
            if data['has_more']:
                latest = data['messages'][-1]['ts']
            else:
                break
        logger.info('get %s messages in %s' % (len(list_channel_hist), channel_id))
        logger.debug('exit')
        return list_channel_hist
