class Orcamento:
    def __init__(
        self,
        numero_os,
        data_orcamento,
        mao_de_obra=None,
        alimentacao=None,
        hospedagem=None,
        viagem=None,
        seguranca_trabalho=None,
        material=None,
        equipamento=None,
        andaime=None,
        documentacao=None,
        outros=None,
        id_orcamento=None
    ):
        self.id_orcamento = id_orcamento
        self.numero_os = numero_os
        self.data_orcamento = data_orcamento
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
        """Soma automática dos valores numéricos."""
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
