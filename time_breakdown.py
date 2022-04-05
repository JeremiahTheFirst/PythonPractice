def split(time):
    '''Takes provided timedelta and breaks it into days, hours, minutes, and seconds'''
    time = time.seconds
    days, remainder = divmod(time,86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    #print ('{} days {:02}:{:02}:{:02}'.format(int(days), int(hours), int(minutes), int(seconds)))
    output = '{} days {:02}:{:02}:{:02}'.format(int(days), int(hours), int(minutes), int(seconds))
    return output