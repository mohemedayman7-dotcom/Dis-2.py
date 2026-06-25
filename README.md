# 📁 Discord File Renamer Bot

A Python Discord bot that lets you rename files directly in Discord.

---

## ⚙️ Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Create your Discord Bot
1. Go to https://discord.com/developers/applications
2. Click **New Application** → give it a name
3. Go to **Bot** tab → click **Add Bot**
4. Under **Token** → click **Copy**
5. Paste your token in `bot.py` where it says `YOUR_BOT_TOKEN_HERE`

### 3. Enable Permissions
In the Bot tab, enable:
- ✅ Message Content Intent
- ✅ Send Messages
- ✅ Attach Files
- ✅ Read Message History

### 4. Invite the Bot to your Server
In **OAuth2 → URL Generator**, select:
- Scopes: `bot`
- Permissions: `Send Messages`, `Attach Files`, `Read Message History`

Copy the generated URL and open it in your browser.

### 5. Run the bot
```bash
python bot.py
```

---

## 🤖 Commands

| Command | Description |
|---|---|
| `!rename <new_name>` | Attach 1 file → renames it |
| `!renameall <base_name>` | Attach multiple files → renames them base_1, base_2 … |
| `!listfiles` | Shows all saved files |
| `!help_bot` | Shows all commands |

---

## 📌 Examples

```
!rename my_report         → my_report.pdf  (keeps original extension)
!rename photo.jpg         → photo.jpg      (forces extension)
!renameall vacation       → vacation_1.jpg, vacation_2.png, vacation_3.gif
```
