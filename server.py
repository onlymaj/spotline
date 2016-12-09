
import glob
import myConnector
from bs4 import BeautifulSoup
import base64
from Crypto import Random
from Crypto.Cipher import AES
import json,mymail
import config
import MySQLdb


# get all clients file in order to get their connection information
clients = glob.glob('clients/*.xml')


def decrypt( enc ):
    BS = 16 # block size
    pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) #pad for encryption
    unpad = lambda s : s[0:-ord(s[-1])]
    key = 'mysecretpassword'
    enc = base64.b64decode(enc)
    iv = enc[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv )
    return unpad(cipher.decrypt( enc[16:] ))


conn = MySQLdb.connect(host= config.SERVER,
                  user=config.USERNAME,
                  passwd=config.PASSWORD,
                  db=config.DATABASE)
x = conn.cursor()

#get ech client to have the data
for client in clients:
    with open(client) as f:
        cfile = BeautifulSoup(f.read(),'html5lib')
        cip =  str(cfile.client['ip'])                          # Client ip
        cpt =  str(cfile.client['port'])                        # Client Port
        cun =  str(cfile.client['username'])                    # Client username
        cpw =  str(cfile.client['password'])                    # Client password
        cem =  str(cfile.client['mail'])                        # Client mail
        cml =  cfile.client.find("alert", {"type":"memory"})['limit'] # Client Memory Limit
        ccp =  cfile.client.find("alert", {"type":"cpu"})['limit']    # Client CPU Limit

        # fetch data from client encrypted
        print 'Starting fetching data from '+cip
        res = myConnector.connectToClient(cip , cpt, cun , cpw , cem, cml , ccp)

        #decrypt client's data
        decrypted = decrypt(res)

        # rawval contains following data:
        #   0: Client's Memory Limit in percent
        #   1: Client's CPU limit in percent
        #   2: Client's Server Up Time
        #   3: Client's Server Time
        #   4: Client's Server Security Logs

        rawval = json.loads(decrypted)


        try:
           tsql =  """INSERT INTO `crossover`.`audit` ( `ip`, `memory`, `cpu`, `uptime`, `sdate`, `cdate`, `logs`) VALUES ( %s, '%s', '%s', '%s', %s, NOW(), %s)"""
           x.execute(tsql,(cip,rawval[0],rawval[1],round(rawval[2],2),rawval[3], ' '.join(rawval[4])))
           conn.commit()
           print "Data inserted to DB successfylly !"
        except MySQLdb.Error, e:
            try:
                print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
            except IndexError:
                print "MySQL Error: %s" % str(e)

        conn.close()




        #
        # Send Client's server logs to provided email
        #   mymail.sendMail(FROM,TO,SUBJ,CONT,SERVER)
        #
        mymail.sendMail(cem,'Server Logs',' '.join(rawval[4]))

        #
        # Send Client's server alert to provided email when the Memory limit exceeded
        #   mymail.sendMail(FROM,TO,SUBJ,CONT,SERVER)
        #
        if  int(rawval[0]) >= int(cml[:-1]):
            msg = 'MEMORY LIMIT EXCEDED !'
            mymail.sendMail(cem,'SERVER ALERT !!!',msg)

        #
        # Send Client's server alert to provided email when the CPU limit exceeded
        #   mymail.sendMail(FROM,TO,SUBJ,CONT,SERVER)
        #
        if  int(rawval[1]) >= int(ccp[:-1]):
            msg = 'CPU LIMIT EXCEDED !'
            mymail.sendMail(cem,'SERVER ALERT !!!',msg)

