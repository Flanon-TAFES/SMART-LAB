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

print("A moment of silence, please...")
with mic as source: pi_ear.adjust_for_ambient_noise(source)
print("Set minimum energy threshold to {}".format(pi_ear.energy_threshold))

while True:
    need_speak = False
    with mic as source:
        # pi_ear.pause_thpi_eareshold=1
        # pi_ear.adjust_for_ambient_noise(source, duration=0.5)
        print("\033[0;35mpi: \033[0m I'm listening")
        audio = pi_ear.listen(source)
    try:
        you = pi_ear.recognize_google(audio)
    except:
        you = ""
    msg = you
    if you == "":
        msg="I cant hear you, please try again"
        need_speak = True
    elif "turn on light" in you:
        msg="sure, Im turning on the light"
        light_1.off()
        need_speak = True
    elif "turn on fan" in you:
        msg="sure, Im turning on the fan"
        fan.off()
        need_speak = True
    elif "turn on the light" in you:
        msg = "sure, Im turning on the light"
        light_1.off()
        need_speak = True
    elif "turn off light" in you:
        msg = "sure, Im turning off the light"
        light_1.on()
        need_speak = True
    elif "turn off fan" in you:
        msg = "sure, Im turning off the fan"
        fan.on()
        need_speak = True
    elif "turn off the light" in you:
        msg="sure, Im turning off the light"
        light_1.on()
        need_speak = True

    #added
    elif "reset HP 34401" in you:
        msg="Ok, reseting HP34401A"
        inst.write("*RST")
        need_speak = True

    elif "read HP 34401" in you:

        inst.write("CONF:RES")
        inst.write("READ?")
        data = inst.read()

        msg="measured resistance is " + str(float(data)) + " ohm"
        need_speak = True

    #

    elif "reset HP 3458" in you:
        msg="Ok, reseting HP3458A"
        inst1.write("RESET")
        inst1.write("NDIG 9")
        inst1.write("END ALWAYS")
        need_speak = True

    elif "read HP 3458" in you:

        inst1.write("TARM SGL, 1")
        data = inst1.read()

        msg="measured voltage is " + str(float(data)) + " volt"
        need_speak = True
    #

    elif "turn on overhead light" in you:
        msg = "Ok, turning on"
        ovhl.on()
        need_speak = True

    elif "turn off overhead light" in you:
        msg="Ok, turning off"
        ovhl.off()
        need_speak = True
    #added end

    elif "bye" in you:
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
