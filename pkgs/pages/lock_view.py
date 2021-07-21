locked = False


##
# Handle the lock screen drawing and locking input (unlocked handled elsewhere)
##
def do_lock_screen(button_B, draw, width, font):
    global locked

    if not button_B.value:  # button 6
        locked = True

    draw.rectangle((0, 0, width, 10), outline=1, fill=1)
    draw.text(((width / 2) - 26, 0), "Lock Status", fill=0)

    if locked:
        draw.text((0, 10), "Locked", font=font, fill=1)
    else:
        draw.text((0, 10), "Unlocked", font=font, fill=1)
