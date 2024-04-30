import psycopg2
from config.config import host, user, password, db_name


class SQL:
    @staticmethod
    def add_user_request(data: tuple):
        query = f"""
            INSERT INTO user_requests
            VALUES {data};"""
        SQL.send_request(query)

    @staticmethod
    def send_request(query):
        try:
            # connect to exist database
            connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
            connection.autocommit = True

            with connection.cursor() as cursor:
                cursor.execute(query)
        except Exception as _ex:
            print("[INFO] Error while working with PostgreSQL", _ex)
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgreSQL connection closed")
