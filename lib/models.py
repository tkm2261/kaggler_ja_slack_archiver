import re
import datetime
from google.appengine.ext import ndb


class Settings(ndb.Model):
    api_key = ndb.StringProperty()


class User(ndb.Model):

    id = ndb.StringProperty()
    team_id = ndb.StringProperty()

    name = ndb.StringProperty()
    deleted = ndb.BooleanProperty()

    color = ndb.StringProperty()

    real_name = ndb.StringProperty()

    tz = ndb.StringProperty()

    tz_label = ndb.StringProperty()
    tz_offset = ndb.IntegerProperty()

    profile = ndb.JsonProperty(indexed=False)
    is_admin = ndb.BooleanProperty()

    is_owner = ndb.BooleanProperty()

    is_primary_owner = ndb.BooleanProperty()

    is_restricted = ndb.BooleanProperty()
    is_ultra_restricted = ndb.BooleanProperty()

    is_bot = ndb.BooleanProperty()
    updated = ndb.IntegerProperty()
    is_app_user = ndb.BooleanProperty()


class Channel(ndb.Model):

    id = ndb.StringProperty()
    name = ndb.StringProperty()
    is_channle = ndb.BooleanProperty()
    created = ndb.IntegerProperty()

    creator = ndb.StringProperty()
    is_archived = ndb.BooleanProperty()
    is_general = ndb.BooleanProperty()
    name_normalized = ndb.StringProperty()

    is_shared = ndb.BooleanProperty()
    is_org_shared = ndb.BooleanProperty()
    is_member = ndb.BooleanProperty()
    is_private = ndb.BooleanProperty()
    is_mpim = ndb.BooleanProperty()
    members = ndb.StringProperty(repeated=True)
    topic = ndb.JsonProperty(indexed=False)
    purpose = ndb.JsonProperty(indexed=False)
    previous_names = ndb.JsonProperty(indexed=False)
    num_members = ndb.IntegerProperty()


URL_PATTERN = re.compile(r'([^"]|^)(https?|ftp)(://[\w:;/.?%#&=+-]+)')


def conv_url(text):
    return URL_PATTERN.sub(r'\1<a href="\2\3", target="_blank">\2\3</a>', text)


class Message(ndb.Model):
    channel_id = ndb.StringProperty()
    type = ndb.StringProperty()
    user = ndb.StringProperty()
    text = ndb.StringProperty(indexed=False)
    ts = ndb.FloatProperty()
    ts_raw = ndb.StringProperty()
    reactions = ndb.JsonProperty()

    def get_ts_timestamp(self):
        try:
            return datetime.datetime.fromtimestamp(self.ts).strftime('%Y/%m/%d %H:%M')
        except Exception:
            return None

    def get_user_name(self):
        return User.query(User.id == self.user).get().name

    def get_user_img_url(self):
        return User.query(User.id == self.user).get().profile['image_48']

    def get_conved_text(self):
        return conv_url(self.text)
