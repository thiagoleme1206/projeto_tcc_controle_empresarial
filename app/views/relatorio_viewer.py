import tkinter as tk
from tkinter import ttk, messagebox
from app.services.relatorio_service import RelatorioService
from app.services.auditoria_service import AuditoriaService

class RelatorioViewer:
    def __init__(self, master, usuario):
        self.master = master
        self.usuario = usuario

        # Acesso restrito a TI e Gerência
        if self.usuario.grupo not in ["ti", "gerencia"]:
            messagebox.showerror("Acesso negado", "❌ Este módulo é restrito à TI e Gerência.")
            self.master.destroy()
            return

        self.relatorio_service = RelatorioService()
        self.auditoria = AuditoriaService()

        self.master.title("📊 Relatórios Financeiros")
        self.master.geometry("500x300")
        self.centralizar_janela(500, 300)
        self.master.configure(bg="#f0f2f5")

        self.create_widgets()

    def centralizar_janela(self, largura, altura):
        """Centraliza a janela na tela."""
        self.master.update_idletasks()
        largura_tela = self.master.winfo_screenwidth()
        altura_tela = self.master.winfo_screenheight()
        x = (largura_tela // 2) - (largura // 2)
        y = (altura_tela // 2) - (altura // 2)
        self.master.geometry(f"{largura}x{altura}+{x}+{y}")

    def create_widgets(self):
        titulo = ttk.Label(self.master, text="📊 Gerar Relatório por OS", font=("Helvetica", 16, "bold"))
        titulo.pack(pady=20)

        frame_input = ttk.Frame(self.master)
        frame_input.pack(pady=10)

        ttk.Label(frame_input, text="Número da OS:").grid(row=0, column=0, padx=5)
        self.os_entry = ttk.Entry(frame_input, width=30)
        self.os_entry.grid(row=0, column=1, padx=5)

        gerar_btn = ttk.Button(self.master, text="Gerar Relatório", command=self.gerar_relatorio)
        gerar_btn.pack(pady=20)

        voltar_btn = ttk.Button(self.master, text="Voltar", command=self.master.destroy)
        voltar_btn.pack()

    def gerar_relatorio(self):
        numero_os = self.os_entry.get().strip()
        if not numero_os:
            messagebox.showwarning("Campo obrigatório", "Digite o número da OS.")
            return

        try:
            self.relatorio_service.gerar_relatorio_por_os(numero_os)
            self.auditoria.registrar_acao(
                self.usuario.login,
                "RELATORIO_GERADO",
                "relatorios",
                f"Relatório gerado para OS {numero_os}"
            )
            messagebox.showinfo("Sucesso", f"✅ Relatório gerado com sucesso!\nArquivo salvo na pasta atual.")
        except ValueError as ve:
            messagebox.showerror("Erro", str(ve))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {e}")
