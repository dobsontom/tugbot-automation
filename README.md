# Automating TUG Event Posting with TUGBot

## Project Description
The TUGBot project automates the detection and posting of relevant Tableau User Group (TUG) events to The Information Lab (TIL)'s Convo network, streamlining the delivery of event notifications to employees.

## Workflow
1. **Data Collection and Processing**
* A Python script downloads TUG events from the Tableau User Group website in JSON format. The script then parses the data and writes the events to a CSV.
2. **Ingestion into Snowflake and Transformation**
* The Python Snowflake Connector is used to stage and upload the CSV to the table *td_all_events* on TIL's Snowflake server.
* The script then creates a new called table *td_accessible_events* which contains upcoming events that are accessible to TIL staff. Accessible events are either hosted in countries with a TIL office or hosted virtually during staff waking hours.
* Two tables are then created for two different types of event:
  * *td_upcoming_accessible_events* contains accessible events that are within the next two weeks.
  * *td_distant_accessible_events* contains accessible events that are more than two weeks in the future.
3. **Automation Schedule**
* A GitHub action is used to run the script every three hours at 20 minutes past that hour, between 08:00 and 22:59, Monday through Friday. This ensures that posts are created during TIL working hours.
4. **Integration with Convo**
* Zapier, an external webapp, is set up to post to Convo when new rows are detected:
  * New rows in *td_upcoming_accessible_events* trigger a TUG event reminder.
  * New rows in *td_distant_accessible_events* trigger a new TUG alert.
## Acknowlegements
* Thanks to The Information Lab for supporting the TUGBot project.