# dependencies - peewee, broadlink, psycopg2-binary

from peewee import *
import json
from time import sleep
import broadlink

blasters_db_path = 'data/blasters.db'

blasters_db = SqliteDatabase(blasters_db_path)

#### Blaster DB classes and functions

class BaseBlastersModel(Model):
    class Meta:
        database = blasters_db

class Blaster(BaseBlastersModel):
    uid = AutoField()
    ip = TextField()
    port = IntegerField()
    devtype = IntegerField()
    mac = TextField(unique=True)
    mac_hex = TextField(unique=True)
    name = TextField(unique=True, null=True)

    def get_device(self):
        device = broadlink.rm(
            host=(self.ip, self.port), 
            mac=dec_hex(self.mac_hex), 
            devtype=self.devtype
            )
        device.auth()
        return device

    def to_dict(self):
        return {
            "name": self.name, 
            "ip": self.ip, 
            "mac": self.mac
            }
    
    def put_name(self, name):
        check_blaster = Blaster.get_or_none(Blaster.name == name)
        
        if check_blaster:
            return False
        else:
            self.name = name
            self.save()
            return True
    
    def send_command(self, command):
        device = self.get_device()
        device.send_data(dec_hex(command.value))
    
    def send_raw(self, value):
        device = self.get_device()
        device.send_data(dec_hex(value))
    
    def get_command(self):
        device = self.get_device()
        device.enter_learning()

        sleep(2)
        value = device.check_data()
        x = 0

        while not value and x < 5:
            x = x + 1
            sleep(2)
            value = device.check_data()

        if value:
            value = enc_hex(value)
            if value.replace("0","") == "":
                return None
            else:
                return value
        else:
            return None

def friendly_mac_from_hex(raw):
    return raw[10:12] + ":" + raw[8:10] + ":" + raw[6:8] + ":" + raw[4:6] + ":" + raw[2:4] + ":" + raw[0:2]

def enc_hex(raw):
    return str(raw).encode('hex')

def dec_hex(raw):
    return bytearray(raw.decode('hex'))

def get_new_blasters():
    blasters = list(filter(lambda blaster: blaster.get_type() == "RM2", broadlink.discover(timeout=5)))
    cnt = 0
    for blaster in blasters:
        mac_hex = enc_hex(blaster.mac)
        (Blaster.insert(
            ip=blaster.host[0], 
            port=blaster.host[1], 
            devtype=blaster.devtype, 
            mac_hex=mac_hex, 
            mac=friendly_mac_from_hex(mac_hex), 
            name=None
            )
            .on_conflict(
                conflict_target=[Blaster.mac], 
                preserve=[Blaster.ip, Blaster.port]
            ).execute())
    
    return {"new_devices": cnt}

def get_all_blasters():
    try:
        blasters = [blaster for blaster in Blaster.select()]
    except Blaster.DoesNotExist:
        blasters = []

    return blasters

def get_all_blasters_as_dict():
    try:
        blasters = [blaster.to_dict() for blaster in Blaster.select()]
    except Blaster.DoesNotExist:
        blasters = []

    return blasters

def get_blaster_by_name(name):
    return Blaster.get_or_none(Blaster.name == name)

def get_blaster_by_ip(ip):
    return Blaster.get_or_none(Blaster.ip == ip)

def get_blaster_by_mac(mac):
    return Blaster.get_or_none(Blaster.mac == mac)

def send_command_to_all_blasters(command):
    blasters = get_all_blasters()
    for blaster in blasters:
        blaster.send_command(command.value)
