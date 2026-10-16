from slowapi import Limiter
from fastapi import Request
from slowapi.util import get_remote_address


def get_user_id_or_ip_key(request: Request):
    if hasattr(request.state, "user") and request.state.user:
        return str(request.state.user.id)
    return get_remote_address(request)


limiter_by_ip_address = Limiter(key_func=get_remote_address)
limiter_by_user_id = Limiter(key_func=get_user_id_or_ip_key)