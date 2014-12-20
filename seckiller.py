import string
import socket
import urllib2
import urllib
import cookielib
import re
import ConfigParser

CONFIGFILE='./killer.cfg'

TARGET_SECTION='target'
URI_OPTION='uri'
URICHUZHENT_OPTION='urichuzhent'
URICHUZHEN_OPTION='urichuzhen'
COOKIE_OPTION='cookie'
REFER_OPTION='referer'
USERAGENT_OPTION='user-agent'
HOST_OPTION='host'
ACCEPT_OPTION='accept'
ACCEPTLANG_OPTION='accept-language'
ACCEPTENCODING_OPTION='accept-encoding'
CONNECTION_OPTION='connection'
CACHE_CONTROL_OPTION='cache-control'

USER_SECTION='user'
IDNO_OPTION='IDNO'
NAME_OPTION='name'

parser = ConfigParser.ConfigParser()
parser.read( CONFIGFILE )
uri=parser.get( TARGET_SECTION , URI_OPTION );
chuzhenwildcard=parser.get( TARGET_SECTION , URICHUZHEN_OPTION );
cookie=parser.get( TARGET_SECTION , COOKIE_OPTION );
referer=parser.get( TARGET_SECTION , REFER_OPTION );
user_agent=parser.get( TARGET_SECTION , USERAGENT_OPTION );
accept_encoding=parser.get( TARGET_SECTION , ACCEPTENCODING_OPTION );
accept_language=parser.get( TARGET_SECTION , ACCEPTLANG_OPTION );
host=parser.get( TARGET_SECTION , HOST_OPTION );
accept=parser.get( TARGET_SECTION , ACCEPT_OPTION );
connection=parser.get( TARGET_SECTION , CONNECTION_OPTION );
cache_control=parser.get( TARGET_SECTION , CACHE_CONTROL_OPTION);

socket.setdefaulttimeout(10)
global opener
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

def unzipresponse(f): # f is returned object by urlopen
    headers=f.info()
    rawdata = f.read()
    if ('Content-Encoding' in headers and headers['Content-Encoding']) or \
    ('content-encoding' in headers and headers['content-encoding']):
        import gzip
        import StringIO
        data = StringIO.StringIO(rawdata)
        gz = gzip.GzipFile(fileobj=data)
        rawdata = gz.read()
        gz.close()
    return rawdata

def queryticket():  
    opener.addheaders= [
    (COOKIE_OPTION,cookie),
    (REFER_OPTION,referer),
    (USERAGENT_OPTION,user_agent),
    (HOST_OPTION,host),
    (ACCEPT_OPTION,accept),
    (ACCEPTLANG_OPTION,accept_language),
    (ACCEPTENCODING_OPTION,accept_encoding),
    (CACHE_CONTROL_OPTION,cache_control),
    ]

    rethtml=opener.open(uri)
    rawdata=unzipresponse(rethtml)
    return rawdata

def querychuzhen(urichuzhen ):
    opener.addheaders= [
    (COOKIE_OPTION,cookie),
    (REFER_OPTION,uri),
    (USERAGENT_OPTION,user_agent),
    (HOST_OPTION,host),
    (ACCEPT_OPTION,accept),
    (ACCEPTLANG_OPTION,accept_language),
    (ACCEPTENCODING_OPTION,accept_encoding),
    (CACHE_CONTROL_OPTION,cache_control),
    ]
    
    rethtml=opener.open( urichuzhen )
    rawdata=unzipresponse(rethtml)
    opener.close()
    return rawdata


def registpage(reguri):
    regurl=r'http://'+host + '/comm' + reguri
    referurl=regurl
    opener.addheaders= [
    (COOKIE_OPTION,cookie),
    (REFER_OPTION,uri),
    (USERAGENT_OPTION,user_agent),
    (HOST_OPTION,host),
    (ACCEPT_OPTION,accept),
    (ACCEPTLANG_OPTION,accept_language),
    (ACCEPTENCODING_OPTION,accept_encoding),
#    CONNECTION_OPTION:connection,
    (CACHE_CONTROL_OPTION,cache_control),
    ]
    rethtml=opener.open( regurl )
    rawdata=unzipresponse(rethtml)
#    print rawdata
    regpage = rawdata

    strref=r'\?hpid=(.*)&ksid=(.*)&datid=(.*)'
    pattern=re.compile(strref)
    ids=pattern.findall(reguri)
    if not ids:
        print 'no IDS'
        return
    print ids
    strref=r'\.get\("\.\./shortmsg/dx_code\.php\?hpid="\+hpid\+"(.*)"\+"&ksid="\+ksid\+"&datid="\+datid\+"&jiuz="\+jiuz\+"&ybkh="\+ybkh\+"&baoxiao="\+baoxiao'
    pattern=re.compile(strref)
    mobject=pattern.findall(rawdata)
    dxurl=r'http://'+host + '/comm' + r'/shortmsg/dx_code.php?hpid=' + ''.join(ids[0][0]) + mobject[0] +'&ksid=' + ''.join(ids[0][1])+'&datid=' + ''.join(ids[0][2]) + '&jiuz=' + "&ybkh=320724198602250075"+ '&baoxiao=1'
    print regurl

    opener.addheaders= [
    (COOKIE_OPTION,cookie),
    (REFER_OPTION,regurl),
    (USERAGENT_OPTION,user_agent),
    (HOST_OPTION,host),
    (ACCEPT_OPTION,'*/*'),
    ('x-requested-with','XMLHttpRequest'),
    (ACCEPTLANG_OPTION,accept_language),
    (ACCEPTENCODING_OPTION,accept_encoding),
    (CACHE_CONTROL_OPTION,cache_control),
    ]

    rethtml = opener.open(dxurl)
    rawdata=unzipresponse(rethtml)
    print rawdata.decode('gbk',"ignore")

    finalsubmit(referurl, regpage , ''.join(ids[0][0]) ,  ''.join(ids[0][1]) ,  ''.join(ids[0][2]))
    opener.close()
    return rawdata

def finalsubmit(referurl,regpage , hpid , ksid , datid ):
    regurl=r'http://'+host + '/comm/beiyi3/ghdown.php'
    
    regex = r'<input[^>]*name="?([A-Za-z0-9]*)"?[^>]*\svalue="?([A-Za-z0-9]*)"?' #(?:) not capture group
    pattern = re.compile(regex)
    rst=pattern.findall(regpage)
    params={}
    if not rst:
        print 'no match'
        return
    
    print rst
    for ival in rst:
        params[ival[0]] = ival[1]
    params['hpid'] = hpid
    params['ksid'] = ksid
    params['datid'] = datid
    params['baoxiao'] = '1'
    params['jiuz'] = ''
    params['ybkh'] = '320724198602250075'
    dxcode=raw_input("dxcode:")
    params['dxcode'] = dxcode
    req = urllib2.Request(regurl , urllib.urlencode(params) )
    
    req.add_header(COOKIE_OPTION,cookie)
    req.add_header(REFER_OPTION,referurl),
    req.add_header(USERAGENT_OPTION,user_agent),
    req.add_header(HOST_OPTION,host),
    req.add_header(ACCEPT_OPTION,accept)
    req.add_header(ACCEPTLANG_OPTION,accept_language),
    req.add_header(ACCEPTENCODING_OPTION,accept_encoding),
    req.add_header(CACHE_CONTROL_OPTION,cache_control),
     
#    print params
    rethtml=urllib2.urlopen(req)
    rawdata=unzipresponse(rethtml)
    print rawdata.decode('gbk',"ignore")
    opener.close()
    return rawdata



def startkilling(subday):
    patterprefix='date1=2014-10-'
    patter=re.compile(patterprefix + "(?P<day>\d{2})")
    cururi=patter.sub(patterprefix + subday, chuzhenwildcard)
    rethtml=querychuzhen( cururi)

    strre='''<td>(?P<price>.*)</td>\n\s*<td>.*</td>\n\s*<td>.*</td><td>.*</td><td><a\shref='\.(?P<ghpage>.*)'\sonclick='.*'''
    pattern=re.compile(strre)
    mobject=pattern.findall(rethtml)
    if not mobject:
        print 'no chuzhen'
        return
    for entry in mobject:
        print entry
        price=string.atof(entry[0])
        if price > 5:
            registpage(entry[1])
            return
    registpage(mobject[0][1])


import time
if __name__ == "__main__":
    while 1:
        try:
            cj = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            for day in range(22,28):
                strday='%d' % day
                startkilling(strday)
                opener.close()
                time.sleep(0.1)
                print 'finish one day'
        except KeyboardInterrupt:
            print 'quit'
            break
        except:
            print 'exception'
            pass
