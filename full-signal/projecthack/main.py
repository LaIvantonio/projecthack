from fastapi import FastAPI, HTTPException
import platform
import subprocess
import socket
import paramiko
import os
import json
import pandas as pd
from typing import Dict, List
from fastapi.responses import HTMLResponse, JSONResponse
from jinja2 import Environment, FileSystemLoader
from fastapi.responses import StreamingResponse
from reportlab.pdfgen import canvas
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware
from reportlab.pdfbase import pdfmetrics
from fastapi.responses import FileResponse

# Условный импорт для wmi и winreg
# Поддержка кроссплатформенности
if platform.system() == 'Windows':
    import wmi
    import winreg
else:
    wmi = None
    winreg = None

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Разрешенные источники
    allow_credentials=True,
    allow_methods=["*"],  # Разрешенные методы
    allow_headers=["*"],  # Разрешенные заголовки
)

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

def remove_black_square_char(text):
    return text.replace("■", "")
@app.get("/")
async def read_root():
    return {"message": "Welcome to the security audit API!"}

def get_processor_info():
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
        # Пример простого парсинга: получаем первую строку с model name
        model_name = next((line.split(': ')[1].strip() for line in cpuinfo.splitlines() if "model name" in line), "Unknown")
        return model_name
    except IOError:
        return "Unknown"

@app.get("/system-info")
async def read_system_info() -> Dict[str, str]:
    system_info = {
        "platform": platform.system(),
        "platform-release": platform.release(),
        "platform-version": platform.version(),
        "architecture": platform.machine(),
        "hostname": platform.node(),
        "ip-address": get_ip_address(),
        "processor": get_processor_info() if platform.system() == "Linux" else platform.processor(),
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
    if wmi is None:
        raise HTTPException(status_code=501, detail="WMI not available on this system.")
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
        # можно добавить доп условия для определения типа устройства

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
    devices = []
    try:
        # Выполнение команды lshw и вывод в формате JSON
        result = subprocess.run(['lshw', '-json'], capture_output=True, text=True, check=True)
        # Парсинг JSON вывода
        devices_info = json.loads(result.stdout)
        # Проходимся по всем устройствам и собираем необходимую информацию
        for device in devices_info:
            if 'children' in device:
                for child in device['children']:
                    device_info = {
                        "Name": child.get('product', ''),
                        "DeviceID": child.get('id', ''),
                        "Status": child.get('status', ''),
                        "Description": child.get('description', ''),
                        "Manufacturer": child.get('vendor', ''),
                        "Type": child.get('class', '')  # Тип устройства
                    }
                    devices.append(device_info)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"lshw command failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return devices

def get_installed_programs_from_registry():
    programs = []
    for registry_key in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        with winreg.OpenKey(registry_key, key_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_32KEY) as key:
            for i in range(0, winreg.QueryInfoKey(key)[0]):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey_name) as subkey:
                        name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                        programs.append({"name": name, "version": version})
                except EnvironmentError:
                    continue
    return programs

@app.get("/installed-programs")
async def read_installed_programs() -> List[Dict[str, str]]:
    if platform.system() == "Windows":
        if winreg is not None:
            return get_installed_programs_from_registry()
        else:
            raise HTTPException(status_code=501, detail="winreg module is not available on this system.")
    elif platform.system() == "Linux":
        result = subprocess.run(["dpkg", "-l"], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')[5:]  # Skip the header lines
        programs = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 3:
                name, version = parts[1], parts[2]
                programs.append({"name": name, "version": version})
        return programs
    else:
        raise HTTPException(status_code=501, detail="Unsupported OS")

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
            # Запускаем lshw с sudo для получения информации о системе
            output = subprocess.check_output(["sudo", "lshw", "-C", "system"], text=True)
            # Парсим вывод для поиска серийного номера
            for line in output.splitlines():
                if 'serial:' in line:
                    serials["bios_serial"] = line.split('serial:')[-1].strip()
                    break
            else:
                serials["bios_serial"] = "Serial number not found"
        except subprocess.CalledProcessError as e:
            serials["bios_serial"] = f"Error: {e.output}"
        except Exception as e:
            serials["bios_serial"] = f"Error: {str(e)}"
    else:
        serials["bios_serial"] = "Unsupported OS"
    return serials

@app.get("/report/html", response_class=HTMLResponse)
async def create_html_report():
    hardware_serials = await read_hardware_serials()
    print(hardware_serials)
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
    devices_info = await read_devices()

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
    p.drawString(120, 630, f"BIOS Serial: {hardware_serials.get('bios_serial', 'N/A')}")

    # Установленные программы
    p.drawString(100, 600, "Installed Programs:")
    y = 580
    for program in installed_programs:
        p.drawString(120, y, f"{program.get('name', 'N/A')} - {program.get('version', 'N/A')}")
        y -= 20
        if y < 50:
            p.showPage()
            y = 800

    # Добавление информации об устройствах в PDF
    p.drawString(100, y, "Devices:")
    y -= 20
    for device in devices_info:
        device_name = device.get('Name', 'N/A')
        device_type = device.get('Type', 'N/A')
        p.drawString(120, y, f"{device_name} - {device_type}")
        y -= 20
        if y < 50:  # Переход на новую страницу, если достигнут низ страницы
            p.showPage()
            y = 800

    # Завершение страницы и сохранение PDF
    p.showPage()
    p.save()
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf")

@app.get("/report/excel")
async def create_excel_report():
    # Gather your data
    installed_programs = await read_installed_programs()
    system_info = await read_system_info()
    hardware_serials = await read_hardware_serials()
    devices_info = await read_devices()

    print("Installed Programs Data:", installed_programs)
    print("System Info Data:", system_info)
    print("Hardware Serials Data:", hardware_serials)
    print("Devices Info Data:", devices_info)

    # создаём датафрейм в Pandas
    system_info_df = pd.DataFrame([system_info])
    installed_programs_df = pd.DataFrame(installed_programs)
    hardware_serials_df = pd.DataFrame([hardware_serials])
    devices_info_df = pd.DataFrame(devices_info)

    # Создаём Pandas excel используя openpyxl как "движок"
    excel_file = "Security_Audit_Report.xlsx"
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # На каждый лист вынесены различные данные
        system_info_df.to_excel(writer, sheet_name='System Information', index=False)
        installed_programs_df.to_excel(writer, sheet_name='Installed Programs', index=False)
        hardware_serials_df.to_excel(writer, sheet_name='Hardware Serials', index=False)
        devices_info_df.to_excel(writer, sheet_name='Devices', index=False)

    # Возращаем готовый файл клиенту
    return FileResponse(path=excel_file, filename=excel_file, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')