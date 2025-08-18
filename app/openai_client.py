import os
import openai
from dotenv import load_dotenv

laod_doteenv()

OPEN_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPEN_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set in the environment variables.")
openai.api_key = OPENAI_API_KEY

async def create_chat_completion_stream(messages, model: str):
    resp = await openai.ChatCompletion.acreate( 
        model=model,
        messages=messages,
        stream=True,
        temperature=0.2,
    )
    async for chunk in resp:
        yield chunk

async def create_chat_completion(messages, model: str, max_token=512, temperature=0.2):
    resp = await openai.ChatCompletion.acreate(
        model=model,
        messages=messages,
        max_tokens=max_token,
        temperature=temperature,
    )
    return resp['choices'][0]['message']['content']

async def embed_text(texts, model: str):
    resp = await openai.Embedding.acreate(
        model=model,
        input=texts,
    )
    return [r['embedding'] for r in resp['data']]