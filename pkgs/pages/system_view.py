from pkgs.api.sys.cpu_util import cpu_util
from pkgs.api.sys.disk import disk_usage
from pkgs.api.sys.mem import total_mem, mem_free
from pkgs.api.sys.temp import temp


def do_system_view(driver):
    width = driver.get_display_width()
    driver.draw_rect((0, 0, width, 10))
    driver.draw_text((width / 2) - 36, 0, "System Status", fill=0)

    cpu = cpu_util()
    total_memory = total_mem()
    total_memory_free = mem_free()
    disk_use = disk_usage()
    temp_c = temp()

    if cpu is None:
        driver.draw_text(0, 10, "CPU: Unknown%")
    else:
        value = 100 - int(float(cpu.group(1)))
        driver.draw_text(0, 10, "CPU: " + str(value) + "%")

    if total_memory is None or total_memory_free is None:
        driver.draw_text(0, 20, "Memory: Unknown%")
    else:
        value = 100 - ((float(total_memory.group(1)) / float(total_memory_free.group(1))) * 100)
        driver.draw_text(0, 20, "Memory: " + str(int(value)) + "%")

    if disk_usage is None:
        driver.draw_text(0, 30, "Disk: Unknown%")
    else:
        driver.draw_text(0, 30, "Disk: " + disk_use.group(1).decode("utf-8") + "%")

    if temp_c is None:
        driver.draw_text(0, 40,  "Temp: Unknown")
    else:
        driver.draw_text(0, 40, "Temp: " + temp_c.group(1).decode("utf-8"))
