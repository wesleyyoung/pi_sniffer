locked = False


##
# Handle the lock screen drawing and locking input (unlocked handled elsewhere)
##
def do_lock_screen(driver):
    global locked
    width = driver.get_display_width()
    b_press = driver.button_B.value

    if not b_press:  # button 6
        locked = True

    driver.draw_rect((0, 0, width, 10))
    driver.draw_text((width / 2) - 26, 0, "Lock Status", fill=0)

    if locked:
        driver.draw_text(0, 10, "Locked")
    else:
        driver.draw_text(0, 10, "Unlocked")
