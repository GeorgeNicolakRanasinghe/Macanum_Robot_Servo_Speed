from pca9685 import PCA9685
import time

class Servo:
    def __init__(self):
        self.pwm_frequency = 50
        self.initial_pulse = 1500
        self.pwm_channel_map = {
            '0': 8,
            '1': 9,
            '2': 10,
            '3': 11,
            '4': 12,
            '5': 13,
            '6': 14,
            '7': 15
        }
        self.pwm_servo = PCA9685(0x40, debug=True)
        self.pwm_servo.set_pwm_freq(self.pwm_frequency)
        self.servo_speeds = {'0': 5, '1': 5, '2': 5, '3': 5, '4': 5, '5': 5, '6': 5, '7': 5}  # degrees per step
        self.current_angles = {'0': 90, '1': 90, '2': 90, '3': 90, '4': 90, '5': 90, '6': 90, '7': 90}
        for channel in self.pwm_channel_map.values():
            self.pwm_servo.set_servo_pulse(channel, self.initial_pulse)

    def set_servo_speed(self, channel: str, speed: int) -> None:
        """Set the speed for a servo channel (degrees per step). Lower = slower."""
        if channel not in self.pwm_channel_map:
            raise ValueError(f"Invalid channel: {channel}. Valid channels are {list(self.pwm_channel_map.keys())}.")
        self.servo_speeds[channel] = max(1, speed)  # Minimum 1 degree per step

    def increase_servo_speed(self, channel: str = '0', increment: int = 1) -> int:
        """Increase servo speed and return the new speed."""
        current_speed = self.servo_speeds.get(channel, 5)
        new_speed = current_speed + increment
        self.set_servo_speed(channel, new_speed)
        return new_speed

    def decrease_servo_speed(self, channel: str = '0', decrement: int = 1) -> int:
        """Decrease servo speed and return the new speed."""
        current_speed = self.servo_speeds.get(channel, 5)
        new_speed = max(1, current_speed - decrement)
        self.set_servo_speed(channel, new_speed)
        return new_speed

    def get_servo_speed(self, channel: str = '0') -> int:
        """Get current servo speed."""
        return self.servo_speeds.get(channel, 5)

    def set_servo_pwm(self, channel: str, target_angle: int, error: int = 10) -> None:
        target_angle = int(target_angle)
        if channel not in self.pwm_channel_map:
            raise ValueError(f"Invalid channel: {channel}. Valid channels are {list(self.pwm_channel_map.keys())}.")
        
        current_angle = self.current_angles[channel]
        speed = self.servo_speeds[channel]
        
        # Gradually move to target angle
        while current_angle != target_angle:
            if current_angle < target_angle:
                current_angle = min(current_angle + speed, target_angle)
            else:
                current_angle = max(current_angle - speed, target_angle)
            
            angle_to_set = current_angle
            pulse = 2500 - int((angle_to_set + error) / 0.09) if channel == '0' else 500 + int((angle_to_set + error) / 0.09)
            self.pwm_servo.set_servo_pulse(self.pwm_channel_map[channel], pulse)
            time.sleep(0.02)  # Small delay between steps (50ms)
        
        self.current_angles[channel] = target_angle

# Main program logic follows:
if __name__ == '__main__':
    print("Now servos will rotate to 90 degree.") 
    print("If they have already been at 90 degree, nothing will be observed.")
    print("Please keep the program running when installing the servos.")
    print("After that, you can press ctrl-C to end the program.")
    pwm_servo = Servo()
    try:
        while True:
            pwm_servo.set_servo_pwm('0', 90)
            pwm_servo.set_servo_pwm('1', 90)
    except KeyboardInterrupt:
        print("\nEnd of program")