import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import requests
import configparser
import json


class ComponentsWindow(tk.Toplevel):
    def __init__(self, parent, token):
        super().__init__(parent)
        self.parent = parent
        self.token = token
        print(f"Token received in ComponentsWindow: {self.token}")
        self.title("Управление комплектующими")
        self.geometry("800x600")

        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.api_url = self.config.get("API", "url")

        self.tree = ttk.Treeview(self, columns=("ID", "Название", "Описание",
                                 "Категория", "Производитель", "Цена", "Количество"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Название", text="Название")
        self.tree.heading("Описание", text="Описание")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Производитель", text="Производитель")
        self.tree.heading("Цена", text="Цена")
        self.tree.heading("Количество", text="Количество")
        self.tree.pack(expand=True, fill="both")

        self.add_button = ttk.Button(
            self, text="Добавить", command=self.add_component)
        self.add_button.pack(pady=5)

        self.edit_button = ttk.Button(
            self, text="Изменить", command=self.edit_component)
        self.edit_button.pack(pady=5)

        self.delete_button = ttk.Button(
            self, text="Удалить", command=self.delete_component)
        self.delete_button.pack(pady=5)

        self.load_components()

    def load_components(self):
        # Очищаем Treeview перед загрузкой данных
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.api_url}/components", headers=headers)
            response.raise_for_status()
            components = response.json()

            for component in components:
                self.tree.insert("", "end", values=(
                    component["component_id"],
                    component["component_name"],
                    component["description"],
                    component["category_id"],
                    component["manufacturer_id"],
                    component["price"],
                    component["quantity_in_stock"]
                ))

        except requests.exceptions.RequestException as e:
            messagebox.showerror(
                "Ошибка", f"Ошибка при загрузке компонентов: {e}")

    def add_component(self):
        # Передаем load_components
        ComponentForm(self, self.token, self.load_components)

    def edit_component(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo(
                "Внимание", "Выберите компонент для редактирования.")
            return

        component_id = self.tree.item(selected_item, "values")[0]
        ComponentForm(self, self.token, self.load_components,
                      component_id=component_id)

    def delete_component(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Внимание", "Выберите компонент для удаления.")
            return

        component_id = self.tree.item(selected_item, "values")[0]
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот компонент?"):
            try:
                headers = {"Authorization": f"Bearer {self.token}"}
                response = requests.delete(
                    f"{self.api_url}/components/{component_id}", headers=headers)
                response.raise_for_status()
                self.load_components()  # Обновляем Treeview
                messagebox.showinfo("Успех", "Компонент успешно удален.")
            except requests.exceptions.RequestException as e:
                messagebox.showerror(
                    "Ошибка", f"Ошибка при удалении компонента: {e}")


class ComponentForm(tk.Toplevel):
    def __init__(self, parent, token, refresh_callback, component_id=None):
        super().__init__(parent)
        self.parent = parent
        self.token = token
        # Сохраняем ссылку на функцию обновления
        self.refresh_callback = refresh_callback
        self.component_id = component_id
        self.title("Добавить/Редактировать компонент")
        self.geometry("400x450")  # Увеличиваем высоту окна
        self.transient(parent)  # Делаем окно модальным
        self.grab_set()  # Перехватываем все события

        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.api_url = self.config.get("API", "url")

        self.component_name_label = ttk.Label(self, text="Название:")
        self.component_name_label.pack(pady=5)
        self.component_name_entry = ttk.Entry(self, width=30)
        self.component_name_entry.pack(pady=5)

        self.description_label = ttk.Label(self, text="Описание:")
        self.description_label.pack(pady=5)
        self.description_entry = ttk.Entry(self, width=30)
        self.description_entry.pack(pady=5)

        self.category_id_label = ttk.Label(self, text="ID категории:")
        self.category_id_label.pack(pady=5)
        self.category_id_entry = ttk.Entry(self, width=30)
        self.category_id_entry.pack(pady=5)

        self.manufacturer_id_label = ttk.Label(self, text="ID производителя:")
        self.manufacturer_id_label.pack(pady=5)
        self.manufacturer_id_entry = ttk.Entry(self, width=30)
        self.manufacturer_id_entry.pack(pady=5)

        self.price_label = ttk.Label(self, text="Цена:")
        self.price_label.pack(pady=5)
        self.price_entry = ttk.Entry(self, width=30)
        self.price_entry.pack(pady=5)

        self.quantity_in_stock_label = ttk.Label(
            self, text="Количество на складе:")
        self.quantity_in_stock_label.pack(pady=5)
        self.quantity_in_stock_entry = ttk.Entry(self, width=30)
        self.quantity_in_stock_entry.pack(pady=5)

        self.save_button = ttk.Button(
            self, text="Сохранить", command=self.save_component)
        self.save_button.pack(pady=10)

        if self.component_id:
            self.load_component_data()

    def load_component_data(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.api_url}/components/{self.component_id}", headers=headers)
            response.raise_for_status()
            component = response.json()

            self.component_name_entry.insert(0, component["component_name"])
            self.description_entry.insert(0, component["description"])
            self.category_id_entry.insert(0, component["category_id"])
            self.manufacturer_id_entry.insert(0, component["manufacturer_id"])
            self.price_entry.insert(0, component["price"])
            self.quantity_in_stock_entry.insert(
                0, component["quantity_in_stock"])

        except requests.exceptions.RequestException as e:
            messagebox.showerror(
                "Ошибка", f"Ошибка при загрузке данных компонента: {e}")

    def save_component(self):
        component_name = self.component_name_entry.get()
        description = self.description_entry.get()
        category_id = self.category_id_entry.get()
        manufacturer_id = self.manufacturer_id_entry.get()
        price = self.price_entry.get()
        quantity_in_stock = self.quantity_in_stock_entry.get()

        if not all([component_name, description, category_id, manufacturer_id, price, quantity_in_stock]):
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
            return

        try:
            category_id = int(category_id)
            manufacturer_id = int(manufacturer_id)
            price = float(price)
            quantity_in_stock = int(quantity_in_stock)
        except ValueError:
            messagebox.showerror(
                "Ошибка", "Неверный формат данных. Проверьте числовые поля.")
            return

        data = {
            "component_name": component_name,
            "description": description,
            "category_id": category_id,
            "manufacturer_id": manufacturer_id,
            "price": price,
            "quantity_in_stock": quantity_in_stock
        }

        headers = {"Authorization": f"Bearer {self.token}",
                   "Content-Type": "application/json"}

        try:
            if self.component_id:
                response = requests.put(
                    f"{self.api_url}/components/{self.component_id}", headers=headers, json=data)
            else:
                response = requests.post(
                    f"{self.api_url}/components", headers=headers, json=data)

            response.raise_for_status()
            messagebox.showinfo("Успех", "Компонент успешно сохранен.")
            self.destroy()  # Закрываем окно формы
            self.refresh_callback()  # Вызываем функцию обновления
        except requests.exceptions.RequestException as e:
            messagebox.showerror(
                "Ошибка", f"Ошибка при сохранении компонента: {e}")
