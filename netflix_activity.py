#!/usr/bin/env python3
'''Analyze Netflix Viewing Activity Data'''

from cgitb import grey
from mmap import PAGESIZE
from textwrap import dedent
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
from matplotlib.backends.backend_pdf import PdfPages
import graphs
import time_breakdown
import reports

# Columns - Profile Name, Start Time, Duration, Attributes, Title, 
#           Supplemental Video Type, Device Type, Bookmark, Latest Bookmark, 
#           Country

def analyze(file='ViewingActivity.csv'):
    '''Convert 'Start Time' column from object to datetime, \
        then convert to Central timezone '''
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
    dotw=['Monday', 'Tuesday', 'Wednesday', 'Thursday', \
        'Friday', 'Saturday', 'Sunday']
    df['weekday'] = pd.Categorical(df['weekday'], categories=dotw, ordered=True)

    # Convert 'Duration' column from object to timedelta to allow next trim
    df['Duration'] = pd.to_timedelta(df['Duration'])
    # Make new dataframe to trim out previews, trailers, etc.
    no_previews = df[(df['Duration'] > '0 days 00:02:30')]
    return no_previews

def expand_dataframe(limited_dataframe):
    '''Clean up and standerdize dataframe to make data comparable'''

    #Regex patterns for corrolating TV to movie to specials
    tv_pat = r'^(?P<EP_title>[\w\W].*?):? \
        (?P<EP_season>Season \d{1,3})?:? (?P<EP_name>[\w\W].*?)? \(?\
            (?P<EP_number>Episode \d{1,3})?\).*?$|'
    spec_pat = r'^(?P<SPEC_title>[\w\W].*?): (?P<SPEC_name>[\w\W].*?)$|'
    other_pat = r'^(?P<OTHER_title>[\w\W].*?)$'
    Breakdown = limited_dataframe['Title'].str.extract(tv_pat + spec_pat + other_pat)
    #Fill NaN in named column with value from last column - EP_name with SPEC_name
    #And then EP_title with SPEC_title and OTHER_title, so that EP_title will always have title info
    Breakdown['EP_name'] = Breakdown['EP_name'].str.strip().replace('', \
        np.nan).fillna(Breakdown['SPEC_name'])
    Breakdown['EP_title'] = Breakdown['EP_title'].str.strip().replace('', \
        np.nan).fillna(Breakdown['SPEC_title'])
    Breakdown['EP_title'] = Breakdown['EP_title'].str.strip().replace('', \
        np.nan).fillna(Breakdown['OTHER_title'])
    #Combine df with better title info with original df
    Breakdown = pd.concat([Breakdown,limited_dataframe],axis=1)
    #Drop original df title column since it is broken into more useful columns
    Breakdown = Breakdown.drop(['Title'], axis=1)
    return Breakdown

def limited_analysis(limited_dataframe):
    '''Gets datapoints from the more limited sample provided '''

    total_time_watched = limited_dataframe['Duration'].sum()
    mode_time_watched = limited_dataframe['Duration'].mode(dropna=True)[0]
    mean_time_watched = limited_dataframe['Duration'].mean()
    median_time_watched = limited_dataframe['Duration'].median()
    mode_time_watched = time_breakdown.split(mode_time_watched)
    mean_time_watched = time_breakdown.split(mean_time_watched)
    median_time_watched = time_breakdown.split(median_time_watched)
    print ('The total time watched is: {}\nThe mode time watched is: \
        {}'.format(total_time_watched,mode_time_watched))
    print ('The mean time watched is: {}\nThe median time watched is: \
        {}'.format(mean_time_watched,median_time_watched))
    return total_time_watched,mode_time_watched,\
        mean_time_watched,median_time_watched

def top5_analysis(expanded_dataframe):
    '''Identify the top 5 watched items from the analyzed file'''

    top5 = expanded_dataframe['EP_title'].value_counts().nlargest(5).to_string\
        (name=False,dtype=False)
    top5 = top5.split('\n')
    for x in range(5):
        print("%d. %s" % (x+1,top5[x]))
    #print top5 to return clean look
    return top5

def graph_by_day(by_day_dataframe):
    '''Graph provided dataset by day and output to PDF'''
    no_previews_by_day = by_day_dataframe['weekday'].value_counts()
    no_previews_by_day = no_previews_by_day.sort_index()
    graph_result = no_previews_by_day.plot(kind='bar', figsize=(10,5), 
        title='Anything Watched by Day (ex. Previews)')
    #plt.tight_layout()
    #plt.show()
    #plt.close()
    return graph_result

def graph_test(graph_result):
    graph_result.plot()
    plt.tight_layout()
    plt.show()
    plt.close()
    
def generate_report(analysis):
    pdf_txt = ["The total time watched is:        {}".format(analysis[0])]
    pdf_txt.append("The mode time watched is:      {}".format(analysis[1]))
    pdf_txt.append("The mean time watched is:      {}".format(analysis[2]))
    pdf_txt.append("The median time watched is:   {}".format(analysis[3]))
    return pdf_txt

if __name__ == "__main__":
    limited_dataframe = analyze()
    expanded_dataframe = expand_dataframe(limited_dataframe)
    analysis = limited_analysis(expanded_dataframe)
    top5 = top5_analysis(expanded_dataframe)
    pdf_txt = generate_report(analysis)
    graph_plots = graphs.graphnalysis(limited_dataframe,\
        'Anything Watched by Day (ex. Previews)')
    drawing=graphs.graph_result(graph_plots)
    reports.AnalyticsReport('NetflixActivityAnalysis.pdf',\
        'Netflix Activity Analysis',pdf_txt,top5,drawing)