from bt_proximity import BluetoothRSSI
import time
import sys
import numpy

#here we calculate the rssi
def calc_rssi(addresses, loops):
    print "Calculating"
    btrssi = BluetoothRSSI(addr = address)
    vals = []
    for i in range (0, loops):
        vals.append(btrssi.get_rssi())
        time.sleep(1)
    return numpy.mean(vals)

def calc_distance(dataPoint):
    #need to edit this for your specific bluetooth device (on computer not tracking)
    tx_power = -89
    ratio = dataPoint[0] / tx_power
    if ratio < 1.0:
        return numpy.power(ratio, 10)
    else:
        return (0.89976) * numpy.power(ratio, 7.7095) + 0.111

def in_radius(x, y, radius, ox, oy):
    dist = numpy.power(x - ox, 2) + numpy.power(y - oy, 2)
    test_radius = numpy.power(radius, 2)

    if dist < test_radius:
        return True
    else:
        return False

def get_location(one, two, three, four):
    a_b = two[1] - one[1]
    b_c = three[1] - two[1]
    c_d = four[1] - three[1]

    #human walking speed in m/ms
    speed = 1.4 / 1000

    om = calc_distance(one)
    tm = calc_distance(two)
    thm = calc_distance(three)
    fm = calc_distance(four)

    #how big is the place?
    area =  numpy.zeros((a_b * 1000, b_c * 1000))
    originx = [0, a_b * 1000, 0, a_b * 1000]
    originy = [0, 0, b_c * 1000, b_c * 1000]
    radius = [om, tm, thm, fm]
    for m in range(0, 4):
        for i in range(0, a_b * 1000):
            for j in range (0, b_c * 1000):
                if in_radius(i, j, radius[m], originx[m], origin[y]):
                    area[i, j] = area[i, j]++
    for i in range(0, a_b * 1000):
        for j in range (0, b_c * 1000):
            if area[i,j] == 4:
                return (i, j)
    dist = numpy.power(x - originx[3], 2) + numpy.power(y - originy[3], 2)
    dist = dist / 1000
    angle = numpy.arcsin(dist, a_b)
    angle = (angle * 180) / numpy.pi
    return (dist, angle)

def main()
        if len(sys.argv) > 1:
            addr = sys.argv[1]
        else:
            return
        if len(sys.argv) == 3:
            loops = int(sys.argv[2])
        else:
            return
        input("Press enter to start")
        one = (calc_rssi(addr, loops), time.time())
        input("Press enter to continue")
        two = (calc_rssi(addr, loops), time.time())
        input("Press enter to continue")
        three = (calc_rssi(addr, loops), time.time())
        input("Press enter to continue")
        four = (calc_rssi(addr, loops), time.time())
        loc = get_location(one, two, three, four)
        print "Face the starting point. Turn right " + str(loc[1]) + " degrees. Now go forward " + str(loc[0]) + "meters. There is the bluetooth device"
