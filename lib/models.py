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

    def get_display_name(self):
        user_name = self.profile['display_name']
        if user_name == '':
            user_name = self.name
        return user_name


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


URL_PATTERN = re.compile(r'<(https?|ftp)(://[\w:;/.?%#&=+-]+)>')
IMG_PATTERN = re.compile(r'<(https?|ftp)(://[\w:;/.?%#&=+-]+)\|(.+?)>')
CHANNEL_PATTERN = re.compile(r'<#([A-Z0-9]+)\|([\w;/.?%#&=+-]+)>')
USER_PATTERN = re.compile(r'<@([A-Z0-9]+)>')


class Message(ndb.Model):
    channel_id = ndb.StringProperty()
    type = ndb.StringProperty()
    user = ndb.StringProperty()
    text = ndb.StringProperty(indexed=False)
    ts = ndb.FloatProperty()
    ts_raw = ndb.StringProperty()
    reactions = ndb.JsonProperty()

    _user_data = None

    @property
    def user_data(self):
        if self._user_data is None:
            self._user_data = User.query(User.id == self.user).get()
        return self._user_data

    def get_ts_timestamp(self):
        try:
            return datetime.datetime.fromtimestamp(self.ts).strftime('%Y/%m/%d %H:%M')
        except Exception:
            return None

    def get_user_name(self):
        return self.user_data.get_display_name()

    def get_user_img_url(self):
        return self.user_data.profile['image_48']

    def get_reactions(self):
        ret = []
        for react in self.reactions:
            text = react['name']
            if text == '+1':
                text = 'thumbsup'
            react['name'] = text
            ret.append(react)
        return ret

    def _conv_url(self, text):
        text = URL_PATTERN.sub(r'<a class="link" href="\1\2", target="_blank">\1\2</a>', text)
        text = IMG_PATTERN.sub(r'<a class="link" href="\1\2", target="_blank">\1\2</a>', text)
        return text

    def _conv_channel_url(self, text):
        return CHANNEL_PATTERN.sub(r'<a class="link-channel" href="/?ch=\1">#\2</a>', text)

    def _conv_user_name(self, text):
        return USER_PATTERN.sub(lambda x: r'<span class="link-user" user_id="\1">@' + User.query(User.id == x.group(1)).get().get_display_name() + '</span>', text)

    def _conv_emoji(self, text):
        print(text)
        return text.replace(':+1:', ':thumbsup:')

    def get_conved_text(self):
        text = self.text
        text = self._conv_url(text)
        text = self._conv_channel_url(text)
        text = self._conv_user_name(text)
        #text = self._conv_emoji(text)

        text = text.replace('\n', '<br/>')
        return text
