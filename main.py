import discord
from discord.ext import commands
import os
import aiohttp
import aiofiles
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────
TOKEN = "YOUR_BOT_TOKEN_HERE"   # 👈 Replace with your bot token
DOWNLOAD_FOLDER = "downloads"   # Folder where renamed files are saved
PREFIX = "!"
# ───────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ── Helper: sanitize filename ───────────────────────────────────
def sanitize(name: str) -> str:
    """Remove characters that are illegal in filenames."""
    illegal = r'\/:*?"<>|'
    for ch in illegal:
        name = name.replace(ch, "_")
    return name.strip()


# ── Events ──────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print(f"   Prefix: {PREFIX}  |  Download folder: {DOWNLOAD_FOLDER}/")
    print("─" * 40)


# ── Commands ─────────────────────────────────────────────────────

@bot.command(name="rename")
async def rename_file(ctx, new_name: str = None):
    """
    Upload a file WITH this command to rename it.
    Usage:  !rename <new_name>   (attach your file to the same message)

    Example:
        !rename my_document          ← keeps original extension
        !rename report.pdf           ← forces a specific extension
    """
    if not ctx.message.attachments:
        await ctx.send(
            "⚠️ Please **attach a file** to your message.\n"
            f"Usage: `{PREFIX}rename <new_name>` (with a file attached)"
        )
        return

    if not new_name:
        await ctx.send(
            f"⚠️ Please provide a new name.\n"
            f"Usage: `{PREFIX}rename <new_name>` (with a file attached)"
        )
        return

    attachment = ctx.message.attachments[0]
    original_ext = Path(attachment.filename).suffix  # e.g. ".png"

    # If the user didn't include an extension, keep the original one
    if "." not in new_name:
        new_name = new_name + original_ext

    new_name = sanitize(new_name)
    save_path = os.path.join(DOWNLOAD_FOLDER, new_name)

    # Download the file
    async with aiohttp.ClientSession() as session:
        async with session.get(attachment.url) as resp:
            if resp.status != 200:
                await ctx.send("❌ Failed to download the file. Please try again.")
                return
            data = await resp.read()

    async with aiofiles.open(save_path, "wb") as f:
        await f.write(data)

    # Send the renamed file back
    await ctx.send(
        f"✅ File renamed to **`{new_name}`** and saved!",
        file=discord.File(save_path, filename=new_name),
    )


@bot.command(name="renameall")
async def rename_all(ctx, prefix_name: str = None):
    """
    Upload MULTIPLE files to rename them all with a numbered prefix.
    Usage:  !renameall <base_name>   (attach multiple files)

    Example:
        !renameall photo
        → photo_1.jpg, photo_2.png, photo_3.gif …
    """
    if not ctx.message.attachments:
        await ctx.send(
            "⚠️ Please **attach files** to your message.\n"
            f"Usage: `{PREFIX}renameall <base_name>` (with files attached)"
        )
        return

    if not prefix_name:
        await ctx.send(
            f"⚠️ Please provide a base name.\n"
            f"Usage: `{PREFIX}renameall <base_name>` (with files attached)"
        )
        return

    prefix_name = sanitize(prefix_name)
    renamed_files = []

    async with aiohttp.ClientSession() as session:
        for i, attachment in enumerate(ctx.message.attachments, start=1):
            ext = Path(attachment.filename).suffix
            new_name = f"{prefix_name}_{i}{ext}"
            save_path = os.path.join(DOWNLOAD_FOLDER, new_name)

            async with session.get(attachment.url) as resp:
                if resp.status != 200:
                    await ctx.send(f"❌ Failed to download `{attachment.filename}`. Skipping.")
                    continue
                data = await resp.read()

            async with aiofiles.open(save_path, "wb") as f:
                await f.write(data)

            renamed_files.append(save_path)

    if not renamed_files:
        await ctx.send("❌ No files were renamed successfully.")
        return

    # Send all renamed files back
    discord_files = [
        discord.File(p, filename=os.path.basename(p)) for p in renamed_files
    ]
    names_list = "\n".join(f"• `{os.path.basename(p)}`" for p in renamed_files)
    await ctx.send(
        f"✅ Renamed **{len(renamed_files)}** file(s):\n{names_list}",
        files=discord_files,
    )


@bot.command(name="listfiles")
async def list_files(ctx):
    """List all files saved in the download folder."""
    files = os.listdir(DOWNLOAD_FOLDER)
    if not files:
        await ctx.send(f"📂 The `{DOWNLOAD_FOLDER}/` folder is empty.")
        return

    file_list = "\n".join(f"• `{f}`" for f in sorted(files))
    await ctx.send(f"📂 **Saved files ({len(files)}):**\n{file_list}")


@bot.command(name="help_bot", aliases=["commands"])
async def help_bot(ctx):
    """Show all available commands."""
    embed = discord.Embed(
        title="📁 File Renamer Bot — Commands",
        color=discord.Color.blue()
    )
    embed.add_field(
        name=f"`{PREFIX}rename <new_name>`",
        value="Attach **1 file** → renames it and sends it back.\n"
              f"Example: `{PREFIX}rename report` (attach file)",
        inline=False,
    )
    embed.add_field(
        name=f"`{PREFIX}renameall <base_name>`",
        value="Attach **multiple files** → renames them `base_1`, `base_2` …\n"
              f"Example: `{PREFIX}renameall photo` (attach files)",
        inline=False,
    )
    embed.add_field(
        name=f"`{PREFIX}listfiles`",
        value="Shows all files saved on the bot's server.",
        inline=False,
    )
    embed.set_footer(text="Files are saved in the 'downloads/' folder on the bot's server.")
    await ctx.send(embed=embed)


# ── Run ─────────────────────────────────────────────────────────
bot.run("TOKEN_HERE")