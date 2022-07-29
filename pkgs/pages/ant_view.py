from pkgs.radio.radio_service import RadioService
import time

selected_ant = 0


##
# Handle antenna view and input
##
def do_ant_view(driver):
    global selected_ant
    down_press = driver.button_D.value
    up_press = driver.button_U.value
    b_press = driver.button_B.value
    width = driver.get_display_width()
    height = driver.get_display_height()

    if not down_press:  # down arrow
        if selected_ant < 2:
            selected_ant = selected_ant + 1
    elif not up_press:  # up arrow
        if selected_ant > 0:
            selected_ant = selected_ant - 1
    elif not b_press and selected_ant != 0:
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

    half_width = width / 2
    right_pane_start = half_width + 2
    driver.draw_rect((0, 0, width, 10))
    driver.draw_text(half_width - 8, 0, "Antenna", fill=0)
    driver.draw_line((half_width, 10, half_width, height))

    iface = ""
    ifaces = ["wlan0mon", "wlan1mon"]
    iface_list_height = 10
    iface_cursor_start = iface_list_height
    iface_index = 1

    for possible_iface in ifaces:
        if selected_ant == iface_index:
            iface = possible_iface
            driver.draw_rect((0, iface_cursor_start, half_width, iface_cursor_start + iface_list_height))
            driver.draw_text(0, iface_cursor_start, possible_iface, fill=0)
        else:
            driver.draw_text(0, iface_cursor_start, possible_iface)
        iface_cursor_start += iface_list_height
        iface_index += 1

    if iface is not "":
        if RadioService.is_antenna_running(iface) is False:
            driver.draw_text(right_pane_start, 10, "Disabled")
        else:
            (channellist, hopping, channel) = RadioService.antenna_info(RadioService.get_uid(iface))
            if hopping == b'':
                driver.draw_text(right_pane_start, 10, "Channel:\nTransitioning")
            elif hopping != b"0":
                driver.draw_text(right_pane_start, 10, "Channel:\nHopping")
            else:
                driver.draw_text(right_pane_start, 10, "Channel:\n" + channel.decode("utf-8"))
