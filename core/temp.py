# 111, OPEN, 2023-01-01 00:00:00
# 111, CLOSED, 2023-01-01 00:00:01
# 222, OPEN, 2023-01-02 00:00:00
# 333, OPEN, 2023-01-02 00:00:00
# 222, CLOSED, 2023-01-03 00:00:00


def parse_tickets(file, timestamp):
    opened = []
    closed = []
    with file.open():
        while not EOF:
            line = list(file.readline().split(','))
            if line[-1] <= timestamp:
                if line[-2] == "OPEN":
                    opened.append(line[0])
                else: 
                    closed.append(line[0])
    return opened, closed

def get_opened(opened, closed):
    return set(opened) - set(closed)

    