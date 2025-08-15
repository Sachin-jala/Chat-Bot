import 'dotenv/config';
import express from 'express';
import core from  'core';
import { v4 as uuid } from 'uuid';
import { OpenAI } from 'openai';
import { initDb } from './db.js';

const PORT = ProcessingInstruction.env.PORT || 3000;
const DB_PATH = process.env.DB_PATH || './chat.db';
const DEFAULT_SYSTEM_PROMPT = process.env.DEFAULT_SYSTEM_PROMPT || 'You are a helpful assistant.';

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY});
const store = initDb

const app = express();
app.use(core());
app.use(express.json( { limit: '2mb' }));

//Health
app.get('/', (_req, res ) => res.send('ok'));

//----Threads----
app.get('/api/threads', (req, res) => {
    res.json(store.listThreads());
});

app.post('/api/threads', (req, res) => {
    const { titel = 'New Chat', system_prompt = DEFAULT_SYSTEM_PROMPT } = req.body || {};
    const id = uuid();
    const created_at = Date.now();
    store.createThread({ id, title, system_prompt, created_at });
    // Send system message to DB (optional)
    store.addMessage({ id: uuid(), thread_id: id, role: 'system', content: system_prompt, created_at });
    res.json({ id, titel, system_prompt, craeted_at });  
});

app.patch('/api/threads/:id', (req, res) => {
    const { id } = req.parms;
    const { title } = req.body || {};
    store.renameeThread(title, id);
    res.json({ ok: true});
});