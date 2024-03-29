import time
import dynamixel_sdk
import motors.consts

# https://emanual.robotis.com/docs/en/dxl/x/xm430-w210/
# https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_sdk/api_reference/python/python_porthandler/#python

DEVICE_NAME = "/dev/ttyUSB0"
PROTOCOL_VERSION = 2.0

BAUDRATE = 57600

ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_VELOCITY = 104
ADDR_PRESENT_VELOCITY = 128
ADDR_ERROR_CODE = 70

DYNAMIXEL_IDS = { # DYNAMIXEL_IDS[side] = [id1, id2]
    "left": [1, 3],
    "right": [2, 4],
}
ORIENTATIONS = { # ORIENTATIONS[side] = direction multiplier
    "left": 1,
    "right": -1,
}

class DynamixelController:
    def __init__(self):
        self.port_handler = dynamixel_sdk.PortHandler(DEVICE_NAME)
        self.packet_handler = dynamixel_sdk.PacketHandler(PROTOCOL_VERSION)

        if self.port_handler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port.")
        if self.port_handler.setBaudRate(BAUDRATE):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate.")

        self.speeds = { # speeds[side] = %
            "left": 0,
            "right": 0,
        }
        self.statuses = { # statuses[side] = %
            "left": 0,
            "right": 0,
        }

        self.velocity_limit = motors.consts.STATE_FROM_SERVER["velocity_limit"]["value"]

        self.to_writes = { # to_writes[id] = #
            1: 0,
            2: 0,
            3: 0,
            4: 0,
        }
        self.has_wrote = { # has_wrote[id] = #
            1: 0,
            2: 0,
            3: 0,
            4: 0,
        }
        self.min_writes = motors.consts.STATE_FROM_SERVER["motor_writes"]

    def close(self):
        self.update_speeds({
            "left": 0,
            "right": 0,
        })
        for _ in range(motors.consts.MAX_WRITES):
            self.try_write_speeds()

        time.sleep(motors.consts.CLOSE_WAIT_TIME)
        self.set_torque_status(False)
        time.sleep(motors.consts.CLOSE_WAIT_TIME)
        
        self.port_handler.closePort()

    def set_torque_status(self, status):
        status_code = 1 if status else 0
        for side_ids in DYNAMIXEL_IDS.values():
            for id in side_ids:
                dxl_comm_result, dxl_error = self.packet_handler.write1ByteTxRx(self.port_handler, id, ADDR_TORQUE_ENABLE, status_code)
                if dxl_comm_result != dynamixel_sdk.COMM_SUCCESS:
                    print(f"dxl_comm_result error {id} {self.packet_handler.getTxRxResult(dxl_comm_result)}")
                elif dxl_error != 0:
                    print(f"dxl_error error {id} {self.packet_handler.getRxPacketError(dxl_error)}")

    def update_speeds(self, speeds):
        self.speeds = speeds
        for id in self.to_writes:
            self.to_writes[id] = self.min_writes
            self.has_wrote[id] = 0

    def try_write_speeds(self):
        for side, side_ids in DYNAMIXEL_IDS.items():
            speed = self.speeds[side]
            orientation = ORIENTATIONS[side]
            power = int(speed * orientation * self.velocity_limit)

            for id in side_ids:
                if self.to_writes[id] > 0 and self.has_wrote[id] < motors.consts.MAX_WRITES:
                    success = True

                    dxl_comm_result, dxl_error = self.packet_handler.write4ByteTxRx(self.port_handler, id, ADDR_GOAL_VELOCITY, power)
                    if dxl_comm_result != dynamixel_sdk.COMM_SUCCESS:
                        print(f"dxl_comm_result error {id} {self.packet_handler.getTxRxResult(dxl_comm_result)}")
                        success = False
                    elif dxl_error != 0:
                        print(f"dxl_error error {id} {self.packet_handler.getRxPacketError(dxl_error)}")
                        success = False

                    self.has_wrote[id] += 1
                    if success:
                        self.to_writes[id] -= 1


    def update_status_and_check_errors(self):
        for side, side_ids in DYNAMIXEL_IDS.items():
            orientation = ORIENTATIONS[side]
            self.statuses[side] = 0

            for id in side_ids:
                dxl_present_velocity, _dxl_comm_result, _dxl_error = self.packet_handler.read4ByteTxRx(self.port_handler, id, ADDR_PRESENT_VELOCITY)
                error_code, _dxl_comm_result, _dxl_error = self.packet_handler.read1ByteTxRx(self.port_handler, id, ADDR_ERROR_CODE)
                
                # adjust for 2's complement
                if dxl_present_velocity > 0x7fffffff:
                    dxl_present_velocity = dxl_present_velocity - 4294967296
                # if dxl_present_current > 0x7fff:
                # 	dxl_present_current = dxl_present_current - 65536
                    
                self.statuses[side] += (dxl_present_velocity / self.velocity_limit * orientation) / 2
                    
                if error_code > 0:
                    print(f"error_code {id} {error_code} {self.packet_handler.getRxPacketError(error_code)}")
                    print(f"rebooting {id}")
                    self.packet_handler.reboot(self.port_handler, id)