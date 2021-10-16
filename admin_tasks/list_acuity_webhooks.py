import local.dev_config  # sets env variables
import local.secrets  # sets env variables
from src.common.acuity_utilities import AcuityClient


def main():
    ac = AcuityClient()
    webhooks = ac.get_webhooks()
    return webhooks


if __name__ == "__main__":
    from pprint import pprint

    pprint(main())
