# calculator-telegram-bot
Project provides simple calculator features wrapped in telegram bot, written in
Python 3 via asynchronous code.

## Configuration
To configure this application environment variables should be used. For
Docker container please use file ``./.venv``.

### Available settings
|Name|Required|Type|Description|
|---|---|---|---|
|CALC_TG_BOT_AUTH_TOKEN|true|string|Telegram bot authorization token.|
|CALC_TG_BOT_PREFIX|false|string|Customizable prefix for ALL environment variables. **Default:** CALC_TG_BOT.|
