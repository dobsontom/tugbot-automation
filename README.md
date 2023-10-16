# Automating TUG Event Posting with TUGBot

## Project Description
The TUGBot project automates the detection and posting of relevant Tableau User Group (TUG) events to The Information Lab (TIL)'s internal [Convo](https://www.convo.com/ "Convo Platform Website") network, streamlining the delivery of event notifications to employees.

## Workflow
1. **Data Collection and Processing**
* A Python script downloads TUG events from a [JSON feed](https://usergroups.tableau.com/api/event/?fields=id,title,description_short,picture,chapter,city,start_date,url,relative_url,video_url,event_type_title,event_type_logo,tags,allows_cohosting&status=Published "TUG Events JSON Feed") on the [Tableau User Groups website](https://usergroups.tableau.com/ "Tableau User Groups Website") in JSON format. The script then parses the data and writes the events to a CSV.
2. **Ingestion into Snowflake and Transformation**
* The [Snowflake Connector for Python](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector "Snowflake Connector Documentation") is used to stage and upload the CSV to the table *td_all_events* on the TIL Snowflake server.
* The script creates a new called table *td_accessible_events* which contains upcoming events that are accessible. Accessible events are defined as either in-person events held in countries that have a TIL office or virtual events scheduled during staff's waking hours.
* The script then creates two tables for distinct subsets of events:
  * *td_upcoming_accessible_events*: accessible events that are within the next two weeks.
  * *td_distant_accessible_events*: accessible events that are scheduled more than two weeks in the future.
3. **Automation Schedule**
* A GitHub action is used to run the script every three hours at 20 minutes past that hour, between 08:00 and 22:59, Monday through Friday. This ensures that TUG alerts are posted during staff working hours.
4. **Integration with Convo**
* [Zapier](https://zapier.com/ "Zapier Website"), an external webapp, is set up to post to Convo when new rows are detected:
  * A new row in *td_upcoming_accessible_events* triggers a TUG event reminder.
  * A new rows in *td_distant_accessible_events* triggers a new TUG alert.
## Acknowlegements
* Thanks to [The Information Lab](https://www.theinformationlab.co.uk/ "The Information Lab Website") for supporting the TUGBot project.