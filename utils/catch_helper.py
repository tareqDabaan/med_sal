def catch(params: str) -> list[int]:
    new_params = []
    for param in params:
        try:
            new_param = int(param)
            new_params.append(new_param)
        except:
            pass
    
    return new_params
