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
    dotw = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', \
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
    tv_pat = r'^(?P<EP_title>[\w\W].*?):? (?P<EP_season>Season \d{1,3})?:? '\
        '(?P<EP_name>[\w\W].*?)? \(?(?P<EP_number>Episode \d{1,3})?\).*?$|'
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
    """print ('The total time watched is: {}\nThe mode time watched is: \
        {}'.format(total_time_watched,mode_time_watched))
    print ('The mean time watched is: {}\nThe median time watched is: \
        {}'.format(mean_time_watched,median_time_watched))"""
    return total_time_watched,mode_time_watched,\
        mean_time_watched,median_time_watched

def top_x_analysis(expanded_dataframe,title_type,content_type,cnt,invert=True):
    '''Identify the top 5 watched items from the analyzed file'''
    
    if not invert:
        no_nulls = expanded_dataframe[expanded_dataframe[title_type].isnull()]
        no_nulls = no_nulls[no_nulls['EP_title'] != 'Unknown Title']
        #Just for mov: top_x["EP_title"].mask(lambda x: x.eq("Unknown Title")).value_counts().nlargest(cnt) - clunky
    else:
        no_nulls = expanded_dataframe[~expanded_dataframe[title_type].isnull()]
        
    no_nulls = no_nulls.assign(
        EP_combined = lambda x: x['EP_name'] + ' - ' + x['EP_title'],
        EP_context = lambda x: x['EP_combined'] + ' (' + x['EP_season'] + ')'
    )
    top_x = no_nulls['EP_title'].value_counts().nlargest(cnt)
    topCnt = top_x.index
    num_x = top_x.count()
    top_x = top_x.to_string(name=False,dtype=False)
    top_x = top_x.split('\n')
    # Filter only rows with top 5 values
    mask = no_nulls['EP_title'].isin(topCnt)

    # Groupby name and title and count occurrences
    counts = (no_nulls[mask].groupby(['EP_title', 'EP_name', 'EP_combined']).size().reset_index(name='count'))
    # Combine title and name for labeling. For each title, get the name with the highest count
    #counts['EP_combined'] = counts['EP_title'] + ' - ' + counts['EP_name']
    #[['EP_name','count']] - this at the end of top_per_title opens it to showing three columns
    '''top_per_title = (counts.sort_values(['EP_title', 'count'], ascending=[True, False])
        .drop_duplicates(subset='EP_title', keep='first').set_index('EP_combined')['count'])'''
    top_per_title = (counts.sort_values(['EP_title', 'count'], ascending=[True, False])
        .drop_duplicates(subset='EP_title', keep='first').set_index('EP_combined')[['EP_title', 'EP_name', 'count']])
    top_per_title.index = top_per_title['EP_title']
    top_per_title = top_per_title.drop(columns=['EP_title'])
    top_per_title.index.name = None
    top_per_title = top_per_title.to_string(header=False)
    top_per_title = top_per_title.split('\n')
    #Still need EP_combined to identify top_episodes, but can just display it better to get season and show info
    top_episodes = no_nulls[['EP_combined', 'EP_name', 'EP_title', 'EP_season']].value_counts().nlargest(cnt)
    top_episodes = top_episodes.reset_index(level = ['EP_combined'], drop=True)
    top_episodes = top_episodes.to_string(name=False,dtype=False,header=False)
    top_episodes = top_episodes.split('\n')
    #pd.set_option('display.multi-sparse', False)
    if num_x == 1:
        content_type = content_type[:-1]
        content = "Here is the top %s you watched and the number of times you watched"\
            " it" % (content_type)
        ep_content = "Here is the most watched episode for the top %s you watched and"\
            " the number of times you watched it" % (content_type)
        untethered_ep_content = "Here is the most watched episode and the number of times"\
            " you watched it" % (content_type)
    else:
        content = "Here are the top %s %s you watched and the number of views for each"\
            " item" % (num_x,content_type)
        """for x in range(num_x):
            print("%d. %s" % (x+1,top_x[x]))"""
        if content_type == 'TV shows':
            ep_content = "Here are the most watched episodes for your top %s %s and the"\
            " number of views for each episode" % (num_x,content_type)
            untethered_ep_content = "Here are the top %s %s episodes you watched,"\
            " irrespective of the main show, and the number of views for each episode" % (num_x,content_type[:-1])
    result = top_x,content
    if content_type == 'TV shows':
        result = result + (top_per_title,ep_content,top_episodes,untethered_ep_content)
    return result

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
    topx = top_x_analysis(expanded_dataframe,'EP_title',"things",5)
    topxtv = top_x_analysis(expanded_dataframe,'EP_name',"TV shows",5)
    topxmov = top_x_analysis(expanded_dataframe,'EP_name',"movies",5,False) 
    topxspec = top_x_analysis(expanded_dataframe,'SPEC_name',"specials",5)
    topxep = topxtv[2],topxtv[3]
    topxiep = topxtv[4],topxtv[5]
    topxtv = topxtv[0],topxtv[1]
    vars = [topx,topxtv,topxep,topxiep,topxmov,topxspec]
    #Test for no specials, etc., also consider a limit on x
    pdf_txt = generate_report(analysis)
    graph_plots = graphs.graphnalysis(limited_dataframe,\
        'Anything Watched by Day (ex. Previews)')
    drawing = graphs.graph_result(graph_plots)
    reports.AnalyticsReport('NetflixActivityAnalysis.pdf',\
        'Netflix Activity Analysis',pdf_txt,drawing,vars)