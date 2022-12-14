/************************************************************************
Title:    smart_lab_V1.0
Author:   Flanon <sus2607@gmail.com>  https://blog.naver.com/sinu8361
File:     V2.0 12/07/2022 07:11:26 PM
Software: AVR-GCC 4.x, AVR Libc 1.4 or higher
Hardware: ATmega128
Usage:    AVR firmware for smart lab

LICENSE:
    Copyright (C) 2016-2022 Flanon, CC BY-NC-ND 2.0 KR
    이 프로그램은 시제품 제작 용도로 작성되었으며, 상업적 이용을 금함

************************************************************************/

#define F_CPU 16000000UL
#define UART_BAUD_RATE 9600

//str lib
#include <stdio.h>
#include <stdbool.h>

//avr lib
#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/sleep.h>

//util lib
#include <util/delay.h>

//user lib
#include "millis.h"
//#include "rtc.h"
#include "uart.h"
#include "lcd.h"

//string
#include <string.h>

//input - PORTB
#define GAS PB1
#define FIRE PB0

//output - PORTC
#define FAN PC2
#define SOL PC1
#define PUMP PC0

#define SERVO_PIN PE5

//servo
#define PWM_FREQ 50//define the PWM frequency input to the servo motor(50Hz)
int servoPos = 0;//servo positioin(in dgree)
int prevPos = 0;

//servo 함수
//--------------------------------------------------------------------------------------------------------------

//PWM발생 함수, PWM 주파수 및 duty비 설정
//16Bit Timer/Counter3를 사용(Timer/Counter1은 millis()함수에서 사용하고, Timer/Counter2은 ICRn이 없기 때문에 주파수 설정에 제약이 있어 사용 불가)
//WGM(Waveform Generation Mode): 14
//Fast PWM, TOP:ICR3, Update OCR3C:BOTTOM, TOV3 Flag set: TOP
void PWM(unsigned long freq, float duty)
{
    TCCR3B &= 0b11111000;//stop timer for update

    unsigned long period = (F_CPU / 8 / freq);//calculate the waveform period

    ICR3 = period;//assign calculateed period
    TCNT3 = period - 1;//initialize TCNT3 value to prevent jitter
    OCR3C = period * duty / 100UL;//calculate duty ratio

    TCCR3A |= (1 << COM3C1) | (1 << WGM31); //use OC3C(PE5) as output, non-inverting, Fast PWM mode
    TCCR3B |= (1 << WGM33) | (1 << WGM32) | (1 << CS31); //fast PWM mode, prescaler division ratio 8
    DDRE |= 1 << SERVO_PIN; //declare PWM output
}

//utility 함수
//--------------------------------------------------------------------------------------------------------------

//딜레이 util, ms단위로 딜레이 시간 설정
void delay(int ms)
{
    for (int i = 0; i < ms; i++)
        _delay_ms (1);
}

//map function, perform range mapping
float map(float x, float in_min, float in_max, float out_min, float out_max)
{
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

//

//--------------------------------------------------------------------------------------------------------------

unsigned long lastmillis_fan;
unsigned long lastmillis_sol;
unsigned long lastmillis_pump;

unsigned long lastmillis_gas;
unsigned long lastmillis_fire;

#define interval_fan 5000
#define interval_sol 1000
#define interval_pump 5000
#define interval_pause 500

#define interval_send 3000

unsigned char text[] = " --- SMART LAB --- ";

unsigned char gas_detected[] = "Gas detected        ";
unsigned char fire_detected[] = "Fire detected       ";

unsigned char fg_detected[] = "Fire & Gas detected ";

unsigned char lcd_clear[] = "                    ";

unsigned int message = 0;
unsigned int prevmessage = 0;

int main(void)
{
    //
    //DDRF = 0x00;
    DDRB = 0x00;
    DDRC = 0xff;

    PORTC = 0x00;

    SREG = 0x80;//글로벌 인터럽트 활성화

    //초기화 작업
    uart1_init(UART_BAUD_SELECT(UART_BAUD_RATE, F_CPU));//UART 초기화
    init_millis(F_CPU);//millis 함수 초기화
    LCD_Init(); //LCD initialization

    //LCD_Pos(0, 0); //Cursor 위치 0행 0열 지정
    //LCD_Str(fire_removed); //문자열 str을 LCD에 출력
	
	LCD_Pos(0, 0); //Cursor 위치 0행 0열 지정
	LCD_Str(text); //문자열 str을 LCD에 출력

    while (1) {

        if (!(PINB & (1 << GAS))) {
            lastmillis_fan = millis();
            //LCD_STR(gas_detected);
			
			lastmillis_gas = millis();

            //message = 2;
        }

        if (PINB & (1 << FIRE)) {
            lastmillis_sol = millis();
            lastmillis_pump = millis ();
			
			lastmillis_fire = millis();

            //message = 1;
        }

        if ((PINB & (1 << GAS)) && !(PINB & (1 << FIRE))) {
            //message = 0;
        }

         if (!(PINB & (1 << GAS)) && (PINB & (1 << FIRE))) {
			//message = 3;
        }

        //message = (millis () / 1000) % 4;

        if (millis () - lastmillis_fan < interval_fan) {
            PORTC |= (1 << FAN);
            servoPos = 90;
        } else {
            PORTC &= ~(1 << FAN);
            servoPos = 0;
        }

        if (millis () - lastmillis_sol < interval_sol) {
            PORTC |= (1 << SOL);
        } else {
            PORTC &= ~(1 << SOL);
        }

        if ((millis () - lastmillis_pump > interval_sol + interval_pause) && (millis () - lastmillis_pump < interval_sol + interval_pause + interval_pump)) {
            PORTC |= (1 << PUMP);
        } else {
            PORTC &= ~(1 << PUMP);
        }

        //servo
        if (servoPos != prevPos) {
            PWM(PWM_FREQ, map(servoPos, 0, 180, 2.5, 12.5));//value mapping and set PWM output
            prevPos = servoPos;
        }
		
		//lcd
        if (message != prevmessage) {
            switch (message) {
            case 0:
                LCD_Pos(1, 0); //Cursor 위치 0행 0열 지정
                LCD_Str(lcd_clear); //문자열 str을 LCD에 출력
                break;
            case 1:
                LCD_Pos(1, 0); //Cursor 위치 0행 0열 지정
                LCD_Str(fire_detected); //문자열 str을 LCD에 출력
                break;
            case 2:
                LCD_Pos(1, 0); //Cursor 위치 0행 0열 지정
                LCD_Str(gas_detected); //문자열 str을 LCD에 출력
                break;
            case 3:
                LCD_Pos(1, 0); //Cursor 위치 0행 0열 지정
                LCD_Str(fg_detected); //문자열 str을 LCD에 출력
                break;
            }
            prevmessage = message;
        }
		
		//uart
		if(millis () - lastmillis_gas < interval_send){
			uart1_putc('G');
			message = 2;
		}
		
		if(millis () - lastmillis_fire < interval_send){
			uart1_putc('F');
			message = 1;
		}
		
		if((millis () - lastmillis_fire < interval_send) && (millis () - lastmillis_gas < interval_send)){
			message = 3;
		}
		
		if(!(millis () - lastmillis_fire < interval_send) && !(millis () - lastmillis_gas < interval_send)){
			message = 0;
		}
    }
}
