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

import time

# #
# inst = Gpib.Gpib(0, 23, timeout = 20)#34401A
# inst.clear()
#
# inst1 = Gpib.Gpib(0, 24, timeout = 20)#3458A
# inst1.clear()
#
# inst.write("*RST")
#
# inst1.write("PRESET NORM")
# inst1.write("END ALWAYS")


inst = 1
inst1 = 1

class GoogleTTS():
    def say(text):
        subprocess.run("cd /home/flanon/voice_control_using_raspberry", shell=True)
        cmd = "./text2speech " + text
        #print(cmd)
        subprocess.run(cmd, shell=True)
        #subprocess.run("python test.py", shell=True)


for i, mic_name in enumerate (sr.Microphone.list_microphone_names()):
    print("mic: " + mic_name)
    if "USB" in mic_name:
        print("USB" + mic_name)
        mic = sr.Microphone()
        #mic = sr.Microphone(device_index=i, chunk_size=1024, sample_rate=4800>


pi_ear = sr.Recognizer()
pi_mouth = GoogleTTS
light_1 = LED(19)
fan = LED(26)
#light_1.on()
#fan.on()

#
ovhl = LED(13)
sig = LED(5)

def buzzer():
    sig.on()
    time.sleep(0.05)
    sig.off()
    time.sleep(0.05)
    sig.on()
    time.sleep(0.05)
    sig.off()

light_list = {"desk light" : light_1, "overhead light" : ovhl}
fan_list = {"fan" : fan}
machine_list = {"HP 34401" : inst, "HP 3458" : inst1}
command = ""

hotword_list = {"Tilia", "Thalia", "Celia", "Kirlia", "Kelia", "India", "Tulio", "Trulia"}

while True :

    print("A moment of silence, please...")
    with mic as source: pi_ear.adjust_for_ambient_noise(source)
    print("Set minimum energy threshold to {}".format(pi_ear.energy_threshold))
    repeat_count = 5

    while True :
        with mic as source:
            # pi_ear.pause_thpi_eareshold=1
            # pi_ear.adjust_for_ambient_noise(source, duration=0.5)
            print("\033[0;35mpi: \033[0m Waiting for hotword")
            audio = pi_ear.listen(source)
        try:
            you = pi_ear.recognize_google(audio)
        except:
            you = ""
            
        print("\033[0;32myou:\033[0m " + you)

        hotword_user = you
        hotword_user_removed = you.replace(" ", "")
        
        #if hotword_user_removed == "computer" :
        
        if hotword_user_removed in hotword_list:
            print("\033[0;31msys: \033[0m hotword detected")
            print("\033[0;35mpi: \033[0m Hello, do you need any help?")
            pi_mouth.say("Hello, do you need any help?")
            break

    while True:
        need_speak = False
        user_mentioned = False
        
        #sig start
        buzzer()
        
        with mic as source:
            # pi_ear.pause_thpi_eareshold=1
            # pi_ear.adjust_for_ambient_noise(source, duration=0.5)
            print("\033[0;35mpi: \033[0m I'm listening")
            audio = pi_ear.listen(source)
        try:
            you = pi_ear.recognize_google(audio) + command
        except:
            you = ""
        
        #sig end
        buzzer()
        
        msg = "you said: " + you
        need_speak = False
        
        you_removed = you.replace(" ", "")
        
        if you_removed == "" :
            msg = "I cant hear you, please try again"
            user_mentioned = False
            need_speak = True
            
        elif "turnon" in you_removed:
            temp_dict = dict(light_list , **fan_list)
            for i in temp_dict.keys() :#light_list.keys() + fan_list.keys() :
                if i.replace(" ", "") in you_removed :
                    msg = "sure, Im turning on " + i
                    temp_dict[i].on()
                    user_mentioned = True
                    command = ""
            if user_mentioned == False :
                msg = "which fan or light you want to turn on"
                command = " + turn on"
            need_speak = True

        elif "turnoff" in you_removed:
            temp_dict = dict(light_list, **fan_list)
            for i in temp_dict.keys() :#light_list.keys() + fan_list.keys() :
                if i.replace(" ", "") in you_removed:
                    msg = "sure, Im turning off the " + i
                    temp_dict[i].off()
                    user_mentioned = True
                    command = ""
            if user_mentioned == False:
                msg = "which fan or light you want to turn off"
                command = " + turn off"
            need_speak = True

        #added
        elif "reset" in you_removed:
            for i in machine_list.keys() :
                if i.replace(" ", "") in you_removed :
                    msg = "Ok, reseting " + i + "A"
                    if i == "HP 34401" :
    #                     inst.write("*RST")
                        print("test")
                    elif i == "HP 3458" :
    #                     inst1.write("RESET")
    #                     inst1.write("NDIG 9")
    #                     inst1.write("END ALWAYS")
                        print("test")
                    user_mentioned = True
                    command = ""
            if user_mentioned == False :
                msg = "which instrument you want to reset"
                command = " + reset"
            need_speak = True

        elif "read" in you_removed:
            for i in machine_list.keys() :
                if i.replace(" ", "") in you_removed :
                    if i == "HP 34401":
    #                     inst.write("CONF:RES")
    #                     inst.write("READ?")
    #                     data = inst.read()
                        print("test")
                        msg = "measured resistance is " #+ str(float(data)) + " oh>
                        user_mentioned = True
                    elif i == "HP 3458":
    #                     inst1.write("TARM SGL, 1")
    #                     data = inst1.read()
                        print("test")
                        msg = "measured voltage is " #+ str(float(data)) + " volt"
                        user_mentioned = True
                    command = ""

            if user_mentioned == False :
                msg = "which instrument you want to read"
                command = " + read"
            need_speak = True

        #added end
            
        elif "acquisition" in you_removed:
            pi_mouth.say("ok running data acquisition program")
            msg="data acquisition program is finished"
            subprocess.run("cd Desktop/", shell=True)
            cmd = "python3 bg_script.py"
            #print(cmd)
            subprocess.run(cmd, shell=True)
            user_mentioned = True
            need_speak = True
            
        elif "monitoring" in you_removed:
            pi_mouth.say("ok running laboratory monitoring program")
            msg="laboratory monitoring program is finished"
            subprocess.run("cd Desktop/", shell=True)
            cmd = "python3 script.py"
            #print(cmd)
            subprocess.run(cmd, shell=True)
            user_mentioned = True
            need_speak = True
        
        elif "yourself" in you_removed:
            msg="Im your virtual lab assistant, tealea, I can control and read data from test equipments, run D.A.Q. programs, monitoring lab status and control user devices"
            user_mentioned = True
            need_speak = True
            
        elif "yourname" in you_removed:
            msg="My name, tealea, is short for Test Equipment Automation and Laboratory Environment Administrator slash Assistant"
            #"Test Equipment Automation & Laboratory Environment Administrator/Assistant"
            #"Im your virtual lab assistant"
            user_mentioned = True
            need_speak = True
        
        #end

        elif "nevermind" in you_removed:
            msg="ok, if you need any help, call me later"
            print("\033[0;32myou:\033[0m " + you)
            print("\033[0;35mpi:\033[0m " + msg)
            pi_mouth.say(msg)
            #pi_mouth.runAndWait()
            print("\033[0;31msys: \033[0m break loop")
            break
        
        else :
            msg="sorry, i dont recognize that query, please give me valid command"
            user_mentioned = False
            need_speak = True

        print("\033[0;32myou:\033[0m " + you)
        print("\033[0;35mpi:\033[0m " + msg)
        
        if need_speak == True:
            pi_mouth.say(msg)
            #pi_mouth.runAndWait()

        if user_mentioned == False :
            repeat_count -= 1
            if repeat_count == 0 :
                print("\033[0;31msys: \033[0m repeat count over")
                print("\033[0;31msys: \033[0m break loop")
                #pi_mouth.say("repeat count over")
                command = ""
                break
            
        if user_mentioned == True :
            print("\033[0;35mpi: \033[0m do you need any more help?")
            pi_mouth.say("do you need any more help?")
            
            #sig sart
            
            buzzer()
            
            with mic as source:
                # pi_ear.pause_thpi_eareshold=1
                # pi_ear.adjust_for_ambient_noise(source, duration=0.5)
                print("\033[0;35mpi: \033[0m I'm listening")
                audio = pi_ear.listen(source)
            try:  
                you = pi_ear.recognize_google(audio)
            except:
                you = ""
            
            #sig end
            buzzer()
            
            print("\033[0;32myou:\033[0m " + you)
            
            you = you.replace(" ", "")
            
            if "yes" in you :
                print("\033[0;35mpi: \033[0m ok give me an order")
                pi_mouth.say("ok give me an order")
                repeat_count = 5
            elif "no" in you :
                print("\033[0;35mpi: \033[0m ok bye")
                pi_mouth.say("ok bye")
                print("\033[0;31msys: \033[0m break loop")
                break
            else :
                print("\033[0;31msys: \033[0m break loop")
                break

