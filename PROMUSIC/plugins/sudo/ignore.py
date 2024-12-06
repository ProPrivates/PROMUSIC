from pyrogram import filters
from pyrogram.types import Message
from PROMUSIC import app
from config import OWNER_ID, OWNER_USERNAME  # Replace this with the specific owner ID
from PROMUSIC.utils.database import add_ignored_user, is_ignored_user, remove_ignored_user, get_ignored_users

# Ignore a user
@app.on_message(filters.command("ignore") & filters.user(OWNER_ID))
async def ignore_user(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a user's message to ignore them.")
    
    ignored_user_id = message.reply_to_message.from_user.id
    if await is_ignored_user(ignored_user_id):
        return await message.reply_text("This user is already ignored.")
    
    await add_ignored_user(ignored_user_id)
    await message.reply_text(f"User {ignored_user_id} is now ignored.")



# Stop ignoring a user
@app.on_message(filters.command("unignore") & filters.user(OWNER_ID))
async def unignore_user(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a user's message to unignore them.")
    
    ignored_user_id = message.reply_to_message.from_user.id
    if not await is_ignored_user(ignored_user_id):
        return await message.reply_text("This user is not in the ignore list.")
    
    await remove_ignored_user(ignored_user_id)
    await message.reply_text(f"User {ignored_user_id} is no longer ignored.")



# Check ignored users
@app.on_message(filters.command("ignoredlist") & filters.user(OWNER_ID))
async def ignored_list(client, message: Message):
    ignored_users = await get_ignored_users()
    if not ignored_users:
        return await message.reply_text("No users are currently ignored.")
    
    ignored_text = "Ignored Users:\n"
    for user_id in ignored_users:
        ignored_text += f"- {user_id}\n"
    await message.reply_text(ignored_text)



# Automatically delete messages if an ignored user mentions the owner

# List of ignored users
IGNORED_USERS = [7480332189]  # Add more user IDs as needed

@app.on_message(filters.group & filters.text)
async def handle_mentions(client, message: Message):
    # Check if the user is in the ignore list
    if message.from_user.id in IGNORED_USERS:
        # Check if message is a reply to the owner
        mentioned_owner = False
        if message.reply_to_message and message.reply_to_message.from_user.id == OWNER_ID:
            mentioned_owner = True

        # Check for mentions in the message text
        owner_mentions = [OWNER_USERNAME, "Zeo"]  # Add variations of your name/username
        if message.entities:
            for entity in message.entities:
                if entity.type == "mention":
                    mentioned_text = message.text[entity.offset:entity.offset + entity.length]
                    if mentioned_text in [f"@{OWNER_USERNAME}"]:
                        mentioned_owner = True

        # Check for name-based mentions in the text
        if any(name in message.text for name in owner_mentions):
            mentioned_owner = True

        if mentioned_owner:
            try:
                # Delete the message and send the "Fuck off" message
                await message.delete()
                await message.reply_text(f"Fuck off, {message.from_user.mention} !!")
            except Exception as e:
                print(f"Error in deleting or replying: {e}")

# Command to dynamically add a user to the ignore list
@app.on_message(filters.command("ignore_user") & filters.user(OWNER_ID))
async def add_ignored_user(client, message: Message):
    try:
        # Extract user ID from the command
        if len(message.command) > 1:
            user_id = int(message.command[1])
            if user_id not in IGNORED_USERS:
                IGNORED_USERS.append(user_id)
                await message.reply_text(f"User {user_id} has been added to the ignore list.")
            else:
                await message.reply_text(f"User {user_id} is already in the ignore list.")
        else:
            await message.reply_text("Please specify a user ID.")
    except ValueError:
        await message.reply_text("Invalid user ID. Please provide a valid number.")

# Command to dynamically remove a user from the ignore list
@app.on_message(filters.command("unignore_user") & filters.user(OWNER_ID))
async def remove_ignored_user(client, message: Message):
    try:
        # Extract user ID from the command
        if len(message.command) > 1:
            user_id = int(message.command[1])
            if user_id in IGNORED_USERS:
                IGNORED_USERS.remove(user_id)
                await message.reply_text(f"User {user_id} has been removed from the ignore list.")
            else:
                await message.reply_text(f"User {user_id} is not in the ignore list.")
        else:
            await message.reply_text("Please specify a user ID.")
    except ValueError:
        await message.reply_text("Invalid user ID. Please provide a valid number.")
