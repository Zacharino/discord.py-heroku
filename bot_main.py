# This example requires the 'message_content' intent.
import os
import ast
import discord
import re
from dotenv import load_dotenv
from discord.ext import commands
from datetime import datetime

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

with open('db/static_values.txt') as f:
  consts = f.read()
consts = ast.literal_eval(consts)

@bot.event
async def on_ready():
  print(f'We have logged in as {bot.user}')

@bot.command(aliases= ['purge','delete'])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=None): # Set default value as None
  if amount == None:
    await ctx.channel.purge(limit=1000000)
  else:
    try:
      int(amount)
    except: # Error handler
      await ctx.send('Please enter a valid integer as amount.')
    else:
      await ctx.channel.purge(limit=int(amount))

@bot.command()
async def boss(ctx, arg):
  p = re.compile("[a-zA-Z]+://[a-zA-Z]+\.[a-zA-Z]+/4[a-zA-Z]+([+-]?(?=\.\d|\d)(?:\d+)?(?:\.?\d*))(?:[eE]([+-]?\d+))?([+-]?(?=\.\d|\d)(?:\d+)?(?:\.?\d*))(?:[eE]([+-]?\d+))?_[a-zA-Z]+")
  boss_name = ''
  thumbnail = ''
  if(re.search(p, arg)):
    author_id = ctx.message.author.id
    try:
      boss_value = arg.split('_')[1]
    except:
      ctx.send("Pls use dps.report link")
    else:
      kill_date_raw = arg.split('-')[1].split('_')[0]
      kill_date = datetime.strptime(kill_date_raw, "%Y%m%d").date()
      if boss_value in consts:
        boss_name = consts.get(boss_value)
        thumbnail = consts.get(boss_value + '-thumb')

        embed_title = boss_name + ' ' + str(kill_date)

        embed_msg = discord.Embed(title=embed_title, description='Our RL submission for ' + boss_name + '. \nMake sure to add your PoVs.', colour=0x1c1c1c, url=arg)
        embed_msg.set_image(url=thumbnail)
        embed_msg.add_field(name='Roster', value='\u200b\n', inline=True)
        embed_msg.add_field(name='PoVs', value='\u200b\n', inline=True)

        message_id = ''

        class View(discord.ui.View):

          # ADD ROSTER BUTTON
          @discord.ui.button(label='Add Roster', style=discord.ButtonStyle.green)
          async def roster_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):

            old_roster_value = embed_msg.fields[0].value
            await interaction.response.send_message("Please submit the names for the roster: ", ephemeral=True)

            def check(m):
              return m.author.id == author_id and m.channel.id == message_channel
            
            msg = await bot.wait_for("message", check=check)
            msg_content = msg.content
            joined_msg = "".join(msg_content)
            formatted_msg = joined_msg.replace(' ', '\n')
            if old_roster_value == "\u200b\n":
              new_roster_value = formatted_msg
            else:
              new_roster_value = old_roster_value + "\n" + formatted_msg
            
            embed_msg.set_field_at(0, name="Roster", value=new_roster_value, inline=True)
            await interaction.edit_original_response(content="Successfully added the roster!")
            await message.edit(embed=embed_msg)
            await msg.delete()


          # ADD POV BUTTON
          @discord.ui.button(label='Add PoV', style=discord.ButtonStyle.green)
          async def pov_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):

            old_pov_value = embed_msg.fields[1].value
            await interaction.response.send_message("Please submit your PoV: ", ephemeral=True)

            def check(m):
              return m.author.id == author_id and m.channel.id == message_channel
            
            msg = await bot.wait_for("message", check=check)
            msg_content = msg.content
            formatted_msg = "".join(msg_content)
            if old_pov_value == "\u200b\n":
              new_pov_value = formatted_msg
            else:
              new_pov_value = old_pov_value + "\n" + formatted_msg
            
            embed_msg.set_field_at(1, name="PoVs", value=new_pov_value, inline=True)
            await interaction.edit_original_response(content="Successfully added PoV!")
            await message.edit(embed=embed_msg)
            await msg.delete()


          # REMOVE ROSTER BUTTON
          @discord.ui.button(label='Remove Roster', style=discord.ButtonStyle.red)
          async def delete_roster_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
            embed_msg.set_field_at(0, name="Roster", value='\u200b\n', inline=True)
            await message.edit(embed=embed_msg)
            if(embed_msg.fields[1].value == '\u200b\n'):
              await interaction.response.send_message("Nothing to remove you monkey!", ephemeral=True)
            else:
              await interaction.response.send_message("Roster removed successfully!", ephemeral=True)

          # REMOVE POV BUTTON
          @discord.ui.button(label='Remove PoV', style=discord.ButtonStyle.red)
          async def delete_pov_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):

            old_pov_value = embed_msg.fields[1].value
            old_pov_value_split = old_pov_value.split('\n')
            print(len(old_pov_value_split))
            print(old_pov_value_split)
            if(len(old_pov_value_split)>1):
              new_pov_value = '\n'.join(old_pov_value_split[:-1])
              embed_msg.set_field_at(1, name="PoVs", value=new_pov_value, inline=True)
              await message.edit(embed=embed_msg)
              await interaction.response.send_message("Latest PoV entry removed successfully!", ephemeral=True)
            elif(len(old_pov_value_split)==2 and old_pov_value_split[0]!='\u200b'):
              embed_msg.set_field_at(1, name="PoVs", value='\u200b\n', inline=True)
              await message.edit(embed=embed_msg)
              await interaction.response.send_message("Latest PoV entry removed successfully!", ephemeral=True)
            else:
              await interaction.response.send_message("Nothing to remove you monkey!", ephemeral=True)
            

        view = View()
        message = await ctx.send(embed=embed_msg, view=view)
        message_id = message.id
        message_channel = message.channel.id
      
      else:
        await ctx.send('Name not found - ping the fuck out of Zach', delete_after=1)

  else:
    await ctx.send("Incorrect URL! Please try running the command again with a different URL.", delete_after=1)

@bot.event
async def on_message(message):
  if message.author == bot.user:
    return

  if message.content.startswith('$hello'):
    await message.channel.send('Hello!')

  if message.content.startswith('$'):
    await bot.process_commands(message)
    await message.delete()
  
bot.run(TOKEN)