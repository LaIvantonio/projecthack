from fastapi import FastAPI, HTTPException
import platform
import subprocess
import socket
import paramiko
import os
import wmi
import json
from typing import Dict, List
from fastapi.responses import HTMLResponse, JSONResponse
from jinja2 import Environment, FileSystemLoader
from fastapi.responses import StreamingResponse
from reportlab.pdfgen import canvas
from io import BytesIO


app = FastAPI()

env = Environment(loader=FileSystemLoader('templates'))

def get_ip_address() -> str:
    """Получение IP-адреса хоста."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # не подключаемся, просто используем для получения IP-адреса
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@app.get("/")
async def read_root():
    return {"message": "Welcome to the security audit API!"}

@app.get("/system-info")
async def read_system_info() -> Dict[str, str]:
    system_info = {
        "platform": platform.system(),
        "platform-release": platform.release(),
        "platform-version": platform.version(),
        "architecture": platform.machine(),
        "hostname": platform.node(),
        "ip-address": get_ip_address(),
        "processor": platform.processor(),
    }
    return system_info

@app.get("/devices")
async def read_devices() -> List[Dict[str, str]]:
    if platform.system() == "Windows":
        return await read_windows_devices()
    elif platform.system() == "Linux":
        return await read_linux_devices()
    else:
        return {"error": "Unsupported OS"}

# Функция для сбора информации об устройствах в Windows
async def read_windows_devices() -> List[Dict[str, str]]:
    c = wmi.WMI()
    devices = []
    for device in c.Win32_PnPEntity():
        # Определение типа устройства на основе его свойств
        device_type = "Unknown"
        if "keyboard" in (device.Name or "").lower():
            device_type = "Input Device"
        elif "mouse" in (device.Name or "").lower():
            device_type = "Input Device"
        elif "usb" in (device.Description or "").lower():
            device_type = "Connected Device"
        elif "drive" in (device.Description or "").lower():
            device_type = "Storage Device"
        # Добавьте дополнительные условия для определения типа устройства

        info = {
            "Name": device.Name or "",
            "DeviceID": device.DeviceID or "",
            "Status": device.Status or "",
            "Description": device.Description or "",
            "Manufacturer": device.Manufacturer or "",
            "Service": device.Service or "",
            "Type": device_type  # Добавленный тип устройства
        }
        devices.append(info)
    return devices


# Функция для сбора информации об устройствах в Linux
async def read_linux_devices() -> List[Dict[str, str]]:
    try:
        # Выполнение команды lshw и вывод в формате JSON
        result = subprocess.run(['lshw', '-json'], capture_output=True, text=True)
        # Парсинг JSON вывода
        devices = json.loads(result.stdout)
        return devices
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/installed-programs")
async def read_installed_programs() -> List[Dict[str, str]]:
    programs = []
    if platform.system() == "Windows":
        result = subprocess.run(["wmic", "product", "get", "name,version"], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')[1:]  # Skip the header line
        for line in lines:
            if line.strip() == '':
                continue
            name, version = line.split()[:2]
            programs.append({"name": name, "version": version})
    elif platform.system() == "Linux":
        result = subprocess.run(["dpkg", "-l"], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')[5:]  # Skip the header lines
        for line in lines:
            parts = line.split()
            if len(parts) >= 3:
                name, version = parts[1], parts[2]
                programs.append({"name": name, "version": version})
    else:
        programs = "Unsupported OS"
    return programs

@app.get("/hardware-serials")
async def read_hardware_serials() -> Dict[str, str]:
    serials = {}
    if platform.system() == "Windows":
        try:
            # Запускаем скрипт с правами администратора
            process = subprocess.Popen(["powershell", "Get-WmiObject -Class Win32_BIOS"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                # Парсим вывод скрипта
                output = stdout.decode()
                bios_serial = output.split("SerialNumber")[1].split("\r")[0].strip()
                serials["bios_serial"] = bios_serial
            else:
                # Выводим ошибку
                serials["bios_serial"] = f"Error: {stderr.decode()}"
        except Exception as e:
            serials["bios_serial"] = f"Error: {str(e)}"
    elif platform.system() == "Linux":
        try:
            output = subprocess.check_output(["sudo", "dmidecode", "-s", "bios-vendor"])
            bios_vendor = output.decode().strip()
            output = subprocess.check_output(["sudo", "dmidecode", "-s", "bios-version"])
            bios_version = output.decode().strip()
            output = subprocess.check_output(["sudo", "dmidecode", "-s", "system-serial-number"])
            system_serial = output.decode().strip()
            bios_serial = f"{bios_vendor} {bios_version} {system_serial}"
            serials["bios_serial"] = bios_serial
        except Exception as e:
            serials["bios_serial"] = f"Error: {str(e)}"
    else:
        serials["bios_serial"] = "Unsupported OS"
    return serials


@app.get("/report/html", response_class=HTMLResponse)
async def create_html_report():
    hardware_serials = await read_hardware_serials()
    print(hardware_serials)  # Добавьте эту строку
    template = env.get_template('report_template.html')
    data = {
        "system_info": await read_system_info(),
        "installed_programs": await read_installed_programs(),
        "hardware_serials": hardware_serials,
    }
    return template.render(data=data)




@app.get("/report/pdf")
async def create_pdf_report():
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setTitle("Security Audit Report")

    system_info = await read_system_info()
    installed_programs = await read_installed_programs()
    hardware_serials = await read_hardware_serials()

    # Заголовок отчета
    p.drawString(100, 800, "Security Audit Report")

    # Информация о системе
    p.drawString(100, 780, f"Hostname: {system_info['hostname']}")
    p.drawString(100, 760, f"IP Address: {system_info['ip-address']}")
    p.drawString(100, 740, f"Platform: {system_info['platform']} {system_info['platform-release']}")
    p.drawString(100, 720, f"Platform Version: {system_info['platform-version']}")
    p.drawString(100, 700, f"Architecture: {system_info['architecture']}")
    p.drawString(100, 680, f"Processor: {system_info['processor']}")

    # Серийные номера оборудования
    p.drawString(100, 650, "Hardware Serial Numbers:")
    p.drawString(120, 630, f"BIOS Serial: {hardware_serials['bios_serial']}")
    # Добавьте дополнительные серийные номера, если они доступны

    # Установленные программы
    p.drawString(100, 600, "Installed Programs:")
    y = 580
    for program in installed_programs:
        p.drawString(120, y, f"{program['name']} - {program['version']}")
        y -= 20
        # Переход на новую страницу, если достигнут низ страницы
        if y < 50:
            p.showPage()
            y = 800

    # Завершение страницы и сохранение PDF
    p.showPage()
    p.save()
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf")


# Функция для подключения к удаленной Linux-системе через SSH и сбора информации
def get_linux_system_info(hostname: str, username: str, password: str) -> Dict[str, str]:
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname, username=username, password=password)

    commands = {
        "platform": "uname -s",
        "platform-release": "uname -r",
        "platform-version": "uname -v",
        "architecture": "uname -m",
        "hostname": "hostname",
        # Добавьте другие команды, если необходимо
    }

    system_info = {}
    for key, command in commands.items():
        stdin, stdout, stderr = ssh_client.exec_command(command)
        system_info[key] = stdout.read().decode().strip()

    ssh_client.close()
    return system_info


# Функция для подключения к удаленной Windows-системе через WMI и сбора информации
def get_windows_system_info(hostname: str, username: str, password: str) -> Dict[str, str]:
    connection = wmi.WMI(computer=hostname, user=username, password=password)

    system_info = {}
    for os in connection.Win32_OperatingSystem():
        system_info["platform"] = "Windows"
        system_info["platform-release"] = os.Version
        system_info["platform-version"] = os.BuildNumber
        system_info["architecture"] = os.OSArchitecture
        system_info["hostname"] = os.CSName
        # Добавьте другие свойства, если необходимо

    return system_info

# Эндпоинт для получения информации о системе на удаленном компьютере
@app.get("/remote-system-info/{hostname}")
async def remote_system_info(hostname: str, username: str, password: str):
    try:
        c = wmi.WMI(computer=hostname, user=username, password=password)
        os = c.Win32_OperatingSystem()[0]
        system_info = {
            "system": os.Caption,
            "architecture": os.OSArchitecture,
            "version": os.Version,
            "service_pack": os.ServicePackMajorVersion,
            "build_number": os.BuildNumber,
            "install_date": os.InstallDate,
            "last_boot_up_time": os.LastBootUpTime,
            "number_of_users": len(c.Win32_ComputerSystem()[0].Users),
            "system_directory": os.SystemDirectory,
            "system_drive": os.SystemDrive,
            "total_physical_memory": os.TotalPhysicalMemory,
            }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=hostname, username=username, password=password)
        stdin, stdout, stderr = ssh.exec_command("cat /etc/*-release")
        output = stdout.read().decode()
        system_info = {
            "system": output.split("\n")[0].split("=")[1].strip(),
            "architecture": output.split("\n")[1].split("=")[1].strip(),
            "version": output.split("\n")[2].split("=")[1].strip(),
            "kernel_version": output.split("\n")[3].split("=")[1].strip(),
            "hostname": output.split("\n")[4].split("=")[1].strip(),
            "uptime": output.split("\n")[5].split("=")[1].strip(),
            "processor_type": output.split("\n")[6].split("=")[1].strip(),
            "processor_architecture": output.split("\n")[7].split("=")[1].strip(),
            "processor_cores": output.split("\n")[8].split("=")[1].strip(),
            "processor_threads": output.split("\n")[9].split("=")[1].strip(),
            "processor_model": output.split("\n")[10].split("=")[1].strip(),
            "processor_speed": output.split("\n")[11].split("=")[1].strip(),
            "total_physical_memory": output.split("\n")[12].split("=")[1].strip(),
            "total_swap_space": output.split("\n")[13].split("=")[1].strip(),
            }
        return system_info

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


        #  raise HTTPException(status_code=501, detail="Unsupported OS")


