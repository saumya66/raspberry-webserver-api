import uos
import machine
import utime
import time
from machine import Pin, ADC, PWM

led1 = Pin(8,Pin.OUT)
led2 = Pin(6,Pin.OUT)
led3 = Pin(2,Pin.OUT)
led4 = Pin(3,Pin.OUT)
led5 = Pin(4,Pin.OUT)
led6 = Pin(5,Pin.OUT)


led1.value(1)#guestroom
led2.value(1)#swimmingpool
led3.value(1)#liftroom
led4.value(1)#loungeroom
led5.value(1)#bedroom
led6.value(1)#studyroom

A_1A_pin = 15                 # Motor drive module

a1 = Pin(15,Pin.OUT)
a2 = Pin(14,Pin.OUT)
en = Pin(13,Pin.OUT)

en.high()
a1.low()
a2.low()
    
recv_buf="" # receive buffer global variable

buzzer = PWM(Pin(9))
buzzer.freq(500)

pir = Pin(16,Pin.IN,Pin.PULL_UP)

print()
print("Machine: \t" + uos.uname()[4])
print("MicroPython: \t" + uos.uname()[3])
#buzzer.duty_u16(0)

while(True):
    if pir.value()==0:
        print("Buzzer On")
        buzzer.duty_u16(1000)
        utime.sleep(1.0)
    else:
        print("Waiting for movement")
        buzzer.duty_u16(0)
        utime.sleep(0.2)

uart0 = machine.UART(0, baudrate=115200)
print(uart0)


#common template of below functions : these are called with a command and .write() executes the command,
#and then the Wait_ESP_Rsp() is called to wait for some time and get the response back from pico and print it
def Rx_ESP_Data():
    recv=bytes()
    while uart0.any()>0:
        recv+=uart0.read(1)
    res=recv.decode('utf-8')
    return res

def Connect_WiFi(cmd, uart=uart0, timeout=3000):
    print("CMD: " + cmd)
    uart.write(cmd) 
    utime.sleep(7.0)
    Wait_ESP_Rsp(uart, timeout)
    print()

def Send_AT_Cmd(cmd, uart=uart0, timeout=3000):
    print("CMD: " + cmd)
    uart.write(cmd)
    Wait_ESP_Rsp(uart, timeout)
    print()
    
def Wait_ESP_Rsp(uart=uart0, timeout=3000):
    prvMills = utime.ticks_ms()
    resp = b""
    while (utime.ticks_ms()-prvMills)<timeout:
        if uart.any():
            resp = b"".join([resp, uart.read(1)])
    print("Wait_ESP_Rsp resp:")
    try:
        decoded = resp.decode()
        print("wft"+decoded)
    except UnicodeError:
        print(resp)
    
Send_AT_Cmd('AT\r\n')          #Test AT startup
Send_AT_Cmd('AT+GMR\r\n')      #Check version information
Send_AT_Cmd('AT+CIPSERVER=0\r\n')      #Check version information
Send_AT_Cmd('AT+RST\r\n')      #Check version information
Send_AT_Cmd('AT+RESTORE\r\n')  #Restore Factory Default Settings
Send_AT_Cmd('AT+CWMODE?\r\n')  #Query the WiFi mode
Send_AT_Cmd('AT+CWMODE=1\r\n') #Set the WiFi mode = Station mode
Send_AT_Cmd('AT+CWMODE?\r\n')  #Query the WiFi mode again
#Send_AT_Cmd('AT+CWLAP\r\n', timeout=10000) #List available APs
Connect_WiFi('AT+CWJAP="WIFI_NAME","WIFI_PASSWORD"\r\n', timeout=5000) #Connect to AP
Send_AT_Cmd('AT+CIFSR\r\n')    #Obtain the Local IP Address
utime.sleep(3.0)
Send_AT_Cmd('AT+CIPMUX=1\r\n')    #Obtain the Local IP Address
utime.sleep(1.0)
Send_AT_Cmd('AT+CIPSERVER=1,80\r\n')    #Obtain the Local IP Address
utime.sleep(1.0)
print ('Starting connection to ESP8266...')

while True:
    res =""
    res=Rx_ESP_Data()
    utime.sleep(2.0)
    if '+IPD' in res: # if the buffer contains IPD(a connection), then respond with HTML handshake
        id_index = res.find('+IPD')
        print("main resp:")
        print(res)
        get_index = res.find("GET")
        
        api = res[get_index+4:65].split(' ')[0]
        print(f'api : {api}')
        connection_id =  res[id_index+5]
        print("connectionId:" + connection_id)
        #from usb side to back : Green - GP2(4), White - GP3(5), Blue - GP5(7), Pink - GP6(9),Red- GP7(10)
        if(api=='/'):
            uart0.write('AT+CIPSEND='+connection_id+',200'+'\r\n')  #Send a HTTP response then a webpage as bytes the 108 is the amount of bytes you are sending, change this if you change the data sent below
            utime.sleep(1.0)
            uart0.write('HTTP/1.1 200 OK'+'\r\n')
            uart0.write('Content-Type: text/html'+'\r\n')
            uart0.write('Connection: close'+'\r\n')
            uart0.write(''+'\r\n')
            uart0.write('<!DOCTYPE HTML>'+'\r\n')
            uart0.write('<html>'+'\r\n')
            uart0.write('<body><center><h1>I\'m Raspberry Pi & I\'m listening...</h1></center>'+'\r\n')
            uart0.write('<center><a href="https://iot-smart-home-nine.vercel.app/">Go to Controller</a></center>'+'\r\n')
            uart0.write('</body></html>'+'\r\n')
            utime.sleep(4.0)
        elif(api=='/loungeroomon'):
            print("Lounge On!")
            led4.value(1)
        elif(api=='/loungeroomoff'):
            print("Lounge Off!")
            led4.value(0)
        elif(api=='/guestroomon'):
            print("Guest On!")
            led1.value(1)
        elif(api=='/guestroomoff'):
            print("Guest OFF!")
            led1.value(0)
        elif(api=='/studyroomon'):
            print("Living On!")
            led6.value(1)
        elif(api=='/studyroomoff'):
            print("Living OFF!")
            led6.value(0)   
        elif(api=='/bedroomon'):
            print("Bed On!")
            led5.value(1)
        elif(api=='/bedroomoff'):
            print("Bed OFF!")
            led5.value(0)
        elif(api=='/swimmingpoolon'):
            print("Swimmingpool On!")
            led2.value(1)
        elif(api=='/swimmingpooloff'):
            print("Swimmingpool OFF!")
            led2.value(0)
            liftroom
        elif(api=='/liftroomon'):
            print("Lift Room On!")
            led3.value(1)
        elif(api=='/liftroomoff'):
            print("Lift Room OFF!")
            led3.value(0)
        elif api == '/fanon':
            a1.low()
            a2.high()
        elif api == '/fanoff':
            a1.low()
            a2.low()
        elif api == '/buzzeron':
            buzzer.duty_u16(1000)
        elif api == '/buzzeroff':
            buzzer.duty_u16(0)

        
            
        Send_AT_Cmd('AT+CIPCLOSE='+ connection_id+'\r\n') # once file sent, close connection
        utime.sleep(2.0)
        recv_buf="" #reset buffer
        print ('Waiting For connection...')
