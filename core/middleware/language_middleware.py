from django.http import HttpRequest

from users.models import UserIP



def choose_lang(request):
    """
    this function checking two things:
    1] if there is a language header 
    2] and if there is a record with the same IP Address
    
    if not 1] and 2] => return language from DB
    if 1] and 2] => update language from DB, then return it
    if 1] and not 2] => create UserIP model record, then return language
    """
    
    IP_Address = request.META.get("REMOTE_ADDR")
    
    language_code = request.headers.get("Accept-Language") or "en"
    if language_code:
        language_code = language_code[:2]
        
    obj = UserIP.objects.filter(ip_address=IP_Address)
    if obj.exists():
        obj = obj.first()
        if language_code and language_code != obj.language_code:
            obj.language_code = language_code
            obj.save()
    
    elif not obj.exists():
        obj = UserIP.objects.create(
            ip_address=IP_Address
            , language_code=language_code)
    
    return obj.language_code


def language(get_response):
    def middleware(request: HttpRequest):
        request.META["Accept-Language"] = choose_lang(request)
        reponse = get_response(request)
        return reponse
    
    return middleware
