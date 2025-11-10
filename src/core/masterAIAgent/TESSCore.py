# ============================
# MASTER AI AGENT (TESS CORE)
# ============================
import uvicorn
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from uuid import uuid4
import datetime
import logging
import requests
import os
import json
import re

from src.core.masterAIAgent.sandboxRunner import ScriptSandbox


# ======================================
# CONFIGURATION AND GLOBAL DEFINITIONS
# ======================================

LLM_ENDPOINTS = {
    "mixtral": "http://localhost:11434/api/generate",
    "codellama": "http://localhost:11436/api/generate"
}

LOG_PATH = "tess_action_log.jsonl"

app = FastAPI(title="TESS Master AI Agent")

sandbox = ScriptSandbox(time_limit_sec=60)

# ==============
# AI ENGINE (Basic Intent Matcher)
# ==============

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

# Instantiate the AI Engine singleton to be used across agent
agent_ai_engine = AIEngine()

# ==============
# UTILS
# ==============

def get_timestamp():
    return datetime.datetime.now().isoformat()

def save_log(entry: Dict[str, Any]):
    with open(LOG_PATH, "a") as logf:
        logf.write(json.dumps(entry) + "\n")

def select_llm_model(task_type: str):
    if task_type == "code":
        return "codellama"
    return "mixtral"

def query_llm(model: str, prompt: str) -> str:
    url = LLM_ENDPOINTS[model]
    payload = {"model": model, "prompt": prompt}
    try:
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        result = resp.json().get("response", "")
        return result
    except Exception as e:
        logging.error(f"LLM Query Failed: {e}")
        return f"Error: {str(e)}"

# ==============
# DATA MODELS
# ==============

class AgentAction(BaseModel):
    user_id: str
    input_text: str
    context: Optional[Dict[str, Any]] = None
    task_type: Optional[str] = "chat"  # 'chat', 'code', 'sandbox', etc.

class AgentLog(BaseModel):
    timestamp: str
    user_id: str
    input_text: str
    action_type: str
    llm_response: str
    result: Optional[Any] = None
    context: Optional[Dict[str, Any]] = None

class SandboxTask(BaseModel):
    user_id: str
    script: str
    language: str = "python"

# ==============
# MAIN AGENT LOGIC
# ==============

class MasterAgentCore:
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    def process(self, action: AgentAction) -> str:
        session_id = action.user_id or str(uuid4())
        # 1. Log initial action basics
        log_entry = {
            "timestamp": get_timestamp(),
            "user_id": session_id,
            "input_text": action.input_text,
            "action_type": action.task_type,
            "context": action.context,
        }

        # 2. First, use AIEngine intent matcher for quick intent recognition
        intent_result = agent_ai_engine.process_input(action.input_text)

        if intent_result["intent"] == "unknown" or intent_result.get("confidence", 0) < 0.6:
            # 3. Fall back to LLM if intent not confidently detected
            model = select_llm_model(action.task_type)
            llm_output = query_llm(model, action.input_text)
            log_entry["llm_response"] = llm_output
            response_text = llm_output
        else:
            # 4. Use intent matcher result directly
            log_entry["llm_response"] = intent_result["text"]
            response_text = intent_result["text"]

        # 5. Save interaction log
        save_log(log_entry)

        # 6. Return response to API/UI
        return response_text

    def run_sandbox_task(self, task: SandboxTask) -> Dict[str, Any]:
        # Delegate script execution to sandbox runner
        result = sandbox.run_script(script=task.script, language=task.language)
        return {
            "output": result.get("stdout", ""),
            "error": result.get("stderr", "")
        }

agent_core = MasterAgentCore()

# ==============
# API ENDPOINTS (CORE)
# ==============

@app.post("/chat")
async def chat_action(action: AgentAction):
    result = agent_core.process(action)
    return {"response": result}

@app.post("/sandbox")
async def sandbox_run(task: SandboxTask):
    result = agent_core.run_sandbox_task(task)
    save_log({
        "timestamp": get_timestamp(),
        "user_id": task.user_id,
        "input_text": task.script,
        "action_type": "sandbox",
        "result": result,
        "context": {"language": task.language}
    })
    return result

@app.get("/logs")
async def get_logs(count: int = 20):
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH, "r") as logf:
        lines = logf.readlines()[-count:]
        return [json.loads(line) for line in lines]

@app.get("/")
def root():
    return {"status": "TESS Master Agent running."}

# ==============
# MAIN RUNNER
# ==============

if __name__ == "__main__":
    uvicorn.run("TESSCore:app", host="0.0.0.0", port=8080, reload=True)
