
"""
Description: publisher for imy
Author: Victor & this lovely github post https://github.com/ev3dev-lang-java/ev3dev-lang-java/issues/356
Date
"""

import sys
from time import time

import struct as st
import binascii

# ros packages for publishing
import rospy
from sensor_msgs.msg import Imu, MagneticField

from tf.transformations import quaternion_from_euler
from dynamic_reconfigure.server import Server
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue

# libraries required for imu / circuitpython wrapper (I think it's circuitpython?)
import board
import adafruit_icm20x

imu_data = Imu()            # Filtered data
imu_raw = Imu()             # Raw IMU data
mag_msg = MagneticField()   # Magnetometer data

i2c = board.I2C()  # uses board.SCL and board.SDA
icm = adafruit_icm20x.ICM20948(i2c)

def get_imu_values():
    imu_raw = {
        'lin_acceleration': icm.acceleration,
        'gyro': icm.gyro,
        'magnetometer': icm.magnetic,
    }

    print(icm.acceleration, "<-- type of icm.acceleration:", type(icm.acceleration))
    print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2" % (icm.acceleration))
    print("Gyro X:%.2f, Y: %.2f, Z: %.2f rads/s" % (icm.gyro))
    print("Magnetometer X:%.2f, Y: %.2f, Z: %.2f uT" % (icm.magnetic))

    return imu_raw

# Main function
if __name__ == '__main__':
    # change "imu" to whatever you want Node name to be
    rospy.init_node("imu")

    # Sensor measurements publishers
    pub_data = rospy.Publisher('imu/data', Imu, queue_size=1)
    pub_raw = rospy.Publisher('imu/raw', Imu, queue_size=1)
    pub_mag = rospy.Publisher('imu/mag', MagneticField, queue_size=1)

    # Get parameters values
    frame_id = rospy.get_param('~frame_id', 'imu_link')
    frequency = rospy.get_param('~frequency', 100)

    rate = rospy.Rate(frequency)

    # Factors for unit conversions
    acc_fact = 1000.0
    mag_fact = 16.0
    gyr_fact = 900.0
    seq = 0

    while not rospy.is_shutdown():
        # Publish raw data
        imu_raw.header.stamp = rospy.Time.now()
        imu_raw.header.frame_id = frame_id
        imu_raw.header.seq = seq
        imu_raw.orientation_covariance[0] = -1
        imu_raw.linear_acceleration.x = float(st.unpack('h', st.pack('BB', buf[0], buf[1]))[0]) / acc_fact
        imu_raw.linear_acceleration.y = float(st.unpack('h', st.pack('BB', buf[2], buf[3]))[0]) / acc_fact
        imu_raw.linear_acceleration.z = float(st.unpack('h', st.pack('BB', buf[4], buf[5]))[0]) / acc_fact
        imu_raw.linear_acceleration_covariance[0] = -1
        imu_raw.angular_velocity.x = float(st.unpack('h', st.pack('BB', buf[12], buf[13]))[0]) / gyr_fact
        imu_raw.angular_velocity.y = float(st.unpack('h', st.pack('BB', buf[14], buf[15]))[0]) / gyr_fact
        imu_raw.angular_velocity.z = float(st.unpack('h', st.pack('BB', buf[16], buf[17]))[0]) / gyr_fact
        imu_raw.angular_velocity_covariance[0] = -1
        pub_raw.publish(imu_raw)

        # Publish filtered data
        imu_data.header.stamp = rospy.Time.now()
        imu_data.header.frame_id = frame_id
        imu_data.header.seq = seq
        imu_data.orientation.w = float(st.unpack('h', st.pack('BB', buf[24], buf[25]))[0])
        imu_data.orientation.x = float(st.unpack('h', st.pack('BB', buf[26], buf[27]))[0])
        imu_data.orientation.y = float(st.unpack('h', st.pack('BB', buf[28], buf[29]))[0])
        imu_data.orientation.z = float(st.unpack('h', st.pack('BB', buf[30], buf[31]))[0])
        imu_data.linear_acceleration.x = float(st.unpack('h', st.pack('BB', buf[32], buf[33]))[0]) / acc_fact
        imu_data.linear_acceleration.y = float(st.unpack('h', st.pack('BB', buf[34], buf[35]))[0]) / acc_fact
        imu_data.linear_acceleration.z = float(st.unpack('h', st.pack('BB', buf[36], buf[37]))[0]) / acc_fact
        imu_data.linear_acceleration_covariance[0] = -1
        imu_data.angular_velocity.x = float(st.unpack('h', st.pack('BB', buf[12], buf[13]))[0]) / gyr_fact
        imu_data.angular_velocity.y = float(st.unpack('h', st.pack('BB', buf[14], buf[15]))[0]) / gyr_fact
        imu_data.angular_velocity.z = float(st.unpack('h', st.pack('BB', buf[16], buf[17]))[0]) / gyr_fact
        imu_data.angular_velocity_covariance[0] = -1
        pub_data.publish(imu_data)

        # Publish magnetometer data
        mag_msg.header.stamp = rospy.Time.now()
        mag_msg.header.frame_id = frame_id
        mag_msg.header.seq = seq
        mag_msg.magnetic_field.x = float(st.unpack('h', st.pack('BB', buf[6], buf[7]))[0]) / mag_fact
        mag_msg.magnetic_field.y = float(st.unpack('h', st.pack('BB', buf[8], buf[9]))[0]) / mag_fact
        mag_msg.magnetic_field.z = float(st.unpack('h', st.pack('BB', buf[10], buf[11]))[0]) / mag_fact
        pub_mag.publish(mag_msg)

        seq = seq + 1
        rate.sleep()

    ser.close()
