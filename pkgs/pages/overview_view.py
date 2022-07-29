from pkgs.command.command_service import CommandService


##
# Populate the overview screen
##
def do_overview(driver):
    width = driver.get_display_width()
    height = driver.get_display_height()

    driver.draw_rect((0, 0, width, 10))
    driver.draw_text((width / 2) - 16, 0, "Overview", fill=0)
    driver.draw_line((width / 2, 10, width / 2, height))

    overview_stats = CommandService.run(b"o", True)

    if overview_stats is not None:
        stats = overview_stats.split(b",")
        second_pane_start_x = width / 2 + 2
        try:
            driver.draw_text(0, 10, "Time: " + stats[0].decode("utf-8"))
            driver.draw_text(0, 20, "APs: " + stats[1].decode("utf-8"))
            driver.draw_text(0, 30, "Open: " + stats[2].decode("utf-8"))
            driver.draw_text(0, 40, "WEP: " + stats[3].decode("utf-8"))
            driver.draw_text(0, 50, "WPA: " + stats[4].decode("utf-8"))
            driver.draw_text(second_pane_start_x, 10, "Pkts: " + stats[5].decode("utf-8"))
            driver.draw_text(second_pane_start_x, 20, "Bcns: " + stats[6].decode("utf-8"))
            driver.draw_text(second_pane_start_x, 30, "Data: " + stats[7].decode("utf-8"))
            driver.draw_text(second_pane_start_x, 40, "Enc: " + stats[8].decode("utf-8"))
            driver.draw_text(second_pane_start_x, 50, "EAPOL: " + stats[9].decode("utf-8"))
        except Exception as e:
            print(e)
