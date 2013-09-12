from datetime import datetime,timedelta
from sqlalchemy import create_engine, MetaData, Table

import time

from apscheduler.scheduler import Scheduler

from config import SQLALCHEMY_DATABASE_URI
import tasks

def fire_job(request_id):
    print "Ticker firing: %s" % request_id
    tasks.validate_message(request_id)

if __name__ == '__main__':
    scheduler = Scheduler()
    scheduler.start()

    print "Scheduler started"
    db = create_engine(SQLALCHEMY_DATABASE_URI)
    metadata = MetaData(db)
    entries = Table('entries', metadata, autoload=True)

    time.sleep(2)

    while True:
        esel = entries.select(entries.c.status==True)
        cursor = esel.execute()

        for each in cursor:
            time_delta = each.fire_dt - datetime.now()

            if  time_delta > timedelta(0,0,0,0,1,0,0):
                print "Adding %s to queue." % each.request_id
                scheduler.add_date_job(fire_job, each.fire_dt, [each.request_id])
            else:
                print "Rejecting %s from queue." % each.request_id
            eup = entries.update(entries.c.id==each.id)
            eup.execute(status=False)

        time.sleep(10)
