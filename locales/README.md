## Locales

By default, the bot will use the English locale, and have the portuguese locale available as an alternative.

If you want to use a different locale, you can create a new file in the `locales` folder with the name of the locale you want to use, and then set the `BOT_LOCALE` environment variable to the name of the locale you want to use.

The locale file must be a JSON file with the following structure as an example:

```json
{
  "user_joined_call": "{member} joined the call! @everyone",
  "user_in_channel": "{member} joined {channel}",
  "user_left_channel": "{member} left {channel}",
  "user_moved_to_channel": "{member} left {old_channel} and went to {new_channel}",
  "leaderboard_title": "Entry Leaderboard:",
  "leaderboard_entry": "{position}. {name}: {count} times",
  "toggle_enabled": "Functionality to send a message when someone enters a call is now enabled.",
  "toggle_disabled": "Functionality to send a message when someone enters a call is now disabled.",
  "help_title": "Hello, {author}! Here's the list of available commands:",
  "help_leaders": "/leaders - Shows how many times each user entered calls.",
  "help_toggle": "/toggle - Turns on/off the functionality of sending a message when someone enters a call.",
  "help_help": "/help - Get a list of commands."
}

```

[NOTE] Keep an eye on the `en_US.json` file, as it could be updated in the future and you might need to update your locale file.