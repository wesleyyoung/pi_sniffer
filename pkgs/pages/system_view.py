from pkgs.api.sys.cpu_util import cpu_util
from pkgs.api.sys.disk import disk_usage
from pkgs.api.sys.mem import total_mem, mem_free
from pkgs.api.sys.temp import temp


def do_system_view(draw, font, width):
    draw.rectangle((0, 0, width, 10), outline=1, fill=1)
    draw.text(((width / 2) - 36, 0), "System Status", fill=0)

    cpu = cpu_util()
    total_memory = total_mem()
    total_memory_free = mem_free()
    disk_use = disk_usage()
    temp_c = temp()

    if cpu is None:
        draw.text((0, 10), "CPU: Unknown%", font=font, fill=1)
    else:
        value = 100 - int(float(cpu.group(1)))
        draw.text((0, 10), "CPU: " + str(value) + "%", font=font, fill=1)

    if total_memory is None or total_memory_free is None:
        draw.text((0, 20), "Memory: Unknown%", font=font, fill=1)
    else:
        value = 100 - ((float(total_memory.group(1)) / float(total_memory_free.group(1))) * 100)
        draw.text((0, 20), "Memory: " + str(int(value)) + "%", font=font, fill=1)

    if disk_usage is None:
        draw.text((0, 30), "Disk: Unknown%", font=font, fill=1)
    else:
        draw.text((0, 30), "Disk: " + disk_use.group(1).decode("utf-8") + "%", font=font, fill=1)

    if temp_c is None:
        draw.text((0, 40), "Temp: Unknown", font=font, fill=1)
    else:
        draw.text((0, 40), "Temp: " + temp_c.group(1).decode("utf-8"), font=font, fill=1)
