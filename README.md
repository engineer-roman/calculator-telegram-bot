# calculator-telegram-bot
Project provides simple calculator features wrapped in telegram bot interface.

## Configuration
To configure this application environment variables should be used. Docker-compose expects `.env` file in the root of the project.

### Available settings
|Name|Required|Type|Description|
|---|---|---|---|
|CALC_TG_BOT_AUTH_TOKEN|true|string|Telegram bot authorization token.|
|CALC_TG_BOT_PREFIX|false|string|Customizable prefix for ALL environment variables. **Default:** CALC_TG_BOT.|
