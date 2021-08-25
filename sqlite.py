import sqlite3


class SQLiteDatabase:

    # connect to db
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    # get list of active watchers
    def get_users(self, status=True):
        with self.connection:
            sql = "SELECT * FROM `users` WHERE `status` = ?"
            return self.cursor.execute(sql, (status,)).fetchall()

    # check if person exists in db
    def user_exists(self, user_id):
        with self.connection:
            sql = 'SELECT * FROM `users` WHERE `user_id` = ?'
            result = self.cursor.execute(sql, (user_id,)).fetchall()
            return bool(len(result))

    # add watcher (watching status)
    def add_user(self, user_id, status=True, stream='text'):
        with self.connection:
            return self.cursor.execute("INSERT INTO `users` (`user_id`, `status`, `stream`) VALUES(?,?,?)", (user_id, status, stream))

    # update watching status and stream link
    def update_stream(self, user_id, status, stream):
        with self.connection:
            sql = ''' UPDATE `users`
                      SET `status` = ? ,
                          `stream` = ?
                      WHERE `user_id` = ?'''
            return self.cursor.execute(sql, (status, stream, user_id))

    # update watching status
    def update_status(self, user_id, status, predictions_since_last=1, defects_since_last=1,
                      detect_defects=True, defects_mute=False):
        with self.connection:
            sql = ''' UPDATE `users`
                      SET `status` = ? ,
                          `predictions_since_last` = ? ,
                          `defects_since_last` = ? ,
                          `detect_defects` = ? ,
                          `defects_mute` = ? 
                      WHERE `user_id` = ?'''
            return self.cursor.execute(sql, (status, predictions_since_last,
                                             defects_since_last, detect_defects,
                                             defects_mute, user_id))

    # setting notifications period
    def update_notifications_period(self, user_id, status, notifications_period=300):
        with self.connection:
            sql = ''' UPDATE `users`
                      SET `status` = ? ,
                          `notifications_period` = ?
                      WHERE `user_id` = ?'''
            return self.cursor.execute(sql, (status, notifications_period, user_id))

    # setting defects period
    def update_defects_period(self, user_id, status, defects_period=30):
        with self.connection:
            sql = ''' UPDATE `users`
                      SET `status` = ? ,
                          `defects_period` = ?
                      WHERE `user_id` = ?'''
            return self.cursor.execute(sql, (status, defects_period, user_id))

    # muting or unmuting defects notifications
    def update_mute(self, user_id, defects_mute):
        with self.connection:
            sql = ''' UPDATE `users`
                      SET `defects_mute` = ?
                      WHERE `user_id` = ?'''
            return self.cursor.execute(sql, (defects_mute, user_id))

    # if false, then only scheduled notifications
    def update_defects_detect(self, user_id, detect_defects):
        with self.connection:
            sql = ''' UPDATE `users`
                      SET `detect_defects` = ? 
                      WHERE `user_id` = ?'''
            return self.cursor.execute(sql, (detect_defects, user_id))

    # updates the number of predictions
    def update_predictions_since_last(self, user_id, predictions_since_last):
        with self.connection:
            sql = ''' UPDATE `users`
                      SET `predictions_since_last` = ? 
                      WHERE `user_id` = ?'''
            return self.cursor.execute(sql, (predictions_since_last, user_id))

    # updates the current number of defects detected
    def update_defects_since_last(self, user_id, defects_since_last):
        with self.connection:
            sql = ''' UPDATE `users`
                      SET `defects_since_last` = ? 
                      WHERE `user_id` = ?'''
            return self.cursor.execute(sql, (defects_since_last, user_id))

    # close db connection
    def close(self):
        self.connection.close()
