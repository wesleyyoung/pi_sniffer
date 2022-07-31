from pkgs.driver.display_driver import DisplayDriver


def is_no_input_given(driver: DisplayDriver):
    return not driver.is_a_pressed() and not driver.is_b_pressed() \
           and not driver.is_up_pressed() and not driver.is_down_pressed() \
           and not driver.is_left_pressed() and not driver.is_right_pressed()