# Automating TUG Event Posting with TUGBot

## Project Description
The TUGBot project automates the detection and posting of relevant Tableau User Group (TUG) events to The Information Lab (TIL)'s internal [Convo](https://www.convo.com/ "Convo Platform Website") network, streamlining the delivery of event notifications to employees.

## Workflow
1. **Data Collection and Processing**
*  The Python script downloads TUG events from a [JSON feed](https://usergroups.tableau.com/api/event/?fields=id,title,description_short,picture,chapter,city,start_date,url,relative_url,video_url,event_type_title,event_type_logo,tags,allows_cohosting&status=Published "TUG Events JSON Feed") on the [Tableau User Groups website](https://usergroups.tableau.com/ "Tableau User Groups Website"). It then parses the JSON data and writes the events to a CSV.

2. **Ingestion into Snowflake and Transformation**
* The [Snowflake Connector for Python](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector "Snowflake Connector Documentation") is used to stage the CSV on the TIL Snowflake server and copy the data to the table *td_all_events*.
* Next, the script creates the new table *td_accessible_events* that contains upcoming events that are accessible. Two types of events are classified as accessible:
  * in-person events held in a country where a TIL office is based.
  * virtual events held during the waking hours of TIL staff.
* The script then creates two tables with distinct subsets of accessible events:
  * *td_upcoming_accessible_events*: accessible events within the next two weeks.
  * *td_distant_accessible_events*: accessible events more than two weeks in the future.
 
3. **Automation Schedule**
* A GitHub action runs the Python script every three hours at 20 minutes past that hour, between 08:00 and 22:59, Monday through Friday, ensuring that TUG alerts occur during TIL's working hours.

4. **Integration with Convo**
* [Zapier](https://zapier.com/ "Zapier Website"), an external web app, generates a Convo post with event details for each new row that is detected:
  * A new row in *td_upcoming_accessible_events* triggers a TUG event reminder.
  * A new row in *td_distant_accessible_events* triggers a new TUG alert.
 
## Acknowledgements
* Thanks to [The Information Lab](https://www.theinformationlab.co.uk/ "The Information Lab Website") for supporting the TUGBot project.
