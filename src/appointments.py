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
import datetime
import json
import re
import thiscovery_lib.utilities as utils

from collections import ChainMap
from dateutil import parser
from http import HTTPStatus
from thiscovery_lib.core_api_utilities import CoreApiClient
from thiscovery_lib.dynamodb_utilities import Dynamodb
from thiscovery_lib.emails_api_utilities import EmailsApiClient

from common.acuity_utilities import AcuityClient

# from common.constants import ACUITY_USER_METADATA_INTAKE_FORM_ID, APPOINTMENTS_TABLE, APPOINTMENT_TYPES_TABLE, DEFAULT_TEMPLATES, STACK_NAME


class AcuityEvent:
    def __init__(self, acuity_event, logger=None, correlation_id=None):
        self.logger = logger
        if logger is None:
            self.logger = utils.get_logger()
        self.core_api_client = CoreApiClient(correlation_id=correlation_id)
        self.correlation_id = correlation_id

        event_pattern = re.compile(
            r"action=appointment\.(?P<action>scheduled|rescheduled|canceled|changed)"
            r"&id=(?P<appointment_id>\d+)"
            r"&calendarID=(?P<calendar_id>\d+)"
            r"&appointmentTypeID=(?P<type_id>\d+)"
        )
        m = event_pattern.match(acuity_event)
        try:
            self.event_type = m.group("action")
            appointment_id = m.group("appointment_id")
            type_id = m.group("type_id")
        except AttributeError as err:
            self.logger.error(
                "event_pattern does not match acuity_event",
                extra={"acuity_event": acuity_event},
            )
            raise
        self.appointment = AcuityAppointment(
            appointment_id=appointment_id,
            logger=self.logger,
            correlation_id=self.correlation_id,
        )
        self.appointment.appointment_type.type_id = type_id
        try:
            self.appointment.appointment_type.ddb_load()
        except utils.ObjectDoesNotExistError:
            self.logger.error(
                "Failed to process Acuity event (Appointment type not found in Dynamodb)",
                extra={"event": acuity_event, "correlation_id": self.correlation_id},
            )
            raise

    def __repr__(self):
        return str(self.__dict__)

    def process(self):
        """
        Returns: Tuple containing:
            storing_result,
            thiscovery_team_notification_result,
            participant_and_researchers_notification_results
        """
        pass
        # if self.event_type == 'scheduled':
        #     return self._process_booking()
        # elif self.event_type == 'canceled':
        #     return self._process_cancellation()
        # elif self.event_type == 'rescheduled':
        #     return self._process_rescheduling()
        # else:
        #     raise NotImplementedError(f'Processing of a {self.event_type} appointment has not been implemented')


@utils.lambda_wrapper
@utils.api_error_handler
def acuity_appointment_api(event, context):
    """
    Listens to events posted by Acuity via webhooks
    """
    logger = event["logger"]
    correlation_id = event["correlation_id"]
    acuity_event = event["body"]
    appointment_event = AcuityEvent(acuity_event, logger, correlation_id=correlation_id)
    result = appointment_event.process()
    return {"statusCode": HTTPStatus.OK, "body": json.dumps(result)}
