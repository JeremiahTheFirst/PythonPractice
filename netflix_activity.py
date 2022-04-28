#!/usr/bin/env python3
'''Analyze Netflix Viewing Activity Data'''

import pandas as pd
import matplotlib.pyplot as plt
import datetime
from matplotlib.backends.backend_pdf import PdfPages
import graphs
import time_breakdown

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
    top5 = df['Title'].value_counts().nlargest(5).to_string(name=False,dtype=False)
    #print top5 to return clean look
    Season = testf['Title'].str.extract(r'^(([\w\W].*?) (Season \d{1,3})(?:: ))?.*?([A-Za-z: ].*)?')
    pattern = r'^([\w\W].*?) (?=.*?(Season \d{1,3})?(?:: ))\2.([\w !@#$%\^&\*\(\)-_\=\+].*)$'
    pattern = r'^([\w\W].*?) (?=.*?(Season \d{1,3})?(?:: ))\2.| ?([\w !@#$%\^&\*\(\)\-_\=\+].*)$'
    pattern = r'^([\w\W].*?) (?=.*?(Season \d{1,3})?(?:: ))\2.([\w !@#$%\^&\*\(\)\-_\=\+].*)| ?([\w !@#$%\^&\*\(\)\-_\=\+].*)$'
    workingpattern = r'^([\w\W].*?):? (?=.*?(Season \d{1,3})?: )\2. ([\w !@#$%\^&\*\(\)\-_\=\+].*) \((Episode \d{1,3})\)$| ?([\w !@#$%\^&\*\(\)\-_\=\+].*)$'
    simplerpattern = r'^(([\w\W].*?):? (Season \d{1,3})?:? ([\w\W].*?)? \(?(Episode \d{1,3})?\).*?)|([\w\W].*?)$'
    #Wanting to change the pattern up to stop at the first : before Season: or after the last : - would treat comedians like series, would catch 30 for 30
    #Split pattern into or variable chunks for ease of reading, line saving
    pattern = r'^([\w\W].*?):? ((Season \d{1,3})?:? ([\w\W].*?)? \(?(Episode \d{1,3})?\).*?)$|^([\w\W].*?): ([\w\W].*?)$|^([\w\W].*?)$'
    namedpat = r'(?|^(?P<sries>[\w\W].*?):? (?P<seasn>Season \d{1,3})?:? ([\w\W].*?)? \(?(?P<episd>Episode \d{1,3})?\).*?$|^(?P<sries>[\w\W].*?): (?P<episd>[\w\W].*?)$|^(?P<sries>[\w\W].*?)$)'
    testc = pd.concat([testf,Season],axis=1)
    testc.drop(['Title'], axis=1, inplace=True)
    #Don't want to do above just yet, but how it would be done
    total_time_watched = limited_dataframe['Duration'].sum()
    mode_time_watched = limited_dataframe['Duration'].mode(dropna=True)[0]
    mean_time_watched = limited_dataframe['Duration'].mean()
    median_time_watched = limited_dataframe['Duration'].median()
    mode_time_watched = time_breakdown.split(mode_time_watched)
    mean_time_watched = time_breakdown.split(mean_time_watched)
    median_time_watched = time_breakdown.split(median_time_watched)
    print ('The total time watched is: {}\nThe mode time watched is: {}'.format(total_time_watched,mode_time_watched))
    print ('The mean time watched is: {}\nThe median time watched is: {}'.format(mean_time_watched,median_time_watched))
    return total_time_watched,mode_time_watched,mean_time_watched,median_time_watched

def graph_by_day(by_day_dataframe):
    '''Graph provided dataset by day and output to PDF'''
    no_previews_by_day = no_previews['weekday'].value_counts()
    no_previews_by_day = no_previews_by_day.sort_index()
    graph_result = no_previews_by_day.plot(kind='bar', figsize=(10,5), title='Anything Watched by Day (ex. Previews)')
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
    rpt_txt = 'The total time watched is:        {}\nThe mode time watched is:      {}\n'.format(analysis[0],analysis[1])
    rpt_txt += 'The mean time watched is:      {}\nThe median time watched is:   {}\n'.format(analysis[2],analysis[3])
    return rpt_txt    
    
def graph_change(rpt_txt):
    '''Alternate graph method '''
    with PdfPages('NetflixActivityAnalysis.pdf') as pdf:
        first_page = plt.figure(figsize=(11.69,8.27))
        first_page.clf()
        rpt_title = 'Netflix Activity Analysis'
        first_page.text(0.5,.9,rpt_title,fontsize=24, ha='center')
        first_page.text(0.1,.75,rpt_txt)
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
    limited_dataframe = analyse()
    analysis = limited_analysis(limited_dataframe)
    rpt_txt = generate_report(analysis)
    #graph_change(rpt_txt)
    graph_plots = graphs.graphnalysis(limited_dataframe,'Anything Watched by Day (ex. Previews)')
    graphs.graph_result(rpt_txt,graph_plots)
    
    #Report section
    #title = 'Netflix Activity Analysis'
    #filename = 'NetflixActivityAnalysis.pdf'
    #paragraph = generate_report(analysis)