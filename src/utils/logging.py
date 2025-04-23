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
        "https://311f74ccaf5b994e142af119f09b6267@o4508725934948352.ingest.us.sentry.io/4508725939273728",
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
    logging.getLogger("prisma").setLevel(logging.INFO)


def logger(name):
    return logging.getLogger(name)
