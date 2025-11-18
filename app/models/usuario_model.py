class Usuario:
    def __init__(self, id, nome, login, senha_hash, grupo, ativo=True):
        self.id = id
        self.nome = nome
        self.login = login
        self.senha_hash = senha_hash
        self.grupo = grupo
        self.ativo = ativo
