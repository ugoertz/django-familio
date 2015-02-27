import json
from django.contrib.auth import get_user_model
from dajaxice.decorators import dajaxice_register


@dajaxice_register(method="GET")
def getuser(request, query):
    User = get_user_model()

    qs = User.objects.filter(username__icontains=query) |\
        User.objects.filter(first_name__icontains=query) |\
        User.objects.filter(last_name__icontains=query)

    result = [
        {'username': u.username,
         'label': '%s (%s)' % (u.get_full_name(), u.username)}
        for u in qs.distinct()]
    return json.dumps(result)
