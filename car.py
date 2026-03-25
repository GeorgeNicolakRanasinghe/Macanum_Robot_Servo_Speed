from ultrasonic import Ultrasonic
from motor import Ordinary_Car
from servo import Servo
from infrared import Infrared
from adc import ADC
import time
import math
import threading
import sys

class Car:
    def __init__(self, servo_speed=5):
        self.servo = None
        self.sonic = None
        self.motor = None
        self.infrared = None
        self.adc = None
        self.servo_speed = servo_speed
        self.car_record_time = time.time()
        self.car_sonic_servo_angle = 30
        self.car_sonic_servo_dir = 1
        self.car_sonic_distance = [15, 15, 15]
        self.time_compensate = 3 #Depend on your own car,If you want to get the best out of the rotation mode, change the value by experimenting.
        self.running = True
        self.start()
    def start(self):  
        if self.servo is None:
            self.servo = Servo()
            self.servo.set_servo_speed('0', self.servo_speed)
        if self.sonic is None:
            self.sonic = Ultrasonic()
        if self.motor is None:
            self.motor = Ordinary_Car()
        if self.infrared is None:
            self.infrared = Infrared()
        if self.adc is None:
            self.adc = ADC() 

    def close(self):
        self.motor.set_motor_model(0,0,0,0)
        self.sonic.close()
        self.motor.close()
        self.infrared.close()
        self.adc.close_i2c()
        self.servo = None
        self.sonic = None
        self.motor = None
        self.infrared = None
        self.adc = None

    def run_motor_ultrasonic(self, distance):
        if (distance[0] < 15 and distance[1] < 15 and distance[2] <15) or distance[1] < 15 :
            self.motor.set_motor_model(-1450,-1450,-1450,-1450) 
            time.sleep(0.1)   
            if distance[0] < distance[2]:
                self.motor.set_motor_model(1450,1450,-1450,-1450)
            else :
                self.motor.set_motor_model(-1450,-1450,1450,1450)
        elif distance[0] < 15 and distance[1] < 15:
            self.motor.set_motor_model(1500,1500,-1500,-1500)
        elif distance[2] < 15 and distance[1] < 15:
            self.motor.set_motor_model(-1500,-1500,1500,1500)
        elif distance[0] < 10 :
            self.motor.set_motor_model(2000,2000,-500,-500)
            if distance[0] < 5 :
                self.motor.set_motor_model(1500,1500,-1000,-1000)
        elif distance[2] < 10 :
            self.motor.set_motor_model(-500,-500,2000,2000)
            if distance[2] < 5 :
                self.motor.set_motor_model(-1500,-1500,1500,1500)
        else :
            self.motor.set_motor_model(600,600,600,600)

    def mode_ultrasonic(self):
        if (time.time() - self.car_record_time) > 0.2:
            self.car_record_time = time.time()
            self.servo.set_servo_pwm('0', self.car_sonic_servo_angle)
            if self.car_sonic_servo_angle == 30:
                self.car_sonic_distance[0] = self.sonic.get_distance()
            elif self.car_sonic_servo_angle == 90:
                self.car_sonic_distance[1] = self.sonic.get_distance()
            elif self.car_sonic_servo_angle == 150:
                self.car_sonic_distance[2] = self.sonic.get_distance()
            #print("L:{}, M:{}, R:{}".format(self.car_sonic_distance[0], self.car_sonic_distance[1], self.car_sonic_distance[2]))
            self.run_motor_ultrasonic(self.car_sonic_distance)
            if self.car_sonic_servo_angle <= 30:
                self.car_sonic_servo_dir = 1
            elif self.car_sonic_servo_angle >= 150:
                self.car_sonic_servo_dir = 0
            if self.car_sonic_servo_dir == 1:
                self.car_sonic_servo_angle += 60
            elif self.car_sonic_servo_dir == 0:
                self.car_sonic_servo_angle -= 60

    def mode_infrared(self):
        if (time.time() - self.car_record_time) > 0.2:
            self.car_record_time = time.time()
            infrared_value = self.infrared.read_all_infrared()
            #print("infrared_value: " + str(infrared_value))
            if infrared_value == 2:
                self.motor.set_motor_model(800,800,800,800)
            elif infrared_value == 4:
                self.motor.set_motor_model(-1500,-1500,2500,2500)
            elif infrared_value == 6:
                self.motor.set_motor_model(-2000,-2000,4000,4000)
            elif infrared_value == 1:
                self.motor.set_motor_model(2500,2500,-1500,-1500)
            elif infrared_value == 3:
                self.motor.set_motor_model(4000,4000,-2000,-2000)
            elif infrared_value == 7:
                self.motor.set_motor_model(0,0,0,0)

    def mode_light(self):
        if (time.time() - self.car_record_time) > 0.2:
            self.car_record_time = time.time()
            self.motor.set_motor_model(0,0,0,0)
            L = self.adc.read_adc(0)
            R = self.adc.read_adc(1)
            #print("L: {}, R: {}".format(L, R))
            if L < 2.99 and R < 2.99 :
                self.motor.set_motor_model(600,600,600,600)
            elif abs(L-R)<0.15:
                self.motor.set_motor_model(0,0,0,0)
            elif L > 3 or R > 3:
                if L > R :
                    self.motor.set_motor_model(-1200,-1200,1400,1400)
                elif R > L :
                    self.motor.set_motor_model(1400,1400,-1200,-1200)

    def mode_rotate(self, n):
        angle = n
        bat_compensate = 7.5 / (self.adc.read_adc(2) * (3 if self.adc.pcb_version == 1 else 2))
        while True:
            W = 2000
            VY = int(2000 * math.cos(math.radians(angle)))
            VX = -int(2000 * math.sin(math.radians(angle)))
            FR = VY - VX + W
            FL = VY + VX - W
            BL = VY - VX - W
            BR = VY + VX + W
            print("rotating")
            self.motor.set_motor_model(FL, BL, FR, BR)
            time.sleep(5*self.time_compensate*bat_compensate/1000)
            angle -= 5

    def listen_for_speed_commands(self):
        """Listen for keyboard input to adjust servo speed."""
        print("\n--- Speed Control Keys ---")
        print("Press '+' to increase servo speed")
        print("Press '-' to decrease servo speed")
        print("Press 'q' to quit")
        print("------------------------\n")
        
        try:
            import select
            import tty
            import termios
            
            old_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
            
            while self.running:
                rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
                if rlist:
                    ch = sys.stdin.read(1)
                    if ch == '+':
                        new_speed = self.servo.increase_servo_speed('0', 1)
                        print(f"Servo speed increased to: {new_speed} degrees/step")
                    elif ch == '-':
                        new_speed = self.servo.decrease_servo_speed('0', 1)
                        print(f"Servo speed decreased to: {new_speed} degrees/step")
                    elif ch.lower() == 'q':
                        print("Stopping motors and closing...")
                        self.running = False
                        self.motor.set_motor_model(0,0,0,0)  # Stop motors immediately
                        time.sleep(0.5)  # Give motor command time to process
                        break
        except Exception as e:
            print(f"Note: Speed control not available on this platform: {e}")
            print("You can still change speed by restarting with --speed argument")
        finally:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            except:
                pass

def test_car_sonic(servo_speed=5):
    car = Car(servo_speed=servo_speed)
    # Start speed control listener in a separate thread
    speed_thread = threading.Thread(target=car.listen_for_speed_commands, daemon=True)
    speed_thread.start()
    
    try:
        while car.running:
            car.mode_ultrasonic()
    except KeyboardInterrupt:
        car.running = False
    
    car.motor.set_motor_model(0,0,0,0)  # Ensure motors stop
    time.sleep(0.2)
    car.close()
    print("\nEnd of program")

def test_car_infrared(servo_speed=5):
    car = Car(servo_speed=servo_speed)
    # Start speed control listener in a separate thread
    speed_thread = threading.Thread(target=car.listen_for_speed_commands, daemon=True)
    speed_thread.start()
    
    try:
        while car.running:
            car.mode_infrared()
    except KeyboardInterrupt:
        car.running = False
    
    car.motor.set_motor_model(0,0,0,0)  # Ensure motors stop
    time.sleep(0.2)
    car.close()
    print("\nEnd of program")

def test_car_light(servo_speed=5):
    car = Car(servo_speed=servo_speed)
    # Start speed control listener in a separate thread
    speed_thread = threading.Thread(target=car.listen_for_speed_commands, daemon=True)
    speed_thread.start()
    
    try:
        print("Program is starting...")
        while car.running:
            car.mode_light()
    except KeyboardInterrupt:
        car.running = False
    
    car.motor.set_motor_model(0,0,0,0)  # Ensure motors stop
    time.sleep(0.2)
    car.close()
    print("\nEnd of program")

def test_car_rotate(servo_speed=5):
    car = Car(servo_speed=servo_speed)
    # Start speed control listener in a separate thread
    speed_thread = threading.Thread(target=car.listen_for_speed_commands, daemon=True)
    speed_thread.start()
    
    print("Program is starting...")
    try:
        while car.running:
            car.mode_rotate(0)
    except KeyboardInterrupt:
        car.running = False
    
    car.motor.set_motor_model(0,0,0,0)  # Ensure motors stop
    time.sleep(0.2)
    print ("\nEnd of program")
    car.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Parameter error: Please assign the device")
        exit()
    
    # Parse servo speed argument
    servo_speed = 5  # Default speed
    if '--speed' in sys.argv:
        try:
            speed_index = sys.argv.index('--speed')
            if speed_index + 1 < len(sys.argv):
                servo_speed = int(sys.argv[speed_index + 1])
                print(f"Servo speed set to: {servo_speed} degrees per step")
        except (ValueError, IndexError):
            print("Invalid speed value. Using default speed of 5.")
    
    if sys.argv[1] == 'Sonic' or sys.argv[1] == 'sonic':
        test_car_sonic(servo_speed=servo_speed)
    elif sys.argv[1] == 'Infrared' or sys.argv[1] == 'infrared':
        test_car_infrared(servo_speed=servo_speed)
    elif sys.argv[1] == 'Light' or sys.argv[1] == 'light':
        test_car_light(servo_speed=servo_speed)
    elif sys.argv[1] == 'Rotate' or sys.argv[1] == 'rotate':
        test_car_rotate(servo_speed=servo_speed)