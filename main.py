from pysnmp import hlapi
import quicksnmp, csv, json, datetime, smtplib, ssl

ROUTER_FILE = "router.csv"
PC_FILE = "pc.csv"
OID_DESC = ".1.3.6.1.2.1.1.1.0"
OID_HOSTNAME = ".1.3.6.1.2.1.1.5.0"
OID_CISCO_MEMORY =".1.3.6.1.4.1.9.9.48.1.1.1.6.1"
OID_CISCO_CPU_LOAD = ".1.3.6.1.4.1.9.2.1.58.0"
OID_AKAGI_IN = ".1.3.6.1.2.1.2.2.1.10.5"
OID_AKAGI_OUT = ".1.3.6.1.2.1.2.2.1.16.5"
OID_AKAGI_SPEED = ".1.3.6.1.2.1.2.2.1.5.5"
OID_SHOUKAKU_IN = ".1.3.6.1.2.1.2.2.1.10.4"
OID_SHOUKAKU_OUT = ".1.3.6.1.2.1.2.2.1.16.4"
OID_SHOUKAKU_SPEED = ".1.3.6.1.2.1.2.2.1.5.4"
OID_PC_LOAD = ".1.3.6.1.4.1.2021.10.1.3.2"
OID_PC_USED_DISK = ".1.3.6.1.4.1.2021.9.1.9.1"
OID_PC_USED_RAM = ".1.3.6.1.4.1.2021.4.6.0"
OID_PC_TOTAL_RAM = ".1.3.6.1.4.1.2021.4.5.0"
OID_PC_IN = ".1.3.6.1.2.1.2.2.1.10.2"
OID_PC_OUT = ".1.3.6.1.2.1.2.2.1.16.2"
OID_PC_SPEED = ".1.3.6.1.2.1.2.2.1.5.2"
OID_TEST = "1.3.6.1.4.1.2021.4.11.0"

def main():
    warning_list = []
    a = []
    x = datetime.datetime.now()
    x = x.strftime("%c")
    a.append(x)
    router_list = read_csv(ROUTER_FILE)
    pc_list = read_csv(PC_FILE)
    for router in router_list:
        x, y = monitor_router(router)
        a.append(x)
        if len(y) > 0:
            warning_list.append(y)
    for pc in pc_list:
        x, y = monitor_pc(pc)
        a.append(x)
        if len(y) > 0:
            warning_list.append(y)
    print(a)
    print(warning_list)
    with open('log.json', 'a') as fout:
        fout.write(",\n")
        json.dump(a , fout)
    if len(warning_list) > 0:
        context = ssl.create_default_context()
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "raul.delacruz120@gmail.com"  # Enter your address
        receiver_email = "leytefuenteslucina@gmail.com"  # Enter receiver address
        password = "passworti"
        message = """Hi the error is."""+str(warning_list)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)


def read_csv(filename):
    with open(filename, "r") as f:
        reader = csv.reader(f)
        a = list(reader)
    return a

def monitor_router(router):
    ip_address = str(router[0])
    community = str(router[1])
    hostname = str(router[2])
    status = {}
    warning = []
    status.update({"Type": "Router"})
    status.update({"Host": hostname})
    status.update({"IP": ip_address}) 
    cpu = quicksnmp.get(ip_address, [OID_CISCO_CPU_LOAD], hlapi.CommunityData(community))
    ram = quicksnmp.get(ip_address, [OID_CISCO_MEMORY], hlapi.CommunityData(community))
    ramm = 90
    ramm = round(memory_percent_router(float(ram), 512.00),2)
    status.update({"CPU%": float(cpu)})
    status.update({"Memory%": round(memory_percent_router(float(ram), 512.00),2)})
    if hostname == "Akagi":
        i = quicksnmp.get(ip_address, [OID_AKAGI_IN], hlapi.CommunityData(community))
        o = quicksnmp.get(ip_address, [OID_AKAGI_OUT], hlapi.CommunityData(community))
        s = quicksnmp.get(ip_address, [OID_AKAGI_SPEED], hlapi.CommunityData(community))
        bandwidth = calculate_bandwidth(i,o,s,300)
        status.update({"Bandwidth": bandwidth})
    elif hostname == "Shoukaku":
        i = quicksnmp.get(ip_address, [OID_SHOUKAKU_IN], hlapi.CommunityData(community))
        o = quicksnmp.get(ip_address, [OID_SHOUKAKU_OUT], hlapi.CommunityData(community))
        s = quicksnmp.get(ip_address, [OID_SHOUKAKU_SPEED], hlapi.CommunityData(community))
        bandwidth = calculate_bandwidth(i,o,s,300)
        status.update({"Bandwidth": bandwidth})
    if float(cpu) >= 70.0 or ramm >= 80:
        warning.append("ip: "+ ip_address)
        warning.append("host: "+ hostname)
        warning.append("cpu: " + str(cpu))
        warning.append("memory: " + str(ram))
    return status, warning

def monitor_pc(pc):
    ip_address = str(pc[0])
    community = str(pc[1])
    hostname = str(pc[2])
    status = {}
    warning = []
    status.update({"Type": "PC"})
    status.update({"Host": hostname})
    status.update({"IP": ip_address})
    cpu = quicksnmp.get(ip_address, [OID_PC_LOAD], hlapi.CommunityData(community))
    used_ram = quicksnmp.get(ip_address, [OID_PC_USED_RAM], hlapi.CommunityData(community))
    total_ram = quicksnmp.get(ip_address, [OID_PC_TOTAL_RAM], hlapi.CommunityData(community))
    status.update({"CPU%": float(cpu)})
    ram = 80.0
    ram = round(memory_percent_pc(float(used_ram), float(total_ram)),2)
    status.update({"Memory%": round(memory_percent_pc(float(used_ram), float(total_ram)),2)})
    hdd = quicksnmp.get(ip_address, [OID_PC_USED_DISK], hlapi.CommunityData(community))
    status.update({"HDD%": int(hdd)})
    i = quicksnmp.get(ip_address, [OID_PC_IN], hlapi.CommunityData(community))
    o = quicksnmp.get(ip_address, [OID_PC_OUT], hlapi.CommunityData(community))
    s = quicksnmp.get(ip_address, [OID_PC_SPEED], hlapi.CommunityData(community))
    bandwidth = calculate_bandwidth(i,o,s,300)
    status.update({"Bandwidth": bandwidth})
    if float(cpu) >= 70.0 or ram >= 80 or int(hdd) >= 90:
        warning.append("ip: "+ ip_address)
        warning.append("host: "+ hostname)
        warning.append("cpu: " + str(cpu))
        warning.append("memory: " + str(ram))
        warning.append("hdd%: "+ str(hdd))
    return status, warning
    
def memory_percent_router(free_ram, total_ram):
    free_ram = (free_ram / 10**6)
    percent = (free_ram * 100)/total_ram
    return percent
    
def memory_percent_pc(used_ram, total_ram):
    used = (used_ram/ 10**6)
    percent = (used * 100)/(total_ram/10**6)
    return percent

def calculate_bandwidth(if_in, if_out, if_speed, seconds):
    bandwidth = (float(if_in) + float(if_out) * 8.0 *100.0)/(float(seconds) * float(if_speed))
    return bandwidth

main()
