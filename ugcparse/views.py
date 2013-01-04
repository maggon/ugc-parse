import simplejson as json
import urllib, ParsePy
import pprint

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext

YELP_URL = 'http://api.yelp.com/business_review_search?limit=5&term=Indian&location=Los%20Angeles,%20CA&ywsid=-plm-0Rh05_drahY7eUCXg'

# Parse Keys - Should be stored in local_settings.py
ParsePy.APPLICATION_ID = settings.PARSE_APPLICATION_ID
ParsePy.MASTER_KEY = settings.PARSE_MASTER_KEY


def getParseBizObj(bid, user):
    query = ParsePy.ParseQuery("BizUgc")
    query = query.eq("bid", bid).eq("uid", user)
    bizes = query.fetch()
    if len(bizes) <= 0:
        return None
    return bizes[0]

def getBizCount(bid, bh=True):
    query = ParsePy.ParseQuery("BizUgc")
    query = query.eq("bid", bid).eq("bh", True)
    bizes = query.fetch()
    return len(bizes)

def home(request, template_name='index.html'):

    user = 'sameer'
    if request.GET.get('user'):
        user = request.GET['user']
    
    if request.GET.get('bh'):
        bid = request.GET['bh']
	# Need to first check if already present
	bizugc = getParseBizObj(bid, user)
	if not bizugc:
            bizugc = ParsePy.ParseObject("BizUgc")
	    bizugc.bid = bid
	    bizugc.uid = user
	    bizugc.bh = True
	else:
	    bizugc.bh = True
	bizugc.save()

    
    businesses = json.load(urllib.urlopen(YELP_URL))

    # Surgically modify the objects to return required data to render
    bizes = businesses['businesses']
    for biz in bizes:
	bizugc = getParseBizObj(biz['id'], user)
	if bizugc:
	    biz['p_bh'] = bizugc.bh
        biz['p_bh_c'] = getBizCount(biz['id'])

    return render_to_response(template_name, {'user': user, 'businesses': businesses['businesses']}, context_instance=RequestContext(request))
