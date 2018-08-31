#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from config import constants
from main.database.db_helper import SqlHelper, DatastoreHelper
from main.helper import util
import logging

logger = logging.getLogger(__name__)


def main():
    gcp_entity = None
    choices = {1: 'restaurant', 2: 'kaufkraft', 3: 'rent', 4: 'speisekarte', 5: 'zip_code'}

    action_string = 'What do you want to reset?\n'

    for key in choices.keys():
        choice = '({0}){1}\n'.format(str(key), choices[key])
        action_string += choice

    action_string += "Answer by type in the number."

    util.setup_logging()

    action_number = int(input(action_string))

    if action_number == 1:
        gcp_entity = constants.GCP_ENTITY_RESTAURANT
    elif action_number == 2:
        gcp_entity = constants.GCP_ENTITY_KAUFKRAFT
    elif action_number == 3:
        gcp_entity = constants.GCP_ENTITY_RENT
    elif action_number == 4:
        gcp_entity = constants.GCP_ENTITY_SPEISEKARTE

    if action_number != 5:
        if gcp_entity is not None:
            reset_datastore(gcp_entity)
    else:
        reset_postgres()


def reset_datastore(gcp_entity):
    datastore = DatastoreHelper()

    ds_entities = datastore.fetch_entity(gcp_entity)
    for ds_entity in ds_entities:
        datastore.set_transported(ds_entity, False)


def reset_postgres():
    sql = SqlHelper(constants.SQL_DATABASE_NAME)

    sql.create_session()
    sql_entities = sql.fetch_entity_where('ZipCode', True)
    for sql_entity in sql_entities:
        sql_entity.requested = False

    sql.commit_session()
    sql.close_session()


if __name__ == '__main__':
    main()
