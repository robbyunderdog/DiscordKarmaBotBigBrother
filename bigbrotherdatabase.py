import sqlite3

def init_db():
    conn = sqlite3.connect('discord_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, numMessages INTEGER, karma INTEGER)''')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('discord_bot.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (user_id, numMessages, karma) VALUES (?, ?, ?)", 
              (user_id, 0, 0))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('discord_bot.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def alterRecord(user_id, karmaDelta):
    conn = sqlite3.connect('discord_bot.db')
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    record = c.fetchone()
    userMessages = record[1]
    userKarma = record[2]

    finalValue = userKarma + karmaDelta

    c.execute('''UPDATE users SET numMessages = ? WHERE user_id = ?''', (userMessages+1, user_id))
    c.execute('''UPDATE users SET karma = ? WHERE user_id = ?''', (round(finalValue, 2), user_id))
    conn.commit()
    conn.close()

def maxKarma():
    conn = sqlite3.connect('discord_bot.db')
    c = conn.cursor()

    c.execute('''SELECT user_id FROM users WHERE karma = (SELECT max(karma) FROM users)''')
    maxID = c.fetchone()

    return maxID


def minKarma():
    conn = sqlite3.connect('discord_bot.db')
    c = conn.cursor()

    c.execute('''SELECT * FROM users WHERE karma = (SELECT min(karma) FROM users)''')
    minID = c.fetchone()

    return minID