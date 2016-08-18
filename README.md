# instant-steem

A Python 3 command line tool that allows to stream steem content to your favourite instant messenger.
Currently supported messenger clients: 

* Slack
* Skype
* Telegram

Uses python-steem, Skype4Py, slackclient and twx.botapi.

0.1 ALPHA revision: API can change.

TODO: add new API, docs, tests, dockerize.

## Installation

`sudo apt-get python-dbus` for Skype dbus support.

Then with or without virtualenv:

`pip3 install -r requirements.txt`

## Configuration

The tool uses a simple YAML configuration file with separate sections.

Example configuration:

```
slack:
    username: slack_username
    channel: random
    token: xxxx-0123456789-0123456789-0123456789-0123456789
    icon_url: https://avatars3.githubusercontent.com/u/20819151?v=3&s=460
telegram:
    username: steem-bot
    token: 0123456789012345678901234567890123456789
skype:
    username: skype_username
```

## Example usage

python 
Tested on Ubuntu 14.04 64bit
