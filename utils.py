import threading
from napalm import get_network_driver
import queue



class myThread (threading.Thread):
   def __init__(self, threadID, name,keyword1,keyword2,operator,case_sensitive,vendor_list,group):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.group = group
      self.keyword1 = keyword1
      self.keyword2 = keyword2
      self.operator = operator
      self.case_sensitive = case_sensitive
      self.vendor_list = vendor_list

   def run(self):
      thread_run(self.name, self.keyword1, self.keyword2, self.operator, self.case_sensitive, self.vendor_list, self.group)


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

    # If devices number < 10; then we will use one thread only
    if device_count < 10:

        # Create new Thread
        thread1 = myThread(1, "Thread-1",keyword1,keyword2,operator,case_sensitive,vendor_list,devices_info)

        # Start new Thread
        thread1.start()

        # Wait for the Thread to be completed
        thread1.join()

    # If number of devices >= 10, then use multi-Threads
    else:
        # Dividing the list of devices to groups for Threading
        device_per_thread = (device_count//thread_num) + (device_count%thread_num)
        group1 = devices_info[0:device_per_thread]
        group2 = devices_info[(device_per_thread):(2*device_per_thread)]
        group3 = devices_info[(2*device_per_thread):(3*device_per_thread)]
        group4 = devices_info[(3*device_per_thread):(4*device_per_thread)]
        group5 = devices_info[(4*device_per_thread):(5*device_per_thread)]

        # Create new Threads
        thread1 = myThread(1, "Thread-1",keyword1,keyword2,operator,case_sensitive,vendor_list,group1)
        thread2 = myThread(2, "Thread-2",keyword1,keyword2,operator,case_sensitive,vendor_list,group2)
        thread3 = myThread(3, "Thread-3",keyword1,keyword2,operator,case_sensitive,vendor_list,group3)
        thread4 = myThread(4, "Thread-4",keyword1,keyword2,operator,case_sensitive,vendor_list,group4)
        thread5 = myThread(5, "Thread-5",keyword1,keyword2,operator,case_sensitive,vendor_list,group5)

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


def thread_run(threadName,keyword1,keyword2,operator,case_sensitive,vendor_list,group):

    i = 0
    for device_info in group:
        driver = get_network_driver(vendor_list[i])
        device = driver(**device_info)

        # For Juniper devices, default device type is Juniper
        if vendor_list[i] == ("junos" or "juniper" or ""):
            try:
                device.open()

                facts = device.get_facts()  # Retrieve device facts

                # Device IP address
                device_IP = device_info['hostname']

                # Device name or hostname
                hostname = facts['hostname']

                device_model = facts['model']
                # Get the configuration with "display set" format for juniper devices
                config = device.get_config(retrieve="running", format="set")['running']

                # If searching by non-case-sensitive keyword; then lower all chars in both keyword and configuration lines and find match
                if case_sensitive is False:
                    keyword1 = keyword1.lower()
                    matching_lines = [line for line in config.splitlines() if keyword1 in line.lower()]
                else:
                    matching_lines = [line for line in config.splitlines() if keyword1 in line]

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
                    data_queue.put([device_IP, hostname,"Juniper / "+device_model, keyword1 +" "+ operator + " " + keyword2,case_sensitive, str_matching_lines])
                # print(f" queue size: {data_queue.qsize()}")
            except Exception as e:
                print(f"exception: {e}")

        i = +1
