#!/bin/bash
source ../ai-os-env/bin/activate
uvicorn src.master_ai_agent.tess_core:app --host 0.0.0.0 --port 8080 --reload
