import time

ARM_LOW_READ_RATE = 1 # reads 1 joint a second, every 3 seconds it will have read all 3

MOTOR_SHUTOFF_TIME = 1.0
MOTOR_TEST_FPS = 10
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
STATE_FROM_SERVER = {
    "last_get": time.time(),
    "velocity_limit": {
        "value": 330,
        "count": 0,
    },
    "motor_writes": 1,
    "write_every_frame": False,
    "arm_active": False,
    "invert": False,
	"high_send_rate": 20,
    "time_offset": 0,
}
STATE_FROM_SELF = {
    "motors": {
        "target": {
            "left": 0,
            "right": 0,
        },
        "current": {
            "left": 0,
            "right": 0,
        }
    },
    "arm": {
        "target": {
            "j1": 0,
            "j2": 0,
            "j3": 0,
        },
        "current": {
            "j1": 0,
            "j2": 0,
            "j3": 0,
        },
        "active": False,
    },
    "arm_reader_fps": 20,
    "arm_delay": 0.1,
    "motor_fps": 20,
}