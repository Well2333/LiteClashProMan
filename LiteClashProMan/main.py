from uvicorn import Config, Server

from .api import app
from .config import config
from .log import LOGGING_CONFIG

if config.sentry_dsn:
    import sentry_sdk

    sentry_sdk.init(
        dsn=config.sentry_dsn,
        traces_sample_rate=1.0,
    )


def main():
    Server(
        Config(
            app,
            host=config.host,
            port=config.port,
            log_config=LOGGING_CONFIG,
            reload=True,  # Enable "hot-reloading"
            reload_includes=[config.config_file_path],  # Watch 'config.yaml'
        )
    ).run()
