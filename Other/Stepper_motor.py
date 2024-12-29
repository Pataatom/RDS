import time

import pigpio

pi = pigpio.pi()

control_pin = [26, 19, 13, 6]
for pin in control_pin:
    pi.set_mode(pin, pigpio.OUTPUT)
    pi.write(pin, 0)

full_step = [
    (1,0,0,0),
    (0,1,0,0),
    (0,0,1,0),
    (0,0,0,1),
]

half_step = [
    (1,0,0,0),
    (1,1,0,0),
    (0,1,0,0),
    (0,1,1,0),
    (0,0,1,0),
    (0,0,1,1),
    (0,0,0,1),
    (1,0,0,1),
]

double_step = [
    (1,1,0,0),
    (0,1,1,0),
    (0,0,1,1),
    (1,0,0,1),
]
try:
    while True:
        user = input("> ")
        if input().lower() in ("h", "f", "d"):
            if user == "h":
                seq = half_step
                steps = 8
            elif user == "f":
                seq = full_step
                steps = 4
            elif user == "d":
                seq = double_step
                steps = 4
            for i in range(512):
                for step in range(steps):
                    for pin in range(4):
                        pi.write(control_pin[pin], seq[step][pin])
                        time.sleep(0.1)

except KeyboardInterrupt:
    pass
pi.stop()
