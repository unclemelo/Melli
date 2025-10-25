# Melli

**Melli** is now public! Built with community management in mind, Melli enhances moderation, automation, and engagement in your Discord server. This README will guide you through setting up and running the bot locally.

---

## 🚀 Features & Commands

### 🔨 Moderation Tools
- `/mute <user> <duration> [reason]` — Temporarily mute a user.  
- `/unmute <user>` — Remove a timeout from a user.  
- `/clear <amount>` — Bulk delete messages.  
- `/warn <user> <reason>` — Warn a user.  
- `/warnings <user>` — Show a user's warning history.  
- `/delwarn <warning_id>` — Delete a specific warning.  
- `/clearwarns <user>` — Remove all warnings from a user.  
- `/kick <user> [reason]` — Kick a member from the server.  
- `/ban <user> [reason]` — Ban a member from the server.  
- `/unban <user>` — Unban a previously banned user.

### 🔊 Voice Channel Tools
- `/bump <user> <target_vc>` — Move a user to another voice channel.  
- `/vc_mute <user>` — Server mute a user in voice chat.  
- `/vc_unmute <user>` — Unmute a user in voice chat.  
- `/deafen <user>` — Server deafen a user.  
- `/undeafen <user>` — Remove deafening from a user.  
- `/kickvc <user>` — Disconnect a user from a voice channel.

### 🎉 Fun & Extra Commands
- `/knockout <user>` — Timeout a user dramatically.  
- `/revive <user>` — Bring a timed-out user back.  
- `/prank <user>` — Harmlessly prank a user.  
- `/chaos` — Temporarily unleash controlled chaos.

---

## 🧰 Latest Update — **Royal Stats & Prestige System**

The latest update introduces a full **progression system** to reward activity and engagement!

### ⚔️ New Command: `/royalstats`
Check your personalized stats with an elegant embed showing:
- **Kills**, **Deaths**, and **Revives**
- **K/D Ratio** and **XP Progress**
- **Prestige Rank** with star icons

Example:
> 🏆 *Royal Stats — Melo ★★*  
> Kills: 10 Deaths: 3 K/D: 3.33  
> Level: 50 XP: 1425/1525  
> Prestige: ★★

---

### 🌟 Prestige System
Once you hit **Level 50**, a **“Prestige Now ⭐”** button appears automatically.  
Prestiging resets your XP and level while granting a **new star** and marking your ascension!

**Features:**
- Prestige button only appears when eligible.  
- XP, level, and progress saved locally (`data/royal_stats.json`).  
- Dynamic embed updates upon prestige.  
- Fully self-contained — no external database needed.

---

### 🧩 Technical Details
- Data stored in JSON (`data/royal_stats.json`)  
- XP formula: `100 + (level * 25)`  
- Max level: `50`  
- Uses Discord’s **Button View system** for interactive menus  
- Safe checks to prevent other users from using your Prestige button


---

## 🤝 Contributing

Contributions are welcome! If you help improve Melli's codebase, your Discord ID will be added to the bot's badge system as a contributor.

Feel free to open issues, submit pull requests, or suggest new features!

---

*Let us know if you need help setting up or want to expand Melli’s features. We're always happy to collaborate!*