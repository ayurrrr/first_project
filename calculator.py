import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Crypto & Fiat Converter v2.0")
root.geometry("400x320")
root.resizable(False, False)

style = ttk.Style()
style.theme_use("clam")

label_title = ttk.Label(root, text="Крипто-Валютный Конвертер", font=("Arial", 14, "bold"))
label_title.pack(pady=15)

frame = ttk.Frame(root)
frame.pack(pady=10)

ttk.Label(frame, text="Сумма:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=5)
entry_amount = ttk.Entry(frame, width=18, font=("Arial", 12))
entry_amount.grid(row=1, column=0, padx=5, pady=5)
entry_amount.insert(0, "100")

ttk.Label(frame, text="Из:", font=("Arial", 10)).grid(row=0, column=1, sticky="w", padx=5)
currencies = ["RUB", "USD", "EUR", "BTC", "ETH"]
combo_from = ttk.Combobox(frame, values=currencies, width=6, font=("Arial", 11), state="readonly")
combo_from.grid(row=1, column=1, padx=5, pady=5)
combo_from.set("USD")

label_arrow = ttk.Label(frame, text="➡️", font=("Arial", 12))
label_arrow.grid(row=1, column=2, padx=5)

ttk.Label(frame, text="В:", font=("Arial", 10)).grid(row=0, column=3, sticky="w", padx=5)
combo_to = ttk.Combobox(frame, values=currencies, width=6, font=("Arial", 11), state="readonly")
combo_to.grid(row=1, column=3, padx=5, pady=5)
combo_to.set("RUB")

btn_convert = ttk.Button(root, text="Рассчитать конвертацию")
btn_convert.pack(pady=20)

label_result = ttk.Label(root, text="Результат: ", font=("Arial", 13, "bold"), foreground="#107c10")
label_result.pack(pady=10)

root.mainloop()
