import re

class AIEngine:
    INTENT_PATTERNS = {
        "list_files": ["list files", "show files", "ls", "dir"],
        "find_files": ["find", "search", "locate"],
        "create_folder": ["create folder", "make directory", "mkdir"],
        "delete_file": ["delete file", "remove file", "rm"],
        "help": ["help", "assist", "guide"],
        "system_status": ["status", "system info", "uptime"],
        "system_info": ["system info", "show system", "info", "specs"],
        "backup_data": ["backup", "backup my data", "make a backup", "save everything"]


    }

    def __init__(self):
        print("AI Engine initialized (basic intent matcher)")

    def process_input(self, user_input: str):
        user_input_lower = user_input.lower()
        for intent, patterns in self.INTENT_PATTERNS.items():
            if any(p in user_input_lower for p in patterns):
                # Try to extract search/query for find_files intent
                if intent == "find_files":
                    match = re.search(r"find (.+)", user_input_lower)
                    query = match.group(1) if match else ""
                    return {
                        "intent": intent,
                        "text": f"Searching for: {query}" if query else "What would you like me to find?",
                        "query": query,
                        "confidence": 0.9
                    }
                # Try to extract folder name for create_folder intent
                if intent == "create_folder":
                    match = re.search(r"create folder(?: called)? ?([\w.\- ]+)?", user_input_lower)
                    folder = match.group(1).strip() if match and match.group(1) else "new_folder"
                    return {
                        "intent": intent,
                        "text": f"Creating folder: {folder}",
                        "folder": folder,
                        "confidence": 0.9
                    }
                if intent == "delete_file":
                    match = re.search(r"delete file(?: called)? ?([\w.\- ]+)?", user_input_lower)
                    filename = match.group(1).strip() if match and match.group(1) else ""
                    return {
                        "intent": intent,
                        "text": f"Delete file: {filename if filename else '[no file detected]'}",
                        "filename": filename,
                        "confidence": 0.9
                    }
                if intent == "backup_data":
                    return {
                        "intent": intent,
                        "text": "Preparing to back up your Documents folder...",
                        "confidence": 0.95
                    }
            
                
                return {
                    "intent": intent,
                    "text": f"Detected intent: {intent}",
                    "confidence": 0.9
                }
                
        return {
            "intent": "unknown",
            "text": "Sorry, I didn't understand. Try asking about files, system, or type 'help'.",
            "confidence": 0.3
        }

import os

class AIShell:
    def __init__(self):
        self.ai_engine = AIEngine()
        self.history_file = "data/logs/ai_shell_history.txt"
        self.history = []
        print("AI Shell started with AI Engine")
        # Restore history if exists
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                self.history = [line.strip() for line in f]
        print(f"Loaded {len(self.history)} lines of history.")
