from app.models.receita_model import Receita
from app.repositories.receita_repository import ReceitaRepository
from app.repositories.projeto_repository import ProjetoRepository
from app.repositories.cliente_repository import ClienteRepository

class ReceitaService:
    def __init__(self):
        self.repo = ReceitaRepository()
        self.projeto_repo = ProjetoRepository()
        self.cliente_repo = ClienteRepository()

    def criar_receita(self, receita: Receita):
        self._validar_os_existente(receita.numero_os_projeto)

        # Cálculo do valor líquido
        servico = receita.valor_servico or 0
        material = receita.valor_material or 0
        perc_imposto = receita.imposto or 0
        perc_icms = receita.icms or 0

        if servico > 0:
            valor_imposto = servico * (perc_imposto / 100)
            valor_icms = 0
            receita.valor_liquido = servico - valor_imposto
        elif material > 0:
            valor_imposto = material * (perc_imposto / 100)
            base_icms = material - valor_imposto
            valor_icms = base_icms * (perc_icms / 100)
            receita.valor_liquido = material - valor_imposto - valor_icms
        else:
            receita.valor_liquido = 0.0

        return self.repo.criar(receita)

    def listar_receitas(self):
        return self.repo.listar_todos()

    def buscar_por_os(self, numero_os: int):
        return self.repo.buscar_por_os(numero_os)

    def buscar_por_id(self, id_receita: int):
        return self.repo.buscar_por_id(id_receita)

    def atualizar_receita(self, receita: Receita):
        valor_servico = float(receita.valor_servico or 0)
        valor_material = float(receita.valor_material or 0)
        perc_imposto = float(receita.imposto or 0)
        perc_icms = float(receita.icms or 0)

        if valor_servico > 0:
            valor_imposto = valor_servico * (perc_imposto / 100)
            valor_icms = 0
            liquido = valor_servico - valor_imposto
        elif valor_material > 0:
            valor_imposto = valor_material * (perc_imposto / 100)
            base_icms = valor_material - valor_imposto
            valor_icms = base_icms * (perc_icms / 100)
            liquido = valor_material - valor_imposto - valor_icms
        else:
            liquido = 0

        receita.valor_liquido = liquido

        # ✅ CHAMADA QUE ESTAVA FALTANDO
        self.repo.atualizar(receita)

    def excluir_receita(self, id_receita: int):
        return self.repo.excluir(id_receita)

    def _validar_os_existente(self, numero_os):
        projeto = self.projeto_repo.buscar_por_os(numero_os)
        if not projeto:
            raise ValueError("Número de OS não localizado na base de projetos.")