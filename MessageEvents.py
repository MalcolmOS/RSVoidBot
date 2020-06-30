import discord
import asyncio
from concurrent.futures import ThreadPoolExecutor
import enum
import RSVoidWebsiteUtils
import Utils
import AWS
from Crypto import BinanceClient

RSVOID_GUILD = 710071315423297549
LOGGER_CHANNEL = 726922426000081058

PREFIX = '!'


class MessageEvent:

    def __init__(self, client):
        print('Loading GuildMessageEvent class...')
        self.client = client
        self.message = None
        self.content = None
        self.binance = BinanceClient()

    def run_message_events(self):
        @self.client.event
        async def on_message(message):
            if not message.author.bot and message.content.startswith(PREFIX):
                self.message = message
                self.content = self.message.content.lower()
                if message.channel.type is discord.ChannelType.text:
                    await self.run_text_channel_events()
                elif message.channel.type is discord.ChannelType.private:
                    await self.run_direct_channel_events()

    async def run_direct_channel_events(self):
        if self.is_command(Command.VERIFY):
            if AWS.does_unique_id_exist(unique_id=self.message.author.id):
                await self.message.channel.send("This Discord Profile is already linked to an account. Please speak to a moderator if you believe this is an error or you need to request a change.")
            else:
                await self.send_token_to_user()
        elif self.is_command(Command.REDEEM):
            await self.verify_user()

    async def run_text_channel_events(self):
        if self.is_command(Command.CRYPTO):
            await self.send_embed(title="Crypto", message=self.binance.get_crypto_info())
        elif self.is_command(Command.FARMATON):
            #await self.message.channel.send("https://discord.gg/KPcGnyx")
            await self.message.channel.send("Crops")
        elif self.is_command(Command.GET_ROLES):
            await self.get_roles()
        elif self.is_command(Command.HELP):
            await self.send_help_message()
        elif self.is_command(Command.PROFILE):
            await self.get_profile()
        elif self.is_command(Command.REP):
            await self.get_rep()
        elif self.is_command(Command.UPDATE_ROLES):
            await self.update_user_roles()

    async def send_token_to_user(self):
        user = RSVoidWebsiteUtils.get_user_url_from_message(message=self.message.content)
        channel = self.message.channel
        user_id = self.message.author.id
        if user:
            if AWS.does_profile_exist(profile=user):
                await self.message.channel.send("This RSVoid Profile is already linked to an account. Please speak to a moderator if you believe this is an error or you need to request a change.")
            else:
                print(f'Token requested for {user} by {user_id}')
                await channel.send(f'Sending token...please wait a few minutes for it to appear.')
                token = Utils.generate_user_token()
                loop = asyncio.get_event_loop()
                event = RSVoidWebsiteUtils.SendTokenEvent(user=user, token=token)
                resp = await loop.run_in_executor(ThreadPoolExecutor(), event.run)
                if resp == 200:
                    print("Token has successfully been posted to users profile.")
                    await channel.send(f'The token has successfully been sent to your profile.')
                    AWS.create_new_link_in_table(unique_id=user_id, token=token, profile=user)
                else:
                    await channel.send(f'There was an error posting your token to your profile. Admins have been notified of the error.')
                    await self.client.get_channel(LOGGER_CHANNEL).send(f'<@{self.message.author.id}> encountered an error while requesting a DM for a token.\n{resp}')
        else:
            await channel.send('The user entered returned an invalid value')

    async def verify_user(self):
        print("Redemption requested...")
        splits = self.content.split(' ')
        try:
            provided_token = splits[1]
            db_token = AWS.get_field_from_table(unique_id=self.message.author.id, field='AuthToken')
            if db_token and db_token.lower() == provided_token.lower():
                AWS.update_field_in_table(unique_id=self.message.author.id, field='Verified', value=True)
                await self.add_role_to_user(user=self.message.author.id)
                await self.message.channel.send('Verification has been successful.')
                await self.client.get_channel(LOGGER_CHANNEL).send(f'<@{self.message.author.id}> Has been verified as - {AWS.get_field_from_table(unique_id=self.message.author.id, field="Profile")}')
        except Exception as e:
            print(e)
            await self.message.channel.send('There was an error processing this request.')
            await self.client.get_channel(LOGGER_CHANNEL).send(f'<@{self.message.author.id}> encountered an error while processing a token request.\n{e}')

    async def update_user_roles(self):
        splits = self.content.split(' ')
        if len(splits) == 1:
            await self.add_role_to_user(user=self.message.author.id)
        elif self.message.mentions:
            await self.add_role_to_user(user=self.message.mentions[0].id)

    async def add_role_to_user(self, user):
        print(f"Attempting to update roles for {user}")
        guild = self.get_rsvoid_guild()
        for member in guild.members:
            if member.id == user:
                if AWS.does_unique_id_exist(unique_id=user):
                    roles = RSVoidWebsiteUtils.get_user_roles(url=AWS.get_field_from_table(unique_id=user, field='Profile')).split("\n")
                    for role in roles:
                        if role in RSVoidWebsiteUtils.ROLES:
                            role = discord.utils.get(guild.roles, id=RSVoidWebsiteUtils.ROLES[role])
                            await member.add_roles(role)
                else:
                    print(f'{user} is not in DynamoDB database.')
                break

    async def get_roles(self):
        splits = self.content.split(' ')
        if len(splits) == 1:
            await self.get_roles_for_user(user=self.message.author.id)
        elif self.message.mentions:
            await self.get_roles_for_user(user=self.message.mentions[0].id)

    async def get_roles_for_user(self, user):
        url = AWS.get_field_from_table(unique_id=user, field='Profile')
        if url:
            await self.send_embed(title=f"{RSVoidWebsiteUtils.get_user_name_from_url(url=url)}'s Roles", message=f'```fix\n{RSVoidWebsiteUtils.get_user_roles(url=url)}```')
        else:
            await self.message.channel.send('The user entered returned an invalid value')

    async def get_profile(self):
        splits = self.content.split(' ')
        if len(splits) == 1:
            await self.get_profile_for_user(user=self.message.author.id)
        elif self.message.mentions:
            await self.get_profile_for_user(user=self.message.mentions[0].id)

    async def get_profile_for_user(self, user):
        user = AWS.get_field_from_table(unique_id=user, field='Profile')
        if user:
            await self.message.channel.send(user)
        else:
            await self.message.channel.send('No profile found.')

    async def get_rep(self):
        splits = self.content.split(' ')
        if len(splits) == 1:
            await self.get_rep_for_user(user=self.message.author.id)
        elif self.message.mentions:
            await self.get_rep_for_user(user=self.message.mentions[0].id)

    async def get_rep_for_user(self, user):
        try:
            if AWS.does_unique_id_exist(unique_id=user):
                url = AWS.get_field_from_table(unique_id=user, field='Profile')
                name = RSVoidWebsiteUtils.get_user_name_from_url(url=url)
                fb_score = RSVoidWebsiteUtils.get_user_feedback_score(url=url)
                fb_resp = RSVoidWebsiteUtils.get_recent_feedback(url=url)
                rep_resp = RSVoidWebsiteUtils.get_user_rep(url=url)
                await self.send_embed(title=f"{name}'s Reputation", message=f"**Reputation**\n```\nTitle: {rep_resp['Title']}\nScore: {rep_resp['Score']}```\n**Feedback**\n```\nPositive: {fb_score['Positive']}\nNeutral: {fb_score['Neutral']}\nNegative: {fb_score['Negative']}```\n**Recent Feedback**\n{fb_resp}")
            else:
                await self.message.channel.send("This profile is not linked to an RSVoid user.")
        except Exception as e:
            await self.client.get_channel(LOGGER_CHANNEL).send(f'<@{self.message.author.id}> encountered an error while trying to get feedback from the website.\n{e}')

    async def send_help_message(self):
        content = '**Public Channel Commands**'
        for command in PublicChannelCommandDescription:
            content += f'```fix\n{PREFIX}{command.name.replace("_", "").lower()}\n{command.value}```'
        content += '\n**Private Channel Commands**\n'
        for command in PrivateChannelCommandDescription:
            content += f'```fix\n{PREFIX}{command.name.replace("_", "").lower()}\n{command.value}```'
        await self.send_embed(title='Help Menu', message=content)

    async def send_embed(self, title, message):
        embed = discord.Embed(
            title=title,
            description=message,
            color=discord.Color.blue()
        )
        embed.set_footer(text="Created by Malcolm", icon_url=self.client.get_user(216026953130573824).avatar_url)
        await self.message.channel.send(embed=embed)

    def is_command(self, command):
        return self.content.startswith(f'{PREFIX}{command.value}')

    def get_rsvoid_guild(self):
        return self.client.get_guild(RSVOID_GUILD)


class Command(enum.Enum):
    CRYPTO = 'crypto'
    FARMATON = 'farm'
    GET_ROLES = 'getroles'
    HELP = 'help'
    PROFILE = 'profile'
    REDEEM = 'redeem'
    REP = 'rep'
    UPDATE_ROLES = 'updateroles'
    VERIFY = 'verify'


class PublicChannelCommandDescription(enum.Enum):
    CRYPTO = 'Returns popular Crypto prices in current time'
    #FARM = 'Returns the link to the farmaton bot manager'
    FARM = 'Crops'
    GET_ROLES = 'Returns the RSVoid profile displayed roles'
    HELP = 'Returns this help menu'
    PROFILE = 'Returns a link to the RSVoid profile'
    REP = 'Returns the RSVoid users community reputation'
    UPDATE_ROLES = 'Updates a users roles according to their RSVoid profile'


class PrivateChannelCommandDescription(enum.Enum):
    REDEEM = 'Redeems a verification code'
    VERIFY = 'Starts the verification process for the requested user'


















