#!/usr/bin/python

import speech_recognition as sr
import pyaudio
from gpiozero import LED
import os

#
import subprocess

#
#import sys
import Gpib


#
inst = Gpib.Gpib(0, 23, timeout = 20)#34401A
inst.clear()

inst1 = Gpib.Gpib(0, 24, timeout = 20)#3458A
inst1.clear()

inst.write("*RST")

inst1.write("PRESET NORM")
inst1.write("END ALWAYS")

class GoogleTTS():
    def say(text):
        subprocess.run("cd /home/flanon/voice_control_using_raspberry", shell=True)
        cmd = "./text2speech " + text
        print(cmd)
        subprocess.run(cmd, shell=True)
        #subprocess.run("python test.py", shell=True)


for i, mic_name in enumerate (sr.Microphone.list_microphone_names()):
    print("mic: " + mic_name)
    if "USB" in mic_name:
        print("USB" + mic_name)
        mic = sr.Microphone()
        #mic = sr.Microphone(device_index=i, chunk_size=1024, sample_rate=48000)


pi_ear = sr.Recognizer()
pi_mouth = GoogleTTS
light_1 = LED(17)
fan = LED(27)
light_1.on()
fan.on()

#
ovhl = LED(19)

light_list = {"light" : light_1, "overhead light" : ovhl}
fan_list = {"fan" : fan}
machine_list = {"HP 34401" : inst, "HP 3458" : inst1}
command = ""


print("A moment of silence, please...")
with mic as source: pi_ear.adjust_for_ambient_noise(source)
print("Set minimum energy threshold to {}".format(pi_ear.energy_threshold))

while True:
    need_speak = False
    user_mentioned = False

    with mic as source:
        # pi_ear.pause_thpi_eareshold=1
        # pi_ear.adjust_for_ambient_noise(source, duration=0.5)
        print("\033[0;35mpi: \033[0m I'm listening")
        audio = pi_ear.listen(source)
    try:
        you = pi_ear.recognize_google(audio)
    except:
        you = "" + command
    msg = you
    you_removed = you.replace(" ", "")
    if you_removed == "":
        msg="I cant hear you, please try again"
        need_speak = True

    elif "turnon" in you_removed:
        temp_dict = dict(light_list , **fan_list)
        for i in light_list.keys() + fan_list.keys() :
            if i.replace(" ", "") in you_removed :
                msg = "sure, Im turning on" + i
                temp_dict[i].off()
                user_mentioned = True
                command = ""
        if user_mentioned == False :
            msg = "which fan or light you want to turn on"
            command = "turnon"
        need_speak = True

    elif "turnoff" in you_removed:
        temp_dict = dict(light_list, **fan_list)
        for i in light_list.keys() + fan_list.keys():
            if i.replace(" ", "") in you_removed:
                msg = "sure, Im turning off the" + i
                temp_dict[i].on()
                user_mentioned = True
                command = ""
        if user_mentioned == False:
            msg = "which fan or light you want to turn on"
            command = "turnoff"
        need_speak = True

    #added
    elif "reset" in you_removed:
        for i in machine_list.keys() :
            if i.replace(" ", "") in you_removed :
                msg = "Ok, reseting" + i + "A"
                if i == "HP 34401" :
                    inst.write("*RST")
                elif i == "HP 3458" :
                    inst1.write("RESET")
                    inst1.write("NDIG 9")
                    inst1.write("END ALWAYS")
                user_mentioned = True
                command = ""
        if user_mentioned == False :
            msg = "which machine you want to reset"
            command = "reset"
        need_speak = True

    elif "read" in you_removed:
        for i in machine_list.keys() :
            if i.replace(" ", "") in you_removed :
                if i == "HP 34401":
                    inst.write("CONF:RES")
                    inst.write("READ?")
                    data = inst.read()
                    msg = "measured resistance is " + str(float(data)) + " ohm"
                    user_mentioned = True
                elif i == "HP 3458":
                    inst1.write("TARM SGL, 1")
                    data = inst1.read()
                    msg = "measured voltage is " + str(float(data)) + " volt"
                    user_mentioned = True
        if user_mentioned == False :
            msg = "which machine you want to read"
            command = "read"
        need_speak = True

    #added end

    elif "bye" in you_removed:
        msg="thank you"
        print("\033[0;32myou:\033[0m " + you)
        print("\033[0;35mpi:\033[0m " + msg)
        pi_mouth.say(msg)
        #pi_mouth.runAndWait()
        break

    print("\033[0;32myou:\033[0m " + you)
    print("\033[0;35mpi:\033[0m " + msg)
    if need_speak == True:
        pi_mouth.say(msg)
        #pi_mouth.runAndWait()

