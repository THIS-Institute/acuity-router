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
from thiscovery_lib.dynamodb_utilities import Dynamodb

from common.acuity_utilities import AcuityClient
from common.constants import (
    PROCESSED_ACUITY_EVENT_DETAIL_TYPE,
    RAW_ACUITY_EVENT_DETAIL_TYPE,
    ROUTING_TABLE,
    STACK_NAME,
)


class AcuityEvent:
    def __init__(self, acuity_event, logger=None, correlation_id=None):
        self.acuity_event_body = acuity_event
        self.logger = logger
        if logger is None:
            self.logger = utils.get_logger()
        self.correlation_id = correlation_id
        self.target_env = None

        event_pattern = re.compile(
            r"action=appointment\.(?P<action>scheduled|rescheduled|canceled|changed)"
            r"&id=(?P<appointment_id>\d+)"
            r"&calendarID=(?P<calendar_id>\d+)"
            r"&appointmentTypeID=(?P<type_id>\d+)"
        )

        m = event_pattern.match(acuity_event)
        try:
            self.appointment_type_id = m.group("type_id")
        except AttributeError as err:
            self.logger.error(
                "event_pattern does not match acuity_event",
                extra={"acuity_event": acuity_event},
            )
            raise

        ac = AcuityClient(correlation_id=self.correlation_id)
        app_types_dict = {str(x["id"]): x for x in ac.get_appointment_types()}
        appointment_type = app_types_dict[self.appointment_type_id]
        self.logger.debug(
            f"Appointment type", extra={"appointment_type": appointment_type}
        )
        appointment_type_category = appointment_type["category"]

        env_pattern = re.compile(r"\{\{(?P<env>.+)}}")
        m = env_pattern.search(appointment_type_category)
        try:
            self.target_env = m.group("env")
        except AttributeError as err:
            self.logger.info(
                "Not a thiscovery appointment category. Ignoring",
                extra={
                    "acuity_event": acuity_event,
                    "category": appointment_type_category,
                },
            )

    @classmethod
    def from_eb_event(cls, event):
        detail_type = event["detail-type"]
        assert (
            detail_type == RAW_ACUITY_EVENT_DETAIL_TYPE
        ), f"Unexpected detail-type: {detail_type}"
        acuity_event = event["detail"]["body"]
        return cls(
            acuity_event=acuity_event,
            correlation_id=event["id"],
        )

    def get_target_accounts(self):
        ddb_client = Dynamodb(stack_name=STACK_NAME)
        target_accounts = [
            x["account"]
            for x in ddb_client.query(
                table_name=ROUTING_TABLE,
                KeyConditionExpression="env = :env",
                ExpressionAttributeValues={
                    ":env": self.target_env,
                },
            )
        ]
        assert (
            target_accounts
        ), f"No entries found in {ROUTING_TABLE} for {self.target_env}"
        return target_accounts

    def process(self):
        results = list()
        if self.target_env:
            for account in self.get_target_accounts():
                thiscovery_event = eb.ThiscoveryEvent(
                    {
                        "detail-type": PROCESSED_ACUITY_EVENT_DETAIL_TYPE,
                        "detail": {
                            "body": self.acuity_event_body,
                            "target_account": account,
                            "target_environment": self.target_env,
                        },
                        "source": "acuity",
                    }
                )
                result = thiscovery_event.put_event()
                results.append(result["ResponseMetadata"]["HTTPStatusCode"])
        return results


@utils.lambda_wrapper
def process_appointment_event(event, context):
    acuity_event = AcuityEvent.from_eb_event(event=event)
    return acuity_event.process()


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
            "detail": {"body": acuity_event},
            "source": "acuity",
        }
    )
    thiscovery_event.put_event()
    return {"statusCode": HTTPStatus.OK, "body": ""}
