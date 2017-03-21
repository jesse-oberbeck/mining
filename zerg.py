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
        self.north_spaces = 0

    def seekCorner(self, context):
        if context.south not in "#~":
            return 'SOUTH'
        elif context.west not in "#~":
            return 'WEST'
        else:
            self.direction = 'NORTH'
            self.found_corner = True
            return 'NEXT'

    def scan(self, context):
        if self.direction == 'NORTH' and self.north_spaces < 1 and context.north not in '#':
            self.north_spaces += 1
            self.direction = 'NORTH'

        elif self.direction == 'NORTH' and self.north_spaces == 1:
            self.north_spaces = 0
            self.direction = self.opposite
            if self.opposite == 'EAST':
                self.direction = 'EAST'
                self.opposite = 'WEST'
            elif self.opposite == 'WEST':
                self.direction = 'WEST'
                self.opposite = 'EAST'

        elif self.direction == 'EAST' and context.east not in "#":
            self.direction = 'EAST'

        elif self.direction == 'EAST' and context.north not in "#":
            self.direction = 'NORTH'

        elif self.direction == 'WEST' and context.west not in "#":
            self.direction = 'WEST'

        elif self.direction == 'WEST' and context.north not in "#":
            self.direction = 'NORTH'

        else:
            self.direction = 'PASS'
            self.north_spaces = 0

        print("scanning", self.direction)
        return self.direction

    def mineralCheck(self, context):
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

    def move(self, context):
        # Check if unit was just deployed.
        if self.deployed == False:
            self.drop_zone = [context.x, context.y]
            print(self.drop_zone[0], self.drop_zone[1])
            self.deployed = True

        check = self.mineralCheck(context)
        if check is not 'NEXT':
            return check

        if self.found_corner == False:
            check = self.seekCorner(context)
            if check is not 'NEXT':
                return check
            else:
                return 'STAY'

        else:
            check = self.scan(context)
            return check


#    def move(self, context):
#        new = randint(0, 3)
#        if new == 0 and context.north in '* ':
#            return 'NORTH'
#        elif new == 1 and context.south in '* ':
#            return 'SOUTH'
#        elif new == 2 and context.east in '* ':
#            return 'EAST'
#        elif new == 3 and context.west in '* ':
#            return 'WEST'
#        else:
#            return 'CENTER'

class Overlord:
    def __init__(self, total_ticks):
        self.maps = {}
        self.zerg = {}
        self.map_num = 0
        self.num_deployed = 0
        self.IDs = []

        for _ in range(6):
            z = Drone()
            self.zerg[id(z)] = z
            self.IDs.append(id(z))


    def add_map(self, map_id, summary):
        self.maps[map_id] = summary

    def action(self):
        time.sleep(1)#REMOVE THIS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if self.num_deployed < 3:
            for zergling in self.zerg:
                if self.zerg[zergling].deployed == True:
                    pass
                else:
                    tempnum = self.map_num
                    print("Deploying", zergling, "to map", tempnum)
                    self.zerg[zergling].deployed = True
                    self.map_num += 1
                    self.num_deployed += 1
                    self.map_num = self.map_num % 3
                    return 'DEPLOY {} {}'.format(zergling, tempnum)
                    
        else:
            return 'PASS'

#    def action(self):
#        act = randint(0, 3)
#        if act == 0:
#            pass#return 'RETURN {}'.format(choice(list(self.zerg.keys())))
#        else:
#            return 'DEPLOY {} {}'.format(choice(list(self.zerg.keys())),
#                    choice(list(self.maps.keys())))

