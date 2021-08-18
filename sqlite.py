import sqlite3


class SQLiteDatabase:

    # connect to db
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    # get list of active watchers
    def get_subscriptions(self, status=True):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `subs` WHERE `status` = ?", (status,)).fetchall()

    # check if person exists in db
    def subscriber_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `subs` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    # add watcher (watching status)
    def add_subscriber(self, user_id, status=True, stream='text'):
        with self.connection:
            return self.cursor.execute("INSERT INTO `subs` (`user_id`, `status`, `stream`) VALUES(?,?,?)", (user_id, status, stream))

    # update watching status and stream link
    def update_stream(self, user_id, status, stream):
        with self.connection:
            sql = ''' UPDATE `subs`
                      SET `status` = ? ,
                          `stream` = ?
                      WHERE `user_id` = ?'''
            return self.cursor.execute(sql, (status, stream, user_id))

    # update watching status
    def update_subscription(self, user_id, status):
        with self.connection:
            sql = ''' UPDATE `subs`
                      SET `status` = ?
                      WHERE `user_id` = ?'''
            return self.cursor.execute(sql, (status, user_id))

    # close db connection
    def close(self):
        self.connection.close()
