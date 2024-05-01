import psycopg2
from config.config import host, user, password, db_name


class SQL:
    @staticmethod
    def check_limit(user_id: int) -> bool:
        """Проверка на ограничение в 11 записей"""
        if len(SQL.get_requests(user_id)) > 11:
            return False
        return True

    @staticmethod
    def get_requests(user_id=None) -> list:
        where = f'WHERE user_id = {user_id}' if user_id else ''
        query = f"""
            SELECT *
            FROM user_requests
            {where}"""
        return SQL.send_request(query, fetch=True)

    @staticmethod
    def add_request(data: tuple):
        query = f"""
            INSERT INTO user_requests (user_id, warehouse, cargo, time_interested, value_interested)
            VALUES {data};"""
        SQL.send_request(query)

    @staticmethod
    def del_request(request_id: str):
        query = f"""DELETE FROM user_requests WHERE id = {request_id}"""
        SQL.send_request(query)

    @staticmethod
    def send_request(query, fetch=False):
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
                if fetch:
                    return cursor.fetchall()
        except Exception as _ex:
            print("[INFO] Error while working with PostgreSQL", _ex)
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgreSQL connection closed")

