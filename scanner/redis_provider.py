import os
from threading import Lock

import redis


class RedisProvider:
    _INSTANCE = None
    _LOCK = Lock()
    KEY_PREFIX = 'scan_lock'

    def __init__(self, host='localhost', port=6380, db=0):
        self.conn = redis.Redis(host=host, port=port, db=0, max_connections=os.getenv('REDIS_MAX_CONN'),
                                socket_timeout=os.getenv('REDIS_SOCKET_TIMEOUT'))

    def get_key(self, scan_id):
        return f'{self.KEY_PREFIX}:{scan_id}'

    def delete(self, scan_id):
        return self.conn.delete(self.get_key(scan_id))
