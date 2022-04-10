import matplotlib.pyplot as plt

def graphnalysis(data,graph_title):
    '''Graph provided dataset by day and output to PDF'''
    graph_data = data['weekday'].value_counts()
    graph_data = graph_data.sort_index()
    graph_plots = graph_data.plot(kind='bar', figsize=(10,5), title=graph_title)
    return graph_plots
    
def graph_result(graph_plots):
    graph_plots.plot()
    plt.tight_layout()
    plt.show()
    plt.close()