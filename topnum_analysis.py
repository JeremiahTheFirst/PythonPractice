def controller(*args):
    '''Identify and control what sets of stats are derived
    i.e. choice=top_x_controller('all',5) to set choice so that
    choice[0] return the setting and choice[1] returns the cnt'''
    choices = []
    for arg in args:
        choices.append(arg)
    return choices

def runner(choices):
    '''Take output of controller and feed it into analysis to
    produce one single output variable'''
    constants = []
    if 'all' in choices:
        choice = 'all'
        title_type = 'EP_title'
        y = choices.index(choice) + 1
        cnt = choices[y]
        selection = (choice,title_type,cnt)
        constants.append(selection)
    if 'tv' in choices:
        title_type = 'EP_name'
        y = choices.index('tv') + 1
        cnt = choices[y]
        selection = ('tv',title_type,cnt)
        constants.append(selection)
    if 'mov' in choices:
        title_type = 'EP_name'
        y = choices.index('mov') + 1
        selection = ('mov',title_type,cnt,False)
        constants.append(selection)
    if 'spec' in choices:
        title_type = 'SPEC_name'
        y = choices.index('spec') + 1
        selection = ('spec',title_type,cnt)
        constants.append(selection)     
    return constants

def build_selection(choices,choice,title_type):
    y = choices.index(choice) + 1
    cnt = choices[y]
    if choice != 'mov':
        selection = (choice,title_type,cnt)
    else:
        selection = (choice,title_type,cnt,False)
    return selection

def analysis(expanded_dataframe,title_type,content_type,cnt,invert=True):
    '''Identify the top 5 watched items from the analyzed file'''
    
    if not invert:
        top_x = expanded_dataframe[expanded_dataframe[title_type].isnull()]
    else:
        top_x = expanded_dataframe[~expanded_dataframe[title_type].isnull()]
    top_x = top_x['EP_title'].value_counts().nlargest(cnt)
    num_x = top_x.count()
    top_x = top_x.to_string(name=False,dtype=False)
    top_x = top_x.split('\n')
    content = "Here are the top %s %s you watched and the number of views for each"\
        " item" % (num_x,content_type)
    """for x in range(num_x):
        print("%d. %s" % (x+1,top_x[x]))"""
    return top_x,content