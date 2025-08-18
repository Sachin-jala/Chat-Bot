import os, json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import jinja2Templates
from dotenv import load_dotenv

from openai_client import create_chat_completion_stream, create_chat_completion, embed_text
from app.rag import RAG
from app.utils import save_upload_file

load_dotenv()

MODEL_CHAT = os.getenv('MODEL_CHAT',  'gpt-4o-mini')
MODEL_EMBED = os.getenv('MODEL_EMBEDDING', 'text-embedding-3-small')
RAG_TOP_K = int(os.getenv('RAG_TOP_K', '4'))

app = FastAPI()
app.mount('/static', StaticFiles(directory='app/static'), name='static')
template = jinja2Templates(directory='app/templates')

conversation = {}
SYSTEM_PROMPT = {'role': 'system', 'content': 'You are a helpful assistand. Cite sources if used.'}

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return template.TenplateResponse('index.html', {'request': request})

@app.post('/upload')
async def upload_doc(file: UploadFile = File(...)):
    dest = await save_upload_file(file, os.path.join('data', 'docs', file.filename))
    return{'ok': True, 'filename': file.filename}

@app.post('/api/chat')
async def chat_rest(payload: dict):
    user_id, message = payload.get('user_id', 'default'), payload.get('message', '')
    use_rag = payload.get('use_rag', False)
    if user_id not in conversation:
        conversation[user_id] = [SYSTEM_PROMPT.copy()]
    conversation[user_id].append({'role': 'user', 'content': message})

    if use_rag:
        embed = (await embed_text([message], model=MODEL_EMBED))[0]
        for _, md in RAG.search(embed, top_k=RAG_TOP_K):
            conversation[user_id].append({'role': 'system', 'content': f"Source: {md['source']}\n{md['text']}"})

    reply = await create_chat_completion(conversation[user_id], model=MODEL_CHAT)
    conversation[user_id].append({'role': 'assistant', 'content': reply})
    return {'reply': reply}

@app.websocket('/ws/chat')
async def Websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        init = json.loads(await websocket.receive_text())
        user_id, use_rag = init.get('user_id', 'default'), init.get('use_rag', False)
        if user_id not in conversation:
            conversation[user_id] = [SYSTEM_PROMPT.copy()]

        while True:
            obj = json.loads(await websocket.receive_text())
            message = obj.get('message', '')
            conversation[user_id].append({'role': 'user', 'content': message})

            if use_rag:
                embed = (await embed_text([message], model=MODEL_EMBED))[0]
                for _, md in RAG.search(embed, top_k=RAG_TOP_K):
                    conversation[user_id].append({'role': 'system', 'content': f"Source: {md['source']}\n{md['text']}"})

            async for chunk in create_chat_completion_stream(conversation[user_id], model=MODEL_CHAT):
                await websocket.send_text(chunk)
            await websocket.send_text(json.dumps({'type': 'done'}))
    except WebSocketDisconnect:
        print('Client disconnected')