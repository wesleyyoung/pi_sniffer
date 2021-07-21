from pkgs.display.display_service import DisplayService
from pkgs.vendor.vendor_service import VendorService

selected_client = 0
selected_client_mac = ''
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


##
# Populate the client view and handle user input
##
def do_client_view(button_A, button_B, button_U, button_D, draw, width, height, font, ap_service, client_service):
    global selected_client
    global client_view_page_index
    clients = client_service.client_map

    if not button_D.value:  # down arrow
        if selected_client < len(clients.keys()):
            selected_client = selected_client + 1
    elif not button_U.value:  # up arrow
        if selected_client > 0:
            selected_client = selected_client - 1
    elif not button_B.value:
        if selected_client > 0:
            try:
                selected_client_record = clients[clients.keys()[selected_client - 1]]
                client_service.deauth_client(selected_client_record)
            except Exception as e:
                print(e)
                pass
    elif not button_A.value:
        client_view_page_index += 1
        if client_view_page_index >= len(client_view_pages):
            client_view_page_index = 0

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
    while location < 5 and i < len(clients.keys()):
        try:
            client = clients[clients.keys()[i]]
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
                            vendor = client['vendor']
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
