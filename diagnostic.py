import requests
import csv
import snowflake.connector


conn = snowflake.connector.connect(
    user="SVC_DS31",
    password="GqAco2cXrSdf88Hupm",
    account="ad21223.eu-west-1",
    warehouse="DATASCHOOL_WH",
    database="TIL_PORTFOLIO_PROJECTS",
    schema="TD_TUG_SCHEMA",
)

# conn.cursor().execute(
#     """
#     CREATE OR REPLACE TABLE TD_TEST AS
#     SELECT * FROM TIL_PORTFOLIO_PROJECTS.TD_TUG_SCHEMA.TD_UPCOMING_ATTENDABLE_EVENTS;"""
# )

conn.cursor().execute(
    """
    DROP TABLE TD_TEST;"""
)
