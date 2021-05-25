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
import thiscovery_dev_tools.testing_tools as test_tools
from http import HTTPStatus
from pprint import pprint

import src.appointments as app
import tests.test_data as td


class TestAcuityEventClass(test_tools.BaseTestCase):
    def test_init_ok(self):
        ae = app.AcuityEvent(acuity_event=td.EVENT_BODY_WITH_USER_METADATA)
        self.assertEqual("dev", ae.target_env)

    def test_get_target_accounts_ok(self):
        ae = app.AcuityEvent(acuity_event=td.EVENT_BODY_WITH_USER_METADATA)
        expected_results = ["thiscovery-afs25", "engage-dev1"]
        self.assertCountEqual(expected_results, ae.get_target_accounts())

    def test_process_ok(self):
        ae = app.AcuityEvent(acuity_event=td.EVENT_BODY_WITH_USER_METADATA)
        results = ae.process()
        expected_results = [HTTPStatus.OK, HTTPStatus.OK]
        self.assertEqual(expected_results, results)


class TestAcuityEventApi(test_tools.BaseTestCase):
    endpoint_url = "v1/appointment-event"

    def test_appointment_event_api_ok(self):
        result = test_tools.test_post(
            local_method=app.appointment_event_api,
            aws_url=self.endpoint_url,
            request_body=td.EVENT_BODY_WITH_USER_METADATA,
        )
        self.assertEqual(HTTPStatus.OK, result["statusCode"])
