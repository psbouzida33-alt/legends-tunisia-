# Legends Tunisia Bot — Résumé complet

**Préfixe :** `?`  
**Fichier principal :** `bot.py`  
**Build :** `2026-07-08-rate-limit-safe`  
**Deploy :** Render (`legends-tunisisa.onrender.com`) ou `python bot.py` en local

---

## Commandes — tout le monde

| Commande | Aliases | Description |
|----------|---------|-------------|
| `?ping` | — | Vérifie si le bot est en ligne + latence + build. |
| `?level` | `?lvl`, `?niveau` | Affiche level vocal + temps passé (`?level @user`). |

---

## Rooms vocales (Join-to-Create)

| Commande | Aliases | Qui | Description |
|----------|---------|-----|-------------|
| `?panel` | `?controlpanel`, `?roompanel` | Owner de la room | Reposte le panneau de contrôle dans le chat vocal de ta room. |
| `?clear` | `?clearchat`, `?purgechat`, `?purge` | Owner **ou** Manage Messages | Supprime les messages du chat vocal. Après → `?panel` pour remettre les boutons. |

### Boutons du panneau vocal (owner seulement)

| Bouton | Action |
|--------|--------|
| **Lock** 🔒 | Verrouille : @everyone + Boy/Girl ne peuvent plus rejoindre. Staff + owner OK. |
| **Unlock** 🔓 | Déverrouille la room. |
| **Rename** 📝 | Change le nom (modal, max 30 car.). |
| **Kick** 👞 | Déconnecte un membre du vocal. |
| **Transfer** 👑 | Transfère la propriété à un autre membre. |
| **Check Level** 📊 | Rappel : levels = bot séparé (`?level` si installé). |
| **18+** 🔞 | Ajoute / retire le préfixe `🔞` sur le nom du channel. |

### Hubs Join-to-Create

| Hub | Nom de la room | Accès |
|-----|----------------|-------|
| **Create Lounge** | `🎙️\|{username} ✓` | Boy + Girl + owner |
| **Support** | `Support \| {username}` | Staff + owner |
| **Verification 1 / 2** | `Verify \| {username}` | Staff + owner |

- Room **supprimée** quand tout le monde quitte.
- Owner part + autres restent → **60 s** puis transfer aléatoire (lounge).
- Diagnostic admin : `?checkjoincreate`

---

## Admin — Manage Server

| Commande | Aliases | Description |
|----------|---------|-------------|
| `?checkjoincreate` | — | Vérifie hubs, permissions bot, catégories join-to-create. |
| `?checkticketcategory` | — | Vérifie la catégorie tickets. |
| `?setnotifications` | `?mentionsonly`, `?notifmentions` | Notifications serveur → @mentions only. |
| `/postroles` | — | Poste le menu sélection rôles jeux. (slash uniquement) |
| `?syncroles` | `?syncjoinroles` | Donne les 5 rôles join aux membres (`?syncroles` ou `?syncroles @user`). |
| `/ticketpanel` | — | Poste le panneau tickets (Support / Report / Bugs). (slash uniquement) |
| `/punishmentpanel` | — | Poste le panel punishment (Ban/Timeout/Mute/Warn/...). (slash uniquement) |
| `/adminpanel` | — | Poste l'admin panel (diagnostics/syncroles/giveaway/testwelcome/testpunishment en boutons). (slash uniquement) |

---

## Messages — Manage Messages

| Commande | Aliases | Description |
|----------|---------|-------------|
| `?post` | `?say`, `?echo` | Le bot reposte ton message (supprime ta commande). Fichiers attachés OK. |

---

## Tickets

| Action | Description |
|--------|-------------|
| Boutons **Support / Report / Bugs** | Crée un channel ticket privé. |
| `?closeticket` | `?cv` — Ferme le ticket (owner ou staff). |

---

## Giveaway — rôle Giveaway Admin

| Commande | Aliases | Description |
|----------|---------|-------------|
| `?giveaway` | — | Lance un giveaway via **DM** (prix, durée, gagnants, `random` ou ID). |
| `?stop` | — | Arrête le giveaway en cours (host). |
| `?kickuser` | — | Retire / bloque un membre du giveaway actif. |

Boutons giveaway : **Join Giveaway**, **Chkoun Charek**.

---

## Modération / Punishment

**Staff** = rôle Staff **ou** Manage Server / Moderate Members / Ban Members

Panel-only — pas de commande `?ban`/`?timeout`/etc. Tout passe par le [punishment panel](#) (`/punishmentpanel`, slash) : un bouton par action, modal pour l'ID/mention + raison.

| Bouton | Action |
|--------|--------|
| 🔨 **Ban** | Ban + carte punishment. |
| ⏱️ **Timeout** | Timeout Discord (max 28j). |
| 🔇 **Chat Mute** | Chat mute (rôle + timeout + suppression auto messages). |
| 🔈 **Voice Mute** | Voice mute (rôle + server mute en vocal). |
| ⚠️ **Warn** | Avertissement + rôles auto. |
| 📋 **Warnings** | Compteur warnings. |
| 🧹 **Clear Warn** | Efface warnings (`all` ou un nombre) + sync rôles/mutes. |
| 🔓 **Untimeout** | Retire chat mute. |
| 🔊 **Unmute** | Retire voice mute. |

### Système warn (3 warns)

| Warn | Action |
|------|--------|
| **1** | Rôle Warn 1 + carte WARN |
| **2** | + Rôle Warn 2 |
| **3** | Retire Warn 1+2, chat mute 1j + voice mute, compteur → 0 |
| **4e warn** | Recommence à 1 |

### Clear Warn — sync rôles

| Après clear | Rôles retirés |
|-------------|---------------|
| **0/3** | Warn 1 + Warn 2 + chat mute + voice mute |
| **1/3** | Warn 2 seulement |
| **2/3** | Aucun rôle en plus |

---

## Admin Panel (`/adminpanel`)

**Manage Server** requis pour poster le panel et pour la plupart des boutons (Giveaway = rôle Giveaway Admin, Test Punishment = Staff punishment). Chaque bouton appelle exactement la même commande que sa version `?` — même comportement, juste un member picker/modal au lieu de taper la commande.

| Bouton | Équivaut à |
|--------|-----------|
| 🔍 **Check Join/Create** | `?checkjoincreate` |
| 🎫 **Check Ticket Category** | `?checkticketcategory` |
| 🔔 **Set Notifications** | `?setnotifications` |
| 🔄 **Sync Roles** | `?syncroles` (modal : membre optionnel) |
| 👋 **Test Welcome** | `?testwelcome` (modal : membre optionnel) |
| 🎁 **Start Giveaway** | `?giveaway` (lance le même flow par DM) |
| 🛑 **Stop Giveaway** | `?stop` |
| 🚫 **Kick (Giveaway)** | `?kickuser` (modal : membre) |
| 🧪 **Test Punishment** | `?testpunishment` (modal : type/membre/raison) |

Pas dans le panel : `?ping`/`?level` (public, tout le monde), `?panel`/`?clear` (room vocale — self-service owner, déjà son propre panel), `?post` (attachments — un modal Discord ne peut pas recevoir de fichier), `?closeticket` (déjà un bouton Close dédié dans chaque ticket).

---

## Test / Debug

| Commande | Aliases | Description |
|----------|---------|-------------|
| `?testwelcome` | — | Carte bienvenue test (`?testwelcome @user`). |
| `?testpunishment` | `?testpunish` | Preview carte punishment (`?testpunishment ban @user`). |

Types punishment : `ban`, `timeout`, `chatmute`, `voicemute`, `warn`

---

## Menu rôles jeux (après `/postroles`)

Jeux configurés : Free Fire, Rust, COD, GTA V, Brawlhalla, CS GO, Fortnite, Valorant, LoL, Minecraft.

| Action | Description |
|--------|-------------|
| Sélection multiple | Menu déroulant — plusieurs jeux. |
| Mise à jour auto | Retire anciens rôles jeux, ajoute les nouveaux. |
| Désélection totale | Retire tous les rôles jeux. |

---

## Fonctionnalités automatiques (sans commande)

### Bienvenue
- Rôles : **Not Verified** + **5 rôles join**
- Carte image welcome dans le channel welcome

### Mutes actifs
- **Chat mute** → suppression auto des messages
- **Voice mute** → server mute auto en vocal

### Alertes staff
- **Not Verified** dans Verification 1/2 → DM staff
- Membre normal dans **Support** → notification staff

### Bot statique
- Connecté muet/sourd dans son channel vocal fixe
- Status : **Do Not Disturb**
- Message maintenu dans **Bot-Chat**

### Au démarrage
- Charge warnings, nettoie temp rooms vides, ré-enregistre panneaux/tickets
- Health check HTTP sur `PORT` (Render)

---

## Bot séparé — Level Scanner (`level_scanner_bot.py`)

Optionnel — admin scan/export JSON. Le bot principal gère déjà `?level`.

| Commande | Description |
|----------|-------------|
| `?scanlevels` | Scanne tous les membres → JSON levels |
| `?scanlevels @user` | Stats d'un membre |
| `?scanlevels save` | Scan + save `data/members_scan_latest.json` |

---

## Version téléphone — `bot_all_in_one.py`

Version réduite (Pydroid) : join-to-create lounge + `!level` simplifié. Pas de modération complète.

---

## Permissions bot requises

- Manage Channels, Move Members, Manage Messages, **Mute Members**
- Manage Roles, Manage Server, Moderate Members, Ban Members
- **Rôle bot au-dessus** des rôles qu'il assigne

---

## Variables d'environnement (`.env` / Render)

| Variable | Rôle |
|----------|------|
| `DISCORD_TOKEN` | Token bot (**obligatoire**) |
| `DISCORD_LOGIN_MAX_ATTEMPTS` | Retries login si 429 (défaut: 6) |
| `DISCORD_LOGIN_DELAY_SECONDS` | Délai avant login (défaut: 0) |
| `CREATE_CHANNEL_ID` | Hub lounge join-to-create |
| `SUPPORT_CHANNEL_ID` | Hub support |
| `VERIFICATION_1_ID` / `VERIFICATION_2_ID` | Hubs vérification |
| `BOT_CHAT_CHANNEL_ID` | Channel bot-chat |
| `BOT_CHAT_MESSAGE` | Texte bot-chat |
| `TICKET_CATEGORY_ID` | Catégorie tickets |
| `SET_DEFAULT_NOTIFICATIONS_ONLY_MENTIONS` | Auto @mentions au démarrage |
| `BOT_CHAT_KEEPALIVE_MINUTES` | Refresh bot-chat (défaut: 30) |
| `EMPTY_ROOM_CLEANUP_MINUTES` | Cleanup rooms vides (défaut: 10) |
| `PUNISHMENT_POST_CAP` | Max cartes punishment/min |
| `WELCOME_POST_CAP` | Max welcome cards/min |
| `SYNCROLES_MEMBER_DELAY` | Délai entre membres syncroles |
| `GUILD_INIT_STEP_DELAY` | Délai init au démarrage |

---

## Liste rapide — toutes les commandes `?`

```
?ping
?level | ?lvl | ?niveau
?panel | ?controlpanel | ?roompanel
?clear | ?clearchat | ?purgechat | ?purge
?checkjoincreate
?checkticketcategory
?testwelcome
?setnotifications | ?mentionsonly | ?notifmentions
?syncroles | ?syncjoinroles
?closeticket | ?cv
?post | ?say | ?echo
?giveaway
?stop
?kickuser
?testpunishment | ?testpunish
```

Slash uniquement (pas de version `?`):
- `/postroles`, `/ticketpanel`, `/punishmentpanel` — postent chacun leur panel.
- `/adminpanel` — panel admin (checkjoincreate/checkticketcategory/setnotifications/syncroles/testwelcome/giveaway/stop/kickuser/testpunishment en boutons).

Punishment (ban/timeout/mute/warn/...) : boutons du `/punishmentpanel` uniquement, pas de commande texte.

---

## Preview punishment (local)

```powershell
python preview_punishment_card.py ban
```

Génère `preview_output/ban.png` sans lancer le bot.
