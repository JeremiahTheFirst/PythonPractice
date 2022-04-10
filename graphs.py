import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import datetime

def graphnalysis(data,graph_title):
    '''Graph provided dataset by day and output to PDF'''
    graph_data = data['weekday'].value_counts()
    graph_data = graph_data.sort_index()
    graph_plots = graph_data.plot(kind='bar', figsize=(11.69,8.27), title=graph_title)
    return graph_plots
    
def graph_result(rpt_txt,graph_plots):
    with PdfPages('NetflixActivityAnalysis.pdf') as pdf:
        first_page = plt.figure(figsize=(11.69,8.27))
        first_page.clf()
        rpt_title = 'Netflix Activity Analysis'
        first_page.text(0.5,.9,rpt_title,fontsize=24, ha='center')
        first_page.text(0.1,.75,rpt_txt)
        pdf.savefig()
        plt.close()
        
        graph_plots.plot()
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