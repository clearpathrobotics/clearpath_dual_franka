#!/usr/bin/env python3

# Software License Agreement (BSD)
#
# @author    Luis Camero <lcamero@clearpathrobotics.com>
# @copyright (c) 2024, Clearpath Robotics, Inc., All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of Clearpath Robotics nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Redistribution and use in source and binary forms, with or without
# modification, is not permitted without the express permission
# of Clearpath Robotics.
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # Packages
    pkg_clearpath_dual_franka_bringup = FindPackageShare('clearpath_dual_franka_bringup')

    # Launch Arguments
    arg_robot_urdf = DeclareLaunchArgument(
        'robot_urdf',
        default_value='/etc/clearpath/robot.urdf.xacro'
    )

    arg_namespace = DeclareLaunchArgument(
        'namespace',
        default_value='',
        description='Robot namespace'
    )

    # Launch Configurations
    robot_urdf = LaunchConfiguration('robot_urdf')
    namespace = LaunchConfiguration('namespace')

    # Launch Files
    launch_file_franka_manipulators = PathJoinSubstitution([
        pkg_clearpath_dual_franka_bringup,
        'launch',
        'manipulators.launch.py'
    ])

    launch_franka_manipulators = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(launch_file_franka_manipulators),
        launch_arguments=[
            ('robot_urdf', robot_urdf),
            ('use_sim_time', 'false'),
            ('namespace', namespace),
            ('control_delay', '0.0'),
            ('franka_0_control', 'false'),
            ('franka_1_control', 'true'),
            ('franka_parameters', 'franka_1_control.yaml'),
            ('franka_name', 'manipulators/franka_1')
        ]
    )

    node_franka_gripper = Node(
        name='arm_1_gripper_node',
        executable='franka_gripper_node',
        package='franka_gripper',
        namespace=PathJoinSubstitution([
            namespace,
            'manipulators/franka_1'
        ]),
        output='screen',
        remappings=[
            ('~/joint_states', PathJoinSubstitution(['/', namespace, 'platform', 'joint_states'])),
        ],
        parameters=[{
            'robot_ip': '192.168.131.41',
            'joint_names': ['arm_1_gripper_fr3_finger_joint1', 'arm_1_gripper_fr3_finger_joint2'],
            'state_publish_rate': 15,
            'feedback_publish_rate': 30,
            'default_speed': 0.1,
            'default_grasp_epsilon': {'inner': 0.005, 'outer': 0.005},
        }]
    )

    ld = LaunchDescription()
    ld.add_action(arg_robot_urdf)
    ld.add_action(arg_namespace)
    ld.add_action(launch_franka_manipulators)
    ld.add_action(node_franka_gripper)
    return ld
