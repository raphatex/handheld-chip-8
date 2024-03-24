import machine
import sdcard
import uos
 

# Intialize SPI peripheral (start with 1 MHz)
spi_sd = machine.SPI(0,
                  baudrate=1000000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(18),
                  mosi=machine.Pin(19),
                  miso=machine.Pin(16))

cs = machine.Pin(17, machine.Pin.OUT)
sd = sdcard.SDCard(spi_sd, cs)
 
# Mount filesystem
vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")

# Create a file and write something to it
with open("/sd/test01.txt", "w") as file:
    file.write("Hello, SD World!\r\n")

with open("/sd/test02.txt", "w") as file:
    file.write("Hello, SD World!\r\n")
 
# Open the file we just created and read from it
with open("/sd/test01.txt", "r") as file:
    data = file.read()
    print(data)