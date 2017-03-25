#!/usr/local/bin/python

from random import randint, choice
import time


class Drone:

    def __init__(self):
        self.deployed = False
        self.drop_zone = [0, 0]
        self.found_corner = False
        self.direction = 'EAST'
        self.opposite = 'EAST'
        self.vert_spaces = 0
        self.avoiding = False
        self.axis = 0
        self.signal = False
        self.beacon = False
        self.type = None
        self.phase = 'NORTH'
        self.recurse = 0

    def seekCorner(self, context):

        # Before starting it's complete search(scan) the zerg is first
        # sent to the corner, where it can appropriately begin.

        if context.south not in "#~":
            self.axis = context.x
            return 'SOUTH'
        elif context.west not in "#":
            self.axis = context.y
            return 'WEST'
        else:
            self.direction = 'NORTH'
            self.found_corner = True
            return 'NEXT'

    def scan(self, context):

        # Goes from the bottom of the map to the top, weaving side to side
        # as it does so, turning around and weaving toward the bottom
        # once it has reached the top.

        vert = None

        if self.phase == 'NORTH':
            vert = context.north
        elif self.phase == 'SOUTH':
            vert = context.south

        path = vert
        if self.direction == self.phase and self.vert_spaces\
        < 1 and vert not in '#':
            self.vert_spaces += 1
            self.direction = self.phase
            path = vert
            self.axis = context.x

        elif self.direction == self.phase and self.vert_spaces == 1:
            self.vert_spaces = 0
            self.direction = self.opposite
            if self.opposite == 'EAST':
                self.direction = 'EAST'
                path = context.east
                self.axis = context.y
                self.opposite = 'WEST'
            elif self.opposite == 'WEST':
                self.direction = 'WEST'
                path = context.west
                self.axis = context.y
                self.opposite = 'EAST'

        elif self.direction == 'EAST' and context.east not in "#":
            self.direction = 'EAST'
            self.axis = context.y
            path = context.east

        elif self.direction == 'EAST' and vert not in "#":
            self.direction = self.phase
            self.axis = context.y
            path = vert

        elif self.direction == 'WEST' and context.west not in "#":
            self.direction = 'WEST'
            self.axis = context.y
            path = context.west

        elif self.direction == 'WEST' and vert not in "#":
            self.direction = self.phase
            self.axis = context.x
            path = vert

        else:
            if self.phase == 'SOUTH':
                self.signal = True
            self.phase = 'SOUTH'
            print("PHASE CHANGE", self.phase)
            self.direction = 'SOUTH'
            self.vert_spaces = 0

        print("DIR", self.direction)
        # Check if avoidance needs to happen.
        if path in "~#":
            if vert not in '#':
                return self.phase
        if path in "Z":
            return 'WAIT'

        print("scanning", self.direction)
        return self.direction

    def mineralCheck(self, context):

        # Pre-empts other movements if minerals are around
        # to mine said minerals.

        if context.north in "*":
            print("Mineral found N")
            return 'NORTH'
        elif context.south in "*":
            print("Mineral found S")
            return 'SOUTH'
        elif context.east in "*":
            print("Mineral found E")
            return 'EAST'
        elif context.west in "*":
            print("Mineral found W")
            return 'WEST'
        else:
            return 'NEXT'

    def bounce(self, context):

        # The zerg goes straight in a random direction until an
        # obstacle is encountered, or at random intervals.

        directions = ["NORTH", "SOUTH", "EAST", "WEST"]
        heading = None
        if self.direction == "NORTH":
            heading = context.north
        if self.direction == "SOUTH":
            heading = context.south
        if self.direction == "EAST":
            heading = context.east
        if self.direction == "WEST":
            heading = context.west

        if heading in "#~Z" or randint(0, 20) == 6:
            directions.remove(self.direction)
            self.direction = choice(directions)
            self.recurse += 1
            if self.recurse == 50:
                self.recurse = 0
                return 'STAY'
            self.bounce(context)

        return self.direction

    def turn_in(self, context):

        # Brings the zerg closer to the landing zone.

        print("GOIN HOME")
        x = context.x
        y = context.y
        obstacle = False
        x_diff = x - self.drop_zone[0]
        y_diff = y - self.drop_zone[1]
        if x == self.drop_zone[0] and y == self.drop_zone[1]:
            print('on DZ')
            self.beacon = True

        elif abs(x_diff) > abs(y_diff):
            if x > self.drop_zone[0]:
                print('west')
                if context.west in "Z":
                    return 'WAIT'
                else:
                    return 'WEST'
            else:
                print('east')
                if context.east in "Z":
                    return 'WAIT'
                else:
                    return 'EAST'

        elif abs(x_diff) <= abs(y_diff):
            if y > self.drop_zone[1]:
                print('south')
                if context.south in "Z":
                    return 'WAIT'
                return 'SOUTH'
            else:
                print('north')
                if context.north in "Z":
                    return 'WAIT'
                return 'NORTH'

        else:
            print("on DZ...")
            self.beacon = True
            return 'WAITING'

    def move(self, context):

        # Base movement function, determines which movement method to use,
        # and returns the result of that method.

        # Check if unit was just deployed.
        if self.deployed is False:
            self.drop_zone = [context.x, context.y]
            print("DROP ZONE:", self.drop_zone[0], self.drop_zone[1])
            self.deployed = True

        check = self.mineralCheck(context)
        if check is not 'NEXT':
            return check

        if self.signal:
            check = self.turn_in(context)
            return check

        if self.found_corner is False and self.type == 'SCANNER':
            print("SEEKING CORNER")
            check = self.seekCorner(context)
            if check is not 'NEXT':
                return check
            else:
                return 'STAY'

        elif self.type == 'SCANNER':
            print("SCAN!")
            check = self.scan(context)
            return check

        elif self.type == 'ROOMBA':
            print("ROOMBA!")
            check = self.bounce(context)
            return check


class Overlord:
    def __init__(self, total_ticks):
        self.maps = {}
        self.zerg = {}
        self.map_num = 0
        self.num_deployed = 0
        self.IDs = []
        self.ticks = total_ticks
        self.signal = False
        self.mark = self.ticks * .2  # 20% of ticks remaining.

        for _ in range(6):
            z = Drone()
            self.zerg[id(z)] = z
            self.IDs.append(id(z))

    def signal_zerg(self):

        # Tells the zerg units to head to the landing zone.

        for unit in self.zerg:
            self.zerg[unit].signal = True

    def add_map(self, map_id, summary):
        self.maps[map_id] = summary

    def action(self):

        # Deploys and returns zerg.

        if self.ticks == self.mark:
            self.signal = True
            self.signal_zerg()
        elif self.ticks < self.mark:
            print("ATTEMPTING RETURNS")
            for unit in self.IDs:
                if self.zerg[unit].deployed is True\
                and self.zerg[unit].beacon is True:
                    self.zerg[unit].deployed = False
                    return 'RETURN {}'.format(unit)

        # time.sleep(.25)  # Was used for visual purposes.
        self.ticks -= 1
        print("ticks:", self.ticks)

        # Sends the first wave of zerg to methodically scan.
        if self.num_deployed < 3:
            print("DEPLOYING SCANNER")
            for zergling in self.zerg:
                if self.zerg[zergling].deployed is True:
                    pass
                else:
                    tempnum = self.map_num
                    print("Deploying", zergling, "to map", tempnum)
                    self.zerg[zergling].type = 'SCANNER'
                    self.map_num += 1
                    self.num_deployed += 1
                    self.map_num = self.map_num % 3
                    return 'DEPLOY {} {}'.format(zergling, tempnum)

        # Sends the second wave of zerg to bounce about.
        elif self.num_deployed < 6:
            print("DEPLOYING ROOMBA")
            for zergling in self.zerg:
                if self.zerg[zergling].deployed is True:
                    pass
                else:
                    tempnum = self.map_num
                    print("Deploying", zergling, "to map", tempnum)
                    self.zerg[zergling].type = 'ROOMBA'
                    self.map_num += 1
                    self.num_deployed += 1
                    self.map_num = self.map_num % 3
                    return 'DEPLOY {} {}'.format(zergling, tempnum)

        # Pass the time between deploying and retrieving.
        else:
            return 'PASS'
