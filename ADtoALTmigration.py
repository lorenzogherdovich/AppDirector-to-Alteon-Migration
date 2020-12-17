#!/usr/bin/python

############################################### Description ###################################################
# The following script is used to migrate AppDirector Version 2.14 configuration to Alteon configuration.     #
# Manual use was tested on both Linux and windows client(using Pycharm)                                       #
# Currently we only support AppDirector version 2.14 .                                                        #
# Supported Alteon versions are 32.0.0.0 and above (not tested on older versions)                             #
# The script works with both appdirector config file that not contains '/' at the end of the line.            #
#                          MosheCohen-Radware                                                              #
###############################################################################################################

###
### fork. little modification to create configuration compatible with AlteonOS 30...
###




import sys
import os
import datetime

dictMethod = {'Cyclic': 'roundrobin', 'Weighted_Cyclic': 'roundrobin', 'Fewest_Number_of_Users': 'leastconns', 'Least_Amount_of_Traffic': 'leastconns', 'Hashing': 'phash'}
dictFilePars = {'Servers': 'appdirector farm server table', 'Farms': 'appdirector farm table', 'L4-Policy': 'appdirector l4-policy table'}
servicetranslation = {'80': 'http', '443': 'https', '53': 'dns', '554': 'rtsp', '5060': 'sip'}
dictFilePars = {'Servers': 'appdirector farm server table', 'Farms': 'appdirector farm table', 'L4-Policy': 'appdirector l4-policy table', 'L3-Policy': 'net ip-interface create', 'Health-Check': 'health-monitoring check create', 'Methods': 'appdirector l7 farm-selection method-table setCreate', 'Binding': 'health-monitoring binding create', 'Modification': 'appdirector l7 modification table setCreate'}
dictFarm = {}
dictFarms = {}
dictL4Pol = {}
dictL4Pols = {}
dictServer = {}
dictServers = {}
dictL3if = {}
dictL3 = {}

#####################################################
###                  files and path               ###
#####################################################
argument_len = len(sys.argv)
if argument_len == 1:
    appdConfigFile = raw_input('please enter file name :')
    projectName = "AppDirector_Project_"+datetime.datetime.today().strftime("%Y%M%d_%H%M")
elif argument_len == 2:
    appdConfigFile = sys.argv[1]
    projectName = "AppDirector_Project_"+datetime.datetime.today().strftime("%Y%M%d_%H%M")
elif argument_len == 3:
    appdConfigFile = sys.argv[1]
    projectName = sys.argv[2]


#####################################################
###                  functions                    ###
#####################################################

def search(filetosearch, searchquery, newfilename):
    try:
        with open(filetosearch, 'r') as f1:
            with open(newfilename, 'w') as f2:
                f3=''
                for line in f1:
                    if line.startswith(searchquery):
                        f2.write(line)
                    else:
                        f3+=line
        with open(filetosearch, 'w') as f1:
            f1.write(f3)
    except Exception as e:
      print searchquery, "not in file", e


def spaceremove( xx, y, line1 ):
    "remove spaces from the begining and/or the end of the object"
    while line1.find('"', xx, y)>0:
        xx = line1.find('"', xx, y)
        count = line1.count('"', xx, y)
        if (count % 2) > 0:
            if line1.find(' "', xx, y):
                line1 = line1[0:xx - 1] + line1[xx -1:xx + 1].replace(' "', '"') + line1[xx + 1:len(line1)]
            xx = xx + 1
        if (count % 2) == 0:
            if line1.find('" ', xx, y):
                line1 = line1[0:xx] + line1[xx:xx + 2].replace('" ', '"') + line1[xx + 2:len(line1)]
            xx = xx + 1
    spaceremove.line = line1
    return

def spacereplace( x, y, line2 ):
    "replace spaces into underline in objects"
    while line2.find('"', x, y) > 0:
        while line2.find('"', x, y) > 0:
            x = line2.find('"', x, y)
            y = line2.find('"', x + 1, y)
            line2 = line2[0:x] + line2[x:x + 1].replace('"', '') + line2[x + 1:y].replace(' ', '_') + line2[y:y + 1].replace('"', '') + line2[y + 1:len(line2)]
            x = 0
            y = len(line2)
        spacereplace.line = line2
    else:
        spacereplace.line = line2

#####################################################
###                File Parssing                  ###
#####################################################

try:
    filedata = open(appdConfigFile, 'r').read()
    
    leftovers_file_name = os.path.join(os.getcwd(), projectName,'leftovers.txt')
    AppDirector_file_path = os.path.join(os.getcwd(),projectName, 'AppDirector', "")
    Alteon_file_path = os.path.join(os.getcwd(), projectName, 'Alteon',"")
    os.makedirs(os.path.join(os.getcwd(), projectName))
    leftovers = open(leftovers_file_name, 'w+')

except Exception as e:
    print "Tried to load filename \"{}\" and got the error: {}".format(appdConfigFile, e)
    sys.exit(1)
 
leftovers.write(filedata.replace('\\\r\n', '').replace('\\\n', ''))
leftovers.close()
os.makedirs(AppDirector_file_path)
os.makedirs(Alteon_file_path)

for F in dictFilePars:
    searchquery = dictFilePars[F]
    newfilename = os.path.join(AppDirector_file_path, F+".txt" )
    search(leftovers_file_name, searchquery, newfilename)

grp = open(os.path.join(AppDirector_file_path,'Farms.txt'),'r')
pol = open(os.path.join(AppDirector_file_path, 'L4-Policy.txt' ), 'r')
srv = open(os.path.join(AppDirector_file_path, 'Servers.txt' ),'r')
L3 = open(os.path.join(AppDirector_file_path, 'L3-Policy.txt' ),'r')

#####################################################
###            L3 dict creation              ###
#####################################################

for line in L3:
    L3_interface = line.split(' -')
    #print L3_interface
    for info in L3_interface:
        #print info
        if len(info.split(' ')) > 2:
            for z, a in enumerate(info.split(' ')):  # L3 IP import
                if len(a.split('.')) == 4:
                    for item in a.split('.'):
                        if item.isdigit():
                            if int(item) in xrange(0, 255):
                                if z == 3:
                                    L3_ip = a
                                    break
                                else:
                                    break
                if z == 4:  # Mask import
                    L3_mask = a
                if z == 5:  # port import
                    L3_port = a
            dictL3if.update({'L3_ip': L3_ip, 'L3_mask': L3_mask, 'L3_port': L3_port,})
            #print dictL3if
        if len(info.split(' ')) == 2:
            #print info.split(' ')
            for z, a in enumerate(info.split(' ')):
                if z == 0:
                    key = a
                if z == 1:
                    val = a
            dictL3if.update({key: val})
            #print dictL3if
    dictifname = dictL3if['L3_port'] + '_' + dictL3if['L3_ip']
    #print dictL3if
    dictL3[dictifname] = dictL3if.copy()
    dictL3if.clear()
    L3_port = ''
    L3_ip = ''
#print dictL3

#####################################################
###            Servers dict creation              ###
#####################################################

for line in srv:
    spaceremove( xx=0, y=len(line), line1=line );
    if spaceremove.line:
        line = spaceremove.line
    spacereplace( x=0, y=len(line), line2=line );
    if spacereplace.line:
        line = spacereplace.line
    server = line.split(' -')
    #print server
    for info in server:
        if len(info.split(' ')) > 2:
            for z, a in enumerate(info.split(' ')):  # Server IP import
                if len(a.split('.')) == 4:
                    for item in a.split('.'):
                        if item.isdigit():
                            if int(item) in xrange(0, 255):
                                if z == 6:
                                    srvip = a
                                    break
                                else:
                                    break
                if z == 5:  # srvFarm import
                    srvfarm = a
                if z == 7:  # srvPort import
                    srvport = a
            dictServer.update({'srvip': srvip, 'srvfarm': srvfarm, 'srvport': srvport,})
        if len(info.split(' ')) == 2:
            for z, a in enumerate(info.split(' ')):
                if z == 0:
                    key = a
                if z == 1:
                    val = a
            dictServer.update({key: val})
    dictsrvername = dictServer['sn'] + '@MC@' + dictServer['srvfarm']
    #print dictsrvername
    dictServers[dictsrvername] = dictServer.copy()
    dictServer.clear()
    #as = ''
    #w = ''
# print dictServers


#####################################################
###             groups dict creation              ###
#####################################################

for line in grp:
    spaceremove( xx=0, y=len(line), line1=line );
    line = spaceremove.line
    spacereplace( x=0, y=len(line), line2=line );
    line = spacereplace.line
    farm = line.split(' -')
    for info in farm:
        if len(info.split()) == 5:
            for z, a in enumerate(info.split( )):
                if z == 1:
                    key = a
                if z == 4:
                    val = a
            dictFarm.update({key:val})
        if len(info.split( )) == 2:
            for z, a in enumerate(info.split( )):
                if z == 0:
                    key = a
                if z == 1:
                    val = a
            dictFarm.update({key:val})
    dictFarms[dictFarm['farm']] = dictFarm.copy()
    dictFarm.clear()


#####################################################
###             VIPs dict creation                ###
#####################################################


for line in pol:                                          #Space remove
    spaceremove( xx=0, y=len(line), line1=line );
    line = spaceremove.line
    spacereplace( x=0, y=len(line), line2=line );
    line = spacereplace.line
    l4 = line.split(' ')
    l4 = line.split(' -')
    for info in l4:
        if len(info.split(' ')) > 2:
            for z, a in enumerate(info.split(' ')):                                  #VIP IP import
                if len(a.split('.')) == 4:
                    for item in a.split('.'):
                        if item.isdigit():
                            if int(item) in xrange(0, 255):
                                if z == 4:
                                    vipip = a
                                    break
                                else:
                                    break
                if z == 5:                                                          # Protocol import
                    proto = a
                if z == 6:                                                          # Port import
                    port = a
                if z == 8:                                                          # VIP name import
                    vipname = a
            dictL4Pol.update({'vipip': vipip, 'proto': proto, 'port': port, 'vipname': vipname})
        if len(info.split(' ')) == 2:
            for z, a in enumerate(info.split(' ')):
                if z == 0:
                    key = a
                if z == 1:
                    val = a
            dictL4Pol.update({key: val})
    dictL4Pols[vipname] = dictL4Pol.copy()
    dictL4Pol.clear()
    fn = ''
    ta = ''
#print dictL4Pols
#print l4


#####################################################
###            L3 config creation            ###
#####################################################

orig_stdout = sys.stdout
sys.stdout = open(os.path.join(Alteon_file_path, "Alteon_L3_Policy.txt"), 'w+')

print ''
print '*******************    L3 Interface    *******************'
print ''

interfaceid = 1
for s in dictL3:
    if 'v' in dictL3[s]:
        print '/c/l2/vlan', dictL3[s]['v']
        print '        ena'
        print '        add <physical port number>'
        orig_stdout = sys.stdout
        sys.stdout = open(os.path.join(Alteon_file_path, "Alteon_Errors.txt"), 'a')
        print('Error - physical port number should be configured for vlan id: --->', dictL3[s]['v'])
        sys.stdout.close()
        sys.stdout = orig_stdout
    if "MNG" in s:
        if dictL3[s]['L3_port'] == "MNG-1":
            print '/c/sys/mmgmt/net 1', interfaceid
        elif dictL3[s]['L3_port'] == "MNG-2":
            print '/c/sys/mmgmt/net 2', interfaceid
        else:
            print '/c/sys/mmgmt', interfaceid
        print '        ena'
        print '        addr', dictL3[s]['L3_ip']
        print '        mask', dictL3[s]['L3_mask']
    else:
        print '/c/l3/if', interfaceid
        print '        ena'
        print '        addr', dictL3[s]['L3_ip']
        print '        mask', dictL3[s]['L3_mask']
        print '        vlan', dictL3[s]['v']
        if 'pa' in dictL3[s]:
            print '        peer', dictL3[s]['pa']
        interfaceid = interfaceid+1

sys.stdout.close()
sys.stdout=orig_stdout

#####################################################
###            Servers config creation            ###
#####################################################

orig_stdout = sys.stdout
sys.stdout = open(os.path.join(Alteon_file_path, "Alteon_Servers.txt"), 'w+')

print ''
print '*******************    Servers    *******************'
print ''


for s in dictServers:
    # print '/c/slb/real ', dictServers[s]['sn']
    print '/c/slb/real ', dictServers[s]['id'].strip()
    if 'as' in dictServers[s] and dictServers[s]['as'] == 'Disable':
        print '        dis'
    else:
        print '        ena'
    print '        ipver v4'
    print '        rip', dictServers[s]['srvip']
    print '        name ', '"'+dictServers[s]['sn']+'"' 
    # add real server port in case exists:
    if 'srvport' in dictServers[s] and dictServers[s]['srvport'] != 'None':
        print '        addport', dictServers[s]['srvport']
    # add weight to server in case higher then 10min:
    if 'w' in dictServers[s] and int(dictServers[s]['w']) <= 48:
        print '        weight', dictServers[s]['w']
    # add backup server in case exists:
    if 'ba' in dictServers[s]:
        for backup in dictServers:
            if dictServers[s]['srvfarm'].rstrip("\n") == dictServers[backup]['srvfarm'].rstrip("\n") and dictServers[s]['ba'].rstrip("\n") == dictServers[backup]['srvip'].rstrip("\n"):
                print '        backup', dictServers[backup]['sn']
    print '/c/slb/real ', str(dictServers[s]['id'].strip()) + '/adv'
    print '        submac ena'


sys.stdout.close()
sys.stdout=orig_stdout


#####################################################
###            Groups config creation             ###
#####################################################

orig_stdout = sys.stdout
sys.stdout = open(os.path.join(Alteon_file_path, "Alteon_Groups.txt"), 'w+')

dictBCKServers = {}
print ''
print '*******************    Groups    *******************'
print ''


# print dictFarms
incrementagrp = 0
for p in dictFarms:                                                     ###### groups creation ######
    incrementagrp = incrementagrp + 1
    dictFarms[p]['id'] = incrementagrp
    # print '/c/slb/group', p
    print '/c/slb/group', incrementagrp
    print '        ipver v4'
    if 'dm' in dictFarms[p] and dictFarms[p]['dm'] != '':
        for m in dictMethod:
            if dictFarms[p]['dm'] == m:
                print '        metric', dictMethod[m]
    # add real to group
        for real in dictServers:
            if 'om' not in dictServers[real] and dictFarms[p]['farm'] == dictServers[real]['srvfarm']:
                #print '        add', dictServers[real]['sn']
                print '        add', dictServers[real]['id'].strip()
    # create backup group and add backup real server
    for real in dictServers:
        if dictFarms[p]['farm'] == dictServers[real]['srvfarm'] and 'om' in dictServers[real]:
            dictBCKServers[real] = dictServers[real].copy()
    if dictBCKServers:
        print "".join(['        backup g', p,'_BCK'])
        print "".join(['/c/slb/group ', p, '_BCK'])
        if dictFarms[p]['dm'] != '':
            for m in dictMethod:
                if dictFarms[p]['dm'] == m:
                    print '        metric', dictMethod[m]
        for bck in dictBCKServers:
            print '        add', dictServers[bck]['sn']
        dictBCKServers.clear()
    print '        name', '"' + p + '"'

sys.stdout.close()
sys.stdout=orig_stdout

# if z == 5:  # srvFarm import
#     srvfarm = a
# if z == 7:  # srvPort import
#     srvport = a
# dictServer.update({'srvip': srvip, 'srvfarm': srvfarm, 'srvport': srvport, })
# if len(info.split(' ')) == 2:
#     for z, a in enumerate(info.split(' ')):
#         if z == 0:
#             key = a
#         if z == 1:
#             val = a
#     dictServer.update({key: val})
# dictsrvername = dictServer['sn'] + '@MC@' + dictServer['srvfarm']
# # print dictsrvername
# dictServers[dictsrvername] = dictServer.copy()
# dictServer.clear()


#####################################################
###            Virts config creation              ###
#####################################################


orig_stdout = sys.stdout
sys.stdout = open(os.path.join(Alteon_file_path, "Alteon_Virts.txt"), 'w+')

print ''
print '*******************    VIRTs    *******************'
print ''

# print dictL4Pols
incrementav = 0
for l in dictL4Pols:
    incrementav = incrementav + 1
    if 'ta' in dictL4Pols[l] and dictL4Pols[l]['ta'].rstrip("\n") == 'Virtual_IP_Interface':
        orig_stdout = sys.stdout
        sys.stdout = open(os.path.join(Alteon_file_path, "Alteon_Errors.txt"), 'a')
        print('Error - vip should be configured as floating IP: --->', dictL4Pols[l]['vipname'], '--->', dictL4Pols[l])
        sys.stdout.close()
        sys.stdout=orig_stdout
        continue
    if 'po' in dictL4Pols[l]:
        orig_stdout = sys.stdout
        sys.stdout = open(os.path.join(Alteon_file_path, "Alteon_Errors.txt"), 'a')
        print('Error - L7 policy should be configured for : --->', dictL4Pols[l]['vipname'], '--->', dictL4Pols[l])
        sys.stdout.close()
        sys.stdout=orig_stdout
        continue
    # Virt Creation
    # print '/c/slb/virt', l
    print '/c/slb/virt', incrementav
    print '        ena'
    print '        ipver v4'
    # Vip IP
    print '        vip', dictL4Pols[l]['vipip']
    print '        vname ' + '"' + l + '"'
    # Service
    if dictL4Pols[l]['port'] in servicetranslation:
        # print '/c/slb/virt', l,'/service', dictL4Pols[l]['port'], servicetranslation[dictL4Pols[l]['port']]
        print '/c/slb/virt', str(incrementav) + '/service', dictL4Pols[l]['port'], servicetranslation[dictL4Pols[l]['port']]
    elif 'ta' in dictL4Pols[l] and dictL4Pols[l]['ta'].rstrip("\n") != 'Virtual_IP_Interface':
        # print '/c/slb/virt', l, '/service', dictL4Pols[l]['port'], dictL4Pols[l]['ta'].lower()
        print '/c/slb/virt', str(incrementav) + '/service', dictL4Pols[l]['port'], dictL4Pols[l]['ta'].lower()
    elif dictL4Pols[l]['port'] == 'Any':
        # print '/c/slb/virt', l,'/service 1 basic-slb'
        print '/c/slb/virt', str(incrementav) + '/service 1 basic-slb'
    else:
        # print '/c/slb/virt', l,'/service', dictL4Pols[l]['port'], 'basic-slb'
        print '/c/slb/virt', str(incrementav) + '/service', dictL4Pols[l]['port'], 'basic-slb'
    # Group
    print '        group', dictL4Pols[l]['fn'].rstrip("\n")
    print ' '
    # Timeout
    tmout = dictL4Pols[l]['fn'].rstrip("\n")
    if 'at' in dictFarms[tmout] and int(dictFarms[tmout]['at'])/60 >= 10:
        print '        tmout', int(dictFarms[tmout]['at'])/60
    print '        nonat ena'


sys.stdout.close()
sys.stdout=orig_stdout


#####################################################
###             Files Merge                       ###
#####################################################

filenames = [Alteon_file_path + 'Alteon_Errors.txt', Alteon_file_path + 'Alteon_L3_Policy.txt', Alteon_file_path + 'Alteon_Servers.txt', Alteon_file_path + 'Alteon_Groups.txt', Alteon_file_path +'Alteon_Virts.txt']
with open(os.path.join(Alteon_file_path, 'Alteon_CFG.txt'), 'w') as outfile:
    for fname in filenames:
        infile = open(os.path.join(Alteon_file_path, fname))
        outfile.write(infile.read())
        infile.close()
