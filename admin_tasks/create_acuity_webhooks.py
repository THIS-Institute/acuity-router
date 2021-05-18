#
#   Thiscovery API - THIS Institute’s citizen science platform
#   Copyright (C) 2019 THIS Institute
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   A copy of the GNU Affero General Public License is available in the
#   docs folder of this project.  It is also available www.gnu.org/licenses/
#
import local.dev_config
import local.secrets
import thiscovery_lib.utilities as utils
from src.common.acuity_utilities import AcuityClient


EVENTS = [
    "appointment.scheduled",
    "appointment.rescheduled",
    "appointment.canceled",
    # 'appointment.changed',
]


def main():
    logger = utils.get_logger()
    ac = AcuityClient()
    for e in EVENTS:
        try:
            response = ac.post_webhooks(
                e, target=f"{local.dev_config.AWS_TEST_API}v1/appointment-event"
            )
            logger.info("Created webhook", extra={"response": response})
        except utils.DetailedValueError:
            pass


if __name__ == "__main__":
    main()
