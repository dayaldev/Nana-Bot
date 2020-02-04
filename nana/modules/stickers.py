import time
import math
import os
from PIL import Image

from nana import app, setbot, Command, DB_AVAIABLE
if DB_AVAIABLE:
	from nana.assistant.database.stickers_db import get_sticker_set, get_stanim_set

from pyrogram import Filters


__MODULE__ = "Stickers"
__HELP__ = """
This module can help you steal sticker, just reply that sticker, type kang, and sticker is your.

──「 **Steal Sticker** 」──
-> `kang`
Reply a sticker/image, and sticker is your.

──「 **Set Sticker Pack** 」──
-> /setsticker
This command only for Assistant bot, to set your sticker pack. When sticker pack is full, type that command, and select another. Or create new at @Stickers
"""

@app.on_message(Filters.user("self") & Filters.command(["kang"], Command))
async def kang_stickers(client, message):
	if not DB_AVAIABLE:
		await message.edit("Your database is not avaiable!")
		return
	sticker_pack = get_sticker_set(message.from_user.id)
	animation_pack = get_stanim_set(message.from_user.id)
	if not sticker_pack:
		await message.edit("You're not setup sticker pack!\nCheck your assistant for more information!")
		await setbot.send_message(message.from_user.id, "Hello 🙂\nYou're look like want to steal a sticker, but sticker pack was not set. To set a sticker pack, type /setsticker and follow setup.")
		return
	sticker_pack = sticker_pack.sticker
	if message.reply_to_message and message.reply_to_message.sticker:
		if message.reply_to_message.sticker.mime_type == "application/x-tgsticker":
			if not animation_pack:
				await message.edit("You're not setup animation sticker pack!\nCheck your assistant for more information!")
				await setbot.send_message(message.from_user.id, "Hello 🙂\nYou're look like want to steal a animation sticker, but sticker pack was not set. To set a sticker pack, type /setanimation and follow setup.")
				return
			await client.download_media(message.reply_to_message.sticker, file_name="nana/cache/sticker.tgs")
		else:
			await client.download_media(message.reply_to_message.sticker, file_name="nana/cache/sticker.png")
	elif message.reply_to_message and message.reply_to_message.photo:
		await client.download_media(message.reply_to_message.photo, file_name="nana/cache/sticker.png")
	elif message.reply_to_message and message.reply_to_message.document and message.reply_to_message.document.mime_type == "image/png":
		await client.download_media(message.reply_to_message.document, file_name="nana/cache/sticker.png")
	else:
		await message.edit("Reply a sticker or photo to kang it!\nCurrent sticker pack is: {}\nCurrent animation pack is: {}".format(sticker_pack, animation_pack.sticker))
		return
	if not (message.reply_to_message.sticker and message.reply_to_message.sticker.mime_type) == "application/x-tgsticker":
		im = Image.open("nana/cache/sticker.png")
		maxsize = (512, 512)
		if (im.width and im.height) < 512:
			size1 = im.width
			size2 = im.height
			if im.width > im.height:
				scale = 512 / size1
				size1new = 512
				size2new = size2 * scale
			else:
				scale = 512 / size2
				size1new = size1 * scale
				size2new = 512
			size1new = math.floor(size1new)
			size2new = math.floor(size2new)
			sizenew = (size1new, size2new)
			im = im.resize(sizenew)
		else:
			im.thumbnail(maxsize)
		im.save("nana/cache/sticker.png", 'PNG')
		
	await client.send_message("@Stickers", "/addsticker")
	await client.read_history("@Stickers")
	time.sleep(0.2)
	if message.reply_to_message.sticker and message.reply_to_message.sticker.mime_type == "application/x-tgsticker":
		await client.send_message("@Stickers", animation_pack.sticker)
	else:
		await client.send_message("@Stickers", sticker_pack)
	await client.read_history("@Stickers")
	time.sleep(0.2)
	checkfull = await app.get_history("@Stickers", limit=1)
	if checkfull[0].text == "Whoa! That's probably enough stickers for one pack, give it a break. A pack can't have more than 120 stickers at the moment.":
		await message.edit("Your sticker pack was full!\nPlease change one from your Assistant")
		os.remove('nana/cache/sticker.png')
		return
	if message.reply_to_message.sticker and message.reply_to_message.sticker.mime_type == "application/x-tgsticker":
		await client.send_document("@Stickers", 'nana/cache/sticker.tgs')
		os.remove('nana/cache/sticker.tgs')
	else:
		await client.send_document("@Stickers", 'nana/cache/sticker.png')
		os.remove('nana/cache/sticker.png')
	try:
		ic = message.text.split(None, 1)[1]
	except:
		try:
			ic = message.reply_to_message.sticker.emoji
		except:
			ic = "🤔"
	if ic == None:
		ic = "🤔"
	await client.send_message("@Stickers", ic)
	await client.read_history("@Stickers")
	time.sleep(1)
	await client.send_message("@Stickers", "/done")
	if message.reply_to_message.sticker and message.reply_to_message.sticker.mime_type == "application/x-tgsticker":
		await message.edit("**Animation Sticker added!**\nYour animated sticker has been saved on [This sticker animated pack](https://t.me/addstickers/{})".format(animation_pack.sticker))
	else:
		await message.edit("**Sticker added!**\nYour sticker has been saved on [This sticker pack](https://t.me/addstickers/{})".format(sticker_pack))
	await client.read_history("@Stickers")
