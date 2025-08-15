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

app.delete('/api/threads/:id', (req, res) => {
    const { id } = req.params;
    store.deleteThread(id);
    res.json({ ok: true });;
});

app.get('/api/threads/:id/messages', (req, res) => {
    const { id } = req.params;
    const thread = store.getThreasd(id);
    if (!thread) return res.status(404).json({ error: 'Thread not found' });
    const messages = store.getMessages(id);
    res.json({ thread, messages });
});

//---- Chat: non-streaming (JSON) ----
app.post('/api/chat', async (req, res) => {
  try {
    const { threadId, userText } = req.body || {};
    const thread = store.getThread(threadId);
    if (!thread) return res.status(404).json({ error: 'Thread not found' });

    const msgs = store.listMessages(threadId).map(m => ({ role: m.role, content: m.content }));
    // Ensure we include system prompt at the start
    const context = [{ role: 'system', content: thread.system_prompt }, ...msgs.filter(m => m.role !== 'system')];

    // Save user message
    const uMsg = { id: uuid(), thread_id: threadId, role: 'user', content: userText, created_at: Date.now() };
    store.addMessage(uMsg);

    const completion = await client.chat.completions.create({
      model: 'gpt-4o', // change to 'gpt-5' when available
      messages: [...context, { role: 'user', content: userText }],
      temperature: 0.7,
      max_tokens: 600
    });

    const reply = completion.choices?.[0]?.message?.content || '';
    const aMsg = { id: uuid(), thread_id: threadId, role: 'assistant', content: reply, created_at: Date.now() };
    store.addMessage(aMsg);

    res.json({ reply });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: e.message || 'Server error' });
  }
});

//---- Chat: streaming (SSE) ----