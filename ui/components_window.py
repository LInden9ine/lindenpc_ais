# ui/components_window.py
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import requests
import json

# Окно управления компонентами


class ComponentsWindow(tk.Toplevel):
    def __init__(self, master=None):
        print("ComponentsWindow: Initializing")  # Добавлено
        super().__init__(master)
        self.master = master
        self.title("Управление комплектующими")
        self.geometry("800x600")

        self.tree = ttk.Treeview(self, columns=(
            "ID", "Name", "Price", "Quantity"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Название")
        self.tree.heading("Price", text="Цена")
        self.tree.heading("Quantity", text="Количество")
        self.tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.load_components()  # Загрузка списка компонентов
        print("ComponentsWindow: Initialized")  # Добавлено

    def load_components(self):
        print("load_components: Starting")  # Добавлено
        if not self.master.token:
            messagebox.showerror("Ошибка", "Необходимо авторизоваться")
            print("load_components: Finished (no token)")
            return

        headers = {"Authorization": f"Bearer {self.master.token}"}
        try:
            response = requests.get(
                "http://127.0.0.1:8000/components", headers=headers)
            response.raise_for_status()
            components = response.json()
            for item in self.tree.get_children():
                self.tree.delete(item)
            for component in components:
                self.tree.insert("", tk.END, values=(
                    component["component_id"], component["component_name"], component["price"], component["quantity_in_stock"]))

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Ошибка при получении данных: {e}")
        except (KeyError, TypeError) as e:
            messagebox.showerror(
                "Ошибка", f"Ошибка обработки данных: {e}.  Убедитесь, что API возвращает данные в ожидаемом формате.")
        print("load_components: Finished")  # Добавлено
