"""Bot Discord permettant de relayer des demandes vers Codex depuis un salon."""

import asyncio
import os
import subprocess
import time
from pathlib import Path

import discord

ENV_PATH = Path(__file__).with_name(".env")
REPO_ROOT = Path(__file__).resolve().parent.parent
CODEX_PATH = r"C:\Users\cyril\AppData\Roaming\npm\codex.cmd"
CODEX_TIMEOUT_SECONDS = 3600
CODEX_SANDBOX_MODE = "danger-full-access"
CONDAMAD_COMMAND = "!condamad"
CODEX_COMMAND = "!codex"
CONDAMAD_SKILLS = {
    "story": {
        "skill": "$condamad-story-writer",
        "label": "Créer une story",
        "usage": "!condamad story <brief|audit|finding>",
        "description": "Compile une demande en story CONDAMAD prête à implémenter.",
    },
    "dev": {
        "skill": "$condamad-dev-story",
        "label": "Implémenter une story",
        "usage": "!condamad dev <story.md|capsule>",
        "description": "Implémente exactement une story avec preuves, tests et garde-fous.",
    },
    "review": {
        "skill": "$condamad-code-review",
        "label": "Revue adversariale",
        "usage": "!condamad review <story|diff|scope>",
        "description": "Passe une story ou un diff en revue sans modifier le code.",
    },
    "fix": {
        "skill": "$condamad-review-fix-story",
        "label": "Revue puis correction",
        "usage": "!condamad fix <story.md|capsule>",
        "description": "Boucle review, correction et validation jusqu'à clôture.",
    },
    "full": {
        "skill": "$condamad-dev-review-fix-story",
        "label": "Dev complet",
        "usage": "!condamad full <story.md|capsule>",
        "description": "Orchestre implémentation, revue, corrections et clôture.",
    },
    "audit": {
        "skill": "$condamad-domain-auditor",
        "label": "Audit domaine",
        "usage": "!condamad audit <domaine ou dossier>",
        "description": "Produit un audit read-only avec constats et candidates stories.",
    },
    "front": {
        "skill": "$condamad-frontend-dev",
        "label": "Développement frontend",
        "usage": "!condamad front <demande React>",
        "description": "Traite les changements React, UI, hooks, styles et tests frontend.",
    },
    "ux": {
        "skill": "$condamad-ux-ui-lead",
        "label": "Audit ou plan UX/UI",
        "usage": "!condamad ux <page ou objectif>",
        "description": "Produit une analyse ou un plan UX/UI React sans modifier par défaut.",
    },
    "refactor": {
        "skill": "$condamad-refactor-surgeon",
        "label": "Refactor chirurgical",
        "usage": "!condamad refactor <scope + type + invariant>",
        "description": "Refactor borné, mono-domaine, sans changement de comportement.",
    },
    "guards": {
        "skill": "$condamad-regression-guardrails",
        "label": "Garde-fous",
        "usage": "!condamad guards <demande>",
        "description": "Gère le registre CONDAMAD des invariants anti-régression.",
    },
}

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
running_codex_tasks: set[asyncio.Task[None]] = set()


def get_env_value(key: str, env_path: Path) -> str:
    """Lit une clef depuis l'environnement courant puis depuis le fichier .env local."""

    value = os.getenv(key, "").strip()
    if value or not env_path.exists():
        return value

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith("#"):
            continue

        candidate_key, separator, candidate_value = stripped_line.partition("=")
        if separator and candidate_key.strip() == key:
            return candidate_value.strip().strip('"').strip("'")

    return ""


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


def build_condamad_help_embed(alias: str | None = None) -> discord.Embed:
    """Construit l'aide Discord sous forme d'embed lisible."""

    if alias:
        skill = CONDAMAD_SKILLS.get(alias)
        if not skill:
            available_aliases = ", ".join(sorted(CONDAMAD_SKILLS))
            embed = discord.Embed(
                title="Raccourci CONDAMAD inconnu",
                description=f"`{alias}` n'existe pas.",
                color=discord.Color.red(),
            )
            embed.add_field(
                name="Raccourcis disponibles",
                value=available_aliases,
                inline=False,
            )
            embed.set_footer(
                text="Utilise !condamad help pour afficher la liste complète."
            )
            return embed

        embed = discord.Embed(
            title=f"{alias} - {skill['label']}",
            description=skill["description"],
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Commande", value=f"`{skill['usage']}`", inline=False)
        embed.add_field(name="Skill Codex", value=f"`{skill['skill']}`", inline=False)
        embed.set_footer(
            text="Le bot injecte AGENTS.md et interdit commit/push sauf demande explicite."
        )
        return embed

    embed = discord.Embed(
        title="Raccourcis CONDAMAD",
        description=(
            "Utilise `!condamad <raccourci> <demande>` pour lancer Codex.\n"
            "Utilise `!condamad help <raccourci>` pour le détail."
        ),
        color=discord.Color.green(),
    )
    for shortcut, skill in CONDAMAD_SKILLS.items():
        embed.add_field(
            name=f"{shortcut} - {skill['label']}",
            value=f"`{skill['usage']}`\n{skill['description']}",
            inline=False,
        )

    embed.set_footer(
        text="Exemple: !condamad dev _condamad/stories/<story>/00-story.md"
    )
    return embed


async def send_condamad_help(
    channel: discord.abc.Messageable,
    alias: str | None = None,
) -> None:
    """Envoie l'aide CONDAMAD avec la mise en page native Discord."""

    await channel.send(embed=build_condamad_help_embed(alias))


def build_condamad_prompt(alias: str, request: str) -> str:
    """Transforme un raccourci CONDAMAD en prompt explicite pour Codex."""

    skill = CONDAMAD_SKILLS[alias]
    return (
        f"Utilise le skill {skill['skill']}.\n"
        "Respecte les instructions AGENTS.md du repository.\n"
        "Ne commit pas et ne push pas sauf demande explicite.\n"
        f"Demande utilisateur Discord:\n{request}"
    )


def format_elapsed_time(elapsed_seconds: float) -> str:
    """Formate une durée d'exécution courte pour les notifications Discord."""

    rounded_seconds = max(0, round(elapsed_seconds))
    minutes, seconds = divmod(rounded_seconds, 60)

    if minutes:
        return f"{minutes} min {seconds:02d} s"

    return f"{seconds} s"


def run_codex_process(prompt: str) -> subprocess.CompletedProcess[str]:
    """Lance Codex dans un processus isolé sans dépendre de l'event loop Discord."""

    return subprocess.run(
        [
            CODEX_PATH,
            "--ask-for-approval",
            "never",
            "--sandbox",
            CODEX_SANDBOX_MODE,
            "--cd",
            str(REPO_ROOT),
            "exec",
            "--skip-git-repo-check",
            prompt,
        ],
        capture_output=True,
        text=True,
        timeout=CODEX_TIMEOUT_SECONDS,
        encoding="utf-8",
        errors="replace",
        cwd=REPO_ROOT,
    )


async def notify_codex_job_finished(
    channel: discord.abc.Messageable,
    requester_mention: str,
    status: str,
    elapsed_seconds: float,
) -> None:
    """Signale dans Discord qu'un agent Codex a terminé son travail."""

    elapsed_time = format_elapsed_time(elapsed_seconds)
    await channel.send(
        f"🔔 Agent Codex terminé pour {requester_mention} : {status} en {elapsed_time}.",
        allowed_mentions=discord.AllowedMentions(users=True),
    )


async def run_codex_job(message, prompt: str) -> None:
    """Exécute Codex et publie le résultat dans le salon Discord."""

    await message.channel.send("⏳ Codex travaille...")
    started_at = time.monotonic()
    status = "erreur Python"

    try:
        result = await asyncio.to_thread(run_codex_process, prompt)

        output = result.stdout.strip()
        error = result.stderr.strip()

        if result.returncode != 0:
            status = "échec"
            await message.channel.send(
                f"❌ Codex a retourné une erreur :\n```{error[:1800]}```"
            )
            return

        if not output:
            output = "⚠️ Codex n'a rien retourné."

        status = "succès"
        await notify_codex_job_finished(
            message.channel,
            message.author.mention,
            status,
            time.monotonic() - started_at,
        )

        for chunk in split_discord_message(output):
            await message.channel.send(chunk)

    except subprocess.TimeoutExpired:
        status = "timeout"
        await message.channel.send("⏱️ Codex a dépassé le temps limite.")
    except Exception as e:
        status = "erreur Python"
        await message.channel.send(f"❌ Erreur Python : `{e}`")
    finally:
        if status != "succès":
            await notify_codex_job_finished(
                message.channel,
                message.author.mention,
                status,
                time.monotonic() - started_at,
            )


def schedule_codex_job(message, prompt: str) -> None:
    """Planifie un job Codex sans bloquer les événements Discord."""

    task = asyncio.create_task(run_codex_job(message, prompt))
    running_codex_tasks.add(task)
    task.add_done_callback(running_codex_tasks.discard)


@client.event
async def on_ready():
    """Confirme la connexion du bot dans la console locale."""

    print(f"Bot connecte en tant que {client.user}")


@client.event
async def on_message(message):
    """Traite les commandes Discord qui demandent une execution Codex."""

    if message.author == client.user:
        return

    if message.content.startswith(CONDAMAD_COMMAND):
        command = message.content.replace(CONDAMAD_COMMAND, "", 1).strip()
        command_parts = command.split(maxsplit=1)
        alias = command_parts[0].lower() if command_parts else "help"
        request = command_parts[1].strip() if len(command_parts) > 1 else ""

        if alias in {"help", "list"}:
            help_alias = request.split(maxsplit=1)[0].lower() if request else None
            await send_condamad_help(message.channel, help_alias)
            return

        if alias not in CONDAMAD_SKILLS:
            await send_condamad_help(message.channel, alias)
            return

        if not request:
            await send_condamad_help(message.channel, alias)
            return

        schedule_codex_job(message, build_condamad_prompt(alias, request))
        return

    if not message.content.startswith(CODEX_COMMAND):
        return

    prompt = message.content.replace(CODEX_COMMAND, "", 1).strip()

    if not prompt:
        await message.channel.send(f"⚠️ Ajoute une demande après `{CODEX_COMMAND}`.")
        return

    schedule_codex_job(message, prompt)


token = get_env_value("DISCORD_BOT_TOKEN", ENV_PATH)

if not token:
    raise RuntimeError("La variable d'environnement DISCORD_BOT_TOKEN est requise.")

client.run(token)
