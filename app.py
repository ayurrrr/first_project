import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import ttk, messagebox

from converter_tab import ConverterTab
from game_tab import GameTab
from portfolio import Portfolio
from rates import FALLBACK_RATES, get_rates

SAVE_FILE = Path(__file__).with_name("portfolio.json")

# Цвета тем: фон окна, текст, поля ввода, кнопки, результат, подписи
THEMES = {
    "light": {"bg": "#f0f0f0", "fg": "#000000", "field": "#ffffff",
              "button": "#e1e1e1", "result": "#107c10", "hint": "gray"},
    "dark": {"bg": "#2b2b2b", "fg": "#f0f0f0", "field": "#3c3c3c",
             "button": "#454545", "result": "#4ec94e", "hint": "#aaaaaa"},
}


def load_portfolio():
    """Загружает сохранённый портфель. Если файл повреждён, начинает заново"""
    try:
        return Portfolio.load(SAVE_FILE)
    except (OSError, ValueError, KeyError, TypeError):
        messagebox.showwarning("Внимание", "Файл портфеля повреждён. Начинаем с чистого листа.")
        return Portfolio()


class App:
    """Главное окно: вкладки, общие курсы, обновление и тема"""

    def __init__(self, root):
        self.root = root
        self.rates = dict(FALLBACK_RATES)
        self.theme = "light"
        self.portfolio = load_portfolio()

        root.title("Конвертер и торговый симулятор")
        root.geometry("480x660")
        root.resizable(False, False)
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Вкладки
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        self.converter = ConverterTab(self.notebook)
        self.game = GameTab(self.notebook, self.portfolio)
        self.notebook.add(self.converter, text="Конвертер")
        self.notebook.add(self.game, text="Симулятор")

        # Список вкладок: у каждой есть set_rates, on_enter и apply_colors
        self.tabs = [self.converter, self.game]

        # Нижняя панель: общие для всех вкладок кнопки и статус
        bottom = ttk.Frame(root)
        bottom.pack(fill="x", padx=10, pady=8)
        ttk.Button(bottom, text="Обновить курсы", command=self.refresh_rates).pack(side="left")
        self.label_status = ttk.Label(bottom, text="", font=("Arial", 8))
        self.label_status.pack(side="left", padx=10)
        self.btn_theme = ttk.Button(bottom, text="Тёмная тема", command=self.toggle_theme)
        self.btn_theme.pack(side="right")

        # Enter работает на той вкладке, которая сейчас открыта
        root.bind("<Return>", self.on_enter)

        self.apply_theme(self.theme)
        self.set_rates(self.rates)
        # Курсы грузим после показа окна, чтобы оно открылось сразу
        root.after(100, self.refresh_rates)

    def set_rates(self, rates):
        """Раздаёт курсы всем вкладкам"""
        self.rates = rates
        for tab in self.tabs:
            tab.set_rates(rates)

    def refresh_rates(self):
        """Загружает курсы и показывает, откуда они"""
        self.label_status.config(text="Загрузка курсов...")
        self.root.update_idletasks()  # показываем надпись до начала загрузки

        rates, ok = get_rates()
        self.set_rates(rates)
        if ok:
            self.label_status.config(text=f"Курсы обновлены в {datetime.now():%H:%M:%S}")
        else:
            self.label_status.config(text="Нет связи: запасные курсы (устарели)")

    def on_enter(self, event=None):
        self.tabs[self.notebook.index("current")].on_enter()

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.apply_theme(self.theme)
        self.btn_theme.config(text="Светлая тема" if self.theme == "dark" else "Тёмная тема")

    def apply_theme(self, name):
        """Перекрашивает всё окно в выбранную тему"""
        colors = THEMES[name]

        self.root.configure(bg=colors["bg"])
        self.style.configure("TFrame", background=colors["bg"])
        self.style.configure("TLabel", background=colors["bg"], foreground=colors["fg"])
        self.style.configure("TButton", background=colors["button"], foreground=colors["fg"])
        self.style.map("TButton", background=[("active", colors["field"])])
        self.style.configure("TEntry", fieldbackground=colors["field"], foreground=colors["fg"])
        self.style.configure("TCombobox", background=colors["button"], foreground=colors["fg"])
        self.style.map("TCombobox", fieldbackground=[("readonly", colors["field"])])
        self.style.configure("TNotebook", background=colors["bg"])
        self.style.configure("TNotebook.Tab", background=colors["button"], foreground=colors["fg"])
        self.style.map("TNotebook.Tab", background=[("selected", colors["field"])])
        # Таблица на вкладке симулятора
        self.style.configure("Treeview", background=colors["field"],
                             fieldbackground=colors["field"], foreground=colors["fg"])
        self.style.configure("Treeview.Heading", background=colors["button"], foreground=colors["fg"])

        self.label_status.config(foreground=colors["hint"])
        for tab in self.tabs:
            tab.apply_colors(colors)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
