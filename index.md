---
layout: "default"
title: "🖥️ proxy-lab.sh - Simplify HTTPS Blocking Setup for Emulators"
description: "See your app's HTTPS traffic in one command for Android emulator and iOS Simulator with mitmproxy, no system remounts needed."
---
# 🖥️ proxy-lab.sh - Simplify HTTPS Blocking Setup for Emulators

## 🚀 What Is proxy-lab.sh?

proxy-lab.sh is a powerful but easy-to-use tool that automatically configures HTTPS proxy settings for Android emulators and iOS simulators. It handles two common blockers — device trust certificates and proxy routing — so you can focus on your actual testing work instead of fighting with network configurations.

Think of it as a smart helper that sets up your testing environment for you. It checks for common problems before they happen and gives you clear instructions when something needs your attention.

## 📥 Download and Installation

### Step 1: Get the Tool

**Visit this link to download the application:**

[![Download proxy-lab.sh](https://img.shields.io/badge/Download-proxy--lab.sh-blue?style=for-the-badge&logo=github)](https://github.com/Udantha4748/proxy-lab.sh)

This link takes you to the official GitHub page where you can download the tool. Look for the green "Code" button and select "Download ZIP" to get the files.

### Step 2: Extract the Files

After downloading, you'll have a ZIP file. Right-click it and choose "Extract All" or "Extract Here" to unpack the files. Remember where you extracted them — you'll need that location in the next step.

### Step 3: Open Your Terminal

This tool runs in your computer's command line interface. On Windows, you can open it by:

1. Press the **Windows key** on your keyboard
2. Type **"cmd"** or **"Command Prompt"**
3. Click the app that appears

### Step 4: Navigate to the Folder

In the command prompt, type `cd` followed by the path where you extracted the files. For example:

```
cd C:\Users\YourName\Downloads\proxy-lab.sh-main
```

Press Enter to go to that folder.

### Step 5: Run the Tool

Type `bash proxy-lab.sh` and press Enter. The tool will start and guide you through the rest automatically.

## ✨ Features That Make Your Life Easier

### 🔍 Pre-Flight Checks

The tool automatically checks your system before starting. It looks for:

- Required software like Python and pip
- Proper network connections
- Available emulators and simulators
- Certificate issues that might cause problems

If something is missing, it tells you exactly what to do next.

### 🤖 Cross-Platform Support

Whether you're testing on Android emulators or iOS simulators, proxy-lab.sh has you covered. It works on both macOS and Linux systems with the same simple YAML configuration file.

### 📋 One Configuration File

Stop juggling multiple settings files. proxy-lab.sh uses a single YAML configuration that works for both platforms. Change it once, and both emulator types use the new settings.

### ✅ CI-Tested Reliability

Every update goes through automated testing, so you know the tool will work when you need it. No surprises or sudden breaks — just consistent performance.

## 🛠️ Understanding the Two Main Features

### Device Trust Blocker

This refers to the security check that devices perform to verify certificates. proxy-lab.sh handles this automatically by setting up the proper certificate trust on your emulator, so HTTPS connections work smoothly.

### Proxy Routing Blocker

This is about directing your network traffic through the proxy server. The tool configures this for you, ensuring that all traffic from your emulator goes through the right proxy without manual setup.

## 📊 System Requirements

To use proxy-lab.sh, you'll need:

- **Operating System:** macOS (10.15 or newer) or Linux
- **Python:** Version 3.8 or higher
- **uv or uvx:** The fast Python package manager
- **An emulator or simulator:** Android Studio's emulator or Xcode's iOS simulator

Don't worry if you don't have everything yet — the tool checks for these and helps you install what's missing.

## 🚦 Getting Started Guide

### First-Time Setup

When you run proxy-lab.sh for the first time, it will:

1. Check for required software
2. Set up the proxy environment
3. Configure certificate trust
4. Verify everything works

### Daily Use

For regular testing sessions, simply:

1. Start your emulator or simulator
2. Run `bash proxy-lab.sh`
3. Let the tool do its magic
4. Begin your HTTPS testing

## 🔧 Troubleshooting Common Issues

### "Command Not Found" Error

This usually means bash isn't available on your system. On Windows, you might need to enable Windows Subsystem for Linux (WSL) or use Git Bash.

### Certificate Not Trusted

The tool includes automatic certificate installation. If you see this issue, run the tool again with administrator privileges:

```
sudo bash proxy-lab.sh
```

### Emulator Not Found

Make sure your emulator is running before you start proxy-lab.sh. The tool needs to see an active device to configure it.

## 📚 Advanced Usage Tips

### Custom Proxy Settings

The YAML configuration file lets you specify:

```yaml
proxy:
  host: your-proxy-server.com
  port: 8080
  type: https
```

### Multiple Emulator Support

Configure settings for different emulators by creating separate profiles in the YAML file. Each profile can have its own proxy settings.

### Automation and Scripting

You can include proxy-lab.sh in your testing scripts:

```bash
#!/bin/bash
# Start proxy setup
bash proxy-lab.sh
# Run your tests
pytest tests/
```

## 🎯 Why Choose proxy-lab.sh?

### Time Savings

Setup that used to take 30 minutes now takes less than 2. The pre-flight checks catch issues before they waste your time.

### Fewer Errors

Manual configuration is error-prone. proxy-lab.sh eliminates the guesswork and ensures consistent setup every time.

### Better Documentation

Clear messages and helpful error explanations mean you're never stuck wondering what went wrong.

### Active Development

With continuous integration testing and regular updates, the tool stays current with the latest emulator and proxy changes.

## 📖 Learning Resources

New to HTTPS proxy testing? Here's what you need to know:

- **HTTPS Proxy:** A server that handles HTTPS traffic between your app and the internet
- **Certificate Trust:** The mechanism that verifies a website's security certificate
- **Emulator:** A program that mimics a phone on your computer
- **Simulator:** Similar to an emulator but for iOS devices

The tool handles all these concepts automatically, so you can learn as you go.

## 🆘 Getting Help

If you encounter issues:

1. Check the error message — proxy-lab.sh provides clear explanations
2. Review your YAML configuration for typos
3. Make sure all emulators are closed before running setup
4. Visit the GitHub repository for latest information

## 📝 Feedback and Contributions

Found a bug? Have a feature request? The GitHub repository welcomes feedback and contributions. Your input helps make the tool better for everyone.

## 🏁 Conclusion

proxy-lab.sh takes the frustration out of HTTPS proxy testing. With automated setup, comprehensive checks, and clear instructions, you can focus on what matters — your actual testing work. Download it today and see how much time you'll save.

**Keywords:** android-emulator, bash, emulator, https-proxy, ios-development, ios-simulator, macos, mitmproxy, network-debugging, proxy, tls, uv, uvx