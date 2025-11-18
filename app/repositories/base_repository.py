from app.database.db_connection import DatabaseConnection

class BaseRepository:

    def __init__(self):
        self.conn = DatabaseConnection().get_connection()

    def execute(self, query, params=None, fetchone=False, fetchall=False, commit=False):
        """
        Executa uma query com fechamento automático do cursor.
        """
        with self.conn.cursor() as cur:
            try:
                cur.execute(query, params or ())

                if fetchone:
                    return cur.fetchone()

                if fetchall:
                    return cur.fetchall()

                if commit:
                    self.conn.commit()

            except Exception as e:
                self.conn.rollback()
                raise e
