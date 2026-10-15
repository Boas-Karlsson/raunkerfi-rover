from gpiozero import Device, Motor, DigitalOutputDevice, RotaryEncoder
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep, time

Device.pin_factory = PiGPIOFactory()

slp = DigitalOutputDevice(7)

motor_a = Motor(forward=12, backward=18)
motor_b = Motor(forward=13, backward=19)

encoder_a = RotaryEncoder(25, 20, max_steps=0)
encoder_b = RotaryEncoder(26, 5, max_steps=0)

PULSES_PER_REV = 692

POWER_A = 0.15
POWER_B = 0.14

INTERVAL = 0.5
TEST_TIME = 10.0

slp.on()

motor_a.forward(POWER_A)
motor_b.forward(POWER_B)

sleep(1.0)

last_a = encoder_a.steps
last_b = encoder_b.steps
last_time = time()

print("Time[s]\tMotor A RPM\tMotor B RPM")

try:
    for i in range(int(TEST_TIME / INTERVAL)):

        sleep(INTERVAL)

        now = time()

        current_a = encoder_a.steps
        current_b = encoder_b.steps

        delta_a = current_a - last_a
        delta_b = current_b - last_b

        dt = now - last_time

        rpm_a = abs((delta_a / PULSES_PER_REV) / dt * 60)
        rpm_b = abs((delta_b / PULSES_PER_REV) / dt * 60)

        elapsed = (i + 1) * INTERVAL

        print(f"{elapsed:.1f}\t{rpm_a:.1f}\t\t{rpm_b:.1f}")

        last_a = current_a
        last_b = current_b
        last_time = now

finally:
    motor_a.stop()
    motor_b.stop()
    slp.off()
