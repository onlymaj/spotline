import paramiko

def connectToClient( host, port, un , pw, email , cpl , mml ):

    # Log paramiko events on a file
    paramiko.util.log_to_file('/tmp/connectToClient.log')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect( host,port=int(port), username=un, password=pw)
    except paramiko.SSHException,e:
        print "SSH Connection Error",e
        return False
    else:
        sftp = ssh.open_sftp()
        sftp.chdir("/tmp/")
        remotepath  = '/tmp/cscript.py'
        localpath = 'clientScript.py'
        # Uploading the client Script to the remote client server , It overrides if file exists alreay
        sftp.put(localpath, remotepath)
        #command for running script in remote client
        command = 'python ' + remotepath
        print 'running command at '+ un + '@' + host+':'+port +' #' + command

        try:
            ( stdin, stdout, stderr ) = ssh.exec_command(command)
        except paramiko.SSHException,e:
            print 'failed to run command at '+ un + '@' + host+':'+port +' #' + command
            return False
        else:
            errs = ''
            outs = ''

            for err in stderr.readlines():
                errs += err
            for out in stdout.readlines():
                outs += out
            command = 'rm -f ' + remotepath
            print 'running command at '+ un + '@' + host+':'+port +' #' + command
            try:
                ( stdin, stdout, stderr ) = ssh.exec_command(command)
            except paramiko.SSHException,e:
                print 'failed to run command at '+ un + '@' + host+':'+port +' #' + command
                return False


            if errs != '':
                return errs
            else:
                return outs

        ssh.close()

    return
