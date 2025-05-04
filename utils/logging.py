import logging
import os
import sys

env = os.getenv("ENV", "dev").lower()

logging.basicConfig(
    level=logging.INFO if env == "prod" else logging.DEBUG,
    format="[%(asctime)s]-%(levelname)s-%(name)s-%(funcName)s()-L%(lineno)d ==> %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


if env == "prod":
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_sdk.init(
        os.getenv("SENTRY_DSN"),
        send_default_pii=True,
        max_request_body_size="always",
        traces_sample_rate=0,
        integrations=[
            LoggingIntegration(
                level=logging.WARNING,
                event_level=logging.WARNING,
            ),
        ],
    )
    logging.getLogger("httpcore").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.INFO)


def logger(name):
    return logging.getLogger(name)
