Rosterer is an app that generates roasters for the production team at Good nature.

You give it a list of jobs and people and from that you can make a roaster

## How to use
When you open the program you will see an empty roster. There will be no people or jobs. <br>
You can add people and jobs by clicking on 'Edit' in the top menu, then clicking 'Add person' or 'Add job' respectively.


## Definitions
- Hard job: A job that's considered physically taxing. Ideally you wouldn't do 2 hard jobs in a row.
- Casual job: This is a job that you can come and go from throughout the cycle. You might want to assign someone a casual job if they have a meeting in the middle of the cycle.
- Available person: A person who can be assigned any job they are trained to do.
- Casually available person: A person who can be assigned any casual they are trained to do.
- Unavailable person: A person who should not be assigned to any job.
- Job group: This is a way of grouping similar jobs together. For example, all jobs on the same assembly line would go into the same group. Ideally you wouldn't be assigned two jobs in a row that are part of the same job group


## Information for future developers and maintainers
This was made with Python 3.9 and all the pip dependencies are in requirements.txt <br>
The current code was meant to just be an experimental pathfinder for the roster filling algorithm and learning Tkinter.
I intended to quickly throw together stuff till I found something that worked then go back and using what I learned, 
refactor the whole thing into something much more elegant. However, I was leaving GoodNature and running out of time to finish. 
So I took the pathfinder I had and turned it into something usable as fast as possible. 
So I apologize if anyone needs to maintain or extend this in the future.
