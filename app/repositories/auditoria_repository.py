from app.repositories.base_repository import BaseRepository


class AuditoriaRepository(BaseRepository):

    def registrar(self, nome_usuario, acao, modulo, descricao, data_hora):
        self.execute(
            """
            INSERT INTO auditoria (nome_usuario, acao, modulo, descricao, data_hora)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (nome_usuario, acao, modulo, descricao, data_hora),
            commit=True
        )

    def consultar_por_usuario(self, nome_usuario):
        return self.execute(
            """
            SELECT nome_usuario, acao, modulo, descricao, data_hora
            FROM auditoria
            WHERE nome_usuario ILIKE %s
            ORDER BY data_hora DESC
            """,
            (f"%{nome_usuario.strip()}%",),
            fetchall=True
        )

    def consultar_por_data(self, data):
        return self.execute(
            """
            SELECT nome_usuario, acao, modulo, descricao, data_hora
            FROM auditoria
            WHERE data_hora::date = %s
            ORDER BY data_hora DESC
            """,
            (data,),
            fetchall=True
        )
