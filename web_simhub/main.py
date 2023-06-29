from misc import USBNET,Power
import usys
import ujson
from usr.sys import Task,run,sleep
from usr.WebSrv import WebSrv
import modem
import net
import checkNet
import sms
import utime
import dataCall
from usr.logging import get_logger
_log = get_logger(__name__)

wbsock = None
def getDataPlan(operator):
    yield from sleep(30)
    wbsock.SendText(ujson.dumps({"used":"50G","balance":"10G"}))
    srv.Stop()

@WebSrv.route('/sim-info')
def simHub(httpClient, httpResponse) :
    imei = modem.getDevImei()
    stagecode, subcode = checkNet.wait_network_connected(1)
    signal_frag = 32 // 5
    signals = {
        0:' <path {weak}  d="M0 727.578947l188.631579 0 0 296.421053-188.631579 0 0-296.421053Z"></path>',
        1:' <path {weak} d="M269.473684 565.894737l188.631579 0 0 458.105263-188.631579 0 0-458.105263Z"></path>',
        2:' <path {weak} d="M565.894737 377.263158l161.684211 0 0 646.736842-161.684211 0 0-646.736842Z"></path>',
        3:' <path {weak} d="M835.368421 188.631579l188.631579 0 0 835.368421-188.631579 0 0-835.368421Z"></path>',
        4:' <path  {weak}  d="M1104.842105 0l188.631579 0 0 1024-188.631579 0 0-1024Z"></path>',
    }
    signal_flag = ""
    if stagecode == 3 and subcode == 1:
        net_status = '<span style="color: rgb(52, 195, 136);">online</span>'
        signal = net.csqQueryPoll()

        strength_nums =  signal // signal_frag
        weak_nums = 5 - strength_nums
        signal_flag = ""
        for _ in range(strength_nums):
            signal_flag = signal_flag + signals[_].format(weak="")
        for _ in range(weak_nums):
            signal_flag = signal_flag + signals[_+ strength_nums].format(weak='fill="#e6e6e6"')
        operator = net.operatorName()
        if operator[1] == "UNICOM":
            chOperator = "中国联通"
        elif operator[1] == "CMCC":
            chOperator = "中国移动"
        else:
            chOperator = "中国电信"
        #Task(getDataPlan,cb_arg=(chOperator,)).start()
    else:
        net_status = '<span style="color: rgb(52, 195, 136);">offline</span>'
        chOperator = "未知"
        for _ in range(5):
            signal_flag = signal_flag + vars["signal_flag_"+str(_)].format(weak='fill="#e6e6e6"')
    httpResponse.WriteResponseJSON({"net_status":net_status,"carrier":chOperator,"total":"--","balance":"--","deviceId":imei,"signal":signal_flag})


#下面是事例

@WebSrv.route('/json')
def json(httpClient, httpResponse) :
    httpResponse.WriteResponseJSON({1:2,"test":5})


@WebSrv.route('/edit/<index>')  # <IP>/edit/123           ->   args['index']=123
@WebSrv.route('/edit/<index>/abc/<foo>')  # <IP>/edit/123/abc/bar   ->   args['index']=123  args['foo']='bar'
@WebSrv.route('/edit')  # <IP>/edit               ->   args={}
def _httpHandlerEditWithArgs(httpClient, httpResponse, args={}):
    content = """\
	<!DOCTYPE html>
	<html lang=en>
        <head>
        	<meta charset="UTF-8" />
            <title>TEST EDIT</title>
        </head>
        <body>
	"""
    content += "<h1>EDIT item with {} variable arguments</h1>" \
        .format(len(args))

    if 'index' in args:
        content += "<p>index = {}</p>".format(args['index'])

    if 'foo' in args:
        content += "<p>foo = {}</p>".format(args['foo'])

    content += """
        </body>
    </html>
	"""
    httpResponse.WriteResponseOk(headers= None,
                                  contentType= "text/html",
                                  contentCharset= "UTF-8",
                                  content 		= content )



@WebSrv.route('/test', 'POST')
def _httpHandlerTestPost(httpClient, httpResponse) :
	formData  = httpClient.ReadRequestPostedFormData()
	firstname = formData["firstname"]
	lastname  = formData["lastname"]
	content   = """\
	<!DOCTYPE html>
	<html lang=en>
		<head>
			<meta charset="UTF-8" />
            <title>TEST POST</title>
        </head>
        <body>
            <h1>TEST POST</h1>
            Firstname = %s<br />
            Lastname = %s<br />
        </body>
    </html>
	""" % ( WebSrv.HTMLEscape(firstname),
		    WebSrv.HTMLEscape(lastname) )
	httpResponse.WriteResponseOk( headers		 = None,
								  contentType	 = "text/html",
								  contentCharset = "UTF-8",
                                  content 		 = content )



def _acceptWebSocketCallback(webSocket, httpClient) :

    global wbsock
    wbsock = webSocket
    print("WS ACCEPT")
    webSocket.RecvTextCallback   = _recvTextCallback
    webSocket.RecvBinaryCallback = _recvBinaryCallback
    webSocket.ClosedCallback 	 = _closedCallback

def _recvTextCallback(webSocket, msg) :
	print("WS RECV TEXT : %s" % msg)
	webSocket.SendText("Reply for %s" % msg)

def _recvBinaryCallback(webSocket, data) :
	print("WS RECV DATA : %s" % data)

def _closedCallback(webSocket):
    print("WS CLOSED")
    global wbsock
    wbsock = None


def Startup():
    if USBNET.get_worktype() != 1:
        _log.info('Set ECM mode and power restart.')
        USBNET.setMAC(b'\xac\x4b\xb3\xb9\xeb\xe6')
        USBNET.set_worktype(USBNET.Type_ECM)
        Power.powerRestart()
        return None
    while True:
        info = dataCall.getInfo(1, 0)
        if info[2][2] != '0.0.0.0':
            _log.info('data:',info)
            break
        _log.info('Wait for data calling')
        utime.sleep(2)
    counter = 10
    USBNET.open()
    _log.info('USBNET open successed.')
    srv = WebSrv(ip='0.0.0.0',port=80,templatePath="/usr/www/", staticPath="/usr/www/", staticPrefix="/static/")
    srv.MaxWebSocketRecvLen     = 256
    srv.WebSocketThreaded       = True
    srv.AcceptWebSocketCallback = _acceptWebSocketCallback
    srv.Start(threaded=True)
    run()

#启动程序
Startup()