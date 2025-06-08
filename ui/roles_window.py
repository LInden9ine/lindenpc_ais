import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import requests
import configparser
import json


class RolesWindow(tk.Toplevel):
    def __init__(self, parent, token):
        super().__init__(parent)
        self.parent = parent
        self.token = token
        self.title("Управление ролями")
        self.geometry("600x400")

        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.api_url = self.config.get("API", "url")

        self.tree = ttk.Treeview(self, columns=(
            "ID", "Название", "Описание"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Название", text="Название")
        self.tree.heading("Описание", text="Описание")
        self.tree.pack(expand=True, fill="both")

        self.add_button = ttk.Button(
            self, text="Добавить", command=self.add_role)
        self.add_button.pack(pady=5)

        self.edit_button = ttk.Button(
            self, text="Изменить", command=self.edit_role)
        self.edit_button.pack(pady=5)

        self.delete_button = ttk.Button(
            self, text="Удалить", command=self.delete_role)
        self.delete_button.pack(pady=5)

        self.load_roles()

    def load_roles(self):
        # Очищаем Treeview перед загрузкой данных
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{self.api_url}/roles", headers=headers)
            response.raise_for_status()
            roles = response.json()

            for role in roles:
                self.tree.insert("", "end", values=(
                    role["role_id"], role["role_name"], role["description"]))

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке ролей: {e}")

    def add_role(self):
        RoleForm(self, self.token, self.load_roles)

    def edit_role(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo(
                "Внимание", "Выберите роль для редактирования.")
            return

        role_id = self.tree.item(selected_item, "values")[0]
        RoleForm(self, self.token, self.load_roles, role_id=role_id)

    def delete_role(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Внимание", "Выберите роль для удаления.")
            return

        role_id = self.tree.item(selected_item, "values")[0]
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту роль?"):
            try:
                headers = {"Authorization": f"Bearer {self.token}"}
                response = requests.delete(
                    f"{self.api_url}/roles/{role_id}", headers=headers)
                response.raise_for_status()
                self.load_roles()  # Обновляем Treeview
                messagebox.showinfo("Успех", "Роль успешно удалена.")
            except requests.exceptions.RequestException as e:
                messagebox.showerror(
                    "Ошибка", f"Ошибка при удалении роли: {e}")


class RoleForm(tk.Toplevel):
    def __init__(self, parent, token, refresh_callback, role_id=None):
        super().__init__(parent)
        self.parent = parent
        self.token = token
        self.refresh_callback = refresh_callback
        self.role_id = role_id
        self.title("Добавить/Редактировать роль")
        self.geometry("400x300")

        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.api_url = self.config.get("API", "url")

        self.role_name_label = ttk.Label(self, text="Название роли:")
        self.role_name_label.pack(pady=5)
        self.role_name_entry = ttk.Entry(self, width=30)
        self.role_name_entry.pack(pady=5)

        self.description_label = ttk.Label(self, text="Описание:")
        self.description_label.pack(pady=5)
        self.description_entry = ttk.Entry(self, width=30)
        self.description_entry.pack(pady=5)

        self.save_button = ttk.Button(
            self, text="Сохранить", command=self.save_role)
        self.save_button.pack(pady=10)

        if self.role_id:
            self.load_role_data()

    def load_role_data(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.api_url}/roles/{self.role_id}", headers=headers)
            response.raise_for_status()
            role = response.json()

            self.role_name_entry.insert(0, role["role_name"])
            self.description_entry.insert(0, role["description"])

        except requests.exceptions.RequestException as e:
            messagebox.showerror(
                "Ошибка", f"Ошибка при загрузке данных роли: {e}")

    def save_role(self):
        role_name = self.role_name_entry.get()
        description = self.description_entry.get()

        if not role_name:
            messagebox.showerror(
                "Ошибка", "Пожалуйста, введите название роли.")
            return

        data = {
            "role_name": role_name,
            "description": description
        }

        headers = {"Authorization": f"Bearer {self.token}",
                   "Content-Type": "application/json"}

        try:
            if self.role_id:
                response = requests.put(
                    f"{self.api_url}/roles/{self.role_id}", headers=headers, json=data)
            else:
                response = requests.post(
                    f"{self.api_url}/roles", headers=headers, json=data)

            response.raise_for_status()
            messagebox.showinfo("Успех", "Роль успешно сохранена.")
            self.destroy()
            self.refresh_callback()
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении роли: {e}")
