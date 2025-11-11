from app.database.db_connection import DatabaseConnection
from app.models.clientes_model import Cliente

class ClienteRepository:
    def __init__(self):
        self.conn = DatabaseConnection().get_connection()

    def listar_todos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id_cliente, cpf_cnpj, nome FROM clientes ORDER BY id_cliente")
        rows = cursor.fetchall()
        return [Cliente(*row) for row in rows]

    def buscar_por_id(self, id_cliente):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id_cliente, cpf_cnpj, nome FROM clientes WHERE id_cliente = %s", (id_cliente,))
        row = cursor.fetchone()
        return Cliente(*row) if row else None

    def criar_cliente(self, cpf_cnpj, nome):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO clientes (cpf_cnpj, nome)
                VALUES (%s, %s)
                RETURNING id_cliente;
            """, (cpf_cnpj, nome))
            self.conn.commit()
            return cur.fetchone()[0]

    def atualizar_cliente(self, id_cliente, cpf_cnpj, nome):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE clientes
                SET cpf_cnpj = %s, nome = %s
                WHERE id_cliente = %s
            """, (cpf_cnpj, nome, id_cliente))
            self.conn.commit()
            return cur.rowcount > 0

    def excluir_cliente(self, id_cliente):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))
            self.conn.commit()
            return cur.rowcount > 0