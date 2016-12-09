import psutil,datetime,time
import os          # for running command
import json        # to serialize data
import base64
from Crypto import Random
from Crypto.Cipher import AES





def encrypt( raw ):
    BS = 16 # block size
    pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) #pad for encryption
    unpad = lambda s : s[0:-ord(s[-1])]
    key = 'mysecretpassword'
    raw = pad(raw)
    iv = Random.new().read( AES.block_size )
    cipher = AES.new( key, AES.MODE_CBC, iv )
    return base64.b64encode( iv + cipher.encrypt( raw ) )





def ReadLogs(computer, logType="Security", dumpEachRecord = 1):

    # read the entire log back.
    h=win32evtlog.OpenEventLog(computer, logType)
    logs = []
    num=0
    while 1:
        objects = win32evtlog.ReadEventLog(h, win32evtlog.EVENTLOG_BACKWARDS_READ|win32evtlog.EVENTLOG_SEQUENTIAL_READ, 0)
        if not objects:
            break
        for object in objects:

            msg = sidDesc = user = domain = typ =  ltime = lsourceName  = ''

            msg = win32evtlogutil.SafeFormatMessage(object, logType)
            if object.Sid is not None:
                try:
                    domain, user, typ = win32security.LookupAccountSid(computer, object.Sid)
                except win32security.error:
                    sidDesc = str(object.Sid)


            ltime = object.TimeGenerated.Format()
            lsourceName = object.SourceName

            logs.append({'sid':sidDesc,'msg':msg,'user':user,'domain':domain,'time':ltime,'srouce':lsourceName})
    win32evtlog.CloseEventLog(h)
    return logs




memoryp  = psutil.virtual_memory().percent #client memory usage in percent
cpup     = psutil.cpu_percent()            #client cpu usage in percent
btime    = psutil.boot_time()              #client boot time

# calculate uptime from client boot time
uptime   = time.time() - btime
logs = []



if psutil.WINDOWS:
    import win32evtlog
    import win32api
    import win32con
    import win32security # To translate NT Sids to account names.
    import win32evtlogutil
    #You can define a specific computer or put it None to get All Computers event logs
    computer = None
    logs = ReadLogs(computer, "Security")
    #Clear all Security Logs in order to get unique Security Logs always
    os.system("wevtutil.exe cl Security")

outlist = [memoryp,cpup,uptime,datetime.datetime.now().strftime("%Y-%m-%d %H:%I:%S"),logs]
encrypted = encrypt(json.dumps(outlist))
print encrypted
