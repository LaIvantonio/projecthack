import wmi

c = wmi.WMI()
print(c.Win32_BIOS()[0].SerialNumber)