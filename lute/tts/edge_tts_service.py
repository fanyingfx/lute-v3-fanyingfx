#!/usr/bin/env python3

"""
Example of dynamic voice selection using VoicesManager.
"""

import asyncio
import os.path

# import pygame
import subprocess
from hashlib import md5

import edge_tts

from lute.tts.multiplelang_detect import get_lang

voice_dict = {"en": "en-US-JennyNeural", "ja": "ja-JP-NanamiNeural"}


# TEXT = "Hoy es un buen día."
# OUTPUT_FILE = "spanish.mp3"


# async def amain() -> None:
#     """Main function"""
#     # voices = await VoicesManager.create()
#     # voice = voices.find(Gender="Male", Language="es")
#     # Also supports Locales
#     # voice = voices.find(Gender="Female", Locale="es-AR")
#
#     communicate = edge_tts.Communicate(TEXT, )
#     await communicate.save(OUTPUT_FILE)


# if __name__ == "__main__":
#     loop = asyncio.get_event_loop_policy().get_event_loop()
#     try:
#         loop.run_until_complete(amain())
#     finally:
#         loop.close()
def gen_text_filename(text):
    filename = md5(text.encode("utf-8")).hexdigest() + ".mp3"
    return filename


def play_sound(text):
    # filename=md5(text.encode('utf-8')).hexdigest()+'.mp3'
    filename = gen_text_filename(text)
    subprocess.run(["mpv", filename])
    # playsound(filename)


async def save_sound(text, filepath):
    lang = get_lang(text)
    short_name = voice_dict.get(lang)
    # voice = voices.find(ShortName=short_name)

    filename = filepath
    if os.path.exists(filename):
        return
    communicate = edge_tts.Communicate(text, short_name)
    # filename=md5(text.encode('utf-8')).hexdigest()+'.mp3'
    # filename = res.hexdigest()+'.mp3'
    # file_name=md5_hash.hexdigest()+'.mp3'
    if os.path.exists(filename):
        return
    # subprocess.run(["edge-tts",'--voice',short_name,'--text',text,'--write-media',filename])

    await communicate.save(filename)
    #


def save_sound_sync(text, path):
    # loop = asyncio.get_event_loop_policy().get_event_loop()
    asyncio.run(save_sound_sync(text, path))
    # try:
    #     loop.run_until_complete(save_sound(text,path))
    # finally:
    #     loop.close()


if __name__ == "__main__":
    text = "私は元気です"
    save_sound_sync(text)
    play_sound(text)
