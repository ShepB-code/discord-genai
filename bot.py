from env import init_environment, DISCORD_TOKEN, GEMINI_TOKEN
import os
import discord
from discord.ext import commands
import google.generativeai as genai


class CodingBot(commands.Bot):
    def __init__(self):
        # gemini
        genai.configure(api_key=GEMINI_TOKEN)

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "response_mime_type": "text/plain",
        }

        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash", generation_config=generation_config
        )

        # {user_id : chat}
        self.chats = {}

        # discord
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents, command_prefix="!")

    async def setup_hook(self):
        await self.register_commands()
        await self.register_events()

    async def register_events(self):
        @self.event
        async def on_message(message: discord.Message):
            # ignore messages from the bot
            if message.author == self.user:
                return

            # if reply and it's a reply to the bots last message
            if message.reference:
                original_message = await message.channel.fetch_message(
                    message.reference.message_id
                )
                user_id = message.author.id
                if original_message.author.id == self.user.id:
                    if user_id in self.chats:
                        # send another message to the pre-existing chat
                        response = self.chats[user_id].send_message(message.content)
                        await message.channel.send(response.text)
            await self.process_commands(message)

    async def register_commands(self):
        @self.command()
        async def ping(ctx):
            await ctx.send(f"Pong! Latency: {round(self.latency * 1000)}ms")

        @self.command()
        async def code(ctx):
            msg = ctx.message.content

            chat = self.model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": (
                            "You are an assistant that generates code to answer prompts."
                            "Output your response in the following markdown format:\n"
                            "```language (abbreviation)\n code```"
                        ),
                    },
                ]
            )
            response = chat.send_message(f"prompt: {msg}")

            self.chats[ctx.message.author.id] = chat
            print(f"Length: {len(response.text)}")

            # send message as file attatchment if the response is longer than 2k characters (discord limit)
            if len(response.text) > 2000:
                lines = response.text.splitlines()

                trimmed_output = "\n".join(lines[1:-1])

                with open("output.txt", "w") as file:
                    file.write(trimmed_output)

                await ctx.send(
                    "The code is too long to display as a message, so here is a .txt file:",
                    file=discord.File("output.txt"),
                )
                os.remove("output.txt")
            else:
                await ctx.send(response.text)


def main():
    init_environment()

    # Bot setup
    client = CodingBot()
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
