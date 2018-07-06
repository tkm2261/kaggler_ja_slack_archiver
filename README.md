# Kaggler-ja Slack log gatheing system and viwer on GAE

I develop this tool to dump and view log in [Kaggler-ja slack](https://kaggler-ja.herokuapp.com/). 

This tool works on Google App Engine (GAE).

Maybe, you can use this on your slack with small change.

Our demo is here: https://kaggler-ja-slack-archive.appspot.com/

# Requirements

* Python 2.7

# Usage

1. Set up your gcp account and install Google Cloud SDK.
1. Download third-party libraries to pylib directory `pip install -t pylib -r requirements.txt`
1. change `config.py`
   * APP_NAME: set your app name. (it changes html title and left top workspace name)
1. Set your Slack API Key as environment variable: SLACK_API_KEY or set the key as Settings.api_key entity on datastore.
    * On local development server, you can set environment variable like `dev_appserver.py --env_var SLACK_API_KEY=xxxx app.yaml`
1. Deploy your app. `gcloud app deploy app.yaml index.yaml cron.yaml`. If you want to try on local, run `dev_appserver.py app.yaml` instead.
1. Kick first log downloading by accessing http://your_url/cron/job
1. See your top page http://your_url/

### (optional) Import all messages of public channel (over 10,000 messages)

1. Export your slack data. see https://get.slack.help/hc/en-us/articles/201658943-Export-your-workspace-data.
1. Upload it somewhere
1. set your file's url to `SLACK_DUMPED_LOG_URL`, and set `ROBUST_IMPORTING_MODE
