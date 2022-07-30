from pkgs.display.display_service import DisplayService
from pkgs.driver.display_driver import DisplayDriver
from pkgs.vendor.vendor_service import VendorService

selected_ap = 0
ap_view_type_radio_info = 2
ap_view_type_station_info = 1
ap_view_type = ap_view_type_station_info
selected_ant = 0


def do_ap_view(driver: DisplayDriver, ap_service):
    global selected_ap
    global ap_view_type
    global ap_view_type_station_info
    global ap_view_type_radio_info
    width = driver.get_display_width()
    height = driver.get_display_height()
    aps = ap_service.aps

    if driver.is_down_pressed():  # down arrow
        if selected_ap < len(aps.keys()):
            selected_ap = selected_ap + 1
    elif driver.is_up_pressed():  # up arrow
        if selected_ap > 0:
            selected_ap = selected_ap - 1
    elif driver.is_a_pressed():
        if ap_view_type == ap_view_type_station_info:
            ap_view_type = ap_view_type_radio_info
        else:
            ap_view_type = ap_view_type_station_info

    # divide screen
    driver.draw_rect((0, 0, width, 10))
    driver.draw_text((width / 2) - 18, 0, "Live View", fill=0)
    driver.draw_line((width / 2, 10, width / 2, height))

    # this supports forever scrolling... I hope
    if selected_ap > 3:
        i = selected_ap - 4
    else:
        i = 0

    location = 0
    while location < 5 and i < len(aps.keys()):
        ap = aps[aps.keys()[i]]
        display_ssid = ap['ssid']
        if len(display_ssid) > 12:
            display_ssid = display_ssid[:9]
            display_ssid = display_ssid + ".."

        if selected_ap == (i + 1):
            driver.draw_rect((0, (location * 10) + 10, width / 2, (location * 10) + 20))
            driver.draw_text(0, (location * 10) + 10, display_ssid, fill=0)

            data = ap_service.get_ap_info(ap)

            if data is not None:
                try:
                    right_pane_start = width / 2 + 2
                    if ap_view_type == ap_view_type_radio_info:
                        driver.draw_text(right_pane_start, 10, "Sig: " + data["rssi"])
                        driver.draw_text(right_pane_start, 20, "Ch: " + data["channel"])
                        driver.draw_text(right_pane_start, 30, data["security"])
                        driver.draw_text(right_pane_start, 40, "Clnts: " + data["client_count"])
                    elif ap_view_type == ap_view_type_station_info:
                        driver.draw_text(right_pane_start, 10, data["bssid"][:9])
                        driver.draw_text(right_pane_start, 20, data["bssid"][9:])

                        vendor = VendorService.get_vendor(data["bssid"])

                        if vendor is not None:
                            vendor_chunks = DisplayService.get_paragraph(12, 3, vendor)
                            vendor_line_index = 0
                            for vendor_chunk in vendor_chunks:
                                driver.draw_text(right_pane_start, 30 + (vendor_line_index * 10), vendor_chunk)
                                vendor_line_index += 1

                except Exception as e:
                    print(e)
        else:
            driver.draw_text(0, (location * 10) + 10, display_ssid, fill=255)

        i = i + 1
        location = location + 1
