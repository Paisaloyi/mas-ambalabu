# ─────────────────────────────────────────────
#  Mas Ambalabu Jawa™ • bot.py (versi stabil)
# ─────────────────────────────────────────────
import discord
import os
import io
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, timedelta
from keep_alive import keep_alive  # abaikan jika tidak butuh

# ═════════ ENV / TOKEN ══════════════════════
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# ═════════ INTENTS ══════════════════════════
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='.', intents=intents)

# ═════════ KONSTAN ══════════════════════════
HARTING_CHANNEL_ID = 1389229430332719215
TICKET_CHANNEL_ID = 1389161413628661841

# ═════════ ANTI-SPAM ════════════════════════
spam_log, SPAM_LIMIT, SPAM_WIN, TIMEOUT = {}, 3, 5, 60


@bot.event
async def on_message(msg):
    if msg.author.bot:
        return
    uid, now = msg.author.id, datetime.utcnow()
    spam_log.setdefault(uid, []).append(now)
    spam_log[uid] = [
        t for t in spam_log[uid] if (now - t).total_seconds() <= SPAM_WIN
    ]
    if len(spam_log[uid]) >= SPAM_LIMIT:
        try:
            await msg.author.timeout(until=discord.utils.utcnow() +
                                     timedelta(seconds=TIMEOUT),
                                     reason="Auto timeout spam")
            await msg.channel.send(f"{msg.author.mention} jangan spam cok asu")
        except Exception as e:
            print("Timeout error:", e)
        spam_log[uid] = []
    await bot.process_commands(msg)


# ═════════ EVENT READY ══════════════════════
@bot.event
async def on_ready():
    print(f"[✅] {bot.user} siap tempur!")


# ═════════ WELCOMER ═════════════════════════
@bot.event
async def on_member_join(member):
    ch = discord.utils.get(member.guild.text_channels, name="👋︱welcome")
    if not ch:
        return
    created = member.created_at.replace(tzinfo=None)
    age = (datetime.utcnow() - created).days
    em = discord.Embed(description=(
        f"{member.mention} just joined **{member.guild.name}**\n"
        f"There are now **{member.guild.member_count}** members.\n\n"
        f"User created on **{created:%d %b %Y %H:%M}** · **{age} days ago**\n\n🗿"
    ),
                       color=discord.Color.dark_gray())
    em.set_thumbnail(url=member.display_avatar.url)
    em.set_image(url="https://i.imgur.com/oGAHBjQ.gif")
    em.set_footer(text="📬 Disambut hangat oleh Mas Ambalabu™")
    await ch.send(embed=em)


# ═════════ COMMANDS UMUM ════════════════════
@bot.command()
async def about(ctx):
    await ctx.send(embed=discord.Embed(
        title="🧔🏻‍♂️ Mas Ambalabu, Si Bot Jawir",
        description=
        "Aku ciptaan **paisaloyi** paling tampan 😎. Penjaga & penyambut bolo.",
        color=discord.Color.blurple()))


@bot.command()
async def menu(ctx):
    await ctx.send(
        embed=discord.Embed(title="📦 Menu Mas Ambalabu",
                            description=("**.about** – Info bot\n"
                                         "**.qris** – Tampilkan QRIS\n"
                                         "**.payment** – Info transfer + QR\n"
                                         "**.done** – Konfirmasi pembayaran\n"
                                         "**.say <pesan>** – Buat bot bicara\n"
                                         "**.poststock** – Post katalog akun"),
                            color=discord.Color.green()))


@bot.command()
async def say(ctx, *, pesan: str):
    await ctx.message.delete()
    em = discord.Embed(description=pesan, color=discord.Color.blue())
    em.set_footer(text="🗣️ Disuarakan oleh Mas Ambalabu")
    await ctx.send(embed=em)


@bot.command()
async def qris(ctx):
    with open("qris.png", "rb") as f:
        await ctx.send("📸 Scan QRIS:", file=discord.File(f, "qris.png"))


@bot.command()
async def payment(ctx):
    with open("qris.png", "rb") as f:
        em = discord.Embed(
            title="💰 Pembayaran ke Ambalabu",
            description=
            "Transfer / QRIS ➜ `0822-4550-7754` (DANA|GoPay)\nAtas nama **Robby Aji Nugroho**",
            color=discord.Color.orange()).set_image(
                url="attachment://qris.png")
        await ctx.send(embed=em, file=discord.File(f, "qris.png"))


@bot.command()
async def done(ctx):
    await ctx.send(embed=discord.Embed(
        title="✅ Transaksi Diterima",
        description="Dana masuk. Kalau belum, DM Mas Amba.",
        color=discord.Color.gold()))


# ═════════ .poststock FLEX (delete reply) ═════════
@bot.command()
async def poststock(ctx):
    raw = ctx.message.content
    await ctx.message.delete()  # hapus command

    # ⬇️  Ambil attachment dari message ini / reply
    atts = list(ctx.message.attachments)
    replied_msg = None
    if not atts and ctx.message.reference:
        try:
            replied_msg = await ctx.channel.fetch_message(
                ctx.message.reference.message_id)
            atts = replied_msg.attachments
        except Exception as e:
            print("[DBG] fetch reply gagal:", e)

    if not atts:
        return await ctx.send(
            "❌ Upload gambar atau reply gambar saat `.poststock`.")

    # ⬇️  Judul & spek
    lines = [l.strip() for l in raw.split("\n")[1:] if l.strip()]
    if not lines:
        return await ctx.send("❌ Baris pertama = judul, bawahnya spek akun.")
    title = lines[0]
    specs = lines[1:] or ["(tidak ada detail)"]
    desc = "\n".join(f"• {s}" for s in specs)

    # ⬇️  Embed ungu
    embed = discord.Embed(
        title=f"🪴 {title}",
        description=
        f"{desc}\n\n📩 DM **@paisaloyi** atau hartingin di <#{HARTING_CHANNEL_ID}>",
        color=discord.Color.purple())
    embed.set_footer(text="Mas Ambalabu™ Catalog System")

    # ⬇️  Tombol link → open-ticket
    ticket_url = f"https://discord.com/channels/{ctx.guild.id}/{TICKET_CHANNEL_ID}"
    view = discord.ui.View(timeout=None)
    view.add_item(
        discord.ui.Button(label="Buy",
                          emoji="🛒",
                          style=discord.ButtonStyle.link,
                          url=ticket_url))

    await ctx.send(embed=embed, view=view)

    # ⬇️  Kirim gambar terpisah
    files = [
        discord.File(io.BytesIO(await a.read()), filename=a.filename)
        for a in atts if a.content_type and a.content_type.startswith("image")
    ]
    if files:
        await ctx.send(files=files)

    # ⬇️  Hapus pesan gambar yang direply (jika ada)
    if replied_msg and replied_msg.author == ctx.author:
        try:
            await replied_msg.delete()
        except Exception as e:
            print("[DBG] gagal hapus replied msg:", e)


# ═════════ MAIN START ══════════════════════
async def main():
    await bot.start(TOKEN)


if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
