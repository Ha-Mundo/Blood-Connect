import datetime


#print(datetime.now())

donation_day = datetime.date.today()

#print(donation_day)

threshold = datetime.timedelta(days=1)

#print(threshold.days)

#print(donation_day + threshold)

def threshold_donation(donation_day):
    #donation_day = datetime.datetime.now()
    threshold = datetime.timedelta(days=1)
    till_day =  donation_day + threshold
    #print(till_day)
    return till_day

def threshold_request(donation_day):
    #donation_day = datetime.datetime.now()
    threshold = datetime.timedelta(days=1)
    till_day =  donation_day + threshold
    #print(till_day)
    return till_day

condition = threshold_donation(donation_day)     

def timer(condition, donation_day):   
    if condition <= donation_day:
       return True
    else:
        return False

#t = timer(condition, donation_day)
#print(t)


