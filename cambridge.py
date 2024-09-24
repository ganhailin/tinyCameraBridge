print("import maix")
from maix import camera, image#, display, app, image
# print("import cv2")
# import cv2
# import numpy as np
print('import flask')
# import flask
import time
from flask import Flask
from flask_restful import Resource, Api, reqparse
import threading
import base64
import time

print('begin')
print('init camera')
cam = camera.Camera(512, 320, raw=True, fps=30)     # RAW模式 fps=30设置 1440p
# cam.awb_mode(1)
cam.exp_mode(1)
# cam.constrast(50)
# cam.luma(50)
exposure = cam.exposure(100)
gain = cam.gain(1024)
print('set exp:{}'.format(exposure))
print('set gain:{}'.format(gain))
print('take one image to get size, bayer informations')

img = cam.read_raw()          
cam_bayer = img.format()
cam_height = img.height()
cam_width = img.width()
cam_bit = 12
cam_pixsize = 2.9 #2.9um像素大小

cam_maxADU=2**cam_bit-1
cam_maxbinX=1
cam_maxbinY=1
cam_offset_max = 0
cam_offset_min = 0
cam_bayer_offset_x = 0
cam_bayer_offset_y = 0
cam_gain_max = 999893/32 #16bit
cam_gain_min = 1024/32 #16bit
cam_exp_max = 1000000 #us
cam_exp_min = 1
cam_name = "MAIXCAM"
if(cam_bayer==image.Format.FMT_GRBG12):
    cam_bayer = 'RGGB'
    cam_bit = 12
    cam_bayer_offset_x = 1
    cam_bayer_offset_y = 0
else:
    cam_bayer = 'RGB'
    cam_bit = 8
cam_info = {
    'height':       int(cam_height),
    'width':        int(cam_width),
    'pixsize':      float(cam_pixsize),
    'bit':          int(cam_bit),
    'adu':          int(cam_maxADU),
    'bayer':        cam_bayer,
    'bayerx':       int(cam_bayer_offset_x),
    'bayery':       int(cam_bayer_offset_y),
    'offset_min':   int(cam_offset_min),
    'offset_max':   int(cam_offset_max),
    'exp_max':      int(cam_exp_max),
    'exp_min':      int(cam_exp_min),
    'gain_max':     int(cam_exp_max),
    'gain_min':     int(cam_exp_min),
    'name':         cam_name,
    }
del img

print('init done')


if __name__ == "__main__":
    global inited,ser,expstatus,forceoff,greturn,lasttime
    inited = False
    ser = None
    expstatus = 'idle'
    forceoff = False
    greturn = {},404
    lasttime=0
    app = Flask(__name__)
    http_api = Api(app)

    class ExposeApi(Resource):
        def get(self):
            global inited,ser,expstatus,forceoff
            print("expose")
            if(not inited):
                print("not inited")
                return {'status':'init first'},404
            print("expose2")
            if(expstatus != 'idle'):
                print('status is not idle')
                return {'status':'busy'}, 502
            parser = reqparse.RequestParser()  # initialize
            parser.add_argument('time', required=True, location='args')  # add args
            parser.add_argument('gain', required=True, location='args')  # add args
            args = parser.parse_args()
            stime=int(args['time'])
            sgain=int(args['gain'])
            print('start Exposure')
            exposure = cam.exposure(int(stime))
            print('set exp:{}'.format(exposure))
            gain = cam.gain(int(sgain)*32)
            print('set gain:{}'.format(gain))
            expstatus = 'exp'
            forceoff = False
            self.t1 = threading.Thread(target=self.expthread,
                                  args=(stime/1000000,))
            self.t1.start()
            return {'status':'OK'}, 200  # return data and 200 OK code
        def expthread(self,stime):
            global inited, ser, expstatus,forceoff,greturn,lasttime
            timelast = time.time() + stime
            # HERE if cam support async exposure
            # while time.time() < timelast and not forceoff:
            #     time.sleep(0.1)
            #     lasttime = int((timelast - time.time())*1000)
            # if forceoff:
            #     print('TODO:force stop Exposure here')
            #     time.sleep(0.1)
            #     forceoff=False

            lasttime = 0
            forceoff=False
            expstatus = 'reading'
            print('read image here')
            time_start = time.monotonic_ns()
            img = cam.read_raw()              # 读取摄像头画面保存到 img 变量，可以通过 print(img) 来打印 img 的详情
            print('read_raw use {}ms'.format((time.monotonic_ns()-time_start)/1000000))
            bayer = str(img.format())
            imgdata = img.to_bytes()
            height = img.height()
            width = img.width()
            greturn = {'height':height,'width':width,'bayer':bayer,'data':base64.b64encode(imgdata).decode()}, 200  # return data and 200 OK code
            expstatus = 'idle'
            print('readout done')
    class initApi(Resource):
        def get(self):
            global inited,ser
            if(inited):
                print('TODO:uinit comport here')
                #return {},404
            # parser = reqparse.RequestParser()  # initialize
            # parser.add_argument('comport', required=True, location='args')  # add args
            # args = parser.parse_args()
            # print(args['comport'])
            # ser = serial.Serial(args['comport'])  # open serial port
            # print(ser.name)  # check which port was really used

            # time.sleep(1)
            # ser.write(b'fon\r\n')  # write a string
            # time.sleep(1)
            # ser.write(b'foff\r\n')  # write a string
            print('TODO:init here')
            inited=True
            return {"status":'OK', **cam_info}, 200  # return data and 200 OK code
    class uinitApi(Resource):
        def get(self):
            global inited, ser
            if(not inited):
                return {},404
            print('uinit')
            print('TODO:uinit comport here')
            # ser.write(b'foff\r\n')  # write a string

            # ser.close()  # close port

            return {"status": 'OK'}, 200


    class stopApi(Resource):
        def get(self):
            global inited, ser, expstatus,forceoff,greturn
            if (not inited):
                return {}, 404
            print('forceoff')
            forceoff = True

            return {"status": 'OK'}, 200
    class setstatusApi(Resource):
        def get(self):
            global inited, ser, expstatus,forceoff,greturn,lasttime
            if (not inited):
                return {}, 404
            print('status status',{"status": expstatus,'timeleft':lasttime})
            return {"status": expstatus,'timeleft':lasttime}, 200
    class getimgApi(Resource):
        def get(self):
            global inited, ser, expstatus,forceoff,greturn,lasttime
            if (not inited):
                return {}, 404

            return greturn
    http_api.add_resource(ExposeApi, '/expose')
    http_api.add_resource(initApi, '/init')
    http_api.add_resource(uinitApi, '/uinit')
    http_api.add_resource(stopApi, '/stop')
    http_api.add_resource(setstatusApi, '/status')
    http_api.add_resource(getimgApi, '/getimg')

    app.run(host="0.0.0.0")
    print('app run done')
