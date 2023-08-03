import sqlite3
import inspect
import create_bot


class Database:
    def __init__(self, db_file):
        try:
            self.connection = sqlite3.connect(db_file)
            self.cursor = self.connection.cursor()
        except Exception as e:
            create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)

    def add_reg_user_to_db(self, user_id):
        try:
            with self.connection:
                return self.cursor.execute(
                    "INSERT INTO `users` (`id`, `state`) VALUES (?,?)",
                    (user_id,True,))
        except Exception as e:
            create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)

    def reg_user_exists(self, user_id):
        try:
            with self.connection:
                res = self.cursor.execute("SELECT * FROM `users` WHERE `id` = ?",
                                          (user_id,)).fetchmany(1)

                return bool(len(res))
        except Exception as e:
            create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)

    def count_reg_user(self):
        try:
            with self.connection:
                return self.cursor.execute("SELECT COUNT(*) from `users` ").fetchmany(1)
        except Exception as e:
            create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)


