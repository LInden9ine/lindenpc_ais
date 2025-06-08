import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import requests
import configparser
import json


class UsersWindow(tk.Toplevel):
    def __init__(self, parent, token):
        super().__init__(parent)
        self.parent = parent
        self.token = token
        self.title("Управление пользователями")
        self.geometry("800x600")

        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.api_url = self.config.get("API", "url")

        self.tree = ttk.Treeview(self, columns=(
            "ID", "Логин", "Email", "Имя", "Фамилия", "Роль"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Логин", text="Логин")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Имя", text="Имя")
        self.tree.heading("Фамилия", text="Фамилия")
        self.tree.heading("Роль", text="Роль")
        self.tree.pack(expand=True, fill="both")

        self.add_button = ttk.Button(
            self, text="Добавить", command=self.add_user)
        self.add_button.pack(pady=5)

        self.edit_button = ttk.Button(
            self, text="Изменить", command=self.edit_user)
        self.edit_button.pack(pady=5)

        self.delete_button = ttk.Button(
            self, text="Удалить", command=self.delete_user)
        self.delete_button.pack(pady=5)

        self.load_users()

    def load_users(self):
        # Очищаем Treeview перед загрузкой данных
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            # Added trailing slash
            response = requests.get(f"{self.api_url}/users/", headers=headers)
            response.raise_for_status()
            users = response.json()

            for user in users:
                self.tree.insert("", "end", values=(
                    user["user_id"], user["login"], user["email"], user["first_name"], user["last_name"], user["role_id"]))

        except requests.exceptions.RequestException as e:
            messagebox.showerror(
                "Ошибка", f"Ошибка при загрузке пользователей: {e}")

    def add_user(self):
        UserForm(self, self.token, self.load_users)

    def edit_user(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo(
                "Внимание", "Выберите пользователя для редактирования.")
            return

        user_id = self.tree.item(selected_item, "values")[0]
        UserForm(self, self.token, self.load_users,
                 user_id=user_id, method="put")  # Pass method

    def delete_user(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo(
                "Внимание", "Выберите пользователя для удаления.")
            return

        user_id = self.tree.item(selected_item, "values")[0]
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этого пользователя?"):
            try:
                headers = {"Authorization": f"Bearer {self.token}"}
                response = requests.delete(
                    f"{self.api_url}/users/{user_id}", headers=headers)
                response.raise_for_status()
                self.load_users()  # Обновляем Treeview
                messagebox.showinfo("Успех", "Пользователь успешно удален.")
            except requests.exceptions.RequestException as e:
                messagebox.showerror(
                    "Ошибка", f"Ошибка при удалении пользователя: {e}")


class UserForm(tk.Toplevel):
    def __init__(self, parent, token, refresh_callback, user_id=None, method="post"):
        super().__init__(parent)
        self.parent = parent
        self.token = token
        self.refresh_callback = refresh_callback
        self.user_id = user_id
        self.method = method  # Save HTTP method
        self.title("Добавить/Редактировать пользователя")
        self.geometry("400x400")

        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.api_url = self.config.get("API", "url")

        self.login_label = ttk.Label(self, text="Логин:")
        self.login_label.pack(pady=5)
        self.login_entry = ttk.Entry(self, width=30)
        self.login_entry.pack(pady=5)

        self.password_label = ttk.Label(self, text="Пароль:")
        self.password_label.pack(pady=5)
        self.password_entry = ttk.Entry(self, show="*", width=30)
        self.password_entry.pack(pady=5)

        self.email_label = ttk.Label(self, text="Email:")
        self.email_label.pack(pady=5)
        self.email_entry = ttk.Entry(self, width=30)
        self.email_entry.pack(pady=5)

        self.first_name_label = ttk.Label(self, text="Имя:")
        self.first_name_label.pack(pady=5)
        self.first_name_entry = ttk.Entry(self, width=30)
        self.first_name_entry.pack(pady=5)

        self.last_name_label = ttk.Label(self, text="Фамилия:")
        self.last_name_label.pack(pady=5)
        self.last_name_entry = ttk.Entry(self, width=30)
        self.last_name_entry.pack(pady=5)

        self.role_label = ttk.Label(self, text="Роль:")
        self.role_label.pack(pady=5)
        self.role_entry = ttk.Entry(self, width=30)
        self.role_entry.pack(pady=5)

        self.save_button = ttk.Button(
            self, text="Сохранить", command=self.save_user)
        self.save_button.pack(pady=10)

        if self.user_id:
            self.load_user_data()

    def load_user_data(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.api_url}/users/{self.user_id}", headers=headers)
            response.raise_for_status()
            user = response.json()

            self.login_entry.insert(0, user["login"])
            self.email_entry.insert(0, user["email"])
            self.first_name_entry.insert(0, user["first_name"])
            self.last_name_entry.insert(0, user["last_name"])
            self.role_entry.insert(0, user["role_id"])

        except requests.exceptions.RequestException as e:
            messagebox.showerror(
                "Ошибка", f"Ошибка при загрузке данных пользователя: {e}")

    def save_user(self):
        login = self.login_entry.get()
        password = self.password_entry.get()  # Получаем пароль из поля ввода
        email = self.email_entry.get()
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        role_id = self.role_entry.get()

        if not all([login, password, email, role_id]):
            messagebox.showerror(
                "Ошибка", "Пожалуйста, заполните все обязательные поля (Логин, Пароль, Email, Роль).")
            return

        try:
            role_id = int(role_id)
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат ID роли.")
            return

        data = {
            "login": login,
            "password": password,  # Отправляем пароль
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "role_id": role_id
        }

        headers = {"Authorization": f"Bearer {self.token}",
                   "Content-Type": "application/json"}

        try:
            if self.method == "put":
                response = requests.put(
                    f"{self.api_url}/users/{self.user_id}", headers=headers, json=data)
            else:
                response = requests.post(
                    f"{self.api_url}/users", headers=headers, json=data)

            response.raise_for_status()
            messagebox.showinfo("Успех", "Пользователь успешно сохранен.")
            self.destroy()
            self.refresh_callback()
        except requests.exceptions.RequestException as e:
            messagebox.showerror(
                "Ошибка", f"Ошибка при сохранении пользователя: {e}")
