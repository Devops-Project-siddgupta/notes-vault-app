from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from cryptography.fernet import Fernet
import json
import os
from datetime import datetime

app = FastAPI(title="Offline Notes Locker API")

VAULT_FILE = "notes_vault.json"
KEY_FILE = "vault.key"

class NoteInput(BaseModel):
    title: str
    content: str

def get_fernet():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return Fernet(key)

fernet = get_fernet()

def load_vault():
    if not os.path.exists(VAULT_FILE):
        return []
    with open(VAULT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_vault(data):
    with open(VAULT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

@app.get("/api/notes")
def list_notes():
    vault = load_vault()
    # Return metadata without decrypting content upfront
    return [
        {"id": idx, "title": note["title"], "timestamp": note["timestamp"]} 
        for idx, note in enumerate(vault)
    ]

@app.get("/api/notes/{note_id}")
def get_note(note_id: int):
    vault = load_vault()
    if note_id < 0 or note_id >= len(vault):
        raise HTTPException(status_code=404, detail="Note not found")
    
    note = vault[note_id]
    try:
        decrypted_content = fernet.decrypt(note["content"].encode()).decode()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to decrypt note")
        
    return {
        "title": note["title"],
        "timestamp": note["timestamp"],
        "content": decrypted_content
    }

@app.post("/api/notes", status_code=201)
def create_note(note: NoteInput):
    vault = load_vault()
    encrypted_content = fernet.encrypt(note.content.encode()).decode()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_note = {
        "title": note.title,
        "content": encrypted_content,
        "timestamp": timestamp
    }
    vault.append(new_note)
    save_vault(vault)
    return {"message": "Note saved successfully"}

@app.get("/api/search")
def search_notes(q: str):
    vault = load_vault()
    query = q.lower()
    results = [
        {"id": idx, "title": note["title"], "timestamp": note["timestamp"]}
        for idx, note in enumerate(vault)
        if query in note["title"].lower()
    ]
    return results

# Simple UI Endpoint
@app.get("/", response_class=HTMLResponse)
def serve_ui():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()