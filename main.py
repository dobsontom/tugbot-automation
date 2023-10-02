import requests
import csv
import snowflake.connector
import os

url = "https://usergroups.tableau.com/api/search/?result_types=upcoming_event&&country_code=Earth"

response = requests.get(url)
response.raise_for_status()

json_results = response.json()["results"]

combined_data = []
for entry in json_results:
    main_data = {key: value for key, value in entry.items() if key != "chapter"}

    chapter_data = {"chapter_" + key: value for key, value in entry["chapter"].items()}

    combined = {**main_data, **chapter_data}

    combined_data.append(combined)

# print(combined_data[0].keys())

fieldnames = [
    "id",
    "title",
    "description_short",
    "picture",
    "city",
    "start_date",
    "url",
    "relative_url",
    "video_url",
    "event_type_title",
    "event_type_logo",
    "tags",
    "allows_cohosting",
    "result_type",
    "chapter_chapter_location",
    "chapter_city",
    "chapter_country",
    "chapter_country_name",
    "chapter_description",
    "chapter_id",
    "chapter_hide_country_info",
    "chapter_logo",
    "chapter_state",
    "chapter_timezone",
    "chapter_title",
    "chapter_relative_url",
    "chapter_url",
]

with open("events.csv", "w", newline="", encoding="utf-8") as events_data:
    writer = csv.DictWriter(events_data, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(combined_data)

# with open("events.csv", "r", newline="", encoding="utf-8") as events_data:
#     print(events_data.read())

conn = snowflake.connector.connect(
    user="SVC_DS31",
    password=os.environ["SNOW_PASS"],
    account="ad21223.eu-west-1",
    warehouse="DATASCHOOL_WH",
    database="TIL_PORTFOLIO_PROJECTS",
    schema="TD_TUG_SCHEMA",
)

conn.cursor().execute(
    """
    CREATE OR REPLACE STAGE TD_STAGE
    FILE_FORMAT = (TYPE = 'CSV' FIELD_OPTIONALLY_ENCLOSED_BY = '"' SKIP_HEADER = 1);"""
)

conn.cursor().execute(
    """
    CREATE OR REPLACE TABLE TD_ALL_EVENTS (id INTEGER, title TEXT, description_short TEXT, picture TEXT, city TEXT, start_date TEXT, url TEXT, relative_url TEXT, video_url FLOAT, event_type_title TEXT, event_type_logo TEXT, tags TEXT, allows_cohosting BOOLEAN, result_type TEXT, chapter_chapter_location TEXT, chapter_city TEXT, chapter_country TEXT, chapter_country_name TEXT, chapter_description TEXT, chapter_id INTEGER, chapter_hide_country_info BOOLEAN, chapter_logo TEXT, chapter_state TEXT, chapter_timezone TEXT, chapter_title TEXT, chapter_relative_url TEXT, chapter_url TEXT);"""
)

conn.cursor().execute(
    """
    PUT file://events.*csv @TD_STAGE;"""
)

conn.cursor().execute(
    """
    COPY INTO TD_ALL_EVENTS FROM @TD_STAGE;"""
)

conn.cursor().execute(
    """
    ALTER SESSION SET date_output_format = 'MMMM DD, YYYY';"""
)

conn.cursor().execute(
    """
    ALTER SESSION SET TIMEZONE = 'UTC';"""
)

conn.cursor().execute(
    """
    CREATE OR REPLACE TABLE td_attendable_events AS
    (
       WITH main_data AS
       (
          SELECT
             id,
             title,
             concat('"', RTRIM(description_short), '"') AS description_short,
             event_type_title,
             city,
             chapter_country_name,
             to_date(split_part(start_date, 'T', 1)) AS date_original,
             to_char(to_date(split_part(start_date, 'T', 1))) AS date_formatted,
             TIME(LEFT(split_part(start_date, 'T', 2), 8 ) ) AS local_time,
             RIGHT(start_date, 6) AS time_difference,
             url,
             REPLACE( TRANSLATE(tags, '''[]', ''), ', ', ',' ) AS tags,
             REPLACE( REPLACE( REPLACE(picture, '{''url'': ''', ''), '''}', '' ), '{}', '' ) AS picture,
             CONVERT_TIMEZONE('GMT', current_timestamp()) as row_created_timestamp
          FROM
             til_portfolio_projects.td_tug_schema.td_all_events
       ),
       cities AS
       (
          SELECT
             *
          FROM
             til_portfolio_projects.td_tug_schema.cities
       )
       SELECT
          *
       FROM
          (
             SELECT
                *,
                CASE
                   WHEN
                      event_type_title IN
                      (
                         'Virtual Event',
                         'Virtual',
                         'Hybrid Event',
                         'Hybrid'
                      )
                      AND gmt_time NOT BETWEEN TIME('02:00') AND TIME('08:00')
                   THEN
                      TRUE
                   ELSE
                      CASE
                         WHEN
                            chapter_country_name IN
                            (
                               SELECT
                                  country
                               FROM
                                  cities
                            )
                            AND time_difference IN
                            (
                               '+00:00',
                               '+01:00',
                               '+02:00',
                               '-04:00'
                            )
                         THEN
                            TRUE
                         ELSE
                            FALSE
                      END
                END
                AS event_attendable_ind
             FROM
                (
                   SELECT
                      *,
                      CASE
                         WHEN
                            LEFT(time_difference, 1) = '+'
                         THEN
                            DATEADD( HOUR, - SUBSTR(time_difference, 3, 1), local_time )
                         ELSE
                            DATEADD( HOUR, SUBSTR(time_difference, 3, 1), local_time )
                      END
                      AS gmt_time
                   FROM
                      main_data
                )
          )
       WHERE
          event_attendable_ind = TRUE
    )
    ORDER BY
       date_formatted, gmt_time;
"""
)


conn.cursor().execute(
    """
    CREATE OR REPLACE TABLE til_portfolio_projects.td_tug_schema.td_upcoming_attendable_events AS (
       SELECT
          *,
          DATEDIFF(DAY, CURRENT_DATE, date_original) AS days_until_event
       FROM
          til_portfolio_projects.td_tug_schema.td_attendable_events
       WHERE
          DATEDIFF(DAY, CURRENT_DATE, date_original) BETWEEN 0 AND 14
    );
"""
)

print("Job Complete")
