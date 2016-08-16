import yaml
import argparse

from piston.steem import Steem
from slackclient import SlackClient
from Skype4Py import Skype as SkypeClient
from twx.botapi import TelegramBot as TelegramClient


class InstantSteemError(Exception):
    pass


class InstantSteem(object):
    SUPPORTED_CLIENTS = ['skype', 'slack', 'telegram']

    def __init__(self, yaml_cfg):
        self.steem = Steem(nobroadcast=True)
        self.msg_clients = {}
        self.cfg = yaml_cfg
        for client in self.cfg:
            self.init_client(client)

    def init_client(self, client):
        """
        Initialize instant message client.

        :param client: Client name. Supported: skype, slack, telegram.
        :raises :py:class:`InstantSteemError` if client not supported or client
                object could not be initialized.
        """
        if client not in InstantSteem.SUPPORTED_CLIENTS:
            raise InstantSteemError("Client %s not supported!" % client)
        cl_obj = None
        try:
            if client == 'skype':
                cl_obj = SkypeClient()
                cl_obj.Attach()
            if client == 'slack':
                cl_obj = SlackClient(self.cfg[client]['token'])
            if client == 'telegram':
                cl_obj = TelegramClient(self.cfg[client]['token'])
        except Exception as e:
            raise InstantSteemError('Could not initialize %s client: '
                                    '%s' % (client, e))
        self.msg_clients[client] = cl_obj

    def send(self, client, message):
        """
        Route message to appropriate client.

        :param client: Client name.
        :param message: Message.
        """
        if client not in InstantSteem.SUPPORTED_CLIENTS:
            raise InstantSteemError("Client %s not supported!" % client)
        getattr(self, 'send_' + client)(message)

    def send_slack(self, message):
        """
        Send a message to Slack.

        :param message: Message text.
        :raises: :py:class:`InstantSteemError`
        :return: True if message was sent. False otherwise.
        """
        try:
            ic = self.msg_clients['slack']
            ret = ic.api_call('chat.postMessage',
                              text=message,
                              username=self.cfg['slack']['username'],
                              channel=self.cfg['slack']['channel'],
                              icon_url=self.cfg['slack']['icon_url'],
                              unfurl_links='true')
        except ValueError as e:
            raise InstantSteemError('Slack client not available: %s' % e)
        return ret

    def send_skype(self, message):
        """
        Send a message to Skype.

        :param message: Message text.
        :raises: InstantSteemError
        :return: True if message was sent. False otherwise.
        """
        try:
            ic = self.msg_clients['skype']
            ret = ic.SendMessage(self.cfg['skype']['username'], message)
        except ValueError as e:
            raise InstantSteemError('Skype client not available: %s' % e)
        return ret

    def send_telegram(self, message):
        """
        Send a message to Telegram.

        :param message: Message text.

        :raises: InstantSteemError
        :return: True if message was sent. False otherwise.
        """
        try:
            ic = self.msg_clients['telegram']
            print('telegram: ' + message)
            ret = ic.send_message(self.cfg['telegram']['username'], message).wait()
        except ValueError as e:
            raise InstantSteemError('Telegram client not available: %s' % e)
        return ret

    def stream(self, when):
        """
        Stream content to messengers.

        :param when: Specify when to stream steem data based on command line
                     arguments. Stream everything if neither posts or comments
                     were specify, limit otherwise.
        """
        for c in self.steem.stream_comments():
            send_msg = False
            if (not when.posts and not when.comments) or \
                    (when.comments and c['depth'] > 0) or \
                    (when.posts and c['depth'] == 0):
                send_msg = True
            if send_msg:
                for client in self.cfg:
                    self.send(client, InstantSteem._message(c))

    @staticmethod
    def _message(c):
        """
        Helper function that formats message before sending

        :param c: Steem object
        :return: Message string
        """
        return '`%s %s` : %s' % (c['created'], c['author'], c['body'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--comments", help="Stream comments only.",
                        action="store_true")
    parser.add_argument("--posts", help="Stream posts only.",
                        action="store_true")

    args = parser.parse_args()

    with open('stream.yaml', 'r') as config_file:
        cfg = yaml.load(config_file)
        s = InstantSteem(cfg)
        s.stream(args)
