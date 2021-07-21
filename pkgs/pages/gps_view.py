import subprocess
import re


##
# Populate the GPS view
##
def do_gps_view(draw, width, font):
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
