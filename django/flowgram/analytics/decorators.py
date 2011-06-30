from django.utils.decorators import decorator_from_middleware

from middleware import AnalyticsMiddleware

analytics = decorator_from_middleware(AnalyticsMiddleware)