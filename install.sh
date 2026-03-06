#!/bin/bash

# Get the current working directory (where the script is run from)
WORKSPACE_PATH=$(pwd)

# Ensure that the Dynamixel SDK submodule is initialized and updated
echo "Initializing and updating submodules..."
git submodule init
git submodule update

# Install gpiod for GPIO control
sudo apt install python3-gpiozero

# Install Dynamixel SDK from the submodule
echo "Installing Dynamixel SDK..."
cd "$WORKSPACE_PATH/lib/DynamixelSDK/python"
sudo pip3 install --break-system-packages . || { echo 'Installing Dynamixel SDK failed.'; exit 1; }

# Install mbot_servo_library
echo "Installing mbot_servo_library..."
cd "$WORKSPACE_PATH"
sudo pip3 install --break-system-packages . || { echo 'Installing mbot_servo_library failed.'; exit 1; }

echo "Installation completed successfully."