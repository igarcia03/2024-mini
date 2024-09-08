#!/usr/bin/env python3
"""
PWM Tone Generator

based on https://www.coderdojotc.org/micropython/sound/04-play-scale/
"""

import machine
import utime

from machine import Pin, PWM
from math import ceil

from time import sleep

# GP16 is the speaker pin
SPEAKER_PIN = 16

# create a Pulse Width Modulation Object on this pin
speaker = machine.PWM(machine.Pin(SPEAKER_PIN))


def playtone(frequency: float, duration: float) -> None:
    speaker.duty_u16(1000)
    speaker.freq(frequency)
    utime.sleep(duration)


def quiet():
    speaker.duty_u16(0)


freq: float = 30
duration: float = 0.1  # seconds

#With reference to: https://github.com/james1236/buzzer_music

tones = {
    'C0':16,
    'C#0':17,
    'D0':18,
    'D#0':19,
    'E0':21,
    'F0':22,
    'F#0':23,
    'G0':24,
    'G#0':26,
    'A0':28,
    'A#0':29,
    'B0':31,
    'C1':33,
    'C#1':35,
    'D1':37,
    'D#1':39,
    'E1':41,
    'F1':44,
    'F#1':46,
    'G1':49,
    'G#1':52,
    'A1':55,
    'A#1':58,
    'B1':62,
    'C2':65,
    'C#2':69,
    'D2':73,
    'D#2':78,
    'E2':82,
    'F2':87,
    'F#2':92,
    'G2':98,
    'G#2':104,
    'A2':110,
    'A#2':117,
    'B2':123,
    'C3':131,
    'C#3':139,
    'D3':147,
    'D#3':156,
    'E3':165,
    'F3':175,
    'F#3':185,
    'G3':196,
    'G#3':208,
    'A3':220,
    'A#3':233,
    'B3':247,
    'C4':262,
    'C#4':277,
    'D4':294,
    'D#4':311,
    'E4':330,
    'F4':349,
    'F#4':370,
    'G4':392,
    'G#4':415,
    'A4':440,
    'A#4':466,
    'B4':494,
    'C5':523,
    'C#5':554,
    'D5':587,
    'D#5':622,
    'E5':659,
    'F5':698,
    'F#5':740,
    'G5':784,
    'G#5':831,
    'A5':880,
    'A#5':932,
    'B5':988,
    'C6':1047,
    'C#6':1109,
    'D6':1175,
    'D#6':1245,
    'E6':1319,
    'F6':1397,
    'F#6':1480,
    'G6':1568,
    'G#6':1661,
    'A6':1760,
    'A#6':1865,
    'B6':1976,
    'C7':2093,
    'C#7':2217,
    'D7':2349,
    'D#7':2489,
    'E7':2637,
    'F7':2794,
    'F#7':2960,
    'G7':3136,
    'G#7':3322,
    'A7':3520,
    'A#7':3729,
    'B7':3951,
    'C8':4186,
    'C#8':4435,
    'D8':4699,
    'D#8':4978,
    'E8':5274,
    'F8':5588,
    'F#8':5920,
    'G8':6272,
    'G#8':6645,
    'A8':7040,
    'A#8':7459,
    'B8':7902,
    'C9':8372,
    'C#9':8870,
    'D9':9397,
    'D#9':9956,
    'E9':10548,
    'F9':11175,
    'F#9':11840,
    'G9':12544,
    'G#9':13290,
    'A9':14080,
    'A#9':14917,
    'B9':15804
}

class music:
    def __init__(self, songString='0 D4 8 0', looping=True, tempo=3, duty=2512, pin=None, pins=[Pin(0)]):
        self.tempo = tempo
        self.song = songString
        self.looping = looping
        self.duty = duty
        
        self.stopped = False
        
        self.timer = -1
        self.beat = -1
        self.arpnote = 0
        
        self.pwms = []
        
        if (not (pin is None)):
            pins = [pin]
        self.pins = pins
        for pin in pins:
            self.pwms.append(PWM(pin))
        
        self.notes = []

        self.playingNotes = []
        self.playingDurations = []


        #Find the end of the song
        self.end = 0
        splitSong = self.song.split(";")
        for note in splitSong:
            snote = note.split(" ")
            testEnd = round(float(snote[0])) + ceil(float(snote[2]))
            if (testEnd > self.end):
                self.end = testEnd
                
        #Create empty song structure
        while (self.end > len(self.notes)):
            self.notes.append(None)

        #Populate song structure with the notes
        for note in splitSong:
            snote = note.split(" ")
            beat = round(float(snote[0]));
            
            if (self.notes[beat] == None):
                self.notes[beat] = []
            self.notes[beat].append([snote[1],ceil(float(snote[2]))]) #Note, Duration


        #Round up end of song to nearest bar
        self.end = ceil(self.end / 8) * 8
    
    def stop(self):
        for pwm in self.pwms:
            pwm.deinit()
        self.stopped = True

    def restart(self):
        self.beat = -1
        self.timer = 0
        self.stop()
        self.pwms = []
        for pin in self.pins:
            self.pwms.append(PWM(pin))
        self.stopped = False

    def resume(self):
        self.stop()
        self.pwms = []
        for pin in self.pins:
            self.pwms.append(PWM(pin))
        self.stopped = False

    def tick(self):
        if (not self.stopped):
            self.timer = self.timer + 1
            
            #Loop
            if (self.timer % (self.tempo * self.end) == 0 and (not (self.timer == 0))):
                if (not self.looping):
                    self.stop()
                    return False
                self.beat = -1
                self.timer = 0
            
            #On Beat
            if (self.timer % self.tempo == 0):
                self.beat = self.beat + 1

                #Remove expired notes from playing list
                i = 0
                while (i < len(self.playingDurations)):
                    self.playingDurations[i] = self.playingDurations[i] - 1
                    if (self.playingDurations[i] <= 0):
                        self.playingNotes.pop(i)
                        self.playingDurations.pop(i)
                    else:
                        i = i + 1
                
                if (self.beat < len(self.notes)):
                    if (self.notes[self.beat] != None):
                        for note in self.notes[self.beat]:
                            self.playingNotes.append(note[0])
                            self.playingDurations.append(note[1])
                
                #Only need to run these checks on beats
                i = 0
                for pwm in self.pwms:
                    if (i >= len(self.playingNotes)):
                        if hasattr(pwm, 'duty_u16'):
                            pwm.duty_u16(0)
                        else:
                            pwm.duty(0)
                    else:
                        #Play note
                        if hasattr(pwm, 'duty_u16'):
                            pwm.duty_u16(self.duty)
                        else:
                            pwm.duty(self.duty)
                        pwm.freq(tones[self.playingNotes[i]])
                    i = i + 1
            

            #Play arp of all playing notes
            if (len(self.playingNotes) > len(self.pwms)):
                p = self.pwms[len(self.pwms)-1];
                if hasattr(p, 'duty_u16'):
                    p.duty_u16(self.duty)
                else:
                    p.duty(self.duty)
                
                if (self.arpnote > len(self.playingNotes)-len(self.pwms)):
                    self.arpnote = 0
                self.pwms[len(self.pwms)-1].freq(tones[self.playingNotes[self.arpnote+(len(self.pwms)-1)]])
                self.arpnote = self.arpnote + 1
                
            return True
        else:
            return False

#print("Playing frequency (Hz):")

#for i in range(64):
#    print(freq)
#    playtone(freq, duration)
#    freq = int(freq * 1.1)
    
#song = '64 E3 4 13;64 E4 4 13;64 G4 4 13;64 B4 4 13;68 F#3 4 13;76 B3 4 13;80 A3 4 13;84 G3 4 13;88 D3 4 13;72 D5 4 13;72 A4 4 13;72 F#5 4 13;72 G3 4 13;80 F#4 4 13;80 A4 4 13;80 C#5 4 13;88 A4 4 13;88 C#5 4 13;88 E5 4 13;96 E3 4 13;96 E4 4 13;96 G4 4 13;96 B4 4 13;100 F#3 4 13;108 B3 4 13;112 A3 4 13;116 G3 4 13;120 D3 4 13;104 D5 4 13;104 A4 4 13;104 F#5 4 13;104 G3 4 13;112 F#4 4 13;112 A4 4 13;112 C#5 4 13;120 A4 4 13;120 C#5 4 13;120 E5 4 13;0 E3 4 13;4 F#3 4 13;12 B3 4 13;16 A3 4 13;20 G3 4 13;24 D3 4 13;8 G3 4 13;32 E3 4 13;36 F#3 4 13;44 B3 4 13;48 A3 4 13;52 G3 4 13;56 D3 4 13;40 G3 4 13;0 E4 4 13;0 G4 4 13;8 A4 4 13;8 D5 4 13;16 A4 4 13;16 F#4 4 13;24 A4 4 13;24 C#5 4 13;32 E4 4 13;32 G4 4 13;40 A4 4 13;40 D5 4 13;48 A4 4 13;48 F#4 4 13;56 A4 4 13;56 C#5 4 13;128 E3 4 13;128 E4 4 13;128 G4 4 13;128 B4 4 13;132 F#3 4 13;140 B3 4 13;144 A3 4 13;148 G3 4 13;152 D3 4 13;136 D5 4 13;136 A4 4 13;136 F#5 4 13;136 G3 4 13;144 F#4 4 13;144 A4 4 13;144 C#5 4 13;152 A4 4 13;152 C#5 4 13;152 E5 4 13;132 A5 2 13;134 B5 2 13;142 D5 1 13;143 E5 1 13;150 F#5 1 13;151 A5 1 13;160 E3 4 13;160 E4 2 13;160 G4 2 13;160 B4 2 13;164 F#3 4 13;172 B3 4 13;176 A3 4 13;180 G3 4 13;184 D3 4 13;168 D5 4 13;168 A4 4 13;168 F#5 4 13;168 G3 4 13;176 F#4 4 13;176 A4 4 13;176 C#5 4 13;184 A4 4 13;184 C#5 4 13;184 E5 4 13;162 D6 2 13;164 B5 2 13;166 A5 2 13;174 D5 1 13;175 E5 1 13;182 A5 1 13;183 F#5 1 13'
song = '0 E3 1 0;2 E4 1 0;4 E3 1 0;6 E4 1 0;8 E3 1 0;10 E4 1 0;12 E3 1 0;14 E4 1 0;16 A3 1 0;18 A4 1 0;20 A3 1 0;22 A4 1 0;24 A3 1 0;26 A4 1 0;28 A3 1 0;30 A4 1 0;32 G#3 1 0;34 G#4 1 0;36 G#3 1 0;38 G#4 1 0;40 E3 1 0;42 E4 1 0;44 E3 1 0;46 E4 1 0;48 A3 1 0;50 A4 1 0;52 A3 1 0;54 A4 1 0;56 A3 1 0;58 B3 1 0;60 C4 1 0;62 D4 1 0;64 D3 1 0;66 D4 1 0;68 D3 1 0;70 D4 1 0;72 D3 1 0;74 D4 1 0;76 D3 1 0;78 D4 1 0;80 C3 1 0;82 C4 1 0;84 C3 1 0;86 C4 1 0;88 C3 1 0;90 C4 1 0;92 C3 1 0;94 C4 1 0;96 G2 1 0;98 G3 1 0;100 G2 1 0;102 G3 1 0;104 E3 1 0;106 E4 1 0;108 E3 1 0;110 E4 1 0;114 A4 1 0;112 A3 1 0;116 A3 1 0;118 A4 1 0;120 A3 1 0;122 A4 1 0;124 A3 1 0;0 E6 1 1;4 B5 1 1;6 C6 1 1;8 D6 1 1;10 E6 1 1;11 D6 1 1;12 C6 1 1;14 B5 1 1;0 E5 1 6;4 B4 1 6;6 C5 1 6;8 D5 1 6;10 E5 1 6;11 D5 1 6;12 C5 1 6;14 B4 1 6;16 A5 1 1;20 A5 1 1;22 C6 1 1;24 E6 1 1;28 D6 1 1;30 C6 1 1;32 B5 1 1;36 B5 1 1;36 B5 1 1;37 B5 1 1;38 C6 1 1;40 D6 1 1;44 E6 1 1;48 C6 1 1;52 A5 1 1;56 A5 1 1;20 A4 1 6;16 A4 1 6;22 C5 1 6;24 E5 1 6;28 D5 1 6;30 C5 1 6;32 B4 1 6;36 B4 1 6;37 B4 1 6;38 C5 1 6;40 D5 1 6;44 E5 1 6;48 C5 1 6;52 A4 1 6;56 A4 1 6;64 D5 1 6;64 D6 1 1;68 D6 1 1;70 F6 1 1;72 A6 1 1;76 G6 1 1;78 F6 1 1;80 E6 1 1;84 E6 1 1;86 C6 1 1;88 E6 1 1;92 D6 1 1;94 C6 1 1;96 B5 1 1;100 B5 1 1;101 B5 1 1;102 C6 1 1;104 D6 1 1;108 E6 1 1;112 C6 1 1;116 A5 1 1;120 A5 1 1;72 A5 1 6;80 E5 1 6;68 D5 1 7;70 F5 1 7;76 G5 1 7;84 E5 1 7;78 F5 1 7;86 C5 1 7;88 E5 1 6;96 B4 1 6;104 D5 1 6;112 C5 1 6;120 A4 1 6;92 D5 1 7;94 C5 1 7;100 B4 1 7;101 B4 1 7;102 C5 1 7;108 E5 1 7;116 A4 1 7'
from machine import Pin

mySong = music(song, pins=[Pin(0)])

while True:
    print(mySong.tick())
    sleep(0.035)

# Turn off the PWM
quiet()
