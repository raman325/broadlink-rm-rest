# dependencies - peewee, broadlink, psycopg2-binary

from peewee import *
import json
from time import sleep
import broadlink

# Local version
blasters_db_path = 'blasters.db'
# Docker version
# blasters_db_path = '/data/blasters.db'

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
    mac = TextField()
    mac_hex = TextField()
    name = TextField(null=True)

    def get_device(self):
        device = broadlink.rm(host=(self.ip, self.port), mac=bytearray(dec_hex(self.mac_hex)), devtype=self.devtype)
        device.auth()
        return device

    def to_dict(self):
        return {"name": self.name, "ip": self.ip, "mac": self.mac}
    
    def put_name(self, name):
        self.name = name
        self.save()
    
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

def convert_mac(raw):
    return temp[10:12] + ":" + temp[8:10] + ":" + temp[6:8] + ":" + temp[4:6] + ":" + temp[2:4] + ":" + temp[0:2]

def enc_hex(raw):
    return raw.encode('hex')

def dec_hex(raw):
    return raw.decode('hex')

def get_new_blasters():
    blasters = list(filter(lambda blaster: blaster.get_type() == "RM2", broadlink.discover(timeout=5)))
    cnt = 0
    for blaster in blasters:
        mac_hex = enc_hex(blaster.mac)
        tmp_blaster = Blaster.get_or_none(Blaster.mac_hex == mac_hex)
        if tmp_blaster is None:
            cnt = cnt + 1
            Blaster.create(ip=blaster.host[0], port=blaster.host[1], devtype=blaster.devtype, mac_hex=mac_hex, mac=convert_mac(mac_hex), name=None)
        else:
            if not tmp_blaster.ip == blaster.ip:
                tmp_blaster.ip = blaster.ip
                tmp_blaster.save()
    
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
