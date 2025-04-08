import sqlite3

def init_db():
    conn = sqlite3.connect('discord_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER NOT NULL, server_id INTEGER NOT NULL, numMessages INTEGER NOT NULL DEFAULT 0, karma INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (user_id, server_id))''')
    conn.commit()
    conn.close()

def add_user(user_id, server_id):
    conn = sqlite3.connect('discord_bot.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (user_id, numMessages, karma, server_id) VALUES (?, ?, ?, ?)", 
              (user_id, 0, 0, server_id))
    conn.commit()
    conn.close()

def get_user(user_id, server_id):
    conn = sqlite3.connect('discord_bot.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ? AND server_id = ?", (user_id, server_id,))
    user = c.fetchone()
    conn.close()
    return user

def alterRecord(user_id, karmaDelta, server_id):
    conn = sqlite3.connect('discord_bot.db')
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE user_id = ? AND server_id = ?", (user_id, server_id,))
    record = c.fetchone()
    userMessages = record[2]
    userKarma = record[3]

    finalValue = userKarma + karmaDelta

    c.execute('''UPDATE users SET numMessages = ? WHERE user_id = ? AND server_id = ?''', (userMessages+1, user_id, server_id))
    c.execute('''UPDATE users SET karma = ? WHERE user_id = ? AND server_id = ?''', (round(finalValue, 2), user_id, server_id))
    conn.commit()
    conn.close()

def maxKarma(server_id):
    conn = sqlite3.connect('discord_bot.db')
    c = conn.cursor()

    c.execute('''
              SELECT user_id 
              FROM users 
              WHERE karma = (SELECT MAX(karma) FROM users WHERE server_id = ?)''', (server_id,))
    maxID = c.fetchone()
    conn.close()
    return maxID


def minKarma(server_id):
    conn = sqlite3.connect('discord_bot.db')
    c = conn.cursor()

    c.execute('''SELECT user_id 
              FROM users 
              WHERE karma = (SELECT MIN(karma) FROM users WHERE server_id = ?)''', (server_id,))
    minID = c.fetchone()
    conn.close()
    return minID