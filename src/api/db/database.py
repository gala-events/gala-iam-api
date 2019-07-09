from enum import Enum


class Database:

    def __init__(self, connection):
        self.connection = connection

    def close(self):
        self.connection.close()
