import customtkinter as ctk
from PIL import Image
from tkinter import messagebox
import tasks
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(BASE_DIR, "assets", "logo.png")
icon_path = os.path.join(BASE_DIR, "assets", "logo.ico")


def ensure_app_icon():
    try:
        if os.path.exists(logo_path):
            Image.open(logo_path).save(
                icon_path, format="ICO", sizes=[(16, 16), (32, 32), (64, 64)]
            )
    except (FileNotFoundError, OSError, ValueError):
        if os.path.exists(icon_path):
            try:
                os.remove(icon_path)
            except OSError:
                pass


ensure_app_icon()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class TodoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("TaskTracker")
        self.geometry("800x500")
        self.resizable(width=False, height=False)
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(
            row=1, column=0, columnspan=5, padx=20, pady=5, sticky="w"
        )

        self.task_input = ctk.CTkEntry(
            self.button_frame, placeholder_text="Enter a new task...", width=450
        )
        self.add_button = ctk.CTkButton(
            self.button_frame,
            text="Add task",
            command=self.add_task_clicked,
            fg_color="#1f538d",
        )
        self.task_input.grid(
            row=0, column=0, columnspan=3, padx=20, pady=20, sticky="w"
        )
        self.add_button.grid(
            row=0,
            column=3,
            padx=10,
            pady=20,
        )

        self.update_status_button = ctk.CTkButton(
            self.button_frame,
            text="Update status",
            command=self.update_status_clicked,
            fg_color="#1f538d",
        )
        self.update_status_button.grid(row=1, column=0, padx=5, pady=5)
        self.is_update_mode_activate = False

        self.delete_button = ctk.CTkButton(
            self.button_frame,
            text="Delete task",
            command=self.delete_task_clicked,
            fg_color="#1f538d",
        )
        self.delete_button.grid(row=1, column=1, padx=5, pady=5)
        self.is_delete_mode_activate = False

        self.delete_completed_button = ctk.CTkButton(
            self.button_frame,
            text="Delete completed tasks",
            command=self.delete_completed_clicked,
            fg_color="#1f538d",
        )
        self.delete_completed_button.grid(row=1, column=2, padx=5, pady=5)
        self.is_delete_completed_mode_activate = False

        self.delete_all_button = ctk.CTkButton(
            self.button_frame,
            text="Delete all tasks",
            command=self.delete_all_clicked,
            fg_color="#b91c1c",
            hover_color="#7f1d1d",
        )
        self.delete_all_button.grid(row=1, column=3, padx=5, pady=5)
        self.delete_all_mode_activate = False

        self.status_card = ctk.CTkFrame(
            self.button_frame, width=90, height=90, fg_color="#1f2937", corner_radius=12
        )
        self.status_card.grid_propagate(False)
        self.status_card.grid(
            row=0, column=4, rowspan=2, padx=(20, 0), pady=5, sticky="ns"
        )
        self.status_card.grid_rowconfigure((0, 1), weight=1)
        self.status_card.grid_columnconfigure(0, weight=1)

        self.pending_count_label = ctk.CTkLabel(
            self.status_card,
            text="0",
            font=("helvetica", 28, "bold"),
            text_color="#1f538d",
        )
        self.pending_count_label.grid(row=0, column=0, sticky="s", pady=(5, 0))

        self.pending_text_label = ctk.CTkLabel(
            self.status_card,
            text="ACTIVE",
            font=("helvetica", 10, "bold"),
            text_color="#9ca3af",
        )
        self.pending_text_label.grid(row=1, column=0, sticky="n", pady=(0, 5))
        self.task_scroll_frame = ctk.CTkScrollableFrame(self, width=740, height=320)
        self.task_scroll_frame.grid(
            row=2, column=0, columnspan=5, padx=20, pady=15, sticky="nsew"
        )
        self.refresh_task_display()
        self.bind("<Button-1>", self.handle_global_click)


    def reset_action_modes(self):
        self.is_update_mode_activate = False
        self.is_delete_mode_activate = False
        self.is_delete_completed_mode_activate = False
        self.delete_all_mode_activate = False

        self.update_status_button.configure(text="Update status", fg_color="#1f538d")
        self.delete_button.configure(text="Delete task", fg_color="#1f538d")
        self.delete_completed_button.configure(
            text="Delete completed tasks", fg_color="#1f538d"
        )
        self.delete_all_button.configure(text="Delete all tasks", fg_color="#b91c1c")


    def handle_global_click(self, event):
        if self.is_update_mode_activate or self.is_delete_mode_activate:
            clicked_widget = event.widget
            inside_button_frame = False
            inside_task_frame = False

            current_widget = clicked_widget
            while current_widget is not None:
                if current_widget == self.button_frame:
                    inside_button_frame = True
                    break
                if current_widget == self.task_scroll_frame:
                    inside_task_frame = True
                    break
                current_widget = current_widget.master

            if not inside_button_frame and not inside_task_frame:
                self.reset_action_modes()
                self.refresh_task_display()


    def update_button_states(self, tasks_database=None):
        if tasks_database is None:
            tasks_database = tasks.load_tasks()

        has_tasks = bool(tasks_database)
        state = "normal" if has_tasks else "disabled"

        self.update_status_button.configure(state=state)
        self.delete_button.configure(state=state)
        self.delete_completed_button.configure(state=state)
        self.delete_all_button.configure(state=state)


    def refresh_task_display(self):
        for widget in self.task_scroll_frame.winfo_children():
            widget.destroy()

        tasks_database = tasks.load_tasks()
        self.update_button_states(tasks_database)
        self.update_active_counter(tasks_database)

        for task in tasks_database:
            row_panel = ctk.CTkFrame(
                self.task_scroll_frame, fg_color="#302F2F", corner_radius=8, height=50
            )
            row_panel.pack(fill="x", pady=5, padx=5)

            task_text = ctk.CTkLabel(
                row_panel, text=task["task"], font=("Arial", 14), anchor="w"
            )
            task_text.pack(side="left", padx=20, pady=12)

            badge_color = (
                "#3a7ebf"
                if "pending" in task["status"].lower()
                else "#d97706" if "progress" in task["status"].lower() else "#2e7d32"
            )

            status_badge = ctk.CTkLabel(
                row_panel,
                text=task["status"],
                fg_color=badge_color,
                text_color="white",
                corner_radius=6,
                width=90,
                height=26,
                cursor="hand2",
            )

            status_badge.pack(side="right", padx=20, pady=12)

            row_panel.bind(
                "<Button-1>",
                lambda event, t_id=task["id"]: self.handle_row_selection(t_id),
            )

            task_text.bind(
                "<Button-1>",
                lambda event, t_id=task["id"]: self.handle_row_selection(t_id),
            )


    def add_task_clicked(self):
        user_task = self.task_input.get()
        if not user_task.strip():
            return

        tasks.add_task(user_task)
        self.task_input.delete(0, "end")
        self.refresh_task_display()


    def update_status_clicked(self):
        if not tasks.load_tasks():
            return

        if self.is_update_mode_activate:
            self.reset_action_modes()
            self.refresh_task_display()
            return

        self.reset_action_modes()
        self.is_update_mode_activate = True

        self.update_status_button.configure(
            text="Select a task below", fg_color="#d97706"
        )
        self.update_active_counter()
        self.refresh_task_display()


    def handle_row_selection(self, task_id):
        if self.is_update_mode_activate:
            tasks.update_status(task_id)
            self.reset_action_modes()
            self.refresh_task_display()

        elif self.is_delete_mode_activate:
            tasks.delete_tasks(task_id)
            self.reset_action_modes()
            self.refresh_task_display()


    def delete_task_clicked(self):
        if not tasks.load_tasks():
            return

        if self.is_delete_mode_activate:
            self.reset_action_modes()
            self.refresh_task_display()
            return

        self.reset_action_modes()
        self.is_delete_mode_activate = True

        self.delete_button.configure(text="Select a task to delete", fg_color="#b91c1c")
        self.update_active_counter()
        self.refresh_task_display()


    def delete_completed_clicked(self):
        if not tasks.load_tasks():
            return

        self.reset_action_modes()
        tasks.delete_completed_task()
        self.refresh_task_display()
        self.update_active_counter()


    def delete_all_clicked(self):
        if not tasks.load_tasks():
            return

        user_confirmed = messagebox.askyesno(
            title="Warning!",
            message="Are you absolutely sure you want to delete ALL tasks?\nThis cannot be undone!",
        )
        self.reset_action_modes()

        if user_confirmed:
            tasks.delete_all_tasks()
            self.refresh_task_display()
        self.update_active_counter()
        self.refresh_task_display()


    def update_active_counter(self, tasks_database=None):
        if tasks_database is None:
            tasks_database = tasks.load_tasks()

        active_count = tasks.get_active_tasks_count(tasks_database)
        self.pending_count_label.configure(text=str(active_count))


if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()
