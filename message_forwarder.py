from discord_webhook import DiscordWebhook, DiscordEmbed
import discord
from discord.ext import commands
import logging

from dotenv import load_dotenv
import os

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('discord')

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Replace with your webhook URL
WEBHOOK_URL = os.getenv("WEBHOOK_TO_BE_MONITORED")
MESSAGE_FORWARDING_WEBHOOK_URL = os.getenv("WEBHOOK_TO_BE_FORWARDED")
MONITORED_CHANNEL_ID = os.getenv("CHANNEL_ID")


@bot.event
async def on_ready():
    logger.info(f'Bot is ready and logged in as {bot.user}')
    channel = bot.get_channel(MONITORED_CHANNEL_ID)
    logger.info(f'Monitoring channel: {channel.name if channel else "Channel not found"}')


@bot.event
async def on_message(message):
    logger.debug(f'Message received from channel {message.channel.id}')

    if message.author == bot.user:
        logger.debug('Message is from bot, ignoring')
        return

    if message.channel.id == MONITORED_CHANNEL_ID:
        if message.content and not message.content.startswith('http'):
            logger.info(f'Message detected in monitored channel from {message.author}: {message.content}')

            try:
                # Create webhook
                webhook = DiscordWebhook(url=MESSAGE_FORWARDING_WEBHOOK_URL)

                # Create embed
                embed = DiscordEmbed(
                    title="Forwarded Message",
                    description=message.content,
                    color=242424
                )

                # Add author info
                embed.set_author(
                    name=message.author.display_name,
                    icon_url=message.author.avatar.url if message.author.avatar else None
                )

                # Add timestamp
                embed.set_timestamp()

                # Add embed to webhook
                webhook.add_embed(embed)

                # Send files if any
                if message.attachments:
                    logger.info(f'Processing {len(message.attachments)} attachments')
                    for attachment in message.attachments:
                        webhook.add_file(file=await attachment.read(), filename=attachment.filename)

                # Execute webhook
                response = webhook.execute()
                logger.info(f'Webhook executed with response status: {response.status_code if response else "No response"}')

            except Exception as e:
                logger.error(f'Error in webhook execution: {str(e)}', exc_info=True)

    await bot.process_commands(message)


# Add a test command to verify bot is working
@bot.command()
async def test(ctx):
    await ctx.send('Bot is working!')


bot.run(os.getenv("TOKEN"))
