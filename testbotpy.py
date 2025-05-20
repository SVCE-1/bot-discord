import discord
from discord.ext import commands
import random  # Bien placé ici
import threading
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Alfred est prêt, connecté en tant que {bot.user}")

@bot.command()
async def salut(ctx):
    await ctx.send("Salut à toi ! 👋")


@bot.event
async def on_message(message):
    # Ignore les messages du bot lui-même
    if message.author == bot.user:
        return

    # Vérifie que le message est bien dans le bon salon
    if message.channel.name == "『🍿』soigné-ou-lache-ça":
        if message.attachments:
            for attachment in message.attachments:
                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                    # Ajoute les réactions
                    await message.add_reaction("✅")
                    await message.add_reaction("❌")

                    # Crée le fil de discussion
                    thread = await message.create_thread(
                        name=f"Jugement de {message.author.display_name}",
                        auto_archive_duration=60,  # 1h d’inactivité
                        reason="Jugement visuel ouvert par Alfred."
                    )

                    # Alfred lance la discussion dans le fil
                    await thread.send(
                        f"Messieurs, à vos votes.\n"
                        f"Que le jugement commence pour {message.author.mention}... 🎩"
                    )
                    break

    # Pour que les commandes comme !sop continuent de marcher
    await bot.process_commands(message)


@bot.command()
@commands.has_permissions(mute_members=True)
async def mute(ctx, member: discord.Member, *, reason="Aucune raison spécifiée"):
    if ctx.channel.name != "『🤖』-commandes":
        return
    mute_role = discord.utils.get(ctx.guild.roles, name="Mute")
    if not mute_role:
        mute_role = await ctx.guild.create_role(name="Mute")
        for channel in ctx.guild.channels:
            await channel.set_permissions(mute_role, send_messages=False, speak=False)

    await member.add_roles(mute_role)
    await ctx.send(f"🔇 {member.mention} a été réduit au silence. Raison : {reason}")
    await ctx.send(f"ℹ️ Le rôle 'Mute' a été attribué à {member.display_name}.")


@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Aucune raison spécifiée"):
    if ctx.channel.name != "『🤖』-commandes":
        return
    await member.kick(reason=reason)
    await ctx.send(f"🥾 {member.mention} a été éjecté. Raison : {reason}")
    await ctx.send(f"ℹ️ L'utilisateur {member.display_name} a été expulsé du serveur.")


@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Aucune raison spécifiée"):
    if ctx.channel.name != "『🤖』-commandes":
        return
    await member.ban(reason=reason)
    await ctx.send(f"⛔ {member.mention} a été banni. Raison : {reason}")
    await ctx.send(f"ℹ️ L'utilisateur {member.display_name} a été banni du serveur.")


@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason="Aucune raison spécifiée"):
    if ctx.channel.name != "『🤖』-commandes":
        return
    await ctx.send(f"⚠️ {member.mention}, ceci est un avertissement : {reason}")
    await ctx.send(f"ℹ️ Un avertissement a été adressé à {member.display_name}.")


@bot.command()
async def prison(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name='prisonnier')
    if role:
        await member.add_roles(role)
        await ctx.send(f"{member.mention} est maintenant en prison ! 🔒")
    else:
        await ctx.send("❌ Rôle 'prisonnier' introuvable.")


@bot.event
async def on_member_join(member):
    guild = member.guild
    role = discord.utils.get(guild.roles, name="🧊Touriste")  # ← Remplace ici par le nom exact de ton rôle

    if role:
        await member.add_roles(role)
        print(f"Rôle '{role.name}' attribué à {member.name}")
    else:
        print(f"Rôle non trouvé pour {member.name}")

    # Message d'accueil visuel
    channel = discord.utils.get(guild.text_channels, name="『🙏』-bienvenue")
    if channel:
        embed = discord.Embed(
            title=f"Bienvenue à Gotham City, {member.name} 🦇",
            description=(
                f"Bonsoir {member.mention},\n"
                f"Je suis **Alfred**, majordome attitré de cette noble demeure.\n"
                f"Un rôle vous a été assigné automatiquement.\n"
                f"Si vous avez besoin d’assistance, invoquez-moi avec `!aide`.\n"
                f"*Veuillez faire comme chez vous, monsieur.* 🕯️"
            ),
            color=0x1f1f1f
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text="Votre fidèle serviteur, Alfred", icon_url=bot.user.avatar.url)

        await channel.send(embed=embed)


@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.text_channels, name="『👋』-au-revoir")  # Tu peux changer de salon si besoin
    if channel:
        embed = discord.Embed(
            title=f"🕯️ Départ de {member.name}",
            description=(
                f"Un résident nous quitte...\n"
                f"**{member.name}** a quitté **Gotham City**.\n"
                f"Je veillerai à ce que sa chambre reste impeccablement rangée.\n\n"
                f"*Puissiez-vous trouver ce que vous cherchez, monsieur.*"
            ),
            color=0x5c5c5c
        )

        # Photo de profil du membre
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

        embed.set_footer(
            text="Alfred, toujours au service.",
            icon_url=bot.user.avatar.url
        )

        await channel.send(embed=embed)


@bot.command()
async def sop(ctx):
    # Vérifie que la commande est utilisée dans le bon salon
    if ctx.channel.name != "『🍿』soigné-ou-lache-ça":
        await ctx.send("Monsieur, je ne suis autorisé à juger que dans le salon **#『🍿』soigné-ou-lache-ça**. 🎩")
        return

    choix = random.choice(["Smash", "Pass"])

    commentaires_smash = [
        "Avec tout le respect que je vous dois, monsieur, ce serait un *smash* sans hésitation.",
        "Je ne me permettrais point de juger, mais... smash, évidemment.",
        "Même maître Bruce ne resterait pas de marbre. *Smash*.",
        "Une silhouette exquise, monsieur. Smash, assurément.",
        "Je serais bien malavisé de ne pas dire *smash*, monsieur.",
        "Sans vouloir m’immiscer dans vos affaires… Smash. Indiscutable.",
        "Un tel port de tête ne laisse guère place au doute : *smash*.",
        "Ce choix me semble évident, monsieur : smash, tout simplement."
    ]

    commentaires_pass = [
        "Avec tout le respect, je me dois de dire : *pass*.",
        "Je crains que cela ne corresponde pas aux standards de Wayne Manor. Pass.",
        "Monsieur, même un majordome a ses limites. Pass.",
        "Permettez-moi de décliner poliment. Pass.",
        "Je ne voudrais offenser personne, mais… pass, sans l’ombre d’un doute.",
        "Maître Bruce n’approuverait guère. Pass.",
        "L’élégance a ses exigences, monsieur. Pass.",
        "Je m’abstiendrai avec dignité : *pass*."
    ]

    commentaire = random.choice(commentaires_smash if choix == "Smash" else commentaires_pass)
    await ctx.send(f"**{choix.upper()}** – {commentaire}")

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="『🙏』-bienvenue")
    if channel:
        embed = discord.Embed(
            title=f"Bienvenue à Gotham City, {member.name} 🦇",
            description=(
                f"Bonsoir {member.mention},\n"
                f"Je suis **Alfred**, majordome attitré de cette noble demeure.\n"
                f"Si vous avez besoin d’assistance, invoquez-moi avec `!aide`.\n"
                f"*Veuillez faire comme chez vous, monsieur.* 🕯️"
            ),
            color=0x1f1f1f
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text="Votre fidèle serviteur, Alfred", icon_url=bot.user.avatar.url)
        await channel.send(embed=embed)

# Ne publie pas ton token sur internet
bot.run("MTM3NDE0NjE4NzM3NTkzOTY1NA.GEgJoy.5iFi8CVvtKFNB7gqzDAKmkq9DQea_hQ7Q4ncAg")
