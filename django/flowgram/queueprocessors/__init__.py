from datetime import datetime, timedelta

from flowgram.core import models

def get_tasks_to_process(model_class, retry_time):
    tasksUnprocessed = model_class.objects.filter(status_code=models.StatusCode.UNPROCESSED)
    tasksProcessing = model_class.objects.filter(status_code=models.StatusCode.PROCESSING)

    tasksTimedOut = tasksProcessing.filter(started_at__lte=datetime.now() - \
                                               timedelta(seconds=retry_time))
    
    return (tasksUnprocessed | tasksTimedOut).order_by('attempts', 'id')
