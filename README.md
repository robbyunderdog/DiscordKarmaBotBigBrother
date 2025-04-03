# DiscordKarmaBot
A simple Discord bot that uses sentiment analysis to analyze messages and score them based on how positive or negative they are.
## Features
This bot utilizes the natural language toolkit to use sentiment analysis and score every message sent on the Discord server. This does not log the messages, it only logs the compound analysis score alongside the users ID to keep track. Users can have multiple entries, only limited by the number of servers they are apart of which have this bot. All scores are server specific, which means users scores can vary from server to server.
## Commands
There are two commands that this bot has.
### /whatismysocialcreditscore
This command simply returns with your UserID, the number of messages you have sent since the bot has been added to the server, and finally your credit, or karma. Only shows the users in the server which the command was used.
### /socialcreditranking
This command returns the users with the highest and lowest karma scores.
