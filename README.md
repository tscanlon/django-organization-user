This an example repo to try and give an example of how you could make the admin site safe(r) for multiple sets of users. Think a Saas platfrom for multiple businesses.

My use case is I'd like to be able to prototype with a few groups of users that each have thier own collection of data that the other groups of users cannot access.

At the moment there are still some edge cases to work out but I've tried to season the code with lots of comments and doc strings.

The most important to call out is the name field can still leak through the recent actions portion of the admin index.
This might work to solve it but I'm running out of time tonight to test it.
https://stackoverflow.com/a/73499839