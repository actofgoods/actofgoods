import pytz
from django.utils import timezone
import requests
from ipware.ip import get_real_ip
from timezonefinder import TimezoneFinder

class UserTimezoneMiddleware(object):
    """ Middleware to check user timezone. """
    def process_request(self, request):
        user_time_zone = request.session.get('user_time_zone', None)
        user_time_zone = None
        try:
            if user_time_zone is None:
                ip = get_real_ip(request)
                if ip is None:
                    tf = TimezoneFinder()
                    print
                    point = (request.user.userdata.address.longditude,request.user.userdata.address.latitude)
                    user_time_zone = tf.timezone_at(*point)
                    request.session['user_time_zone'] = user_time_zone
                else :
                    freegeoip_response = requests.get('http://freegeoip.net/json/{0}'.format())
                    freegeoip_response_json = freegeoip_response.json()
                    user_time_zone = freegeoip_response_json['time_zone']
                    if user_time_zone:
                        request.session['user_time_zone'] = user_time_zone
            timezone.activate(pytz.timezone(user_time_zone))
        except:
            pass
        return None
