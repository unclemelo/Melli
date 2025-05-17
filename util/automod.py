import json
import hashlib
import discord

def hash_preset(preset_data):
    return hashlib.sha256(json.dumps(preset_data, sort_keys=True).encode()).hexdigest()

def get_temp_data(bot, user_id):
    if not hasattr(bot, "temp_data"):
        bot.temp_data = {}
    return bot.temp_data.setdefault(user_id, {})

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

async def apply_automod_rule(guild, log_channel, rule_data, exempt_roles, exempt_channels, reason="AutoMod update"):
    rule_name = rule_data.get("rule_name", "AutoMod Rule")
    keyword_filter = rule_data.get("keyword_filter", [])
    regex_patterns = rule_data.get("regex_patterns", [])
    allow_list = rule_data.get("allowed_keywords", [])

    existing_rules = await guild.fetch_automod_rules()
    existing = discord.utils.get(existing_rules, name=rule_name)

    actions = [
        discord.AutoModRuleAction(type=discord.AutoModRuleActionType.send_alert_message, channel_id=log_channel.id),
        discord.AutoModRuleAction(type=discord.AutoModRuleActionType.block_message)
    ]

    trigger = discord.AutoModTrigger(
        type=discord.AutoModRuleTriggerType.keyword,
        keyword_filter=keyword_filter,
        allow_list=allow_list,
        regex_patterns=regex_patterns,
    )

    if existing:
        await existing.edit(trigger=trigger, actions=actions, enabled=True, exempt_roles=exempt_roles, exempt_channels=exempt_channels, reason=reason)
    else:
        await guild.create_automod_rule(
            name=rule_name,
            event_type=discord.AutoModRuleEventType.message_send,
            trigger=trigger,
            actions=actions,
            enabled=True,
            exempt_roles=exempt_roles,
            exempt_channels=exempt_channels,
            reason=reason
        )
