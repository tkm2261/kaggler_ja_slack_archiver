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
1. Deploy your app. `gcloud app deploy app.yaml index.yaml cron.yaml`
1. Kick first log downloading by accessing http://<your url>/cron/job
1. See your top page http://<your url>/