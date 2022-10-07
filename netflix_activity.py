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
#           Supplemental Video Type, Device Type, Bookmark, Latest Bookmark, Country

#Below option disables the SettingWithCopyWarning that pop up adding columns to copied frames; added columns to main instead
#pd.options.mode.chained_assignment = None #default='warn'
#file = 'ViewingActivity.csv'

def analyze(file='ViewingActivity.csv'):
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
    #Regex patterns for corrolating TV to movie to specials
    tv_pat = r'^(?P<EP_title>[\w\W].*?):? (?P<EP_season>Season \d{1,3})?:? (?P<EP_name>[\w\W].*?)? \(?(?P<EP_number>Episode \d{1,3})?\).*?$|'
    spec_pat = r'^(?P<SPEC_title>[\w\W].*?): (?P<SPEC_name>[\w\W].*?)$|'
    other_pat = r'^(?P<OTHER_title>[\w\W].*?)$'
    Breakdown = limited_dataframe['Title'].str.extract(tv_pat + spec_pat + other_pat)
    #Fill NaN in named column with value from last column - EP_name with SPEC_name
    #And then EP_title with SPEC_title and OTHER_title, so that EP_title will always have title info
    Breakdown['EP_name'] = Breakdown['EP_name'].str.strip().replace('', np.nan).fillna(Breakdown['SPEC_name'])
    Breakdown['EP_title'] = Breakdown['EP_title'].str.strip().replace('', np.nan).fillna(Breakdown['SPEC_title'])
    Breakdown['EP_title'] = Breakdown['EP_title'].str.strip().replace('', np.nan).fillna(Breakdown['OTHER_title'])
    #Combine df with better title info with original df
    Breakdown = pd.concat([Breakdown,limited_dataframe],axis=1)
    #Drop original df title column since it is broken into more useful columns
    Breakdown = Breakdown.drop(['Title'], axis=1)

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

def top5_analysis(limited_dataframe):
    '''Identify the top 5 watched items from the analyzed file'''

    top5 = limited_dataframe['Title'].value_counts().nlargest(5).to_string(name=False,dtype=False)
    top5 = top5.split('\n')
    for x in range(5):
        print("%d. %s" % (x+1,top5[x]))
    #print top5 to return clean look
    return top5

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
    pdf_txt = ["The total time watched is:        {}".format(analysis[0])]
    pdf_txt.append("The mode time watched is:      {}".format(analysis[1]))
    pdf_txt.append("The mean time watched is:      {}".format(analysis[2]))
    pdf_txt.append("The median time watched is:   {}".format(analysis[3]))
    return pdf_txt

def generate_pdf(input,drawing,path):
    '''Generate a PDF with more refined controls'''

    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.graphics import renderPDF

    my_canvas = canvas.Canvas(path, pagesize=letter)
    my_canvas.setTitle("Netflix Activity Analysis")
    my_canvas.setAuthor("Jeremiah Adams")
    my_canvas.setSubject("Stats and graphs on the user\'s supplied Netflix activity")
    my_canvas.setKeywords("Netflix DataScience Statistics")
    my_canvas.setLineWidth(.3)
    my_canvas.setFont('Helvetica', 20)
    my_canvas.drawString(200,750,'Netflix Activity Analysis')
    my_canvas.setFont('Helvetica', 12)
    my_canvas.drawString(30,715,input[0])
    my_canvas.drawString(30,700,input[1])
    my_canvas.drawString(30,685,input[2])
    my_canvas.drawString(30,670,input[3])

    my_canvas.showPage()
    my_canvas.setPageSize((1120,780))
    renderPDF.draw(drawing,my_canvas,20,10)
    my_canvas.save()

def table_test(input,top5,out_chart):
    
    from reportlab.lib.pagesizes import letter,A2
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import  (
        SimpleDocTemplate, 
        Table, 
        Paragraph, 
        Spacer, 
        ListFlowable,
        NextPageTemplate,
        PageTemplate,
        PageBreak,
        TableStyle
    )
    import re
    import numpy as np

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(
        "test.pdf",
        pagesize=letter,
        )
    doc.addPageTemplates([
        PageTemplate(id='BigDraw', pagesize=(1120,780)),
    ])

    flowables = []
    title = Paragraph("Netflix Activity Analysis", styles['Title'])
    intro = Paragraph("From analyzing the provided data we can provide some facts.",
        styles['Normal'])
    totals = ListFlowable(
                [
                    Paragraph(input[0],styles['Bullet']),
                    Paragraph(input[1],styles['Bullet']),
                    Paragraph(input[2],styles['Bullet']),
                    Paragraph(input[3],styles['Bullet'])
                ],
                bulletType = 'bullet',
                bulletFontSize = 8,
                start='circle',
    )
    text = """Below, you can see the 5 most watched episodes and the
    number of views they received."""
    para = Paragraph(text, styles['Normal'])
    lnbr = Spacer(1,0.25*inch)
    flowables.append(title)
    flowables.append(intro)
    flowables.append(lnbr)
    flowables.append(totals)
    flowables.append(lnbr)
    flowables.append(para)
    flowables.append(lnbr)
    ranks = [str(x+1) for x in range(5)]
    titles = [re.split('  * ',top5[x])[0] for x in range(5)]
    views = [re.split('  * ',top5[x])[1] for x in range(5)]

    tbldat = [
            ranks,titles,views
            ]
    tbldat = np.transpose(tbldat) #transpose turns tbldat list into a np.array
    tbldat = tbldat.tolist() #so turn it back into a list
    tbldat.insert(0,['Rank','Title','Views']) #add column headers to the start
    tbl = Table(tbldat)
    flowables.append(tbl)
    flowables.append(NextPageTemplate('BigDraw'))
    flowables.append(PageBreak())
    flowables.append(drawing)
    doc.build(flowables)

if __name__ == "__main__":
    limited_dataframe = analyze()
    analysis = limited_analysis(limited_dataframe)
    top5 = top5_analysis(limited_dataframe)
    pdf_txt = generate_report(analysis)
    graph_plots = graphs.graphnalysis(limited_dataframe,'Anything Watched by Day (ex. Previews)')
    drawing=graphs.graph_result(graph_plots)
    #generate_pdf(pdf_txt,drawing,'NetflixActivityAnalysis.pdf')
    #table_test(pdf_txt,top5,drawing)
    #reports.pdf_report("test2.pdf",pdf_txt,drawing)
    reports.AnalyticsReport('NetflixActivityAnalysis.pdf','Netflix Activity Analysis',pdf_txt,top5,drawing)