import psycopg2

class DatabaseConnection:
    _instance = None

    def __init__(self):
        if not DatabaseConnection._instance:
            try:
                DatabaseConnection._instance = psycopg2.connect(
                    dbname="projetofinal",
                    user="postgres",
                    password="Edu1Sal2",
                    host="localhost",
                    port="5432"
                )
            except Exception as e:
                print("Erro ao conectar com banco de dados:", e)
                raise e

    def get_connection(self):
        return DatabaseConnection._instance
