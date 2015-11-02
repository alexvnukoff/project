import logging
logger = logging.getLogger('django.request')



def log_exception(log_name="Exception in Task"):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(log_name,  exc_info=True)
        return wrapper
    return decorator










