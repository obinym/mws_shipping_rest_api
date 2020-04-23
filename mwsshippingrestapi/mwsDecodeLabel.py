import pickle
import base64
from io import BytesIO
from zipfile import ZipFile
import gzip
import socket
import subprocess
import os

# MWS Documentation https://docs.developer.amazonservices.com/en_UK/merch_fulfill/MerchFulfill_HowToExtractShippingLabel.html

def print_label(label_zpl, host, port):
    try:
        mysocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        mysocket.connect(host,port)
        mysocket.send(label_zpl)
        mysocket.close()
        print('[ERROR]: could not print on ZPL network printer')
        print('[INFO]: trying USB ...')
    except:
        print_label_usb(label_zpl)

def print_label_usb(label_zpl):
    f = open('~/zpl_label.zpl', 'wb')
    f.write(label_zpl)
    f.close()
    # transfer temporary file to usb printer
    try:
        script = "cat ~/zpl_label.zpl > /dev/usb/lp0"
        os.system(script)
        print('[INFO]: successfully send zpl label to USB printer at LP0')
    except:
        print('[ERROR]: could not send to USB printer at LP0')

def decode_label(label_base64):
# https://www.base64decode.org/ for testing
    label_decoded=base64.b64decode(label_base64)
    return label_decoded
def unzip_label(label_zip):
    unzipped_string = ''
    try:
        temp=BytesIO(label_zip)
        zipfile = ZipFile(temp)
        for name in zipfile.namelist():
            unzipped_string += zipfile.open(name).read()
        return unzipped_string
    except:
        print("[ERROR] Could not unzip file with zip")
def ungzip_label(label_zip):
# https://stackoverflow.com/a/28412763
# for testing https://online-converting.com/
    try:
        gzip_file = BytesIO(label_zip)
        ungzip_file = gzip.GzipFile(fileobj=gzip_file)
        # only one file expected here
        ungzipped_string = ungzip_file.read()
        # with open('zpl_label.zpl', 'wb') as outfile:
        #    outfile.write(ungzip_file.read())
        return ungzipped_string
    except:
        print("[ERROR] Could not unzip file with gzip")
def get_test_label():
    f = open('~/shipping_api_json.pkl', 'rb')
    json_file = pickle.load(f)
    f.close()
    json_label=json_file['Shipment']['label']
    return json_label

if __name__ == '__main__':
#    Testcode if called directly
#    get a testlabel binary file
    json_label = get_test_label()
    zip_label=decode_label(json_label)
    zpl_label=ungzip_label(zip_label)
# send to ZPL printer
    host = "127.0.0.1"
    port = 9999
    print_label(zpl_label,host,port)
