import threading
from napalm import get_network_driver
import queue


def search_network(username,password,keyword1,keyword2,operator,case_sensitive,devices):

    # Global queue for storing the data for all threads outputs
    global data_queue
    data_queue = queue.Queue()

    # List of IPs of the devices
    IPs_list = list(devices.keys())

    # List of vendors of the devices
    vendor_list = list(devices.values())

    # Devices information including IP, username, password to be used in NAPALM
    devices_info = [ {"hostname": IPs_list[i], "username":username,"password": password} for i in range(len(IPs_list))]

    # Maximum 5 threads to work simultaneously
    thread_num = 5

    device_count = len(devices)

    # Dividing the list of devices to groups for Threading
    if device_count < 5:
        device_per_thread = 1
    else:
        device_per_thread = (device_count//thread_num) + (device_count%thread_num)

    group1 = devices_info[0:device_per_thread]
    group2 = devices_info[(device_per_thread):(2*device_per_thread)]
    group3 = devices_info[(2*device_per_thread):(3*device_per_thread)]
    group4 = devices_info[(3*device_per_thread):(4*device_per_thread)]
    group5 = devices_info[(4*device_per_thread):(5*device_per_thread)]

    # Dividing the vendor list of devices for Threading
    vendor_list1 = vendor_list[0:device_per_thread]
    vendor_list2 = vendor_list[(device_per_thread):(2*device_per_thread)]
    vendor_list3 = vendor_list[(2*device_per_thread):(3*device_per_thread)]
    vendor_list4 = vendor_list[(3*device_per_thread):(4*device_per_thread)]
    vendor_list5 = vendor_list[(4*device_per_thread):(5*device_per_thread)]


    # Create new Threads
    thread1 = threading.Thread(target=thread_run, args=(keyword1,keyword2,operator,case_sensitive,vendor_list1,group1))
    thread2 = threading.Thread(target=thread_run, args=(keyword1,keyword2,operator,case_sensitive,vendor_list2,group2))
    thread3 = threading.Thread(target=thread_run, args=(keyword1,keyword2,operator,case_sensitive,vendor_list3,group3))
    thread4 = threading.Thread(target=thread_run, args=(keyword1,keyword2,operator,case_sensitive,vendor_list4,group4))
    thread5 = threading.Thread(target=thread_run, args=(keyword1,keyword2,operator,case_sensitive,vendor_list5,group5))

    # Start new Threads
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()

    # Wait for the Threads to be completed
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    thread5.join()


    # data will be returned in dictionary structure
    data = {}
    while not data_queue.empty():
        items = data_queue.get()
        data[items[0]] = items[1:]   # Key is IP, Value are all other data

    return data


def thread_run(keyword1,keyword2,operator,case_sensitive,vendor_list,group):

    i = 0
    for device_info in group:

        # For Juniper devices, default device type is Juniper
        if vendor_list[i].lower() in ["junos","juniper",""]:
            # Need to configure the following on Juniper router to enable netconf
            ## configure
            ## set system services netconf ssh
            ## commit
            try:
                driver = get_network_driver("junos")
                device = driver(**device_info)
                device.open()

                # Retrieve device facts
                facts = device.get_facts()

                # Device IP address
                device_IP = device_info['hostname']

                # Device name or hostname
                hostname = facts['hostname']

                # Device model
                device_model = facts['model']

                # Get the configuration with "display set" format for juniper devices
                config = device.get_config(retrieve="running", format="set")['running']

                # If searching by non-case-sensitive keyword; then lower all chars in both keyword and configuration lines and find match
                if case_sensitive is False:
                    keyword1 = keyword1.lower()
                    matching_lines = [line for line in config.splitlines() if keyword1 in line.lower()]
                else:
                    matching_lines = [line for line in config.splitlines() if keyword1 in line]

                # If keyword2 is none or sequence of spaces, then it is no meaning of operator and put it to none.
                if keyword2.strip() == "":
                    operator = ""

                if operator == "OR":
                    if case_sensitive is False:
                        keyword2 = keyword2.lower()
                        matching_lines_k2 = [line for line in config.splitlines() if keyword2 in line.lower()]
                    else:
                        matching_lines_k2 = [line for line in config.splitlines() if keyword2 in line]
                    matching_lines = matching_lines + matching_lines_k2

                elif operator == "AND":
                    if case_sensitive is False:
                        keyword2 = keyword2.lower()
                        matching_lines_k2 = [line for line in matching_lines if keyword2 in line.lower()]
                    else:
                        matching_lines_k2 = [line for line in matching_lines if keyword2 in line]
                    matching_lines = matching_lines_k2

                # To return the matching lines in string format
                str_matching_lines = "\n".join(matching_lines)

                # If matching lines are not empty will return matching lines, and if empty, will return None
                if matching_lines!=[]:
                    data_queue.put([device_IP, hostname,"Juniper/"+device_model, keyword1 +" "+ operator + " " + keyword2,case_sensitive, str_matching_lines])

            except Exception as e:
                print(f"exception: {e}")

        elif vendor_list[i].lower() in ["cisco","cisco xe","ios xe"]:
            try:
                driver = get_network_driver("ios")
                device = driver(**device_info)
                device.open()

                # Retrieve device facts
                facts = device.get_facts()

                # Device IP address
                device_IP = device_info['hostname']

                # Device name or hostname
                hostname = facts['hostname']

                device_model = facts['model']
                # Get the configuration with "display set" format for juniper devices
                config = device.get_config(retrieve="running")['running']

                # If searching by non-case-sensitive keyword; then lower all chars in both keyword and configuration lines and find match
                if case_sensitive is False:
                    keyword1 = keyword1.lower()
                    matching_lines = [line for line in config.splitlines() if keyword1 in line.lower()]
                else:
                    matching_lines = [line for line in config.splitlines() if keyword1 in line]

                # If keyword2 is none or sequence of spaces, then it is no meaning of operator and put it to none.
                if keyword2.strip() == "":
                    operator = ""

                if operator == "OR":
                    if case_sensitive is False:
                        keyword2 = keyword2.lower()
                        matching_lines_k2 = [line for line in config.splitlines() if keyword2 in line.lower()]
                    else:
                        matching_lines_k2 = [line for line in config.splitlines() if keyword2 in line]
                    matching_lines = matching_lines + matching_lines_k2

                elif operator == "AND":
                    if case_sensitive is False:
                        keyword2 = keyword2.lower()
                        matching_lines_k2 = [line for line in matching_lines if keyword2 in line.lower()]
                    else:
                        matching_lines_k2 = [line for line in matching_lines if keyword2 in line]
                    matching_lines = matching_lines_k2

                # To return the matching lines in string format
                str_matching_lines = "\n".join(matching_lines)

                # If matching lines are not empty will return matching lines, and if empty, will return None
                if matching_lines!=[]:
                    data_queue.put([device_IP, hostname,"Cisco/"+device_model, keyword1 +" "+ operator + " " + keyword2,case_sensitive, str_matching_lines])
            except Exception as e:
                print(f"exception: {e}")

        elif vendor_list[i].lower() in ["cisco xr","ios xr"]:
            # Need to configure the following on cisco xr router to enable netconf
            ## configure
            ## xml agent tty iteration off
            ## netconf agent ssh
            ## commit

            try:
                driver = get_network_driver("iosxr")
                device = driver(**device_info)
                device.open()

                # Retrieve device facts
                facts = device.get_facts()

                # Device IP address
                device_IP = device_info['hostname']

                # Device name or hostname
                hostname = facts['hostname']

                # Device model
                device_model = facts['model']

                # Get the configuration with "display set" format for juniper devices
                config = device.get_config(retrieve="running")['running']

                # If searching by non-case-sensitive keyword; then lower all chars in both keyword and configuration lines and find match
                if case_sensitive is False:
                    keyword1 = keyword1.lower()
                    matching_lines = [line for line in config.splitlines() if keyword1 in line.lower()]
                else:
                    matching_lines = [line for line in config.splitlines() if keyword1 in line]

                # If keyword2 is none or sequence of spaces, then it is no meaning of operator and put it to none.
                if keyword2.strip() == "":
                    operator = ""

                if operator == "OR":
                    if case_sensitive is False:
                        keyword2 = keyword2.lower()
                        matching_lines_k2 = [line for line in config.splitlines() if keyword2 in line.lower()]
                    else:
                        matching_lines_k2 = [line for line in config.splitlines() if keyword2 in line]
                    matching_lines = matching_lines + matching_lines_k2

                elif operator == "AND":
                    if case_sensitive is False:
                        keyword2 = keyword2.lower()
                        matching_lines_k2 = [line for line in matching_lines if keyword2 in line.lower()]
                    else:
                        matching_lines_k2 = [line for line in matching_lines if keyword2 in line]
                    matching_lines = matching_lines_k2

                # To return the matching lines in string format
                str_matching_lines = "\n".join(matching_lines)

                # If matching lines are not empty will return matching lines, and if empty, will return None
                if matching_lines!=[]:
                    data_queue.put([device_IP, hostname,"Cisco/"+device_model, keyword1 +" "+ operator + " " + keyword2,case_sensitive, str_matching_lines])
            except Exception as e:
                print(f"exception: {e}")

        elif vendor_list[i].lower() in ["huawei","huawei vrp","huawei_vrp"]:

            try:
                driver = get_network_driver("huawei_vrp")
                device = driver(**device_info)
                device.open()

                facts = device.get_facts()  # Retrieve device facts

                # Device IP address
                device_IP = device_info['hostname']

                # Device name or hostname
                hostname = facts['hostname']

                device_model = facts['model']

                # Get the configuration with "display set" format for juniper devices
                config = device.get_config(retrieve="running")['running']

                # If searching by non-case-sensitive keyword; then lower all chars in both keyword and configuration lines and find match
                if case_sensitive is False:
                    keyword1 = keyword1.lower()
                    matching_lines = [line for line in config.splitlines() if keyword1 in line.lower()]
                else:
                    matching_lines = [line for line in config.splitlines() if keyword1 in line]

                # If keyword2 is none or sequence of spaces, then it is no meaning of operator and put it to none.
                if keyword2.strip() == "":
                    operator = ""

                if operator == "OR":
                    if case_sensitive is False:
                        keyword2 = keyword2.lower()
                        matching_lines_k2 = [line for line in config.splitlines() if keyword2 in line.lower()]
                    else:
                        matching_lines_k2 = [line for line in config.splitlines() if keyword2 in line]
                    matching_lines = matching_lines + matching_lines_k2

                elif operator == "AND":
                    if case_sensitive is False:
                        keyword2 = keyword2.lower()
                        matching_lines_k2 = [line for line in matching_lines if keyword2 in line.lower()]
                    else:
                        matching_lines_k2 = [line for line in matching_lines if keyword2 in line]
                    matching_lines = matching_lines_k2

                # To return the matching lines in string format
                str_matching_lines = "\n".join(matching_lines)

                # If matching lines are empty, will return None
                if matching_lines!=[]:
                    data_queue.put([device_IP, hostname,"Huawei/"+device_model, keyword1 +" "+ operator + " " + keyword2,case_sensitive, str_matching_lines])
            except Exception as e:
                print(f"exception: {e}")

        i = +1
