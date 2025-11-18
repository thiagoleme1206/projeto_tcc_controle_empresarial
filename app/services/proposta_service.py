from app.repositories.proposta_repository import PropostaRepository
from app.models.proposta_model import Proposta

class PropostaService:
    def __init__(self):
        self.repo = PropostaRepository()

    # --------------------------------
    # Helpers
    # --------------------------------

    def _to_float(self, valor, default=0.0):
        try:
            return float(valor)
        except (ValueError, TypeError):
            return default

    def _validar_campos_obrigatorios(self, titulo, descricao, status):
        if not titulo or not titulo.strip():
            raise ValueError("❌ O título da proposta é obrigatório.")

        if not descricao or not descricao.strip():
            raise ValueError("❌ A descrição da proposta é obrigatória.")

        if not status or not status.strip():
            raise ValueError("❌ O status da proposta é obrigatório.")

    def _validar_existe(self, id):
        proposta = self.repo.buscar_por_id(id)
        if not proposta:
            raise ValueError(f"❌ Proposta com ID {id} não encontrada.")
        return proposta

    # --------------------------------
    # Operações principais
    # --------------------------------

    def listar_propostas(self):
        return self.repo.listar_todas()

    def cadastrar_proposta(self, titulo, descricao, valor, status):
        # Validação
        self._validar_campos_obrigatorios(titulo, descricao, status)

        # Conversão segura
        valor = self._to_float(valor)

        proposta = Proposta(
            id=None,
            titulo=titulo.strip(),
            descricao=descricao.strip(),
            valor=valor,
            status=status.strip(),
            criado_em=None
        )

        self.repo.inserir(proposta)
        return True

    def atualizar_proposta(self, id, titulo, descricao, valor, status):
        # Valida existência
        self._validar_existe(id)

        # Valida campos obrigatórios
        self._validar_campos_obrigatorios(titulo, descricao, status)

        # Converte valores numéricos
        valor = self._to_float(valor)

        proposta = Proposta(
            id=id,
            titulo=titulo.strip(),
            descricao=descricao.strip(),
            valor=valor,
            status=status.strip(),
            criado_em=None
        )

        self.repo.atualizar(proposta)
        return True

    def deletar_proposta(self, id):
        self._validar_existe(id)
        self.repo.deletar(id)
        return True
