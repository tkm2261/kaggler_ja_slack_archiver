# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from logging import StreamHandler, Formatter, FileHandler, getLogger
import os
from lib.slack_dumper import SlackDumper


logger = getLogger(None)


log_fmt = Formatter('%(asctime)s %(name)s %(lineno)d [%(levelname)s][%(funcName)s] %(message)s ')

handler = StreamHandler()
handler.setLevel('INFO')
handler.setFormatter(log_fmt)
logger.setLevel('INFO')
logger.addHandler(handler)


@pytest.fixture
def app():
    import main
    main.app.testing = True
    return main.app.test_client()


def test_get_slack_api():
    api_key = os.environ.get('KAGGLER_SLACK_API_KEY')
    if api_key is None:
        raise Exception('please set environment variable KAGGLER_SLACK_API_KEY')

    sd = SlackDumper(api_key)
    sd.get_user_list()
    sd.get_channel_list()
    sd.get_channels_histoey()
