# Postgres (Neon) data layer for the karma bot. All access goes through a shared
# asyncpg connection pool, so callers never manage connections themselves.
import os
import asyncpg

DATABASE_URL = os.getenv("DATABASE_URL")

_pool = None

async def init_db():
    """Open the connection pool and make sure the schema exists. Must be awaited
    once, before the bot starts handling events (see setup_hook in BigBrother.py)."""
    global _pool
    _pool = await asyncpg.create_pool(dsn=DATABASE_URL)
    async with _pool.acquire() as conn:
        # user_id/server_id are Discord snowflake IDs, which exceed 32-bit INTEGER
        # range, so they need BIGINT. karma is a running float total, not a count.
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT NOT NULL,
                server_id BIGINT NOT NULL,
                numMessages INTEGER NOT NULL DEFAULT 0,
                karma DOUBLE PRECISION NOT NULL DEFAULT 0,
                PRIMARY KEY (user_id, server_id)
            )
        ''')
        # PRIMARY KEY is (user_id, server_id), so a plain "WHERE server_id = ?"
        # lookup (used by maxKarma/minKarma) can't use it as a leading index -
        # this index keeps those ranking queries fast as the table grows.
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_server_id ON users(server_id)")

async def get_user(user_id, server_id):
    """Look up one user's row in one server. Returns None if they haven't been seen yet."""
    async with _pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM users WHERE user_id = $1 AND server_id = $2", user_id, server_id)

# Creates the user if needed and applies the karma delta for one message, all in a
# single atomic upsert - Postgres handles the concurrency itself, no app-level
# locking required (unlike the old SQLite version this replaced).
async def record_message(user_id, server_id, karma_delta):
    async with _pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO users (user_id, server_id, numMessages, karma)
            VALUES ($1, $2, 1, $3)
            ON CONFLICT (user_id, server_id) DO UPDATE
                SET numMessages = users.numMessages + 1,
                    karma = round((users.karma + EXCLUDED.karma)::numeric, 2)
        ''', user_id, server_id, round(karma_delta, 2))

async def maxKarma(server_id):
    """Returns (user_id,) of the highest-karma user in this server, or None."""
    async with _pool.acquire() as conn:
        # server_id is bound in both the outer WHERE and the inner MAX() subquery -
        # without the outer filter, a tied karma value in a *different* server could
        # match here and return the wrong user.
        return await conn.fetchrow('''
            SELECT user_id
            FROM users
            WHERE server_id = $1 AND karma = (SELECT MAX(karma) FROM users WHERE server_id = $1)
        ''', server_id)

async def minKarma(server_id):
    """Returns (user_id,) of the lowest-karma user in this server, or None."""
    async with _pool.acquire() as conn:
        return await conn.fetchrow('''
            SELECT user_id
            FROM users
            WHERE server_id = $1 AND karma = (SELECT MIN(karma) FROM users WHERE server_id = $1)
        ''', server_id)
