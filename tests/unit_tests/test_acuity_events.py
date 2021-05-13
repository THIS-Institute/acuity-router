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
import copy
import thiscovery_dev_tools.testing_tools as test_tools
import unittest
from http import HTTPStatus
from thiscovery_lib import utilities as utils

import src.appointments as app
import tests.test_data as td



class TestAcuityEvent(test_tools.BaseTestCase):

    def test_appointment_event_api_ok(self):
        result = test_tools.test_post(
            local_method=app.appointment_event_api,
            aws_url=
        )