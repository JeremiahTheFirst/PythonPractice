#!/usr/bin/env python3
'''Analyze Netflix Viewing Activity Data'''

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

file = 'ViewingActivity.csv'

df = pd.read_csv(file)
# Convert 'Start Time' column from object to datetime, then convert to Central timezone
df['Start Time'] = pd.to_datetime(df['Start Time'], utc=True)
df = df.set_index('Start Time')
df.index = df.index.tz_convert('US/Central')
df = df.reset_index()

# Convert 'Duration' column from object to timedelta
df['Duration'] = pd.to_timedelta(df['Duration'])

# Make new dataframe to trim out previews, trailers, etc.
no_previews = df[(df['Duration'] > '0 days 00:02:30')]

# Calculate some interesting points
total_time_watched = no_previews['Duration'].sum()
mode_time_watched = no_previews['Duration'].mode()
mean_time_watched = no_previews['Duration'].mean()
median_time_watched = no_previews['Duration'].median()

# Graph no_previews by day
#no_previews['weekday'] = no_previews['Start Time'].dt.weekday
no_previews['weekday'] = no_previews['Start Time'].dt.day_name()
#weekday_map = {0:'MON', 1:'TUE', 2:'WED', 3:'THU', 4:'FRI', 5:'SAT', 6:'SUN'}
#from matplotlib.dates import MO, TU, WE, TH, FR, SA, SU
#loc = dates.WeekdayLocator(byweekday=(MO, TU, WE, TH, FR, SA, SU))
no_previews['weekday'] = pd.Categorical(no_previews['weekday'], categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], ordered=True)
no_previews_by_day = no_previews['weekday'].value_counts()
no_previews_by_day = no_previews_by_day.sort_index()
no_previews_by_day.plot(kind='bar', figsize=(10,5), title='Anything Watched by Day (ex. Previews)')
plt.tight_layout()
plt.show()

# Tease out some other datapoints
# NOTE: SettingWithCopyWarning
df['weekday'] = df['Start Time'].dt.weekday
df['hour'] = df['Start Time'].dt.hour
df['quarter'] = df['Start Time'].dt.quarter
df['week'] = df['Start Time'].dt.isocalendar().week
df['month'] = df['Start Time'].dt.month
df['month'] = df['Start Time'].dt.year
