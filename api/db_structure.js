import { sql } from '@vercel/postgres';
 
export default async function handler(request, response) {
  try {
    const result =
      await sql`CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        username TEXT NOT NULL,
        hash TEXT NOT NULL
        , 'color' INTEGER NOT NULL DEFAULT 'red');`;
    return response.status(200).json({ result });
  } catch (error) {
    return response.status(500).json({ error });
  }
}