import subprocess
import os
import logging
import psutil
from datetime import datetime
import threading
import time
import json
from src.core.ai_engine import AIEngine

class AIShell:
    def __init__(self):
        self.ai_engine = AIEngine()
        print("AI Shell started with AI Engine")
        # Command history
        self.history_file = "data/logs/ai_shell_history.txt"
        self.history = []
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                self.history = [line.strip() for line in f]
        print(f"Loaded {len(self.history)} lines of history.")

        # Reminders
        self.reminders_file = "data/logs/ai_shell_reminders.json"
        self.reminders = []
        self.load_reminders()

        # Logging setup
        log_dir = "data/logs"
        os.makedirs(log_dir, exist_ok=True)
        self.logger = logging.getLogger("AIOS_Shell")
        self.logger.setLevel(logging.INFO)
        log_file_path = os.path.join(log_dir, "ai_shell.log")
        handler = logging.FileHandler(log_file_path)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)
        self.logger.info("Shell started. History loaded.")

    def load_reminders(self):
        if os.path.exists(self.reminders_file):
            try:
                with open(self.reminders_file, "r") as f:
                    self.reminders = json.load(f)
            except Exception:
                self.reminders = []
        else:
            self.reminders = []

    def save_reminders(self):
        with open(self.reminders_file, "w") as f:
            json.dump(self.reminders, f)

    def show_reminders(self):
        if self.reminders:
            print("\nActive Reminders:")
            for i, rem in enumerate(self.reminders, 1):
                print(f"{i}. {rem['task']} at {rem['reminder_time']}")
        else:
            print("\nNo active reminders.")

    def schedule_reminder(self, task, reminder_time):
        try:
            seconds = int(reminder_time) if reminder_time.isdigit() else 10
            self.logger.info(f"Setting reminder: '{task}' in {seconds} seconds")
            def notify():
                time.sleep(seconds)
                print(f"\n[Reminder] {task}")
                self.logger.info(f"[Reminder] {task}")
            threading.Thread(target=notify, daemon=True).start()
        except Exception as e:
            self.logger.error(f"Reminder error: {e}")

    def show_startup_status(self):
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        user_home = os.path.expanduser("~")
        backup_dir = os.path.join(user_home, "AIOS_Backups")
        if os.path.exists(backup_dir):
            backups = [f for f in os.listdir(backup_dir) if os.path.isdir(os.path.join(backup_dir, f))]
            if backups:
                latest_backup = max(backups)
                backup_str = f"Last backup: {latest_backup}"
            else:
                backup_str = "No backups found."
        else:
            backup_str = "No backups folder found."
        print("=" * 50)
        print("AI OS System Status")
        print(f"CPU usage: {cpu}% | Memory usage: {memory}% | Disk usage: {disk}%")
        print(backup_str)
        print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        self.logger.info(f"Startup status: CPU {cpu}%, MEM {memory}%, DISK {disk}%. {backup_str}")
        if cpu > 80:
            self.logger.warning(f"System alert: High CPU usage ({cpu}%)")
        if memory > 85:
            self.logger.warning(f"System alert: High memory usage ({memory}%)")
        if disk > 90:
            self.logger.warning(f"System alert: Disk nearly full ({disk}% used)")

    def run(self):
        print("Welcome to the AI OS Shell. Type anything or 'exit' to quit.")
        self.show_startup_status()

        while True:
            user_input = input("AI OS> ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                self.logger.info("User exited shell.")
                break

            # Command history
            if user_input.lower() == "history":
                print("Command History:")
                for i, cmd in enumerate(self.history[-10:], 1):
                    print(f"{i}: {cmd}")
                continue

            # Reminders
            if user_input.lower() == "reminders":
                self.show_reminders()
                continue

            if user_input.lower().startswith("dismiss reminder"):
                try:
                    idx = int(user_input.split()[-1]) - 1
                    if 0 <= idx < len(self.reminders):
                        removed = self.reminders.pop(idx)
                        print(f"Dismissed reminder: {removed['task']}")
                        self.save_reminders()
                    else:
                        print("No reminder at that index.")
                except Exception:
                    print("Usage: dismiss reminder <number>")
                continue

            # Save command history
            self.history.append(user_input)
            with open(self.history_file, "w") as f:
                for line in self.history:
                    f.write(line + "\n")
            self.logger.info(f"User command: {user_input}")

            result = self.ai_engine.process_input(user_input)
            intent = result["intent"]
            print(f"AI ({intent}): {result['text']}")

            try:
                if intent == "list_files":
                    self.logger.info("Running command: dir")
                    print("Running: dir")
                    subprocess.run("dir", shell=True)

                elif intent == "system_status" or intent == "system_info":
                    self.logger.info("Running command: systeminfo")
                    print("Running: systeminfo")
                    subprocess.run("systeminfo", shell=True)

                elif intent == "find_files" and result.get("query"):
                    cmd = f'dir /s /b *{result["query"]}*'
                    self.logger.info(f"Running command: {cmd}")
                    print(f"Running: {cmd}")
                    subprocess.run(cmd, shell=True)

                elif intent == "create_folder" and result.get("folder"):
                    folder = result["folder"]
                    cmd = f'mkdir \"{folder}\"'
                    self.logger.info(f"Running command: {cmd}")
                    print(f"Running: {cmd}")
                    subprocess.run(cmd, shell=True)

                elif intent == "delete_file":
                    filename = result.get("filename")
                    if filename:
                        confirm = input(f"Are you sure you want to delete '{filename}'? (y/N): ").lower()
                        if confirm == "y":
                            cmd = f'del \"{filename}\"'
                            self.logger.info(f"Running command: {cmd}")
                            print(f"Running: {cmd}")
                            subprocess.run(cmd, shell=True)
                        else:
                            print("Delete cancelled.")
                            self.logger.info("Delete command cancelled by user.")
                    else:
                        print("No filename detected. Try, e.g., 'delete file called old_report.txt'")

                elif intent == "help":
                    print("You can ask me to: list files, find files, create folder, delete file, get system status, backup data, set reminders, view history/reminders, dismiss reminders.")
                    self.logger.info("Displayed help to user.")

                elif intent == "backup_data":
                    user_folder = os.path.expanduser("~")
                    src = os.path.join(user_folder, "Documents")
                    backup_dir = os.path.join(user_folder, "AIOS_Backups")
                    os.makedirs(backup_dir, exist_ok=True)
                    backup_name = f"Documents_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    dest = os.path.join(backup_dir, backup_name)
                    print(f"Backing up {src} to {dest} ...")
                    self.logger.info(f"Backing up {src} to {dest}")
                    try:
                        subprocess.run(['xcopy', src, dest, '/E', '/I', '/Y'], shell=True, check=True)
                        print("Backup complete.")
                        self.logger.info("Backup completed successfully.")
                    except Exception as e:
                        print(f"Backup failed: {e}")
                        self.logger.error(f"Backup failed: {e}")

                elif intent == "set_reminder":
                    task = result.get("task", "unknown task")
                    reminder_time = result.get("reminder_time", "10")
                    print(f"Reminder scheduled for: {task} in {reminder_time} seconds")
                    self.reminders.append({"task": task, "reminder_time": reminder_time, "created": datetime.now().isoformat()})
                    self.save_reminders()
                    self.schedule_reminder(task, reminder_time)

            except Exception as e:
                print(f"Error: {e}")
                self.logger.error(f"Error during command execution: {e}")

if __name__ == "__main__":
    shell = AIShell()
    shell.run()
