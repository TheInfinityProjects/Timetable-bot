import os
import logging

import psycopg2

from urllib import parse


class UserDatabase(object):
    """This class implements the interaction between the bot and the database.

    The database is used Postgres.
    Psycopg2 is used as PostgreSQL database adapter.

    Attributes:
       logger (:obj:`Logger`): .
       name_table (:obj:`str`): Table name in database.

    """

    def __init__(self):
        # Enable logging
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Table name in database
        self.name_table = 'users'

        parse.uses_netloc.append("postgres")
        database_url = parse.urlparse(os.environ["DATABASE_URL"])

        try:
            # Connection to database
            self.conn = psycopg2.connect(
                database=database_url.path[1:],
                user=database_url.username,
                password=database_url.password,
                host=database_url.hostname,
                port=database_url.port
            )

            # If table not exists in database
            with self.conn:
                with self.conn.cursor() as cur:
                    cur.execute("CREATE TABLE IF NOT EXISTS {} (username varchar(32), group_name varchar(21), "
                                "user_id varchar);".format(self.name_table))
        except psycopg2.ProgrammingError as error_text:
            self.logger.error(error_text)

    def add_new_user(self, username, group_name, user_id):
        """Add a new user to the database.

        If the user exists, will compare the incoming group with
        the group in the database and overwrite if it does not match.

        Args:
            username (:obj:`str`): The username in telegram.
            user_id (:obj:`str`, optional): The telegram user id.
            group_name (:obj:`str`, optional): The group id for use in API.

        """

        try:
            with self.conn:
                with self.conn.cursor() as cur:
                    cur.execute("SELECT user_id FROM {} " 
                                "WHERE user_id = '{}';".format(self.name_table, user_id))
                    try:
                        cur.fetchall()[0][0]
                    except IndexError:
                        cur.execute("INSERT INTO {} (username, group_name, user_id) "
                                    "VALUES ('{}', '{}', '{}');".format(self.name_table, username,
                                                                        group_name, user_id))
                    else:
                        cur.execute("UPDATE {} SET group_name='{}' "
                                    "WHERE user_id = '{}';".format(self.name_table,
                                                                   group_name, user_id))
        except psycopg2.ProgrammingError as error_text:
            self.logger.error(error_text)

    def registry(self, user_id):
        """Checks the user's entry in the database.

        Add a new user to the database if the user exists,
        will compare the incoming group with the group in
        the database and overwrite if it does not match.

        Args:
            user_id (:obj:`str`): The telegram user id.

        Returns:
            :obj:`boolean`: Return True if user exists, else False.

        """
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM {} "
                            "WHERE user_id = '{}';".format(self.name_table, user_id))
                try:
                    cur.fetchall()[0][0]
                except IndexError:
                    return False
                else:
                    return True

    def all_users(self):
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute("SELECT user_id FROM {};".format(self.name_table))
                try:
                    cur.fetchall()[0]
                except IndexError:
                    return ()
                else:
                    return cur.fetchall()[0]

    def get_group_name(self, user_id):
        """##

        #

        Args:
            user_id (:obj:`str`): The telegram user id.

        Returns:
            :obj:`str`: Return group_name if user exists, raise IndexError.

        """
        with self.conn:
            with self.conn.cursor() as cur:
                try:
                    cur.execute("SELECT group_name FROM {} "
                                "WHERE user_id = '{}';".format(self.name_table, user_id))
                    return cur.fetchall()[0][0]
                except IndexError as error_text:
                    self.logger.error(error_text)


if __name__ == '__main__':
    user_db = UserDatabase()

