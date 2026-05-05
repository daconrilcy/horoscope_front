"""Bot Discord permettant de relayer des demandes vers Codex depuis un salon."""

import os
import subprocess

import discord

TOKEN = os.getenv("DISCORD_BOT_TOKEN", "").strip()
CODEX_PATH = r"C:\Users\cyril\AppData\Roaming\npm\codex.cmd"

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


def split_discord_message(text: str, limit: int = 1900) -> list[str]:
    """Découpe une réponse Codex en messages compatibles avec les limites Discord."""

    chunks = []
    current = ""

    for paragraph in text.split("\n\n"):
        if len(current) + len(paragraph) + 2 <= limit:
            current += paragraph + "\n\n"
        else:
            if current.strip():
                chunks.append(current.strip())
            current = paragraph + "\n\n"

    if current.strip():
        chunks.append(current.strip())

    return chunks


@client.event
async def on_ready():
    """Confirme la connexion du bot dans la console locale."""

    print(f"Bot connecte en tant que {client.user}")


@client.event
async def on_message(message):
    """Traite les commandes Discord qui demandent une execution Codex."""

    if message.author == client.user:
        return

    if not message.content.startswith("!codex"):
        return

    prompt = message.content.replace("!codex", "", 1).strip()

    if not prompt:
        await message.channel.send("⚠️ Ajoute une demande après `!codex`.")
        return

    await message.channel.send("⏳ Codex travaille...")

    try:
        result = subprocess.run(
            [
                CODEX_PATH,
                "--ask-for-approval",
                "never",
                "--sandbox",
                "workspace-write",
                "exec",
                "--skip-git-repo-check",
                prompt,
            ],
            capture_output=True,
            text=True,
            timeout=180,
            encoding="utf-8",
            errors="replace",
        )

        output = result.stdout.strip()
        error = result.stderr.strip()

        if result.returncode != 0:
            await message.channel.send(
                f"❌ Codex a retourné une erreur :\n```{error[:1800]}```"
            )
            return

        if not output:
            output = "⚠️ Codex n'a rien retourné."

        for chunk in split_discord_message(output):
            await message.channel.send(chunk)

    except subprocess.TimeoutExpired:
        await message.channel.send("⏱️ Codex a dépassé le temps limite.")
    except Exception as e:
        await message.channel.send(f"❌ Erreur Python : `{e}`")


if not TOKEN:
    raise RuntimeError("La variable d'environnement DISCORD_BOT_TOKEN est requise.")

client.run(TOKEN)
