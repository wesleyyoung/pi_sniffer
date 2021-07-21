from pkgs.radio.radio_service import RadioService
import time

##
# Handle antenna view and input
##
def do_ant_view(button_B, button_U, button_D, draw, width, height, font):
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
