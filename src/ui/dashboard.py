import sys
import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QListWidget, QPushButton,
    QLineEdit, QHBoxLayout, QMessageBox, QSystemTrayIcon, QStyle
)
from PyQt5.QtCore import QTimer
import psutil

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('AI OS Dashboard')
        self.setGeometry(100, 100, 600, 700)
        layout = QVBoxLayout()

        # --- System Status Panel ---
        self.status_label = QLabel('')
        layout.addWidget(QLabel('System Status:'))
        layout.addWidget(self.status_label)
        self.update_status()

        # --- Command History ---
        self.history_label = QLabel('Recent Commands:')
        self.history_list = QListWidget()
        layout.addWidget(self.history_label)
        layout.addWidget(self.history_list)
        self.load_history()

        # --- Notifications Panel ---
        self.notif_label = QLabel('Notifications (Log):')
        self.notif_list = QListWidget()
        layout.addWidget(self.notif_label)
        layout.addWidget(self.notif_list)
        self.load_notifications()

        # --- Reminders Panel ---
        self.reminder_label = QLabel('Reminders (double-click to dismiss):')
        self.reminder_list = QListWidget()
        layout.addWidget(self.reminder_label)
        layout.addWidget(self.reminder_list)
        self.load_reminders()
        self.reminder_list.itemDoubleClicked.connect(self.dismiss_reminder)

        # --- AI Recommendations (from log alerts) ---
        self.ai_recommend_label = QLabel('AI Recommendations:')
        self.ai_recommend_list = QListWidget()
        layout.addWidget(self.ai_recommend_label)
        layout.addWidget(self.ai_recommend_list)
        self.load_ai_recommendations()

        # --- Interactive Controls ---
        controls_layout = QHBoxLayout()
        self.listfiles_btn = QPushButton("List Files")
        self.listfiles_btn.clicked.connect(self.list_files)
        controls_layout.addWidget(self.listfiles_btn)

        self.backup_btn = QPushButton("Backup Documents Now")
        self.backup_btn.clicked.connect(self.backup_documents)
        controls_layout.addWidget(self.backup_btn)

        self.reminder_input = QLineEdit()
        self.reminder_input.setPlaceholderText("Quick reminder (text only)...")
        self.add_reminder_btn = QPushButton("Add Reminder")
        self.add_reminder_btn.clicked.connect(self.add_reminder)
        controls_layout.addWidget(self.reminder_input)
        controls_layout.addWidget(self.add_reminder_btn)
        layout.addLayout(controls_layout)

        # --- Output Panel ---
        self.output_label = QLabel('Output:')
        self.output_content = QListWidget()
        layout.addWidget(self.output_label)
        layout.addWidget(self.output_content)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_all)
        layout.addWidget(refresh_btn)

        self.setLayout(layout)

        # System tray icon for popup notifications
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.tray_icon.show()

        # Timer for polling new log alerts / reminders
        self.last_alert_time = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.poll_notifications)
        self.timer.start(4000)

    def update_status(self):
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status_txt = f"CPU: {cpu}%  |  MEM: {mem}%  |  DISK: {disk}%  |  TIME: {now}"
        self.status_label.setText(status_txt)

    def load_history(self):
        self.history_list.clear()
        hist_file = "data/logs/ai_shell_history.txt"
        if os.path.exists(hist_file):
            with open(hist_file, "r") as f:
                for line in f.readlines()[-10:]:
                    self.history_list.addItem(line.strip())

    def load_notifications(self):
        self.notif_list.clear()
        notif_file = "data/logs/ai_shell.log"
        if os.path.exists(notif_file):
            with open(notif_file, "r") as f:
                lines = [
                    line.strip()
                    for line in f.readlines()
                    if "INFO" in line or "WARNING" in line or "ERROR" in line
                ]
                for line in lines[-10:]:
                    self.notif_list.addItem(line)

    def load_reminders(self):
        self.reminder_list.clear()
        self.reminders = []
        reminders_file = "data/logs/ai_shell_reminders.json"
        if os.path.exists(reminders_file):
            try:
                with open(reminders_file, "r") as f:
                    rems = json.load(f)
                    for rem in rems[-5:]:
                        self.reminder_list.addItem(f"{rem['task']} at {rem['reminder_time']}")
                    self.reminders = rems
            except Exception:
                pass

    def load_ai_recommendations(self):
        self.ai_recommend_list.clear()
        log_file = "data/logs/ai_shell.log"
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                lines = [
                    line.strip()
                    for line in f.readlines()
                    if "WARNING" in line or "System alert" in line or "Backup recommended" in line
                ]
                for line in lines[-5:]:
                    self.ai_recommend_list.addItem(line)

    def refresh_all(self):
        self.update_status()
        self.load_history()
        self.load_notifications()
        self.load_reminders()
        self.load_ai_recommendations()
        self.output_content.clear()

    def list_files(self):
        try:
            files = os.listdir(".")
            self.output_content.clear()
            self.output_content.addItem("Files in current directory:")
            for f in files:
                self.output_content.addItem(f)
            self.load_history()
        except Exception as e:
            self.output_content.addItem(f"Error listing files: {e}")

    def backup_documents(self):
        try:
            user_home = os.path.expanduser("~")
            src = os.path.join(user_home, "Documents")
            backup_dir = os.path.join(user_home, "AIOS_Backups")
            os.makedirs(backup_dir, exist_ok=True)
            backup_name = f"Documents_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            dest = os.path.join(backup_dir, backup_name)
            os.system(f'xcopy "{src}" "{dest}" /E /I /Y')
            self.output_content.addItem(f"Backup done: {dest}")
            self.show_popup("Backup Complete", f"Documents backed up to {dest}")
            self.load_ai_recommendations()
            self.refresh_all()
        except Exception as e:
            self.output_content.addItem(f"Error during backup: {e}")

    def add_reminder(self):
        text = self.reminder_input.text().strip()
        if not text:
            QMessageBox.warning(self, "No Input", "Please enter a reminder.")
            return
        reminders_file = "data/logs/ai_shell_reminders.json"
        reminders = []
        if os.path.exists(reminders_file):
            try:
                with open(reminders_file, "r") as f:
                    reminders = json.load(f)
            except Exception:
                reminders = []
        reminder = {
            "task": text,
            "reminder_time": "manual (via dashboard)",
            "created": datetime.now().isoformat()
        }
        reminders.append(reminder)
        with open(reminders_file, "w") as f:
            json.dump(reminders, f)
        self.reminder_input.clear()
        self.load_reminders()
        self.output_content.addItem(f"Reminder added: {text}")
        self.show_popup("Reminder", f"Added: {text}")

    def dismiss_reminder(self, item):
        reminders_file = "data/logs/ai_shell_reminders.json"
        row = self.reminder_list.row(item)
        if os.path.exists(reminders_file):
            try:
                with open(reminders_file, "r") as f:
                    reminders = json.load(f)
                index_in_full = len(reminders) - self.reminder_list.count() + row
                if 0 <= index_in_full < len(reminders):
                    removed = reminders.pop(index_in_full)
                    with open(reminders_file, "w") as f:
                        json.dump(reminders, f)
                    QMessageBox.information(self, "Reminder Dismissed", f"Dismissed: {removed['task']}")
                    self.show_popup("Reminder", f"Dismissed: {removed['task']}")
                    self.load_reminders()
            except Exception:
                QMessageBox.warning(self, "Error", "Could not dismiss reminder.")

    def poll_notifications(self):
        # Popup any new WARNING/alert entries in the log since last poll
        log_file = "data/logs/ai_shell.log"
        if not os.path.exists(log_file):
            return
        try:
            with open(log_file, "r") as f:
                lines = [line.strip() for line in f if any(word in line for word in ("WARNING", "System alert", "Backup completed", "[Reminder]"))]
                if lines:
                    # Find the latest alert (by timestamp at start of line)
                    last_line = lines[-1]
                    if last_line != getattr(self, "last_alert", None):
                        # Only show if new
                        self.show_popup("AI OS Alert", last_line)
                        self.last_alert = last_line
        except Exception:
            pass

    def show_popup(self, title, message):
        # Show both system tray popup and messagebox for max visibility
        self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 8000)
        QMessageBox.information(self, title, message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dash = Dashboard()
    dash.show()
    sys.exit(app.exec_())
