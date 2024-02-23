from rest_framework import throttling

class UnAuthenticatedRateThrottle(throttling.AnonRateThrottle):
    
    scope = "un_authenticated"
    
    def allow_request(self, request, view):
        if request.method == "POST":
            return super().allow_request(request, view)
        return True


class AuthenticatedRateThrottle(throttling.AnonRateThrottle):
    
    scope = "authenticated"
    
    def allow_request(self, request, view):
        if request.method == "POST":
            return super().allow_request(request, view)
        return True
