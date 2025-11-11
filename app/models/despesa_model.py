# app/models/despesa_model.py

class Despesa:
    def __init__(
        self,
        id_despesa=None,
        numero_os_projeto=None,
        data_despesa=None,
        observacao=None,
        mao_de_obra=0.0,
        alimentacao=0.0,
        hospedagem=0.0,
        viagem=0.0,
        seguranca_trabalho=0.0,
        material=0.0,
        equipamento=0.0,
        andaime=0.0,
        documentacao=0.0,
        outros=0.0
    ):
        self.id_despesa = id_despesa
        self.numero_os_projeto = numero_os_projeto
        self.data_despesa = data_despesa
        self.observacao = observacao
        self.mao_de_obra = mao_de_obra
        self.alimentacao = alimentacao
        self.hospedagem = hospedagem
        self.viagem = viagem
        self.seguranca_trabalho = seguranca_trabalho
        self.material = material
        self.equipamento = equipamento
        self.andaime = andaime
        self.documentacao = documentacao
        self.outros = outros

    @property
    def total(self):
        """Soma automática de todos os campos numéricos"""
        return sum([
            self.mao_de_obra or 0,
            self.alimentacao or 0,
            self.hospedagem or 0,
            self.viagem or 0,
            self.seguranca_trabalho or 0,
            self.material or 0,
            self.equipamento or 0,
            self.andaime or 0,
            self.documentacao or 0,
            self.outros or 0
        ])
