from gevent import socket
from gevent.socket import error as socket_error
from gevent.socket import timeout as socket_timeout
import sys
from tendrl.commons.message import Message
from tendrl.commons.logger import Logger
import traceback


class Event(object):
    def __init__(self, message, socket_path=None):
        if message.publisher == "node_agent":
            Logger(message)
        else:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket_path = socket_path
            if self.socket_path is None:
                self.socket_path = NS.config.data['logging_socket_path']
            self._write(message)

    def _write(self, message):
        try:
            json_str = Message.to_json(message)
            self.sock.connect(self.socket_path)
            self.sock.send(json_str)
        except (socket_error, socket_timeout, TypeError):
            msg = Message.to_json(message)
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(
                exc_type, exc_value, exc_tb, file=sys.stderr)
            sys.stderr.write(
                "Unable to pass the message into socket.%s\n" % msg)
        finally:
            self.sock.close()
