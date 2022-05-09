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
from thiscovery_lib.dynamodb_utilities import DdbBaseTable, DdbBaseItem


ROUTING_TABLE = "ForwardingMap"
RAW_ACUITY_EVENT_DETAIL_TYPE = "raw_acuity_event"
PROCESSED_ACUITY_EVENT_DETAIL_TYPE = "processed_acuity_event"
STACK_NAME = "acuity-router"


class RoutingTable(DdbBaseTable):
    name = ROUTING_TABLE
    partition = "env"
    sort = "account"

    def __init__(self):
        super().__init__(stack_name=STACK_NAME)


class RoutingTableItem(DdbBaseItem):
    def __init__(self, env: str, account: str):
        super().__init__(table=RoutingTable())
        self.env = env
        self.account = account
