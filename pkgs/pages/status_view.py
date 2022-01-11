from pkgs.runtime.runtime_service import RuntimeService
import subprocess


##
# Populate the start/status view
##
def do_status_view(button_A, button_B, draw, font, width, runtime_service):
    if not button_A.value and not button_B.value:
        RuntimeService.power_off()
        return False

    elif not button_B.value:
        runtime_service.start()
    elif not button_A.value:
        runtime_service.stop()

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
