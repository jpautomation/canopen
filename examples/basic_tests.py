
import canopen
import time


# create and connect to CANopen
network = canopen.Network()
network.connect(bustype='pcan', channel='PCAN_USBBUS1', bitrate=250000)

# search for nodes on network - not essential
network.scanner.search()
time.sleep(0.05)
for node_id in network.scanner.nodes:
    print("Found node %d!" % node_id)

nodeid = 0
while not(nodeid >=1 and nodeid <= 127):
    nodeid = int(input('Enter CAN node ID: '))

# add a node with an eds file
node = network.add_node(nodeid, 'C:\BASE8\Trload\eds\Steer.eds')
node.curtis_hack = True

# list all the objects in the eds file
#for obj in node.object_dictionary.values():
    #print('0x%X: %s' % (obj.index, obj.name))
    #if isinstance(obj, canopen.ObjectDictionary.ODRecord):
    #    for subobj in obj.values():
    #        print(' %d: %s' % (subobj.subindex, subobj.name))

response = ''
while response != 'q' and response != 'Q':
    response = input('read single: r, save complete: s, pdo parameters: p, quit: q... ')

    if response == 'r':
        objid = input('enter object id in hex: ')
        sub = input('sub index: ')
        hex = int(objid.encode('utf-8'), 16)
        try:
            if sub != '':
                subhex = int(sub.encode('utf-8'), 16)
                value = node.sdo.upload(hex, sub)
                print( objid, '.', sub, ': ', value)
            else:
                objsdo = node.sdo[hex]
                sub = 0
                value = node.sdo.upload(hex, sub)
                print( objid, '.', sub, ': ', value)
                print (objid, ':', objsdo.raw)
        except:
            print('cant read: ', objid)

    # write motor parameters
    if response == 'w':
        try:
            node.sdo['MotorData4'].raw = 474
#            node.sdo['MotorData5'].raw = 0
            node.sdo['MotorData6'].raw = 2
            node.sdo['MotorData7'].raw = 370
            node.sdo['MotorData8'].raw = 4750
            node.sdo['MotorData9'].raw = 1630
            node.sdo['MotorData10'].raw = 1800
            node.sdo['MotorData11'].raw = 1460
            node.sdo['MotorData12'].raw = 460
            node.sdo['MotorData13'].raw = 380
            node.sdo['MotorData14'].raw = 240
            node.sdo['MotorData15'].raw = 983
            node.sdo['MotorData16'].raw = 2000
            node.sdo['MotorData17'].raw = 280
            node.sdo['MotorData19'].raw = 270
            node.sdo['MotorData20'].raw = 600
            node.sdo['MotorData21'].raw = 390
            node.sdo['MotorData23'].raw = 2500
            node.sdo['MotorData24'].raw = 25000
            node.sdo['MotorData25'].raw = 60
            node.sdo['MotorData26'].raw = 0


        except:
            print('cant write: ')

    if response == 'p':
        # read pdo parameters
        for obj in node.object_dictionary.values():
            if obj.index >= 5120 and obj.index < 6298:
                try:
                    if isinstance(obj, canopen.objectdictionary.ODRecord):
                        print('0x%X: %s' % (obj.index, obj.name)) 
                        for subobj in obj.values():
                            sdo = node.sdo[obj.name][subobj.name]    
                            print(' %d: %s %d' % (subobj.subindex, subobj.name, sdo.raw))
                    else:
                        sdo = node.sdo[obj.name]    
                        print('0x%X,%s,%s' % (obj.index, obj.name, sdo.raw))
                    time.sleep(0.05)
                except:
                    pass

    if response == 's':
        # read value of each object from node
        path = r"C:/temp/curtis.txt"
        f = open(path, 'w')
        for obj in node.object_dictionary.values():
            try:
                if isinstance(obj, canopen.objectdictionary.ODRecord):
                #if isinstance(obj, canopen.ObjectDictionary.ODRecord):
                    print('0x%X: %s' % (obj.index, obj.name)) 
                    f.write('0x%X: %s' % (obj.index, obj.name) + '\n')
                    for subobj in obj.values():
                        sdo = node.sdo[obj.name][subobj.name]    
                        print(' %d: %s %d' % (subobj.subindex, subobj.name, sdo.raw))
                        f.write(' %d,%s,%d' % (subobj.subindex, subobj.name, sdo.raw) + '\n')
                else:
                    sdo = node.sdo[obj.name]    
                    print('0x%X,%s,%s' % (obj.index, obj.name, sdo.raw))
                    f.write('0x%X,%s,%s' % (obj.index, obj.name, sdo.raw) + '\n')
                time.sleep(0.05)
            except:
                pass

# read value of a single variable
wheelpos = node.sdo['WheelPos']         
MotorData4 = node.sdo['MotorData4']
#print ('Wheel postion is %s', wheelpos.raw)   
#print ('MotorData4 is %s', MotorData4.raw)   

# some objects can be scaled automatically
#print ('Wheel postion is %s', wheelpos.phys)   


# or can specify directly eg. if object not in eds file
#temperature = node.sdo[0x441A]
#print ('Temperature is %s ', temperature.raw)

# write value to object
#rpdo1timeout = node.sdo['Receive PDO Parameter 1']['Rx PDO1 Parameter Event Timer']
#rpdo1timeout.raw = 99


# Read current PDO configuration
node.tpdo.read()
node.rpdo.read()

# Do some changes to TPDO4 and RPDO4
#node.tpdo[4].clear()
#node.tpdo[4].add_variable('WheelPos')
#node.tpdo[4].add_variable('Application Status', 'Actual Speed')
#node.tpdo[4].trans_type = 254
#node.tpdo[4].event_timer = 10
#node.tpdo[4].enabled = True

#node.rpdo[4].clear()
#node.rpdo[4].add_variable('SetAngle')
#node.rpdo[4].add_variable('Application Commands', 'Command Speed')
node.rpdo[4].enabled = True

# Save new configuration (node must be in pre-operational)
#node.nmt.state = 'PRE-OPERATIONAL'
#node.tpdo.save()
#node.rpdo.save()

# Start RPDO4 with an interval of 100 ms
node.rpdo[4]['Application Commands.Command Speed'].phys = 1000
node.rpdo[4].start(0.1)
node.nmt.state = 'OPERATIONAL'

network.disconnect()