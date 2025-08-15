import Database from 'better-sqlite3';
import fs from 'fs';

export function initDb(dbPath) {
  const db = new Database(dbPath);
  const schema = fs.readFileSync(new URL('./schema.sql', import.meta.url)).toString();
  db.exec(schema);

  const createThread = db.prepare(`INSERT INTO threads (id, title, system_prompt, created_at) VALUES (@id, @title, @system_prompt, @created_at)`);
  const addMessage   = db.prepare(`INSERT INTO messages (id, thread_id, role, content, created_at) VALUES (@id, @thread_id, @role, @content, @created_at)`);
  const listThreads  = db.prepare(`SELECT id, title, system_prompt, created_at FROM threads ORDER BY created_at DESC`);
  const getThread    = db.prepare(`SELECT id, title, system_prompt, created_at FROM threads WHERE id = ?`);
  const renameThread = db.prepare(`UPDATE threads SET title = ? WHERE id = ?`);
  const delThread    = db.prepare(`DELETE FROM threads WHERE id = ?`);
  const delMsgsByTid = db.prepare(`DELETE FROM messages WHERE thread_id = ?`);
  const listMessages = db.prepare(`SELECT id, role, content, created_at FROM messages WHERE thread_id = ? ORDER BY created_at ASC`);

  return {
    db,
    createThread(data) { return createThread.run(data); },
    addMessage(data) { return addMessage.run(data); },
    listThreads() { return listThreads.all(); },
    getThread(id) { return getThread.get(id); },
    renameThread(title, id) { return renameThread.run(title, id); },
    deleteThread(id) { delMsgsByTid.run(id); return delThread.run(id); },
    listMessages(threadId) { return listMessages.all(threadId); },
  };
}