import socket
import time
import board
import busio
import re
import subprocess
import adafruit_ssd1306
from digitalio import DigitalInOut, Direction, Pull
from PIL import Image, ImageDraw, ImageFont
from pkgs.wifi_client.wifi_client_service import WifiClientService
from pkgs.wifi_ap.wifi_ap_service import WifiApService
from pkgs.command.command_service import CommandService
from pkgs.watchdog.watchdog_service import WatchdogService
from pkgs.radio.radio_service import RadioService
from pkgs.vendor.vendor_service import VendorService
from pkgs.display.display_service import DisplayService

###
# This monolithic madness is the entire UI of pi sniffer. It communicates with
# the pi_sniffer engine over UDP and with Kismet over TCP. It issues various
# shell commands in order to interact with the system. It checks to see if the
# UI needs repainting every 0.1ish seconds. An enterprising individual might
# break this thing up.
###

###
# Hooray for globals!
###

# Socket endpoint address
socket_ip = "127.0.0.1"

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# Create a "display" that represents the OLED screen
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

# Input pins
button_A = DigitalInOut(board.D5)
button_A.direction = Direction.INPUT
button_A.pull = Pull.UP

button_B = DigitalInOut(board.D6)
button_B.direction = Direction.INPUT
button_B.pull = Pull.UP

button_L = DigitalInOut(board.D27)
button_L.direction = Direction.INPUT
button_L.pull = Pull.UP

button_R = DigitalInOut(board.D23)
button_R.direction = Direction.INPUT
button_R.pull = Pull.UP

button_U = DigitalInOut(board.D17)
button_U.direction = Direction.INPUT
button_U.pull = Pull.UP

button_D = DigitalInOut(board.D22)
button_D.direction = Direction.INPUT
button_D.pull = Pull.UP

button_C = DigitalInOut(board.D4)
button_C.direction = Direction.INPUT
button_C.pull = Pull.UP

# views
status_view = 0
overview = 1
ap_view = 2
client_view = 3
antenna = 4
system_view = 5
gps_view = 6
lock_screen = 7
rotate = 8  # place holder

# ap view
selected_ap = 0
ap_view_type_radio_info = 2
ap_view_type_station_info = 1
ap_view_type = ap_view_type_station_info
selected_ant = 0

# client view
selected_client = 0
client_view_type_bssid = 'BSSID'
client_view_type_ssid = 'SSID'
client_view_type_radio = 'RADIO'
client_view_type_vendor = 'VENDOR'
client_view_type_mac = 'MAC'
client_view_pages = [
    client_view_type_bssid,
    client_view_type_ssid,
    client_view_type_radio,
    client_view_type_vendor,
    client_view_type_mac
]
client_view_page_index = 0

# current view
current_view = status_view

# lock controls
locked = False

# do we need to update the view?
redraw = True

# last update time
last_update = 0
last_stats = None

# the font all text writing will use
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 9)

###
# Globals over. I am appropriately embarrassed.
###

##
# Services
##
client_service = WifiClientService()
ap_service = WifiApService()
watchdog_service = WatchdogService()


###
# Have the client attempt to rotate to the next screen
###
def check_view():
    global redraw
    global current_view
    global selected_ap
    global selected_ant
    global selected_client

    # Right joystick controls screen movement
    if not button_R.value:
        redraw = True

        # reset screen specific items
        # todo move this until ap_view
        selected_ap = 0
        selected_ant = 0
        selected_client = 0

        # move to the next screen
        current_view = current_view + 1
        current_view = current_view % rotate
    # Left joystick controls screen movement too
    elif not button_L.value:
        redraw = True

        # reset screen specific items
        # todo move this until ap_view
        selected_ap = 0
        selected_ant = 0
        selected_client = 0

        if current_view == 0:
            current_view = lock_screen
        else:
            current_view = current_view - 1


##
# Populate the start/status view
##
def do_status_view():
    global redraw

    if not button_A.value and not button_B.value:
        # attempt a clean shutdown
        CommandService.run(b"s", False)
        time.sleep(5)
        subprocess.run(["shutdown", "-h", "now"])
        return False

    elif not button_B.value:
        # start kismet and pi sniffer
        kismet = subprocess.run(["ps", "-C", "kismet_server"], capture_output=True)
        if kismet.stdout.find(b"kismet_server") == -1:
            redraw = True
            subprocess.Popen(["kismet_server", "-f", "/home/pi/kismet.conf", "-n", "--daemonize"])
            time.sleep(3)  # give it a second to get established

        pi_sniffer = subprocess.run(["ps", "-C", "pi_sniffer"], capture_output=True)
        if pi_sniffer.stdout.find(b"pi_sniffer") == -1:
            redraw = True
            subprocess.Popen([
                "/home/pi/pi_sniffer/build/pi_sniffer",
                "-c", "/home/pi/pi_sniffer/pi_sniffer.conf",
                "-k",
                socket_ip,
                "-p",
                "3501"
            ])
    elif not button_A.value:
        # shutdown kismet and pi sniffer
        redraw = True
        CommandService.run(b"s", False)
        kismet = subprocess.run(["ps", "-C", "kismet_server"], capture_output=True)
        if kismet.stdout.find(b"kismet_server") != -1:
            CommandService.do_kismet_command(b"SHUTDOWN")
            subprocess.run(["airmon-ng", "stop", "wlan0mon"])
            subprocess.run(["airmon-ng", "stop", "wlan1mon"])

    if redraw:
        draw.rectangle((0, 0, width, 10), outline=1, fill=1)
        draw.text(((width / 2) - 12, 0), "Status", fill=0)

        kismet = subprocess.run(["ps", "-C", "kismet_server"], capture_output=True)
        if kismet.stdout.find(b"kismet_server") != -1:
            draw.text((0, 10), "Kismet: Running", font=font, fill=1)
        else:
            draw.text((0, 10), "Kismet: Stopped", font=font, fill=1)

        pi_sniffer = subprocess.run(["ps", "-C", "pi_sniffer"], capture_output=True)
        if pi_sniffer.stdout.find(b"pi_sniffer") != -1:
            draw.text((0, 20), "PiSniff: Running", font=font, fill=1)
        else:
            draw.text((0, 20), "PiSniff: Stopped", font=font, fill=1)

        wlan0mon = subprocess.run(["ifconfig", "wlan0mon"], capture_output=True)
        if wlan0mon.stdout.find(b"RUNNING,PROMISC") != -1:
            draw.text((0, 30), "wlan0mon: Up", font=font, fill=1)
        else:
            draw.text((0, 30), "wlan0mon: Down", font=font, fill=1)

        wlan1mon = subprocess.run(["ifconfig", "wlan1mon"], capture_output=True)
        if wlan1mon.stdout.find(b"RUNNING,PROMISC") != -1:
            draw.text((0, 40), "wlan1mon: Up", font=font, fill=1)
        else:
            draw.text((0, 40), "wlan1mon: Down", font=font, fill=1)

        gps_found = subprocess.run(["ls", "/dev/ttyACM0"], capture_output=True)
        if len(gps_found.stdout) > 0:
            draw.text((0, 50), "GPS: Available", font=font, fill=1)
        else:
            draw.text((0, 50), "GPS: Not Found", font=font, fill=1)

    return True


##
# Populate the overview screen
##
def do_overview():
    if redraw:
        draw.rectangle((0, 0, width, 10), outline=1, fill=1)
        draw.text(((width / 2) - 16, 0), "Overview", fill=0)
        draw.line((width / 2, 10, width / 2, height), fill=1)
        overview_stats = CommandService.run(b"o", True)
        if overview_stats is not None:
            stats = overview_stats.split(b",")
            second_pane_start_x = width / 2 + 2
            draw.text((0, 10), "Time: " + stats[0].decode("utf-8"), font=font, fill=1)
            draw.text((0, 20), "APs: " + stats[1].decode("utf-8"), font=font, fill=1)
            draw.text((0, 30), "Open: " + stats[2].decode("utf-8"), font=font, fill=1)
            draw.text((0, 40), "WEP: " + stats[3].decode("utf-8"), font=font, fill=1)
            draw.text((0, 50), "WPA: " + stats[4].decode("utf-8"), font=font, fill=1)
            draw.text((second_pane_start_x, 10), "Pkts: " + stats[5].decode("utf-8"), font=font, fill=1)
            draw.text((second_pane_start_x, 20), "Bcns: " + stats[6].decode("utf-8"), font=font, fill=1)
            draw.text((second_pane_start_x, 30), "Data: " + stats[7].decode("utf-8"), font=font, fill=1)
            draw.text((second_pane_start_x, 40), "Enc: " + stats[8].decode("utf-8"), font=font, fill=1)
            draw.text((second_pane_start_x, 50), "EAPOL: " + stats[9].decode("utf-8"), font=font, fill=1)


##
# Handle antenna view and input
##
def do_ant_view():
    global redraw
    global selected_ant

    if not button_D.value:  # down arrow
        if selected_ant < 2:
            redraw = True
            selected_ant = selected_ant + 1
    elif not button_U.value:  # up arrow
        if selected_ant > 0:
            selected_ant = selected_ant - 1
            redraw = True
    elif not button_B.value and selected_ant != 0:
        if selected_ant == 1:
            if RadioService.is_antenna_running("wlan0mon") is False:
                # if the antenna doesn't exist do nothing
                return
            uid = RadioService.get_uid("wlan0mon")
        elif selected_ant == 2:
            if RadioService.is_antenna_running("wlan1mon") is False:
                # if the antenna doesn't exist do nothing
                return
            uid = RadioService.get_uid("wlan1mon")
        else:
            # ignore
            return

        RadioService.cycle_channel_up(uid)

        # kismet needs a little before we slam it with more requests
        time.sleep(0.3)
        redraw = True

    if redraw:
        half_width = width / 2
        right_pane_start = half_width + 2
        draw.rectangle((0, 0, width, 10), outline=1, fill=1)
        draw.text((half_width - 8, 0), "Antenna", fill=0)
        draw.line((half_width, 10, half_width, height), fill=1)

        iface = ""
        ifaces = ["wlan0mon", "wlan1mon"]
        iface_list_height = 10
        iface_cursor_start = iface_list_height
        iface_index = 1
        for possible_iface in ifaces:
            if selected_ant == iface_index:
                iface = possible_iface
                draw.rectangle((0, iface_cursor_start, half_width, iface_cursor_start + iface_list_height), outline=1,
                               fill=1)
                draw.text((0, iface_cursor_start), possible_iface, font=font, fill=0)
            else:
                draw.text((0, iface_cursor_start), possible_iface, font=font, fill=1)
            iface_cursor_start += iface_list_height
            iface_index += 1

        if iface is not "":
            if RadioService.is_antenna_running(iface) is False:
                draw.text((right_pane_start, 10), "Disabled", font=font, fill=1)
            else:
                (channellist, hopping, channel) = RadioService.antenna_info(RadioService.get_uid(iface))
                if hopping == b'':
                    draw.text((right_pane_start, 10), "Channel:\nTransitioning", font=font, fill=1)
                elif hopping != b"0":
                    draw.text((right_pane_start, 10), "Channel:\nHopping", font=font, fill=1)
                else:
                    draw.text((right_pane_start, 10), "Channel:\n" + channel.decode("utf-8"), font=font, fill=1)


##
# Draw the system view
##
def do_system_view():
    if redraw:
        draw.rectangle((0, 0, width, 10), outline=1, fill=1)
        draw.text(((width / 2) - 36, 0), "System Status", fill=0)

        cpu = subprocess.run(["top", "-b", "-n", "1"], capture_output=True)
        result = re.search(b"%Cpu\(s\):[ ]+[0-9\.]+[ ]+us,[ ]+[0-9\.]+[ ]+sy,[ ]+[0-9\.]+[ ]+ni,[ ]+([0-9\.]+)[ ]+id",
                           cpu.stdout)
        if result is None:
            draw.text((0, 10), "CPU: Unknown%", font=font, fill=1)
        else:
            value = 100 - int(float(result.group(1)))
            draw.text((0, 10), "CPU: " + str(value) + "%", font=font, fill=1)

        mem = subprocess.run(["vmstat", "-s"], capture_output=True)
        total_mem = re.search(b"([0-9]+) K total memory\n", mem.stdout)
        total_free = re.search(b"([0-9]+) K free memory\n", mem.stdout)
        if total_mem is None or total_free is None:
            draw.text((0, 20), "Memory: Unknown%", font=font, fill=1)
        else:
            value = 100 - ((float(total_free.group(1)) / float(total_mem.group(1))) * 100)
            draw.text((0, 20), "Memory: " + str(int(value)) + "%", font=font, fill=1)

        disk = subprocess.run(["df"], capture_output=True)
        disk_usage = re.search(b"/dev/root[ ]+[A-Z0-9\.]+[ ]+[A-Z0-9\.]+[ ]+[A-Z0-9\.]+[ ]+([0-9]+)% /", disk.stdout)
        if disk_usage is None:
            draw.text((0, 30), "Disk: Unknown%", font=font, fill=1)
        else:
            draw.text((0, 30), "Disk: " + disk_usage.group(1).decode("utf-8") + "%", font=font, fill=1)

        temp = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True)
        temp_C = re.search(b"temp=(.*)", temp.stdout)
        if temp_C is None:
            draw.text((0, 40), "Temp: Unknown", font=font, fill=1)
        else:
            draw.text((0, 40), "Temp: " + temp_C.group(1).decode("utf-8"), font=font, fill=1)


##
# Populate the GPS view
##
def do_gps_view():
    if redraw:
        draw.rectangle((0, 0, width, 10), outline=1, fill=1)
        draw.text(((width / 2) - 28, 0), "GPS Status", fill=0)

        gps_found = subprocess.run(["ls", "/dev/ttyACM0"], capture_output=True)
        if len(gps_found.stdout) == 0:
            draw.text((0, 10), "Hardware: Not Found", font=font, fill=1)
        else:
            draw.text((0, 10), "Hardware: Available", font=font, fill=1)

            # does gpsd see the device?
            gps_found = subprocess.run(["gpspipe", "-w", "-n", "2"], capture_output=True)
            if gps_found.stdout.find(b'"devices":[]') != -1:
                draw.text((0, 20), "Hardware: Not Recognized", font=font, fill=1)
            else:
                draw.text((0, 20), "Hardware: Recognized", font=font, fill=1)

                # grab lat long
                gps_found = subprocess.run(["gpspipe", "-w", "-n", "4"], capture_output=True)
                result = re.search(b'"lat":([0-9\.-]+),"lon":([0-9\.-]+),', gps_found.stdout)
                if result is None:
                    draw.text((0, 30), "No sync", font=font, fill=1)
                else:
                    draw.text((0, 30), "Lat: " + result.group(1).decode("utf-8"), font=font, fill=1)
                    draw.text((0, 40), "Lon: " + result.group(2).decode("utf-8"), font=font, fill=1)


##
# Populate the client view and handle user input
##
def do_client_view():
    global redraw
    global selected_client
    global client_view_page_index

    if not button_D.value:  # down arrow
        if selected_client < len(client_service.get_clients()):
            redraw = True
            selected_client = selected_client + 1
    elif not button_U.value:  # up arrow
        if selected_client > 0:
            selected_client = selected_client - 1
            redraw = True
    elif not button_B.value:
        if selected_client > 0:
            try:
                selected_client_record = client_service.get_index(selected_client - 1)
                client_service.deauth_client(selected_client_record)
            except Exception as e:
                print(e)
                pass
    elif not button_A.value:
        redraw = True
        client_view_page_index += 1
        if client_view_page_index >= len(client_view_pages):
            client_view_page_index = 0

    if redraw is True and selected_client == 0:
        client_service.refresh_clients()

    if redraw is True:
        # divide screen
        info_box_start_x = width / 2 + 22
        draw.rectangle((0, 0, width, 10), outline=1, fill=1)
        draw.text(((width / 2) - 30, 0), "Client View", fill=0)
        draw.line((info_box_start_x, 10, info_box_start_x, height), fill=1)

        if selected_client > 3:
            i = selected_client - 4
        else:
            i = 0

        location = 0
        while location < 5 and i < len(client_service.get_clients()):
            try:
                client = client_service.get_index(i)
                mac_address = client['mac']
                display_name = client['name']
                station_bssid = client['station_bssid']
                rssi = client['rssi']
                if selected_client == (i + 1):
                    draw.rectangle((0, (location * 10) + 10, info_box_start_x, (location * 10) + 20), outline=1, fill=1)
                    draw.text((0, (location * 10) + 10), display_name, font=font, fill=0)

                    if client is not None:
                        client_view_title = client_view_pages[client_view_page_index]
                        draw_title = False
                        # BSSID
                        if client_view_title == client_view_type_bssid:
                            draw_title = True
                            # Station BSSID
                            draw.text((info_box_start_x, 20), station_bssid[:9], font=font, fill=1)
                            draw.text((info_box_start_x, 30), station_bssid[9:], font=font, fill=1)

                        # SSID
                        elif client_view_title == client_view_type_ssid:
                            draw_title = True
                            ap = ap_service.get_ap_by_bssid(station_bssid)
                            if ap is not None:
                                line_chunks = DisplayService.get_paragraph(8, 4, ap['ssid'], True)
                                start_line_y = 20
                                for chunk in line_chunks:
                                    draw.text((info_box_start_x, start_line_y), chunk, font=font, fill=1)
                                    start_line_y += 10
                            else:
                                print('No AP found for BSSID ' + station_bssid)

                        # Radio
                        elif client_view_title == client_view_type_radio:
                            draw_title = True
                            draw.text((info_box_start_x, 20), "Sig. " + rssi, font=font, fill=1)
                            ap = ap_service.get_ap_by_bssid(station_bssid)
                            if ap is not None:
                                data = ap_service.get_ap_info(ap)
                                try:
                                    draw.text((info_box_start_x, 30), "Ch. " + data["channel"], font=font, fill=1)
                                except:
                                    draw.text((info_box_start_x, 30), "Ch. Error", font=font, fill=1)

                        # Vendor
                        elif client_view_title == client_view_type_vendor:
                            try:
                                vendor = VendorService.get_vendor(mac_address)
                                vendor_chunks = DisplayService.get_paragraph(8, 4, vendor)
                                start_line_y = 10
                                for chunk in vendor_chunks:
                                    draw.text((info_box_start_x, start_line_y), chunk, font=font, fill=1)
                                    start_line_y += 10
                            except:
                                draw.text((info_box_start_x, 20), "Error", font=font, fill=1)

                        # MAC
                        elif client_view_title == client_view_type_mac:
                            draw_title = True
                            # MAC Address
                            draw.text((info_box_start_x, 20), mac_address[:9], font=font, fill=1)
                            draw.text((info_box_start_x, 30), mac_address[9:], font=font, fill=1)

                        if draw_title:
                            # Info Window Title
                            draw.text((info_box_start_x, 10), client_view_title, font=font, fill=1)

                else:
                    draw.text((0, (location * 10) + 10), display_name, font=font, fill=255)
            except:
                pass

            i = i + 1
            location = location + 1


def do_ap_view():
    global redraw
    global selected_ap
    global ap_view_type
    global ap_view_type_station_info
    global ap_view_type_radio_info

    if not button_D.value:  # down arrow
        if selected_ap < len(ap_service.get_ap_list()):
            redraw = True
            selected_ap = selected_ap + 1
    elif not button_U.value:  # up arrow
        if selected_ap > 0:
            selected_ap = selected_ap - 1
            redraw = True
    elif not button_A.value:
        if ap_view_type == ap_view_type_station_info:
            ap_view_type = ap_view_type_radio_info
        else:
            ap_view_type = ap_view_type_station_info
        redraw = True
    elif redraw is True and selected_ap == 0:
        ap_service.refresh_ap_list()

    if redraw:
        # divide screen
        draw.rectangle((0, 0, width, 10), outline=1, fill=1)
        draw.text(((width / 2) - 18, 0), "Live View", fill=0)
        draw.line((width / 2, 10, width / 2, height), fill=1)

        # this supports forever scrolling... I hope
        if selected_ap > 3:
            i = selected_ap - 4
        else:
            i = 0

        location = 0
        while location < 5 and i < len(ap_service.get_ap_list()):
            ap = ap_service.get_index(i)
            display_ssid = ap['ssid']
            if len(display_ssid) > 12:
                display_ssid = display_ssid[:9]
                display_ssid = display_ssid + ".."

            if selected_ap == (i + 1):
                draw.rectangle((0, (location * 10) + 10, width / 2, (location * 10) + 20), outline=1, fill=1)
                draw.text((0, (location * 10) + 10), display_ssid, font=font, fill=0)

                data = ap_service.get_ap_info(ap)
                if data is not None:
                    try:
                        right_pane_start = width / 2 + 2
                        if ap_view_type == ap_view_type_radio_info:
                            draw.text((right_pane_start, 10), "Sig: " + data["rssi"], font=font, fill=1)
                            draw.text((right_pane_start, 20), "Ch: " + data["channel"], font=font, fill=1)
                            draw.text((right_pane_start, 30), data["security"], font=font, fill=1)
                            draw.text((right_pane_start, 40), "Clnts: " + data["client_count"], font=font, fill=1)
                        elif ap_view_type == ap_view_type_station_info:
                            draw.text((right_pane_start, 10), data["bssid"][:9], font=font, fill=1)
                            draw.text((right_pane_start, 20), data["bssid"][9:], font=font, fill=1)

                            vendor = VendorService.get_vendor(data["bssid"])

                            if vendor is not None:
                                vendor_chunks = DisplayService.get_paragraph(12, 3, vendor)
                                vendor_line_index = 0
                                for vendor_chunk in vendor_chunks:
                                    draw.text((right_pane_start, 30 + (vendor_line_index * 10)), vendor_chunk,
                                              font=font, fill=1)
                                    vendor_line_index += 1

                    except Exception as e:
                        print(e)
            else:
                draw.text((0, (location * 10) + 10), display_ssid, font=font, fill=255)

            i = i + 1
            location = location + 1


##
# Handle the lock screen drawing and locking input (unlocked handled elsewhere)
##
def do_lock_screen():
    global redraw
    global locked

    if not button_B.value:  # button 6
        locked = True
        redraw = True

    if redraw:
        draw.rectangle((0, 0, width, 10), outline=1, fill=1)
        draw.text(((width / 2) - 26, 0), "Lock Status", fill=0)

        if locked:
            draw.text((0, 10), "Locked", font=font, fill=1)
        else:
            draw.text((0, 10), "Unlocked", font=font, fill=1)


# ensure the echo is disabled on the gps tty. Really annoying this needs to be done.
subprocess.run(["stty", "-F", "/dev/ttyACM0", "-echo"])

# kill hdmi. power saving.
subprocess.run(["/usr/bin/tvservice", "-o"])

# loop until the user hits the break
# Clear display.
disp.fill(0)
disp.show()

while True:

    if locked:
        # the user can lock the display in the lock screen. If they have, don't
        # do any other UI processing. We will have to still do the watch dog
        # logic though
        if not button_A.value and not button_U.value:
            locked = False
            redraw = True
        else:
            watchdog_service.set_current_time(time.time())
            if (watchdog_service.get_current_time() - 6) > last_update:
                redraw = True
            watchdog_service.do_watchdog()
            time.sleep(0.1)
            continue

    # check if the user is changing the view
    check_view()

    # see if we should be refreshing
    if not redraw:
        watchdog_service.set_current_time(time.time())
        if (watchdog_service.get_current_time() - 6) > last_update:
            redraw = True

        # while we have current time let's kick the dog
        watchdog_service.do_watchdog()

    # we might draw! Create a blank canvas
    width = disp.width
    height = disp.height
    image = Image.new('1', (width, height))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # which view to draw to the screen
    if current_view == status_view:
        if not do_status_view():
            # user has requested shutdown
            break
    elif current_view == overview:
        do_overview()
    elif current_view == antenna:
        do_ant_view()
    elif current_view == system_view:
        do_system_view()
    elif current_view == gps_view:
        do_gps_view()
    elif current_view == client_view:
        do_client_view()
    elif current_view == ap_view:
        do_ap_view()
    elif current_view == lock_screen:
        do_lock_screen()
    else:
        print("oh no! Why are we here?")

    if redraw:
        last_update = time.time()
        disp.image(image)
        disp.show()
        redraw = False

    time.sleep(0.1)

disp.fill(0)
disp.show()
