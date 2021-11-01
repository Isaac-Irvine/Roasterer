This program generates roasters for the production team at Good nature. 
It pulls data about all the jobs and all the people from google sheets.

##Project status: 
Somewhat working but has bugs, not all features are implemented yet and next to no documentation


##Todo:
- add more documentation.
- fix bug where it runs forever if there is more people than jobs
- add data validation with useful error messages to google sheets
- if it can't make a complete timetable, make an incomplete one and/or report back why
- make roaster look nicer. Maybe export data back to google sheets
- add in wild cards
- add available for training in Jobs and Cycles table
- refactor data types. i.e use sets more
- find a way to calculate weather its possible to have a valid roaster
- Should I be using BFS? probably yeah

#Known bugs
- finder algorithm not guaranteed to find best solution
- will search for longer than the lifetime of the universe if no solution is available