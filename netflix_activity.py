#!/usr/bin/env python3
'''Analyze Netflix Viewing Activity Data'''

import pandas as pd
import matplotlib.pyplot as plt

# Columns - Profile Name, Start Time, Duration, Attributes, Title, 
#           Supplemental Video Type, Device Type, Bookmark, Latest Bookmark, Country

#Below option disables the SettingWithCopyWarning that pop up working with slicing these frames;
#Instances are marked, though deep copy does also prevent the warning - if it were usable in all instances, could default back
pd.options.mode.chained_assignment = None #default='warn'
#file = 'ViewingActivity.csv'

def analyse(file='ViewingActivity.csv'):
    '''Convert 'Start Time' column from object to datetime, then convert to Central timezone '''
    df = pd.read_csv(file)
    df['Start Time'] = pd.to_datetime(df['Start Time'], utc=True)
    df = df.set_index('Start Time')
    df.index = df.index.tz_convert('US/Central')
    df = df.reset_index()
    df['weekday'] = df['Start Time'].dt.day_name()
    df['hour'] = df['Start Time'].dt.hour
    df['quarter'] = df['Start Time'].dt.quarter
    df['week'] = df['Start Time'].dt.isocalendar().week
    df['month'] = df['Start Time'].dt.month
    df['year'] = df['Start Time'].dt.year

    # Convert 'Duration' column from object to timedelta
    df['Duration'] = pd.to_timedelta(df['Duration'])
    # Make new dataframe to trim out previews, trailers, etc.
    no_previews = df[(df['Duration'] > '0 days 00:02:30')]
    return no_previews

def limited_analysis(limited_dataframe):
    '''Gets datapoints from the more limited sample provided '''

    # Calculate some interesting points
    total_time_watched = no_previews['Duration'].sum()
    mode_time_watched = no_previews['Duration'].mode(dropna=True)[0]
    mean_time_watched = no_previews['Duration'].mean()
    median_time_watched = no_previews['Duration'].median()
    print ('The total time watched is: {}\nThe mode time watched is: {}'.format(total_time_watched,mode_time_watched))
    print ('The mean time watched is: {}\nThe median time watched is: {}'.format(mean_time_watched,median_time_watched))

def graph_by_day(by_day_dataframe):
    '''Graph provided dataset by day '''
    #SettingWithCopyWarning
    no_previews['weekday'] = no_previews['Start Time'].copy(deep=True).dt.day_name()
    dotw=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    #SettingWithCopyWarning
    no_previews['weekday'] = pd.Categorical(no_previews['weekday'], categories=dotw, ordered=True)
    no_previews_by_day = no_previews['weekday'].value_counts()
    no_previews_by_day = no_previews_by_day.sort_index()
    no_previews_by_day.plot(kind='bar', figsize=(10,5), title='Anything Watched by Day (ex. Previews)')
    plt.tight_layout()
    plt.show()

# Tease out some other datapoints
'''df['weekday'] = df['Start Time'].dt.weekday
df['hour'] = df['Start Time'].dt.hour
df['quarter'] = df['Start Time'].dt.quarter
df['week'] = df['Start Time'].dt.isocalendar().week
df['month'] = df['Start Time'].dt.month
df['month'] = df['Start Time'].dt.year'''

if __name__ == "__main__":
    no_previews = analyse()
    limited_analysis(no_previews)
    graph_by_day(no_previews)