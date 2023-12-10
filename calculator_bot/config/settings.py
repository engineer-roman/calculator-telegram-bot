from dataclasses import dataclass

from calculator_bot.config.env_loader import load_setting


@dataclass
class ApplicationSettings:
    app_type: str
    parentheses_limit: int
    release_stage: str
    version: str


@dataclass
class LogStdSettings:
    log_format: str
    log_level: str
    rich_exceptions: bool


@dataclass
class TelegramSettings:
    bot_api_token: str


@dataclass
class SentrySettings:
    dsn: str
    sample_rate: float


def init_application_settings() -> ApplicationSettings:
    return ApplicationSettings(
        app_type=load_setting("APP_TYPE", str, "main"),
        parentheses_limit=load_setting("PARENTHESES_LIMIT", int, 100),
        release_stage=load_setting("DOPPLER_CONFIG", str, "local"),
        version="2.0.0",
    )


def init_telegram_settings() -> TelegramSettings:
    return TelegramSettings(
        bot_api_token=load_setting("TG_BOT_API_TOKEN"),
    )


def init_sentry_settings() -> SentrySettings:
    return SentrySettings(
        dsn=load_setting("SENTRY_DSN", str, ""),
        sample_rate=load_setting("SENTRY_SAMPLE_RATE", float, 1.0),
    )


def init_logstd_settings() -> LogStdSettings:
    return LogStdSettings(
        log_level=load_setting("LOG_LEVEL", str, "INFO"),
        log_format=load_setting(
            "LOG_FORMAT",
            str,
            "{time:YYYY-mm-dd HH:mm:ss.SSS} | pid:{process} | {level} | {message}"
        ),
        rich_exceptions=load_setting("LOG_RICH_EXCEPTIONS", lambda x: bool(int(x)), 0),
    )


@dataclass
class Settings:
    application: ApplicationSettings
    logstd: LogStdSettings
    telegram: TelegramSettings
    sentry: SentrySettings


def init_settings() -> Settings:
    return Settings(
        application=init_application_settings(),
        logstd=init_logstd_settings(),
        telegram=init_telegram_settings(),
        sentry=init_sentry_settings(),
    )
