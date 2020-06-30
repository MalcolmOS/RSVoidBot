import MessageEvents
import discord
import Utils

TOKEN = ''
client = discord.Client()


@client.event
async def on_ready():
    Utils.log("Client is ready...")
    await client.change_presence(activity=discord.Game(name='www.rsvoid.com/'), status=discord.Status.idle)


@client.event
async def on_member_join(member):
    Utils.log(f'Sending message to new member - {member} - {member.id}')
    message = f'**Welcome to the RSVoid Official Discord Server**\n\nTo be verified please send me a message using the command !verify with your RSVoid profile linked to it\n\n**Example:** !verify https://www.rsvoid.com/profile/201-malcolm/\n\nThis should process a request to send a token to your RSVoid forums account which you will then redeem in this same direct message.\n\n**Example:** !redeem TOKEN\n\nIf you encounter any issues with the bot please send <@216026953130573824> a direct message.'
    try:
        await member.send(message)
    except discord.errors.Forbidden:
        await client.get_channel(MessageEvents.LOGGER_CHANNEL).send(f' <@{member.id}> Has direct messages disabled, cannot send message on join.')


if __name__ == "__main__":

    message_event = MessageEvents.MessageEvent(client=client)
    message_event.run_message_events()
    client.run(TOKEN)





