import os
import discord
from discord import Embed
from dotenv import load_dotenv
import openai
from datetime import datetime
from datetime import timedelta
import random
import string
import config


openai.api_key = config.openai_apikey

TOKEN = config.dassoul_apikey

intents = discord.Intents.default()
intents.message_content = True  # Set to True to receive message content
client = discord.Client(intents=intents)


@client.event
async def on_ready():
  print(f'{client.user} has connected to Discord!')

@client.event
async def on_message_delete(message):
    # Check if the message was deleted in any text channel
    if message.guild is not None and message.guild.channels is not None:
        # Iterate over all channels in the guild
        for channel in message.guild.channels:
            # Check if the channel is a text channel and its ID matches the log channel ID
            if isinstance(channel, discord.TextChannel) and channel.id == 606367772212985866:
                # Get the author's server nickname if it exists, otherwise use their username
                author_name = message.author.nick if message.author.nick else message.author.name
                # Get the current date and time in Unix timestamp format
                current_time = int(datetime.now().timestamp())
                # Get the author's avatar URL
                avatar_url = message.author.avatar if message.author.avatar else message.author.default_avatar
                # Get the user who deleted the message
                async for entry in message.guild.audit_logs(action=discord.AuditLogAction.message_delete, limit=1):
                    deleter = entry.user
                    break  # Only need the first entry
                # Create an Embed object
                embed = discord.Embed(title="Message Deleted", color=0x8700ff)
                # Set the author's icon to the user's avatar URL
                embed.set_author(name=f"{message.author.name} ({author_name})", icon_url=avatar_url)
                # embed.add_field(name="Deleted by", value=deleter.name, inline=False)
                embed.add_field(name="Channel", value=message.channel.mention, inline=False)
                embed.add_field(name="Content", value=f"> {message.content}", inline=False)
                embed.add_field(name="Date", value=f"<t:{current_time}>", inline=False)
                # Send the log message as an embed
                await channel.send(embed=embed)



@client.event
async def on_message_edit(before, after):

    # Check if the message was edited in any text channel
    if before.guild is not None and before.guild.channels is not None:

        # Iterate over all channels in the guild
        for channel in before.guild.channels:
            # Check if the channel is a text channel and its ID matches the log channel ID
            if isinstance(channel, discord.TextChannel) and channel.id == 606367772212985866:
                # get message URL to jump to 
                message_URL = after.jump_url

                # get author server nickname
                author_name = before.author.nick if before.author.nick else before.author.name

                # Create an Embed object
                embed = discord.Embed(title="Message Edited", color=0xf700ff)

                # Set the author's icon to the user's avatar URL
                avatar_url = before.author.avatar if before.author.avatar else before.author.default_avatar
                embed.set_author(name=before.author.name, icon_url=avatar_url)
                embed.set_author(name=f"{before.author.name} ({author_name})", icon_url=avatar_url)

                # Add fields to the embed
                embed.add_field(name="Channel", value=before.channel.mention, inline=False)
                embed.add_field(name="Before", value=before.content, inline=False)
                embed.add_field(name="After", value=after.content, inline=False)
                embed.add_field(name="View Message", value=message_URL, inline=False)
                # Send the log message as an embed
                await channel.send(embed=embed)


@client.event
async def on_voice_state_update(member, before, after):
    avatar_url = member.avatar if member.avatar else member.default_avatar
    author_name = member.nick if member.nick else member.name

    # Check if the member joined a voice channel
    if before.channel is None and after.channel is not None:
        # Get the logger channel
        logger_channel = client.get_channel(606367772212985866)
        if logger_channel:
            # Create an Embed object for the logger message
            embed = discord.Embed(title=f"Joined a Voice Channel", color=0x00ff00)
            embed.set_author(name=f"{member.name} ({author_name})", icon_url=avatar_url)
            embed.add_field(name="User", value=f"{member.name} ({author_name})", inline=False)
            embed.add_field(name="Voice Channel", value=after.channel.jump_url, inline=False)
            # Send the logger message as an embed
            await logger_channel.send(embed=embed)

    # check if someone left a voice channel
    if before.channel is not None and after.channel is None:
        logger_channel = client.get_channel(606367772212985866)
        if logger_channel:
            # Create an Embed object for the logger message
            embed = discord.Embed(title=f"Left a Voice Channel", color=0xFF0000)
            embed.set_author(name=f"{member.name} ({author_name})", icon_url=avatar_url)
            embed.add_field(name="User", value=f"{member.name} ({author_name})", inline=False)
            embed.add_field(name="Voice Channel", value=before.channel.jump_url, inline=False)
            # Send the logger message as an embed
            await logger_channel.send(embed=embed)

    # Check if someone has been server muted
    if before.mute == False and after.mute == True:
        logger_channel = client.get_channel(606367772212985866)
        if logger_channel:
          embed = discord.Embed(title=f"Server Muted", color=0x910000)
          embed.set_author(name=f"{member.name} ({author_name})", icon_url=avatar_url)
          embed.add_field(name="User muted", value=f"{member.name} ({author_name})", inline=False)
          embed.add_field(name="Voice Channel", value=before.channel.jump_url, inline=False)
          await logger_channel.send(embed=embed)

    # Check if someone has been server deafened
    if before.deaf == False and after.deaf == True:
        logger_channel = client.get_channel(606367772212985866)
        if logger_channel:
          embed = discord.Embed(title=f"Server Deafened", color=0x910000)
          embed.set_author(name=f"{member.name} ({author_name})", icon_url=avatar_url)
          embed.add_field(name="User", value=f"{member.name} ({author_name})", inline=False)
          embed.add_field(name="Voice Channel", value=before.channel.jump_url, inline=False)
          await logger_channel.send(embed=embed)
    


current_conversation = ""
curr_msg_count = 0
first_msg_time = 0
latest_msg_time = 0

@client.event
async def on_message(message):
  # Check if the message is from the desired channel
  # satellite haidwars channel id: 599408091380842555
  # fisa hadiwars channel id: 1186433655497834518

  if message.channel.id == 599408091380842555 or message.channel.id == 1186433655497834518:
    # Check if the author of the message is not the bot itself to avoid an infinite loop
    if message.author != client.user:
      global current_conversation
      global curr_msg_count
      global first_msg_time
      global latest_msg_time

      # print(message.content)
      newest_message = str(message.content).lower()

      # remove punctuation from message
      stripped_message = ""
      for char in newest_message:
         if char not in string.punctuation:
            stripped_message += char

      current_conversation += "usr:" + str(
          message.author.name) + " msg:" + str(stripped_message) + "\n"
      curr_msg_count += 1

      if (first_msg_time == 0):
        first_msg_time = datetime.now()
        latest_msg_time = datetime.now()

      elif (latest_msg_time == 0 or latest_msg_time < datetime.now()):
        latest_msg_time = datetime.now()

      if (latest_msg_time - first_msg_time > timedelta(seconds=30)
          and curr_msg_count % 7 == 0 and curr_msg_count != 0):
        print(current_conversation)
        print("")
        print("Latest msg time: " + str(latest_msg_time))
        print("First msg time: " + str(first_msg_time))

        anti_keywords = [
           "fortnite", "brotnite", "bortnite", "abortnite", "abort nite", "fort", "fort nite", "helldivers", "hell divers", "heaven climbers", "heckclimbers", "heck climbers"
        ]

        contains_anti_keyword = False
        for word in anti_keywords:
           if word in current_conversation:
              contains_anti_keyword = True
              print("Contains anti keyword: " + str(contains_anti_keyword))
              print("anti keyword found: " + word)
              break

        keywords = [
            "bedwar", "bw", "highblock", "high block", "sky block", "1179986479397736508",
            " 2s", " 3s", " 4s", "twos", "threes", "fours", "fkdr", "mineplex", "hop on", 
            "online", "dream", "george", "sapnap", "captain", "sparklez",
            "sparkles", "minecraft", "get on", "getting on", "skyblock", "hypixel", "duck", "ducking", "lwar", "4 people", "four people"
        ]

        contains_keyword = False
        for word in keywords:
          if word in current_conversation:
            contains_keyword = True
            print("Contains keyword: " + str(contains_keyword))
            print("keyword found: " + word)
            break

        if contains_keyword is False or contains_anti_keyword is True:
          chatgpt_input = [{
              "role":
              "system",
              "content":
              "your task is to determine if the conversation in the current discord channel is relevant to anything minecraft or bedwars. the topics highblock, headwars, haidwars, 2s, 3s, 4s, twos, threes, fours, discussing how many people are online, or when to hop on or play, are all also considered to be relevant. if any of those terms are present in the conversation it's considered relevant. respond with only yes or no"
          }]
          chatgpt_input.append({
              "role": "user",
              "content": current_conversation
          })

          chat = openai.chat.completions.create(model='gpt-3.5-turbo',
                                                messages=chatgpt_input)
          reply = chat.choices[0].message.content
          reply = reply.lower()

          print(reply)

          if (reply == "no"):
            dassoul_responses = [
                "It doesn't seem like you're talking about Minecraft or Bedwars. Please move to a different channel.",
                "STOP!!! IF YOU'RE NOT TALKING ABOUT HEADWARS MOVE TO A DIFFERENT CHANNEL",
                "STOP STOP STOP STOPPPPP HEADWARS ONLY IN THIS CHANNEL",
                "this channel is only for BEDWARS DISCUSSION. use your eyes YOU DRONE",
                "get this NON MINECRAFT BULL SHIT out of the SACRED MINECRAFT CHANNEL",
                "the soul of @da wishes for there to only be relevant minecraft discussion in this channel", 
                "stop talking about non minecraft topics YOU TROGLODYTE",
                "if i see something non minecraft ONE MORE TIME, i will LOOKS MAX YOU",

            ]
            random_number = random.randint(0, len(dassoul_responses) - 1)
            await message.channel.send(
                f'{message.author.mention} {dassoul_responses[random_number]}')
            curr_msg_count = 0
            current_conversation = ""
            first_msg_time = 0
            latest_msg_time = 0
        
        print("type of latest time - first time" + str(type(latest_msg_time - first_msg_time)))
      if (curr_msg_count > 15):
        curr_msg_count = 0
        current_conversation = ""
        first_msg_time = 0
        latest_msg_time = 0
            

client.run(TOKEN)