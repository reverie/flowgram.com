#!/usr/local/bin/python

import datetime
from flowgram.core.models import AddPageRequest, GetCssRequest, PptImportRequest, SendEmailRequest, ImportMediaRequest, DashboardServiceRecord
from flowgram.queueprocessors.sendemailrequestprocessor import add_to_mail_queue
from flowgram.core import log

#check every 10 mins
CHECK_GAP = 600

current_time = datetime.datetime.now()
log.debug('servicechecker.py starts at %s' % current_time)

old_req_unprocessed_addpagerequest = AddPageRequest.objects.filter(timestamp__gte=current_time - datetime.timedelta(seconds=CHECK_GAP*2), 
                                                                   timestamp__lte=current_time - datetime.timedelta(seconds=CHECK_GAP), 
                                                                   status_code=0)
#log.debug('AddPageRequest %s' % old_req_unprocessed_addpagerequest)

old_req_unprocessed_getcssrequest = GetCssRequest.objects.filter(timestamp__gte=current_time - datetime.timedelta(seconds=CHECK_GAP*2), 
                                                                     timestamp__lte=current_time - datetime.timedelta(seconds=CHECK_GAP), 
                                                                     status_code=0)
#log.debug('GetCssRequest %s' % old_req_unprocessed_getcssrequest)

old_req_unprocessed_pptimportrequest = PptImportRequest.objects.filter(timestamp__gte=current_time - datetime.timedelta(seconds=CHECK_GAP*2), 
                                                                     timestamp__lte=current_time - datetime.timedelta(seconds=CHECK_GAP), 
                                                                     status_code=0)
#log.debug('PptImportRequest %s' % old_req_unprocessed_pptimportrequest)

old_req_unprocessed_sendemailrequest = SendEmailRequest.objects.filter(timestamp__gte=current_time - datetime.timedelta(seconds=CHECK_GAP*2), 
                                                                     timestamp__lte=current_time - datetime.timedelta(seconds=CHECK_GAP), 
                                                                     status_code=0)
#log.debug('SendEmailRequest %s' % old_req_unprocessed_sendemailrequest)

old_req_unprocessed_importmediarequest = ImportMediaRequest.objects.filter(timestamp__gte=current_time - datetime.timedelta(seconds=CHECK_GAP*2), 
                                                                     timestamp__lte=current_time - datetime.timedelta(seconds=CHECK_GAP), 
                                                                     status_code=0)
#log.debug('ImportMediaRequest %s' % old_req_unprocessed_importmediarequest)



def report_to_dashboard(serviceType, oldReqUnprocessed):
    try:
        record = DashboardServiceRecord.objects.get(service_type=serviceType)
    except DashboardServiceRecord.DoesNotExist:
        log.debug('create a new entry in dashboard service record table %s' % serviceType)
        record = DashboardServiceRecord.objects.create(service_type=serviceType,
                                                       service_status=True,
                                                       latest_checkedtime=current_time)
        
    if oldReqUnprocessed:
        log.debug('there are unprocessed jobs pending in %s' % serviceType)
        error_record = record
        error_record.service_status = False
        error_record.latest_checkedtime = current_time
        error_record.save()
        
        try:
            add_to_mail_queue(
                          'mailman@flowgram.com',
                          'suli@flowgram.com',
                          '[STATUS UPDATE] %s -Slow/Not Working' % serviceType,
                          'You need to check db table of: %s . Service found Slow/Not Working at %s.' % (serviceType, error_record.latest_checkedtime))
        except Exception, e:
            log.debug(e)
            log.debug('email service is down')
    


report_to_dashboard('add_page_request', old_req_unprocessed_addpagerequest)
report_to_dashboard('get_css_request', old_req_unprocessed_getcssrequest)
report_to_dashboard('ppt_import_request', old_req_unprocessed_pptimportrequest)
report_to_dashboard('send_email_request', old_req_unprocessed_sendemailrequest)
report_to_dashboard('import_media_request', old_req_unprocessed_importmediarequest)
    


