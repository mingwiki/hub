import logging.config
import os
import sys

env = os.getenv("ENV", "dev").lower()

# Set up basic logging configuration
logging.basicConfig(
    level=logging.INFO if env == "prod" else logging.DEBUG,
    format="[%(asctime)s]-%(levelname)s-%(name)s-%(funcName)s()-L%(lineno)d ==> %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Add Sentry logging handler if in production
if env == "prod":
    import sentry_sdk
    from sentry_sdk.integrations.logging import EventHandler

    sentry_sdk.init(
        "https://736ba83d3a1a4e34add814ce3ed29300@bug.zed.ink/1",
        send_default_pii=True,
        max_request_body_size="always",
        traces_sample_rate=0,
    )
    sentry_handler = EventHandler(level=logging.WARNING)
    logging.getLogger().addHandler(sentry_handler)


def logger(name):
    return logging.getLogger(name)
