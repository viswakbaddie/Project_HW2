from machine import Pin, I2C
from fifo import Fifo
from ssd1306 import SSD1306_I2C
from time import ticks_ms 


class Encoder:
    def __init__(self, rot_a, rot_b, btn):
       self.a = Pin(rot_a, mode = Pin.IN, pull = Pin.PULL_UP)
       self.b = Pin(rot_b, mode = Pin.IN, pull = Pin.PULL_UP)
       self.btn = Pin(btn, mode = Pin.IN, pull = Pin.PULL_UP)
       self.prev_tick = 0
       
       self.fifo = Fifo(30, typecode = 'i')
       self.a.irq(handler = self.handler, trigger = Pin.IRQ_RISING, hard = True)
       self.btn.irq(handler = self.btn_handler, trigger = Pin.IRQ_RISING, hard = True)
            
            
    def btn_handler(self, pin):
        curr_tick = ticks_ms()
    
        if curr_tick - self.prev_tick > 50:
            self.fifo.put(2)
        
        self.prev_tick = curr_tick
        
        
    def handler(self, pin):       
        if self.b():
            self.fifo.put(-1)
        
        else:
            self.fifo.put(1)
                
                
i2c  = I2C(1, scl = Pin(15), sda = Pin(14), freq = 400000)
oled = SSD1306_I2C(128, 64, i2c)
oled.fill(0)

rot = Encoder(10, 11, 12)

leds = [Pin(22, Pin.OUT), Pin(21, Pin.OUT), Pin(20, Pin.OUT)]
led_states  = [led.value() for led in leds]

led_hovers  = [1, 0, 0]
hovered_led = 0

def show_text(states, hovers):
    oled.fill(0)
    
    for i in range(3):
        text = f"{'<' if hovers[i] else ' '}LED{i + 1}-{'ON' if states[i] else 'OFF'}{'>' if hovers[i] else ' '}"
        oled.text(text, 25, 25 * i, 1)
        
    oled.show()
    

show_text(led_states, led_hovers)
while True:
    if rot.fifo.has_data():
        action = rot.fifo.get()
        
        if action == 2:
            led = leds[hovered_led]
            led.toggle()
            
            led_states[hovered_led] = led.value()
            
        
        elif action == 1:
            if not led_hovers[2]:
                led_hovers[hovered_led] = 0
                hovered_led += 1
                led_hovers[hovered_led] = 1
                
        
        elif action == -1:
            if not led_hovers[0]:
                led_hovers[hovered_led] = 0
                hovered_led -= 1
                led_hovers[hovered_led] = 1
                
        show_text(led_states, led_hovers)

