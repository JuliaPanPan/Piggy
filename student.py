from teacher import PiggyParent
import sys
import time

class Piggy(PiggyParent):

    '''
    *************
    SYSTEM SETUP
    *************
    '''

    def __init__(self, addr=8, detect=True):
        PiggyParent.__init__(self) # run the parent constructor

        ''' 
        MAGIC NUMBERS <-- where we hard-code our settings
        '''
        self.LEFT_DEFAULT = 100
        self.RIGHT_DEFAULT = 100
        self.exit_heading = 0
        self.SAFE_DIST = 300
        self.MIDPOINT = 1350  # what servo command (1000-2000) is straight forward for your bot?
        self.load_defaults()


    def load_defaults(self):
        """Implements the magic numbers defined in constructor"""
        self.set_motor_limits(self.MOTOR_LEFT, self.LEFT_DEFAULT)
        self.set_motor_limits(self.MOTOR_RIGHT, self.RIGHT_DEFAULT)
        self.set_servo(self.SERVO_1, self.MIDPOINT)
        

    def menu(self):
        """Displays menu dictionary, takes key-input and calls method"""
        ## This is a DICTIONARY, it's a list with custom index values. Python is cool.
        # Please feel free to change the menu and add options.
        print("\n *** MENU ***") 
        menu = {"n": ("Navigate", self.nav),
                "d": ("Dance", self.dance),
                "o": ("Obstacle count", self.obstacle_count),
                "h": ("Hold Position", self.hold_position),
                "c": ("Calibrate", self.calibrate),
                "q": ("Quit", self.quit)
                }
        # loop and print the menu...
        for key in sorted(menu.keys()):
            print(key + ":" + menu[key][0])
        # store the user's answer
        ans = str.lower(input("Your selection: "))
        # activate the item selected
        menu.get(ans, [None, self.quit])[1]()

    '''
    ****************
    STUDENT PROJECTS
    ****************
    '''

    def dance(self):
        #highered - ordered
        # check ot see it's safe
        if not self.safe_to_dance():
            print("Not cool. Not going to dance")
            return #return closes down the method
        else:
            print("It's safe to dance")
        for x in range(1):
            self.dab()
            self.floss()
            self.whip()
            self.sprinkler()
            self.spin()
            self.shake()

    def safe_to_dance(self):
        """does a 360 distance check and returns true if safe"""
        for x in range(4):
            for ang in range(1000, 2001, 100):
                self.servo(ang)
                time.sleep(.1)
                if self.read_distance() < 250:
                    return False
            self.turn_by_deg(90)
        return True

    def scan(self):
        """Sweep the servo and populate the scan_data dictionary"""
        for angle in range(self.MIDPOINT-350, self.MIDPOINT+350, 100):
            self.servo(angle)
            self.scan_data[angle] = self.read_distance()

    def obstacle_count(self):
        """ Does a 360 scan and returns the number of obstacles it sees"""
        found_something = False #trigger
        trigger_distance = 250
        count = 0
        starting_position = self.get_heading() #write down starting position
        self.right(primary=60, counter=-60)
        while self.get_heading() != starting_position:
            if self.read_distance() < trigger_distance and not found_something:
                found_something = True
                count += 1
                print("\n FOUND SOMETHING!!!! \n")
            elif self.read_distance() > trigger_distance and found_something:
                found_something = False 
                print("I have a clear view. Resetting my counter")
        self.stop()
        print("I found this many things: %d" % count)
        return count 

    def quick_check(self):
        #three wuick checks
        for ang in range (self.MIDPOINT-150, self.MIDPOINT+151, 150):
            self.servo(ang)
            if self.read_distance() < self.SAFE_DIST:
                return False
        #if I didn't get to the end, this means I didn't find anything dangerous
        return True

    def nav(self):
        "robot able to navigate by checking surroundings"
        

        #assuming that we are facing the exit at the start
        self.exit_heading = self.get_heading()      

        print("-----------! NAVIGATION ACTIVATED !------------\n")
        print("-------- [ Press CTRL + C to stop me ] --------\n")
        print("-------------! EXIT IS AT %d !---------------\n" % self.exit_heading) 
        corner_count = 0
        while True:
            self.servo(self.MIDPOINT) #return servo to the center 
            while self.quick_check():
                corner_count = 0
                self.fwd()
                time.sleep(.01)
            self.stop()
            self.scan()
            corner_count += 1
            if corner_count == 3:
                self.escape()
            if not self.path_towards_exit():                
                self.average_turn()

    def path_towards_exit(self):
        where_I_started = self.get_heading() 
        self.turn_to_deg(self.exit_heading)
        if self.quick_check():
            return True
        else:
            self.turn_to_deg(where_I_started)
        return False            
    
    def average_turn(self):
        '''robot decides where an obstacle is and turns left or right from that '''
        corner_count = 0
        corner_count += 1
        if corner_count == 3:
            self.escape()
        left_total = 0
        left_count = 0
        right_total = 0
        right_count = 0
        for ang, dist in self.scan_data.items():
            if ang < self.MIDPOINT:
                right_total += dist
                right_count +=1
            else:
                left_total += dist
                left_count += 1
        left_avg = left_total / left_count
        right_avg = right_total / right_count
        if left_avg > right_avg:
            self.turn_by_deg(-45)
        else:
            self.turn_by_deg(45)
    
    def escape(self):
        self.turn_by_deg(180)
        self.deg_fwd(720)  
        self.turn_to_deg(self.exit_heading)

    def hold_position(self):
        angle_started_at = self.get_heading()
        while True:
            time.sleep(.1)
            current_angle = self.get_heading()
            if abs(angle_started_at - current_angle) > 3:
                self.turn_to_deg(angle_started_at)

    def dab(self): #turn robot right and servo left, return to original position
        #high power left
        self.turn_by_deg(-45)
        #servo right
        self.servo(1000)   
        time.sleep(3)
        #return to original position
        self.turn_by_deg(45)
        self.servo(1500)
        time.sleep(2)
        #stop
        self.stop()
        
    

    def floss(self):# turn body at 45 degrees and go forward and backwards, repeat on other side
        #floss right
        #turn right
        self.turn_by_deg(45)
        #go forward for 1 second
        self.fwd()
        time.sleep(1)
        #go backwards for 1 second
        self.back()
        time.sleep(1)
        #floss left
        #turn left
        self.turn_by_deg(-45)
        #go forward for 1 second
        self.fwd()
        time.sleep(1)
        #go backwards for 1 second
        self.back()
        time.sleep(1)
        #floss right again
        #turn right
        self.turn_by_deg(90)
        #go forward
        self.fwd()
        time.sleep(1)
        #go backwards
        self.back()
        time.sleep(1)
        #stop
        self.stop()


    def whip(self): #medium power, right high power left
        #turn slightly right
        self.turn_by_deg(30)
        time.sleep(1)
        #turn left hard
        self.turn_by_deg(100)
        time.sleep(2)
        #stop
        self.stop()

    def sprinkler(self): #high power right and go left in five short increments
        #servo look right
        self.servo(1000)
        #robot turn right 5 times in short increments
        for x in range(5):
            self.turn_by_deg(-20)
            time.sleep(.5)
        self.servo(1500)
        #stop
        self.stop()

    def spin(self): #spin in a circle clockwise then counterclockwise
        #spin in a circle right
        self.turn_by_deg(180)
        self.turn_by_deg(180)
        #spin in a circle left
        self.turn_by_deg(-180)
        self.turn_by_deg(-180)
        #stop
        self.stop()

    def shake(self): #shake servo, go forward shake robot, bo backward shake robot
        #servo shake head
        for x in range(4):
            self.servo(1000)
            time.sleep(.25)
            self.servo(2000)
            time.sleep(.25)
            #go forward
        self.fwd()
        #robot shake
        time.sleep(1)
        for x in range(3):
            self.turn_by_deg(45)
            self.turn_by_deg(-45)
        #go backward
        self.back()
        time.sleep(1)
        #robot shake
        for x in range(3):
            self.turn_by_deg(45)
            self.turn_by_deg(-45)
        self.stop()


###########
## MAIN APP
if __name__ == "__main__":  # only run this loop if this is the main file

    p = Piggy()

    if sys.version_info < (3, 0):
        sys.stdout.write("Sorry, requires Python 3.x\n")
        p.quit()

    try:
        while True:  # app loop
            p.menu()

    except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
        p.quit()  
