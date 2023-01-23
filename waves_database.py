import asyncio
import sqlite3

connector = sqlite3.connect("storage.db", check_same_thread=False)
connector.execute("CREATE TABLE if not exists users(username str, chat_id integer, mode integer, expiration integer)")
connector.commit()

def _add_user(username):
    cur = connector.cursor()
    cur.execute("INSERT INTO users VALUES(?, ?, ?, ?)", (username, 0, 0, 0))
    connector.commit()

def _remove_user(username):
    cur = connector.cursor()
    cur.execute(f"DELETE FROM users WHERE username = '{username}'")
    connector.commit()

def _set_user_expiration(username, timestamp):
    cur = connector.cursor()
    cur.execute(f"UPDATE users SET expiration = {timestamp} WHERE username = '{username}'")
    connector.commit()

def _get_all_users():
    cur = connector.cursor()
    users = cur.execute(f"SELECT username, mode, expiration FROM users").fetchall()
    return users

def _get_user(username):
    cur = connector.cursor()
    user = cur.execute(f"SELECT username, expiration FROM users WHERE username = '{username}'").fetchone()
    return user

def _set_mode(username, chat_id, mode):
    cur = connector.cursor()
    cur.execute(f"UPDATE users SET chat_id = {chat_id}, mode = {mode} WHERE username = '{username}'")
    connector.commit()

def _get_active_modes():
    cur = connector.cursor()
    active_modes = cur.execute("SELECT chat_id, mode, expiration FROM users WHERE mode != 0").fetchall()
    return active_modes

async def add_user(username):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _add_user, username)

async def remove_user(username):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _remove_user, username)

async def set_user_expiration(username, timestamp):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _set_user_expiration, username, timestamp)

async def get_all_users():
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_all_users)

async def get_user(username):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_user, username)

async def set_mode(username, chat_id, mode):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _set_mode, username, chat_id, mode)

async def get_active_modes():
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_active_modes)
