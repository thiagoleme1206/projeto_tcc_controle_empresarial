from datetime import datetime
from app.repositories.auditoria_repository import AuditoriaRepository


class AuditoriaService:

    def __init__(self):
        self.repo = AuditoriaRepository()

    def registrar_acao(self, nome_usuario, acao, modulo, descricao=None):
        """
        Apenas coordena a regra de negócio.
        A responsabilidade do banco é do repository.
        """
        self.repo.registrar(
            nome_usuario=nome_usuario,
            acao=acao,
            modulo=modulo,
            descricao=descricao,
            data_hora=datetime.now()
        )

    def consultar_por_usuario(self, nome_usuario):
        return self.repo.consultar_por_usuario(nome_usuario)

    def consultar_por_data(self, data):
        return self.repo.consultar_por_data(data)
