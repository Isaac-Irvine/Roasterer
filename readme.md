This program generates roasters for the production team at Good nature. 
It pulls data about all the jobs and all the people from google sheets.

##Project status: 
Somewhat working but has bugs, not all features are implemented yet and next to no documentation


##Todo:
- add more documentation.
- add data validation with useful error messages to google sheets
- if it can't make a complete timetable, report back why
- add in wild cards
- add available for training in Jobs and Cycles table
- refactor data types. i.e use sets more

## known issues in algorithm
- doesn't check if having a trainee will mean all roles can't be filled
- not super random. This one I know how to fix but haven't yet