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
import re
import thiscovery_lib.eb_utilities as eb
import thiscovery_lib.utilities as utils

from http import HTTPStatus


RAW_ACUITY_EVENT_DETAIL_TYPE = "raw_acuity_event"


class AcuityEvent:
    def __init__(self, acuity_event, logger=None, correlation_id=None):
        self.logger = logger
        if logger is None:
            self.logger = utils.get_logger()
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

    @classmethod
    def from_eb_event(cls, event):
        detail_type = event["detail-type"]
        assert (
            detail_type == RAW_ACUITY_EVENT_DETAIL_TYPE
        ), f"Unexpected detail-type: {detail_type}"
        task_response = super().from_eb_event(event=event)
        try:
            interview_task_id = task_response._detail.pop("interview_task_id")
        except KeyError:
            raise utils.DetailedValueError(
                "Mandatory interview_task_id data not found in user_interview_task event",
                details={
                    "event": event,
                },
            )
        return cls(
            response_id=task_response._response_id,
            event_time=task_response._event_time,
            anon_project_specific_user_id=task_response.anon_project_specific_user_id,
            anon_user_task_id=task_response.anon_user_task_id,
            detail_type=detail_type,
            detail=task_response._detail,
            correlation_id=task_response._correlation_id,
            interview_task_id=interview_task_id,
        )

    def process(self):
        """
        Converts incoming Acuity event to an EventBridge event and
        puts it in the local thiscovery-event-bus
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
def process_appointment_event(event, context):
    pass


@utils.lambda_wrapper
@utils.api_error_handler
def appointment_event_api(event, context):
    """
    Listens to events posted by Acuity via webhooks.
    Converts incoming events to EventBridge events and
    puts them in local thiscovery-event-bus
    """
    acuity_event = event["body"]
    thiscovery_event = eb.ThiscoveryEvent(
        {
            "detail-type": RAW_ACUITY_EVENT_DETAIL_TYPE,
            "detail": acuity_event,
            "event_source": "acuity",
        }
    )
    thiscovery_event.put_event()
    return {"statusCode": HTTPStatus.OK, "body": ""}
