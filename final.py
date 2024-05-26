import cv2
import robomaster
from robomaster import robot
import keyboard
import math
import time
#状态类，用于调节程序周期
class States():
    LINE_TRACK=0
    CATCH_SQUARE1=1
    TURN_BACK=2
    CATCH_SQUARE2=3
    PUT_SQUARE1=4
    PUT_SQUARE2=5
    END =6
#marker类，用于接收识别到的标签
class MarkerInfo:
    def __init__(self, x, y, w, h, info):
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._info = info
    @property
    def reveal_x(self):
        return self._x
    @property
    def text(self):
        return self._info
#用于存放识别线信息的类型
class PointInfo:
    def __init__(self, x, y, theta, c):
        self._x = x
        self._y = y
        self._theta = theta
        self._c = c
    @property
    def ceta(self):
        return int(self._theta)
    @property 
    def cs(self):
        return (self._c)
    @property
    def distance(self):
        return math.sqrt(abs(self._x-0.5)*abs(self._x-0.5)+(1-self._y)*(1-self._y))
line = []
markers = []
state =States.LINE_TRACK
robot_arm_state=0
baseSpeed = 55
#识别marker的回调函数
def on_detect_marker(marker_info):
    number = len(marker_info)
    markers.clear()
    #print("共识别到{}个数字".format(number))
    for i in range(0, number):
        x, y, w, h, info = marker_info[i]
        markers.append(MarkerInfo(x, y, w, h, info))
        #print("marker:{0} x:{1}, y:{2}, w:{3}, h:{4}".format(info, x, y, w, h))
#识别线信息的回调函数
def on_detect_line(line_info):
    number = len(line_info)
    line.clear()
    for i in range(1,number):
        x, y, ceta, c = line_info[i]
        #print("x:{}, y:{}, ceta:{}, c:{}".format(x, y, ceta, c))
        line.append(PointInfo(x, y, ceta, c))
#第一次放置
def put1():
    #移动机器人手臂，让摄像头看到图标
    ep_arm.moveto(x=10,y=110).wait_for_completed()
    #ep_arm.recenter()
    time.sleep(1)
    #ep_robot.initialize(conn_type="ap")
    #ep_arm.recenter()
    ep_gripper.close(power=100)
    time.sleep(2)
    markers.clear()
    result = ep_vision.sub_detect_info(name="marker", color="red", callback=on_detect_marker)#周期性调用函数
    endcnn=0
    w=1
    #img = ep_camera.read_cv2_image(strategy="newest")
    #如果没识别到图标，让机器人持续前进
    while len(markers)==0:
        ep_chassis.drive_wheels(w2=20,w3=20,w1=20,w4=20)
        time.sleep(0.1)
        #cv2.imshow("style", img)
        #cv2.waitKey(1)
    ep_chassis.drive_speed(x=0,y=0,z=0)
    time.sleep(2)
    while True:
        #img = ep_camera.read_cv2_image(strategy="newest")
        if keyboard.is_pressed('q'):
            break
        time.sleep(0.01)
        temp_makers=markers.copy()
        #print(len(temp_makers))
        #print(1)
        #如果一直没识别到信息就退出
        if len(temp_makers)==0:
            endcnn+=1
        else:
            endcnn=0
        if endcnn>50:
            break
        #对识别到的线信息进行操作
        for j in range(0,len(temp_makers)):
            #print("*****")
            #print(j)
            if j>=len(temp_makers):
                break
            #确保识别到A信息
            if temp_makers[j].text=='A':
                #如果A图标过远，平移机器人
                if abs(temp_makers[j].reveal_x-0.5)>=0.015:
                    #print(3)
                    ep_chassis.drive_speed(x=0, y=(temp_makers[j].reveal_x-0.5)*2, z=0,timeout=5) 
                    print("move1")
                    time.sleep(0.05)
                else:
                #如果A图标在一定范围内，移动机器人前进，接近篮子
                    print("move2")
                    ep_chassis.drive_speed(x=0.22, y=0, z=0,timeout=5) 
                    time.sleep(0.7)
                    w=0
                if w==0:
                    break
        #cv2.imshow("style", img)
        #cv2.waitKey(1)
        if w==0:
            break
    #cv2.destroyAllWindows()
    result = ep_vision.unsub_detect_info(name="marker")
    #ep_chassis.drive_speed(x=0.15, y=0, z=0,timeout=5) 
    #time.sleep(1)
    #移动机器臂，放置方块
    ep_arm.moveto(x=20,y=140).wait_for_completed()
    ep_arm.moveto(x=150, y=140).wait_for_completed()
    ep_gripper.open(power=30)
    time.sleep(1)
 
    #机器人后移远离篮子，准备下阶段任务
    ep_chassis.drive_wheels(w2=-50,w3=-50,w1=-50,w4=-50)    #ep_gripper.pause()
    time .sleep(2)
    ep_chassis.stop()
    ep_arm.move(x=-50,y=0).wait_for_completed()
    #ep_arm.moveto(x=20, y=140).wait_for_completed()
    time.sleep(2)
    ep_arm.recenter().wait_for_completed()
#put2 原理和put1相近
def put2():
    ep_arm.moveto(x=10,y=110).wait_for_completed()
    #ep_arm.recenter()
    time.sleep(1)
    #ep_robot.initialize(conn_type="ap")
    #ep_arm.recenter()
    ep_gripper.close(power=100)
    time.sleep(2)
    markers.clear()
    result = ep_vision.sub_detect_info(name="marker", color="red", callback=on_detect_marker)#周期性调用函数
    endcnn=0
    w=1
    #img = ep_camera.read_cv2_image(strategy="newest")
    while len(markers)==0:
        ep_chassis.drive_wheels(w2=20,w3=20,w1=20,w4=20)
        time.sleep(0.1)
        #cv2.imshow("style", img)
        #cv2.waitKey(1)
    ep_chassis.drive_speed(x=0,y=0,z=0)
    time.sleep(2)
    while True:
        #img = ep_camera.read_cv2_image(strategy="newest")
        if keyboard.is_pressed('q'):
            break
        time.sleep(0.01)
        temp_makers=markers.copy()
        #print(len(temp_makers))
        #print(1)
        if len(temp_makers)==0:
            endcnn+=1
        else:
            endcnn=0
        if endcnn>50:
            break
        for j in range(0,len(temp_makers)):
            #print("*****")
            #print(j)
            if j>=len(temp_makers):
                break
            if temp_makers[j].text=='B':
                if abs(temp_makers[j].reveal_x-0.5)>=0.013:
                    #print(3)
                    ep_chassis.drive_speed(x=0, y=(temp_makers[j].reveal_x-0.5)*2, z=0,timeout=5) 
                    print("move1")
                    time.sleep(0.05)
                else:
                    print("move2")
                    ep_chassis.drive_speed(x=0.24, y=0, z=0,timeout=5) 
                    time.sleep(0.7)
                    w=0
                if w==0:
                    break
        #cv2.imshow("style", img)
        #cv2.waitKey(1)
        if w==0:
            break
    #cv2.destroyAllWindows()
    result = ep_vision.unsub_detect_info(name="marker")
    #ep_chassis.drive_speed(x=0.15, y=0, z=0,timeout=5) 
    #time.sleep(1)
    ep_arm.moveto(x=20,y=140).wait_for_completed()
    ep_arm.moveto(x=150, y=140).wait_for_completed()
    ep_gripper.open(power=30)
    time.sleep(2)
 
    ep_chassis.drive_wheels(w2=-50,w3=-50,w1=-50,w4=-50)    #ep_gripper.pause()
    time .sleep(2)
    ep_chassis.stop()
    ep_arm.move(x=-50,y=0).wait_for_completed()
    #ep_arm.moveto(x=20, y=140).wait_for_completed()
    time.sleep(2)
    ep_arm.recenter().wait_for_completed()
#巡线函数
def Line_track():
    #设置巡线信息
    result = ep_vision.sub_detect_info(name="line", color="blue", callback=on_detect_line)
    speeds=3
    constant=0.5
    constant2 =60
    quit=0 
    while True:
        #img = ep_camera.read_cv2_image(strategy="newest")
        #print(1)
        if keyboard.is_pressed('q'):
            break
        Line=line
        if len(Line)==0:
            quit+=1
        else:
            quit=0
        if quit>7:
            break
        min_distance=1#用于存放最小距离的变量
        min_err_x=0.5#用于存放最小距离点的x方向偏差
        min_theta =0
        min_c =0.0
        for j in range(0, len(Line)):
            #寻找距离机器人最近的点，并记录它的x方向偏差
            if Line[j].distance<min_distance:
                min_distance=Line[j].distance
                min_theta = line[j].ceta
                min_err_x=Line[j]._x-0.5
        lSpeed=0
        rSpeed=0
        #如果离线过远，改变左右轮子转速，以实现机器人巡线
        if min_err_x!=0.5:
            lSpeed=baseSpeed+min_theta*constant+min_err_x*constant2
            rSpeed=baseSpeed-min_theta*constant-min_err_x*constant2
            #print("*****")
            #print(min_err_x)
            #print("********")
            #print(min_theta)
        ep_chassis.drive_wheels(w2=lSpeed,w3=lSpeed,w1=rSpeed,w4=rSpeed)
        time.sleep(0.1)
        #cv2.imshow("style", img)
        #cv2.waitKey(1)
    #cv2.destroyAllWindows()
    #为下阶段任务准备
    ep_chassis.drive_wheels(w2=0,w3=0,w1=0,w4=0,timeout=0.1)
    ep_chassis.stop()
    result = ep_vision.unsub_detect_info(name="line")
    time.sleep(0.1)
#调头任务
def turn_back():
    ep_chassis.drive_speed(x=0.0, y=0.0, z=60.0, timeout=None)
    time.sleep(3)
    ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0, timeout=None)
    time.sleep(0.1)
#抓取方块任务
def catch1():
    #ep_robot.initialize(conn_type="ap")
    #ep_arm.recenter()
    #移动机器臂，确保方块在摄像头范围内
    ep_arm.moveto(x=20,y=100).wait_for_completed()
    time.sleep(2)
    ep_gripper.open(power=100)
    time.sleep(2)
    result = ep_vision.sub_detect_info(name="marker", color="red", callback=on_detect_marker)#周期性调用函数
    endcnn=0
    w=1
    #img = ep_camera.read_cv2_image(strategy="newest")
    #缓慢移动机器人，确保能够识别方块
    while len(markers)==0:
        ep_chassis.drive_wheels(w2=10,w3=10,w1=10,w4=10)
        time.sleep(0.1)
        #cv2.imshow("style", img)
        #cv2.waitKey(1)
    ep_chassis.drive_speed(x=0,y=0,z=0)
    time.sleep(2)
    while True:
        #img = ep_camera.read_cv2_image(strategy="newest")
        if keyboard.is_pressed('q'):
            break
        time.sleep(0.01)
        temp_makers=markers.copy()
        #print(len(temp_makers))
        #print(1)
        if len(temp_makers)==0:
            endcnn+=1
        else:
            endcnn=0
        if endcnn>50:
            break
        #让机器人对准方块
        for j in range(0,len(temp_makers)):
            #print("*****")
            #print(j)
            if j>=len(temp_makers):
                break
            if temp_makers[j].text=='1':
                if abs(temp_makers[j].reveal_x-0.5)>=0.01:
                    #print(3)
                    ep_chassis.drive_speed(x=0, y=(temp_makers[j].reveal_x-0.5)*1.8, z=0,timeout=5) 
                    print("move1")
                    time.sleep(0.05)
                else:
                    print("move2")
                    ep_chassis.drive_speed(x=0.115, y=0, z=0,timeout=5) 
                    time.sleep(0.7)
                    w=0
                if w==0:
                    break
        #cv2.imshow("style", img)
        #cv2.waitKey(1)
        if w==0:
            break
    #cv2.destroyAllWindows()
    result = ep_vision.unsub_detect_info(name="marker")
    #ep_chassis.drive_speed(x=0.15, y=0, z=0,timeout=5) 
    #time.sleep(1)
    #实现夹取方块任务
    ep_arm.moveto(x=20,y=140).wait_for_completed()
    ep_arm.moveto(x=150, y=140).wait_for_completed()
    ep_gripper.close(power=30)
    time.sleep(1)
 
    #为下阶段任务准备
    ep_chassis.drive_wheels(w2=-50,w3=-50,w1=-50,w4=-50)    #ep_gripper.pause()
    time .sleep(2)
    ep_chassis.stop()
    ep_arm.move(x=-50,y=0).wait_for_completed()
    #ep_arm.moveto(x=20, y=140).wait_for_completed()
    time.sleep(2)
    ep_arm.recenter().wait_for_completed()
#第二次夹取任务和第一次夹取任务差不多
def catch2():
    #ep_robot.initialize(conn_type="ap")
    #ep_arm.recenter()
    ep_arm.moveto(x=20,y=100).wait_for_completed()
    time.sleep(2)
    ep_gripper.open(power=100)
    time.sleep(2)
    result = ep_vision.sub_detect_info(name="marker", color="red", callback=on_detect_marker)#周期性调用函数
    endcnn=0
    w=1
    #img = ep_camera.read_cv2_image(strategy="newest")
    while len(markers)==0:
        ep_chassis.drive_wheels(w2=10,w3=10,w1=10,w4=10)
        time.sleep(0.1)
        #cv2.imshow("style", img)
        #cv2.waitKey(1)
    ep_chassis.drive_speed(x=0,y=0,z=0)
    time.sleep(2)
    while True:
        #img = ep_camera.read_cv2_image(strategy="newest")
        if keyboard.is_pressed('q'):
            break
        time.sleep(0.01)
        temp_makers=markers.copy()
        #print(len(temp_makers))
        #print(1)
        if len(temp_makers)==0:
            endcnn+=1
        else:
            endcnn=0
        if endcnn>50:
            break
        for j in range(0,len(temp_makers)):
            #print("*****")
            #print(j)
            if j>=len(temp_makers):
                break
            if temp_makers[j].text=='2':
                if abs(temp_makers[j].reveal_x-0.5)>=0.01:
                    #print(3)
                    ep_chassis.drive_speed(x=0, y=(temp_makers[j].reveal_x-0.5)*1.8, z=0,timeout=5) 
                    print("move1")
                    time.sleep(0.05)
                else:
                    print("move2")
                    ep_chassis.drive_speed(x=0.115, y=0, z=0,timeout=5) 
                    time.sleep(0.7)
                    w=0
                if w==0:
                    break
        #cv2.imshow("style", img)
        #cv2.waitKey(1)
        if w==0:
            break
    #cv2.destroyAllWindows()
    result = ep_vision.unsub_detect_info(name="marker")
    #ep_chassis.drive_speed(x=0.15, y=0, z=0,timeout=5) 
    #time.sleep(1)
    ep_arm.moveto(x=20,y=140).wait_for_completed()
    ep_arm.moveto(x=150, y=140).wait_for_completed()
    ep_gripper.close(power=30)
    time.sleep(1)
 
    ep_chassis.drive_wheels(w2=-50,w3=-50,w1=-50,w4=-50)    #ep_gripper.pause()
    time .sleep(2)
    ep_chassis.stop()
    ep_arm.move(x=-50,y=0).wait_for_completed()
    #ep_arm.moveto(x=20, y=140).wait_for_completed()
    time.sleep(2)
    ep_arm.recenter().wait_for_completed()

if __name__ == '__main__':
    #初始化机器人
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    #ep_robot.initialize(conn_type="sta")
    ep_vision = ep_robot.vision
    ep_gripper = ep_robot.gripper
    ep_arm=ep_robot.robotic_arm
    ep_camera = ep_robot.camera
    ep_chassis=ep_robot.chassis
    #设置当前机器人状态
    state = States.LINE_TRACK
    ep_arm.recenter().wait_for_completed()
    ep_camera.start_video_stream(display=False)
    while True:
        while state ==States.LINE_TRACK:
            print("line")
            Line_track()
            #按照顺序实现机器人相关任务，即巡线-夹取-巡线-放置-巡线-夹取-巡线-放置
            state = States.TURN_BACK
            if robot_arm_state==0:
                state = States.CATCH_SQUARE1
                robot_arm_state+=1
            elif robot_arm_state==1:
                state = States.PUT_SQUARE1
                robot_arm_state+=1
            elif robot_arm_state==2:
                state = States.CATCH_SQUARE2
                robot_arm_state+=1
            elif robot_arm_state==3:
                state = States.PUT_SQUARE2
                robot_arm_state+=1
            #line
            pass
        while state ==States.CATCH_SQUARE1:
            print("catch1")
            catch1()
            state = States.TURN_BACK
            #catch1
            pass
        while state == States.TURN_BACK:
            print("turn back")
            turn_back()
            state=States.LINE_TRACK
            #state=States.END
            #turn back
            pass
        while state == States.PUT_SQUARE1:
            print("put1")
            state =States.TURN_BACK
            put1()
            #put1
            pass
        while state == States.CATCH_SQUARE2:
            print("catch2")
            state = States.TURN_BACK
            catch2()
            #catch2
            pass
        while state == States.PUT_SQUARE2:
            print("put2")
            state = States.END
            put2()
            #put2
            pass
        if state == States.END:
            turn_back()
            break
    time.sleep(1)

    ep_camera.stop_video_stream()
    ep_robot.close()
    

'''
if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_vision = ep_robot.vision
    ep_camera = ep_robot.camera
    ep_chassis = ep_robot.chassis
    ep_gripper = ep_robot.gripper
    ep_arm=ep_robot.robotic_arm
    ep_arm.moveto(x=20,y=120).wait_for_completed()
    #ep_arm.recenter()
    ep_gripper.open(power=100)
    time.sleep
    ep_camera.start_video_stream(display=False)
    result = ep_vision.sub_detect_info(name="marker", color="red", callback=on_detect_marker)#周期性调用函数
    endcnn=0
    w=1
    while True:
        img = ep_camera.read_cv2_image(strategy="newest")
        if keyboard.is_pressed('q'):
            break
        time.sleep(0.01)
        temp_makers=markers.copy()
        #print(len(temp_makers))
        if len(temp_makers)==0:
            endcnn+=1
        else:
            endcnn=0
        if endcnn>30:
            break
        for j in range(0,len(temp_makers)):
            if j>=len(temp_makers):
                break
            if temp_makers[j].text=='1':
                if abs(temp_makers[j].reveal_x-0.5)>=0.01:
                    ep_chassis.drive_speed(x=0, y=(temp_makers[j].reveal_x-0.5)*2, z=0,timeout=5) 
                    print("move1")
                    time.sleep(0.01)
                else:
                    print("move2")
                    ep_chassis.drive_speed(x=0.15, y=0, z=0,timeout=5) 
                    time.sleep(1)
                    w=0
                if w==0:
                    break
        cv2.imshow("style", img)
        cv2.waitKey(1)
        if w==0:
            break
    cv2.destroyAllWindows()
    result = ep_vision.unsub_detect_info(name="marker")
    ep_arm.moveto(x=20,y=140).wait_for_completed()
    ep_arm.moveto(x=150, y=140).wait_for_completed()
    #ep_chassis.move(x=-1, y=0, z=0, xy_speed=0.7).wait_for_completed()
    ep_gripper.close(power=50)
    time.sleep(1)
    ep_arm.moveto(x=20, y=140).wait_for_completed()
    ep_gripper.pause()
    time.sleep(2)
    ep_camera.stop_video_stream()
    ep_robot.close()
    
    '''
