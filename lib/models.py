
from google.appengine.ext import ndb


class Settings(ndb.Model):
    api_key = ndb.StringProperty()


class User(ndb.Model):

    id = ndb.StringProperty(indexed=True)
    team_id = ndb.StringProperty()

    name = ndb.StringProperty()
    deleted = ndb.BooleanProperty()

    color = ndb.StringProperty()

    real_name = ndb.StringProperty()

    tz = ndb.StringProperty()

    tz_label = ndb.StringProperty()
    tz_offset = ndb.IntegerProperty()

    profile = ndb.JsonProperty()
    is_admin = ndb.BooleanProperty()

    is_owner = ndb.BooleanProperty()

    is_primary_owner = ndb.BooleanProperty()

    is_restricted = ndb.BooleanProperty()
    is_ultra_restricted = ndb.BooleanProperty()

    is_bot = ndb.BooleanProperty()
    updated = ndb.IntegerProperty()
    is_app_user = ndb.BooleanProperty()


class Channel(ndb.Model):

    id = ndb.StringProperty(indexed=True)
    name = ndb.StringProperty()
    is_channle = ndb.BooleanProperty()
    created = ndb.IntegerProperty()

    creator = ndb.StringProperty()
    is_archived = ndb.BooleanProperty()
    is_general = ndb.BooleanProperty()
    name_normalized = ndb.StringProperty()

    is_shared = ndb.StringProperty()
    is_org_shared = ndb.StringProperty()
    is_member = ndb.StringProperty()
    is_private = ndb.StringProperty()
    is_mpim = ndb.StringProperty()
    members = ndb.KeyProperty(repeated=True, kind=User)
    topic = ndb.JsonProperty()
    purpose = ndb.JsonProperty()
    previous_names = ndb.JsonProperty()
    num_members = ndb.IntegerProperty()


class Message(ndb.Model):
    channel_id = ndb.KeyProperty(kind=Channel, indexed=True)
    type = ndb.StringProperty()
    user = ndb.KeyProperty(kind=User, indexed=True)
    text = ndb.StringProperty()
    ts = ndb.StringProperty(indexed=True)
    reactions = ndb.JsonProperty()
