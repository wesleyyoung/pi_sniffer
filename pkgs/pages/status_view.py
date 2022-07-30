from pkgs.runtime.runtime_service import RuntimeService
import subprocess


##
# Populate the start/status view
##
def do_status_view(driver, runtime_service):
    a_press = driver.button_A.value
    b_press = driver.button_B.value
    width = driver.get_display_width()

    if not a_press and not b_press:
        RuntimeService.power_off()
        return False

    elif not b_press:
        runtime_service.start()
    elif not a_press:
        runtime_service.stop()

    driver.draw_rect((0, 0, width, 10))
    driver.draw_text((width / 2) - 12, 0, "Status")

    kismet = subprocess.run(["ps", "-C", "kismet_server"], capture_output=True)
    if kismet.stdout.find(b"kismet_server") != -1:
        driver.draw_text(0, 10, "Kismet: Running")
    else:
        driver.draw_text(0, 10, "Kismet: Stopped")

    pi_sniffer = subprocess.run(["ps", "-C", "pi_sniffer"], capture_output=True)
    if pi_sniffer.stdout.find(b"pi_sniffer") != -1:
        driver.draw_text(0, 20, "PiSniff: Running")
    else:
        driver.draw_text(0, 20, "PiSniff: Stopped")

    wlan0mon = subprocess.run(["ifconfig", "wlan0mon"], capture_output=True)
    if wlan0mon.stdout.find(b"RUNNING,PROMISC") != -1:
        driver.draw_text(0, 30, "wlan0mon: Up")
    else:
        driver.draw_text(0, 30,  "wlan0mon: Down")

    wlan1mon = subprocess.run(["ifconfig", "wlan1mon"], capture_output=True)
    if wlan1mon.stdout.find(b"RUNNING,PROMISC") != -1:
        driver.draw_text(0, 40, "wlan1mon: Up")
    else:
        driver.draw_text(0, 40, "wlan1mon: Down")

    gps_found = subprocess.run(["ls", "/dev/ttyACM0"], capture_output=True)
    if len(gps_found.stdout) > 0:
        driver.draw_text(0, 50, "GPS: Available")
    else:
        driver.draw_text(0, 50, "GPS: Not Found")

    return True
