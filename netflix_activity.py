#!/usr/bin/env python3
'''Analyze Netflix Viewing Activity Data'''

import pandas as pd
import matplotlib.pyplot as plt
import datetime
from matplotlib.backends.backend_pdf import PdfPages
import reports

# Columns - Profile Name, Start Time, Duration, Attributes, Title, 
#           Supplemental Video Type, Device Type, Bookmark, Latest Bookmark, Country

#Below option disables the SettingWithCopyWarning that pop up adding columns to copied frames; added columns to main instead
#pd.options.mode.chained_assignment = None #default='warn'
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
    
    #Categorizing for proper ordering in charts
    dotw=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['weekday'] = pd.Categorical(df['weekday'], categories=dotw, ordered=True)

    # Convert 'Duration' column from object to timedelta to allow next trim
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
    #Ifs work for sample data, but double-digit days will break it
    if len(str(mean_time_watched)) > 15:
        # Convert timedelta to string and drop everything after seconds
        mean_time_watched = str(mean_time_watched)[:-7]
    median_time_watched = no_previews['Duration'].median()
    if len(str(median_time_watched)) > 15:
        # Convert timedelta to string and drop everything after seconds
        median_time_watched = str(median_time_watched)[:-7]
    print ('The total time watched is: {}\nThe mode time watched is: {}'.format(total_time_watched,mode_time_watched))
    print ('The mean time watched is: {}\nThe median time watched is: {}'.format(mean_time_watched,median_time_watched))
    return total_time_watched,mode_time_watched,mean_time_watched,median_time_watched

def graph_by_day(by_day_dataframe):
    '''Graph provided dataset by day and output to PDF'''
    with PdfPages('NetflixActivityAnalysis.pdf') as pdf:
        no_previews_by_day = no_previews['weekday'].value_counts()
        no_previews_by_day = no_previews_by_day.sort_index()
        no_previews_by_day.plot(kind='bar', figsize=(10,5), title='Anything Watched by Day (ex. Previews)')
        plt.tight_layout()
        pdf.savefig()
        plt.show()
        plt.close()
    
        #Set PDF metadata
        d = pdf.infodict()
        d['Title'] = 'Netflix Activity Analysis'
        # Will need to consider identifying user - would need to be OS agnostic
        d['Author'] = u'Jeremiah Adams'
        d['Subject'] = 'Stats and graphs on the user\'s supplied Netflix Activity'
        d['Keywords'] = 'Netflix DataScience Statistics'
        d['CreationDate'] = datetime.datetime(2022, 3, 30)
        d['ModDate'] = datetime.datetime.today()
    
def generate_report(analysis):
    rpt_txt = 'The total time watched is: {}\nThe mode time watched is: {}\n'.format(analysis[0],analysis[1])
    rpt_txt += 'The mean time watched is: {}\nThe median time watched is: {}\n'.format(analysis[2],analysis[3])
    return rpt_txt    
    
def graph_change(rpt_txt):
    '''Alternate graph method '''
    with PdfPages('NetflixActivityAnalysis.pdf') as pdf:
        first_page = plt.figure(figsize=(11.69,8.27))
        first_page.clf()
        first_page.text(0,.75,rpt_txt)
        pdf.savefig()
        plt.close()
        
        no_previews_by_day = no_previews['weekday'].value_counts()
        no_previews_by_day = no_previews_by_day.sort_index()
        no_previews_by_day.plot(kind='bar', figsize=(10,5), title='Anything Watched by Day (ex. Previews)')
        plt.tight_layout()
        pdf.savefig()
        #plt.show()
        plt.close()
        
        #Set PDF metadata
        d = pdf.infodict()
        d['Title'] ='Netflix Activity Analysis'
        # Will need to consider identifying user - would need to be OS agnostic
        d['Author'] = 'Jeremiah Adams'
        d['Subject'] = 'Stats and graphs on the user\'s supplied Netflix Activity'
        d['Keywords'] = 'Netflix DataScience Statistics'
        d['CreationDate'] = datetime.datetime(2022, 3, 30)
        d['ModDate'] = datetime.datetime.today()

if __name__ == "__main__":
    no_previews = analyse()
    analysis = limited_analysis(no_previews)
    rpt_txt = generate_report(analysis)
    graph_change(rpt_txt)
    #graph_by_day(no_previews)
    
    #Report section
    #title = 'Netflix Activity Analysis'
    #filename = 'NetflixActivityAnalysis.pdf'
    #paragraph = generate_report(analysis)
    #reports.generate(filename, title, paragraph)