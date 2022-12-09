/*
 * main.c
 *
 * Created: 11/17/2021 6:38:15 PM
 *  Author: Flanon
 */

#define F_CPU 16000000

#include <avr/io.h>
#include <util/delay.h>

#define LCD_WDATA PORTF//LCD 데이터 I/O 정의
#define LCD_WINST PORTF//LCD 명령어 I/O 정의(데이터 I/O 와 동일)
#define LCD_CTRL PORTG//LCD 제어 I/O 정의

//LCD 제어 I/O bit위치 정의
#define LCD_EN 0
#define LCD_RW 1
#define LCD_RS 2

//출력 initialization 함수
void LCD_PORT_Init(void)
{
    DDRF = 0xFF;//PORTB를 출력으로
    DDRG = 0x0F;//PORTA의 하위 nibble를 출력으로
}

//LCD 데이터 함수
void LCD_Data(unsigned char ch)
{
    //RS=1, RW=0(Write Data to Display Data Resistor)
	LCD_CTRL |= (1 << LCD_RS);
    LCD_CTRL &= ~(1 << LCD_RW);
    //data load
    LCD_CTRL |= (1 << LCD_EN);//LCD Enable
    _delay_us(50);//시간지연
    LCD_WDATA = ch;//데이터 출력
    _delay_us(50);//시간지연
    LCD_CTRL &= ~(1 << LCD_EN);//LCD Disable
}

//LCD 제어 함수
void LCD_Comm(unsigned char ch)
{
    //RS=0, RW=0(Write Data to Instruction Resistor)
	LCD_CTRL &= ~(1 << LCD_RS);
    LCD_CTRL &= ~(1 << LCD_RW);
    //data load
    LCD_CTRL |= (1 << LCD_EN);//LCD Enable
    _delay_us(50);//시간지연
    LCD_WINST = ch;//명령어 쓰기
    _delay_us(50);//시간지연
    LCD_CTRL &= ~(1 << LCD_EN);//LCD Disable
}

//Delay utility 함수
void LCD_Delay(unsigned char ms)
{
    for (int i = 0; i < ms; i++)
        _delay_ms(1);
}

//단일 문자를 출력하는 함수
void LCD_Char(unsigned char c)
{
    LCD_Data(c);
    _delay_ms(1);
}

//문자열을 출력하는 함수
void LCD_Str(unsigned char *str)
{
    while (*str != 0) {//문자열의 마지막에 도달할 때 까지
        LCD_Char(*str);//해당 문자 출력
        str++;//다음 문자에 접근
		//_delay_ms(10);
    }
}

//Cursor 위치를 지정하는 함수
void LCD_Pos(unsigned char row, unsigned char col)
{
    LCD_Comm(0x80 | (row * 0x40 + col));//row=가로행(0-1), col=세로열(0-15)
}

//Display Clear 함수
void LCD_Clear(void)
{
    LCD_Comm(0x01);//Display clear
    LCD_Delay(2);
}

//LCD initialization 함수
void LCD_Init(void) // LCD 초기화
{
    LCD_PORT_Init();//LCD 출력 initialization
    LCD_Comm(0x38);//Set 8bit 2Line 5x7 dots
    LCD_Delay(2);
    LCD_Comm(0x0c);//Display & Cursor On
    LCD_Delay(2);
    LCD_Comm(0x06);//Entry Mode(Cursor move)
    LCD_Delay(2);
    LCD_Clear();//Display Clear
}

/*
void main(void)
{
    unsigned char str[] = "LCD Test..";//사용자 지정 문자열
    LCD_Init(); //LCD initialization
    LCD_Pos(0, 0); //Cursor 위치 0행 0열 지정
    LCD_Str(str); //문자열 str을 LCD에 출력
    while (1) {
    }
}
*/
