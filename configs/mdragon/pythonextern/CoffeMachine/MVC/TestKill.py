import subprocess , time
from copy import deepcopy
import re
INIFileDataTemplate = {
    "parameters":[],
    "sections":{}
    }

cmd1 = ['/home/mwork/mworkcnc/scripts/linuxcnc','/home/mwork/mworkcnc/configs/mdragon/scara.ini']
cmd ='/home/mwork/mworkcnc/scripts/linuxcnc /home/mwork/mworkcnc/configs/mdragon/scara.ini'


proc = subprocess.Popen(cmd1)#,shell=True)
#time.sleep(5)
# get output from process "Something to print"
#one_line_output = proc.stdout.readline()

# write 'a line\n' to the process
proc.stdin.write(b'\n')

#proc.communicate(input=b'\n')
#stdout=subprocess.PIPE,stderr=subprocess.PIPE,
print("end")


def get_ini_data( only_section=None, only_name=None ):
        global INIFileDataTemplate
        INI_FILENAME = '/home/mwork/mworkcnc/configs/mdragon/scara.ini'
        INI_FILE_PATH = '/home/mwork/mworkcnc/configs/mdragon'      
        INIFileData = deepcopy(INIFileDataTemplate)
       
        sectionRegEx = re.compile( r"^\s*\[\s*(.+?)\s*\]" )
        keyValRegEx = re.compile( r"^\s*(.+?)\s*=\s*(.+?)\s*$" )
        try:
            section = 'NONE'
            comments = ''
            idv = 1
            with open( INI_FILENAME ) as file_:
                for line in file_:
                    if  line.lstrip().find('#') == 0 or line.lstrip().find(';') == 0:
                        comments = comments + line[1:]
                    else:
                        mo = sectionRegEx.search( line )
                        if mo:
                            section = mo.group(1)
                            hlp = ''
                            try:
                                if (section in ConfigHelp):
                                    hlp = ConfigHelp[section]['']['help'].encode('ascii','replace')
                            except:
                                pass
                            if (only_section is None or only_section == section):
                                INIFileData['sections'][section] = { 'comment':comments, 'help':hlp }
                            comments = '' 
                        else:
                            mo = keyValRegEx.search( line )
                            if mo:
                                hlp = ''
                                default = ''
                                try:
                                    if (section in ConfigHelp):
                                        if (mo.group(1) in ConfigHelp[section]):
                                            hlp = ConfigHelp[section][mo.group(1)]['help'].encode('ascii','replace')
                                            default = ConfigHelp[section][mo.group(1)]['default'].encode('ascii','replace')
                                except:
                                    pass

                                if (only_section is None or (only_section == section and only_name == mo.group(1) )):
                                    INIFileData['parameters'].append( { 'id':idv, 'values':{ 'section':section, 'name':mo.group(1), 'value':mo.group(2), 'comment':comments, 'help':hlp, 'default':default } } )
                                comments = ''
                                idv = idv + 1
            reply = {'data':INIFileData,'code':'ok'}
        except Exception as ex:
            reply = {'code':'e','data':''}

        return reply
def shutdown_linuxcnc(  ):
    #try:
    displayname = get_ini_data( only_section='DISPLAY', only_name='DISPLAY' )
    print("displayname",displayname)
    print("displayname",displayname['data']['parameters'][0]['values'])
    p = subprocess.Popen( ['pkill',displayname['data']['parameters'][0]['values']['value']] , stderr=subprocess.STDOUT )
    #p = subprocess.Popen( ['kill', '-9', str(displayname['data']['parameters'][0]['id'])], stderr=subprocess.STDOUT )
    #return {'code':'o'}

"""

{'data':
 {'parameters':
  [{'id': 4, 'values': {'section': 'DISPLAY', 'name': 'DISPLAY', 
  'value': 'qtvcp mdragon', 'comment': '', 'help': '', 'default': ''}}],
   'sections': {'DISPLAY': {'comment': '', 'help': ''}}}, 'code': 'ok'}

"""
"""    except:
        print("E")
        return {'code':'e' }"""

#shutdown_linuxcnc()


def getProcesses( str):
    processCommand = ["ps", "-A"]
    checkProcess = ["grep", "-e", str]
    
    processExec = subprocess.Popen(processCommand, stdout = subprocess.PIPE)
    checkExec = subprocess.Popen(checkProcess, stdin = processExec.stdout, stdout = subprocess.PIPE, stderr=subprocess.PIPE)
    
    processesOut, processesErr = checkExec.communicate()
    processSplit = processesOut.split()

    return processSplit

def checkIo():
    ioGrep = getProcesses("io")
    for i in range(int(len(ioGrep) / 4)):
        if len(ioGrep[4*i + 3]) == 2:
            return ioGrep[4*i + 3], ioGrep[4*i]

    return False

def checkProcess( str):
    retVal = []

    strGrep = getProcesses(str)
    for i in range(int(len(strGrep) / 4)):
        retVal.append([strGrep[4*i + 3], strGrep[4*i]])

    return retVal

def killProcess( processId):
    print("KILL",processId)
    killCommand = ["kill",'-9', processId]

    subprocess.Popen(killCommand)

def cleanLinuxcnc():
    if len(checkProcess("axis")) > 0:
        for p in checkProcess("axis"):
            self.killProcess(p[1])
        time.sleep(20)

    if len(checkProcess("linuxcnc")) > 0:
        if len(checkProcess("milltask")) > 0:
            for p in checkProcess("milltask"):
                killProcess(p[1])
        
        if len(checkIo()) != False:
            killProcess(checkIo()[1])

        if len(checkProcess("rtapi")) > 0:
            for p in checkProcess("rtapi"):
                killProcess(p[1])
        if len(checkProcess("qtvcp")) > 0:
            for p in checkProcess("qtvcp"):
                killProcess(p[1])
        if len(checkProcess("linuxcnc")) > 0:
            for p in checkProcess("linuxcnc"):
                killProcess(p[1])
        if len(checkProcess("linuxcncsvr")) > 0:
            for p in checkProcess("linuxcncsvr"):
                killProcess(p[1])
        if len(checkProcess("halui")) > 0:
            for p in checkProcess("halui"):
                killProcess(p[1])
#cleanLinuxcnc()