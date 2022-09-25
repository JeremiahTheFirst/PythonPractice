import matplotlib.pyplot as plt

def graphnalysis(data,graph_title):
    '''Graph provided dataset by day and output to PDF'''
    graph_data = data['weekday'].value_counts()
    graph_data = graph_data.sort_index()
    graph_plots = graph_data.plot(kind='bar', figsize=(11.69,8.27), title=graph_title)
    return graph_plots
    
def graph_result(graph_plots):
    from io import BytesIO
    from svglib.svglib import svg2rlg
        
    imgdata = BytesIO()
    graph_plots.plot()
    plt.tight_layout()
    plt.savefig(imgdata,format='svg')
    imgdata.seek(0)
    drawing=svg2rlg(imgdata)
    #plt.show()

    return drawing