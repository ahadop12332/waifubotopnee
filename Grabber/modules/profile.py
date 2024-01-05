from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from Grabber import collection, user_collection
from Grabber import sudo_users as DEV_USERS
from Grabber import Grabberu as app
import os

user_levels = {}

def generate_progress_bar(percent):
    filled_blocks = int(percent / 5)
    empty_blocks = 20 - filled_blocks
    return "■" * filled_blocks + "□" * empty_blocks
async def get_global_rank(username: str) -> int:
    pipeline = [
        {"$project": {"username": 1, "first_name": 1, "character_count": {"$size": "$characters"}}},
        {"$sort": {"character_count": -1}}
    ]
    cursor = user_collection.aggregate(pipeline)
    leaderboard_data = await cursor.to_list(length=None)
    for i, user in enumerate(leaderboard_data, start=1):
        if user.get('username') == username:
            return i
    return 0
async def get_user_info(user, already=False):
    if not already:
        user = await app.get_users(user)
    if not user.first_name:
        return ["Deleted account", None]
    user_id = user.id
    username = user.username
    first_name = user.first_name
    userr = await user_collection.find_one({'id': user_id})
    if not userr:
        caught_characters = "𝙃𝙖𝙫𝙚𝙣'𝙩 𝙂𝙤𝙩 𝙖𝙣𝙮 𝙨𝙡𝙖𝙫𝙚𝙨"
    else:
        harem_user = await user_collection.find_one({'id': user_id})
        total_count = len(harem_user['characters'])
        global_count = await collection.count_documents({})
        total_percentage = (total_count / global_count) * 100
        Rounded_total_percentage = round(total_percentage, 2)
        progress_bar = generate_progress_bar(Rounded_total_percentage)
        caught_characters = [str(total_count) + "/" + str(global_count) + "[" + str(Rounded_total_percentage) + "%]"]
        photo_id = user.photo.big_file_id if user.photo else None
        global_rank = await get_global_rank(username)
        total_users = await user_collection.count_documents({})  # Count total users
        global_rank_ratio = f"{global_rank}/{total_users}"
        info_text = (
            f"  ✨ 𝙐𝙎𝙀𝙍 𝙋𝙍𝙊𝙁𝙄𝙇𝙀 ✨\n"
            f"───────────────────────\n"
            f"🌸 𝙉𝘼𝙈𝙀 : {first_name}\n"
            f"💮 𝙐𝙎𝙀𝙍𝙉𝘼𝙈𝙀 : @{username}\n"
            f"🍀 𝘾𝙃𝘼𝙍𝘼𝘾𝙏𝙀𝙍𝙎 𝘾𝘼𝙐𝙂𝙃𝙏 : {caught_characters[0]}\n"
            f"⚜️ 𝙋𝙍𝙊𝙂𝙍𝙀𝙎𝙎 𝘽𝘼𝙍: {progress_bar}\n"
            f"🍥 𝙂𝙇𝙊𝘽𝘼𝙇 𝙍𝘼𝙉𝙆 : {global_rank_ratio}"
        )
     
    return [info_text, photo_id]
@app.on_message(filters.command("sinfo"))
async def info_func(_, message: Message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user.id
    elif not message.reply_to_message and len(message.command) == 1:
        user = message.from_user.id
    elif not message.reply_to_message and len(message.command) != 1:
        user = message.text.split(None, 1)[1]
    m = await message.reply_text("𝙋𝙧𝙤𝙘𝙚𝙨𝙨𝙞𝙣𝙜...")
    try:
        info_text, photo_id = await get_user_info(user)
    except Exception as e:
        print(f"kela hua kela {e}")
        return await m.edit("𝙎𝙤𝙧𝙧𝙮 𝙨𝙤𝙢𝙚𝙩𝙝𝙞𝙣𝙜 𝙒𝙚𝙣𝙩 𝙒𝙧𝙤𝙣𝙜 𝙍𝙚𝙥𝙤𝙧𝙩 𝘼𝙩 @WaifuCatherSupport")
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("𝙎𝙀𝙀 𝙎𝙇𝘼𝙑𝙀𝙎 🍀", switch_inline_query_current_chat=f"collection.{user}")],
        [InlineKeyboardButton("🗑", callback_data="delete_message")]
    ])
    if not photo_id:
        return await m.edit(info_text, disable_web_page_preview=True, reply_markup=keyboard)
    photo = await app.download_media(photo_id)
    await message.reply_photo(photo, caption=info_text, reply_markup=keyboard)
    await m.delete()
    os.remove(photo)
@app.on_callback_query()
async def callback_handler(_, query):
    if query.data == "delete_message":
        await query.message.delete()
