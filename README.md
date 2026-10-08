# shred
analyzing workout/health data to track progress & find areas for improvement 
- tailored to my preferences / app usage


## Goals
- understand factors driving strength progress
- see how sleep, recovery, and nutrition affect training
- track consistency over time

## Milestones
- [x] analyze data from hevy
- [x] analyze data from garmin
- [ ] analyze data from strava
- [ ] analyze data from mfp
- [ ] combine analysis from different applications
- [ ] have data being pulled in consistently
- [ ] add interactive components

- [ ] make it work for any user (personal settings like start date/timezones) + add setup/envexample


## Data sources
| app | what's pulled | how |
|---|---|---|
| hevy | workouts, exercises, sets, reps, weight, workout length | official API (requires Hevy Pro) |
| garmin | steps, resting HR, stress, body battery, sleep score + stages, HRV | [`garminconnect`](https://github.com/cyberjunky/python-garminconnect)|

**garmin notes**
- first run pulls everything since `GARMIN_START_DATE`; after that it only pulls new days
- sleep is filed under the day you woke up, so each date's sleep = the night before
- login token is saved to `~/.garminconnect` so you only enter your password once
- built with a vivoactive 5, so training readiness / training status aren't included
