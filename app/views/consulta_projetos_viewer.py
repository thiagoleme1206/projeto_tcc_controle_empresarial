import tkinter as tk
from tkinter import ttk, messagebox
from app.database.db_connection import DatabaseConnection

class ConsultaProjetosViewer:
    def __init__(self, root, usuario_logado):
        self.usuario = usuario_logado
        self.grupo = usuario_logado.grupo

        if self.grupo not in ["gerencia", "engenheiro", "financeiro", "ti"]:
            messagebox.showerror("Acesso Negado", "Você não tem permissão para acessar este módulo.")
            return

        self.root = tk.Toplevel(root)
        self.root.title("🔍 Consulta de Projetos")
        self.root.geometry("1100x500")

        self.conn = DatabaseConnection().get_connection()

        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.pack(fill="both", expand=True)

        self.criar_widgets()
        self.carregar_projetos()

    def criar_widgets(self):
        ttk.Label(self.frame, text="🔍 Consulta de Projetos", font=("Helvetica", 16, "bold")).pack(pady=10)

        colunas = ("Número OS", "Tipo Projeto", "Cliente", "Valor Total Orçamento", "Valor Total Despesas", "Valor Total Receitas")
        self.tree = ttk.Treeview(self.frame, columns=colunas, show="headings", height=15)
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=160)

        self.tree.pack(fill="both", expand=True, pady=10)

        filtro_frame = ttk.Frame(self.frame)
        filtro_frame.pack(fill="x", pady=5)

        ttk.Label(filtro_frame, text="🔍 Buscar por Nº OS:").pack(side="left", padx=5)
        self.entrada_os = ttk.Entry(filtro_frame, width=20)
        self.entrada_os.pack(side="left")
        ttk.Button(filtro_frame, text="Buscar", command=self.filtrar_por_os).pack(side="left", padx=5)

        ttk.Button(self.frame, text="🔄 Atualizar", command=self.carregar_projetos).pack(pady=5)

    def carregar_projetos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        cursor = self.conn.cursor()
        query = """
            SELECT p.numero_os, p.tipo, p.cliente_nome,
                   COALESCE(o.total, 0) AS valor_orcamento,
                   COALESCE(SUM(d.total), 0) AS valor_despesas,
                   COALESCE(SUM(r.valor_liquido), 0) AS valor_receitas
            FROM projetos p
            LEFT JOIN orcamentos o ON o.numero_os_projeto = p.numero_os
            LEFT JOIN despesas d ON d.numero_os_projeto = p.numero_os
            LEFT JOIN receitas r ON r.numero_os_projeto = p.numero_os
            GROUP BY p.numero_os, p.tipo, p.cliente_nome, o.total
            ORDER BY p.numero_os DESC
        """
        cursor.execute(query)
        projetos = cursor.fetchall()

        for p in projetos:
            self.tree.insert("", "end", values=(
                p[0], p[1], p[2], f"R${p[3]:.2f}", f"R${p[4]:.2f}", f"R${p[5]:.2f}"
            ))

    def filtrar_por_os(self):
        numero_os = self.entrada_os.get().strip()
        if not numero_os.isdigit():
            messagebox.showerror("Erro", "Digite um número de OS válido.")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        cursor = self.conn.cursor()
        query = """
            SELECT p.numero_os, p.tipo, p.cliente_nome,
                   COALESCE(o.total, 0) AS valor_orcamento,
                   COALESCE(SUM(d.total), 0) AS valor_despesas,
                   COALESCE(SUM(r.valor_liquido), 0) AS valor_receitas
            FROM projetos p
            LEFT JOIN orcamentos o ON o.numero_os_projeto = p.numero_os
            LEFT JOIN despesas d ON d.numero_os_projeto = p.numero_os
            LEFT JOIN receitas r ON r.numero_os_projeto = p.numero_os
            WHERE p.numero_os = %s
            GROUP BY p.numero_os, p.tipo, p.cliente_nome, o.total
        """
        cursor.execute(query, (numero_os,))
        projetos = cursor.fetchall()

        if not projetos:
            messagebox.showinfo("Aviso", f"Nenhum projeto encontrado com o número OS {numero_os}.")
            return

        for p in projetos:
            self.tree.insert("", "end", values=(
                p[0], p[1], p[2], f"R${p[3]:.2f}", f"R${p[4]:.2f}", f"R${p[5]:.2f}"
            ))
