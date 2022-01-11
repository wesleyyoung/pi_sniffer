from pkgs.display.display_service import DisplayService
from pkgs.vendor.vendor_service import VendorService

selected_ap = 0
ap_view_type_radio_info = 2
ap_view_type_station_info = 1
ap_view_type = ap_view_type_station_info
selected_ant = 0


def do_ap_view(button_A, button_U, button_D, draw, width, height, font, ap_service):
    global selected_ap
    global ap_view_type
    global ap_view_type_station_info
    global ap_view_type_radio_info
    aps = ap_service.aps

    if not button_D.value:  # down arrow
        if selected_ap < len(aps.keys()):
            selected_ap = selected_ap + 1
    elif not button_U.value:  # up arrow
        if selected_ap > 0:
            selected_ap = selected_ap - 1
    elif not button_A.value:
        if ap_view_type == ap_view_type_station_info:
            ap_view_type = ap_view_type_radio_info
        else:
            ap_view_type = ap_view_type_station_info

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
    while location < 5 and i < len(aps.keys()):
        ap = aps[aps.keys()[i]]
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
