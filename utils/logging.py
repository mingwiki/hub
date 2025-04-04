import logging.config
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
        "https://33e4e07829584c17829c61a4284c67e5@bug.api.zed.ink/1",
        send_default_pii=True,
        max_request_body_size="always",
        traces_sample_rate=0,
        integrations=[
            LoggingIntegration(
                level=logging.WARNING,
                event_level=logging.ERROR,
            ),
        ],
    )


def logger(name):
    return logging.getLogger(name)
