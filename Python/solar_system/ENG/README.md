This is the **English** localized version of the program.
这是程序的英文版，**中文版**请看“教具版”文件夹。

# Documentation

## 1.Basic Operations

Click the ``Play`` button to emulate at normal speed, and click the ``Pause`` button to pause the simulation.

Click ``Fast`` or ``Slow`` to adjust the speed; Click the ``Clear`` button to clear the trajectory.

Click on ``Accelerate`` or ``Decelerate`` to adjust the speed of the planet.

Click the ``Exit`` button to exit the program.

## 2.Program 'Solar System with control'

By running the program "Solar System with control", you can display the motion of planets and satellites in the solar system by switching planets and other operations.

In the program 'Gravity Simulating the Solar System':

- (1) Press ``Ctrl+"+"`` or ``Ctrl+"-"`` to zoom.

- (2) Press the ``↑, ↓, ←, →`` keys to move.

- (3) Press the ``+`` or ``-`` keys to increase or decrease speed. Adjusting the speed to a negative value can cause time to reverse.

- (4) Click on the screen to turn on or off the track display. Click on a planet to follow it.

- (5) Press ``Tab``, ``Shift+Tab`` to switch planets, and press ``Delete`` to delete the currently followed planet.
- (6) Drag the mouse to launch the "spaceship", and press ``Ctrl+D`` to delete all spaceships if there are performance problems. After tracking the spaceship, informations such as the spaceship's speed will be displayed on the screen, and the speed is relative to the parent celestial body. The parent celestial body of the spaceship is determined by the celestial body being tracked at the time of spaceship launch. Press the ↑, ↓, ←, → keys to "pilot" the spaceship, with the ↑ and ↓ keys used for acceleration and deceleration, and the ← and → keys used for turning left (counterclockwise) and right (clockwise). Using the spaceship control function allows you to adjust the spaceship's orbital path, simulating the real process of spaceship launch and trajectory adjustment.

- (7) The "Open" and "Save" features allow you to save simulation progress, customize planets in the gravitational system, and create a more diverse and rich celestial system. The program currently supports saving files in xlsx, csv, and pkl (pickle) formats. The "default.xlsx" table stored in the program directory is an example of a saved Excel sheet and is also the default celestial bodies list that the program reads at startup. During editing, clicking on "Help" at the bottom left of the Excel sheet provides detailed instructions on the table. Press ``Ctrl+O`` to open files, ``Ctrl+S`` to save the current file.
- (8) The program includes a tool tip which can display information such as frame rate, parameters of the current following celestial body, current calculation precision and performance in the top right corner of the interface. Press ``F3`` to toggle the tool tip between three modes, including hidden, brief and detailed.
- (9) If you run this directly in Python, you also need to use the command "pip install pandas openpyxl" to install the required libraries.

## 3.Explanation on the Excel file "bodies.xlsx":

### (1) The Coordinate System in the Program

![](https://img-blog.csdnimg.cn/559cc887d35a44c394c420148cada255.png#pic_center =x300)

The program's origin is at the center of the screen. The units for screen dimensions are pixels. The coordinates (x, y) of celestial bodies are in pixels and represent the position of the bodies on the screen. The velocity vector (vx, vy) corresponds to the x and y components of the body's velocity.

### (2) Columns in the Table

The "name" column corresponds to the name of the celestial body, while the columns "m," "x," and "v" correspond to the body's mass, initial coordinates (x, y), and initial velocity vector (vx, vy). Other columns contain information about the body's shape and other properties (For more information,please refer to the source code).

### (3) Adding a New Celestial Body

Add a new row at the end of the table with the coordinates, velocity, and other information of the new body, then save the file.

In the program, the default gravitational constant is 8, and the velocity required for a new celestial body can be calculated based on physical formulas.

Example:


name | m | x| v | type
-------- | -----|----|-----|-----
New celestial body|30|(7500,0)|(0,48)|Star

### (4) Editing Celestial Bodies

Modify the data in the row of the celestial body and save it.

### (5) Deleting Celestial Bodies

Delete the row of data corresponding to the celestial body and save the table.

### (6) Adding Satellites

Create a new celestial body using the method mentioned above, then change the "parents" column of the celestial body to the corresponding planet's name and save the table.

Note: The row corresponding to the satellite should not be placed above the row corresponding to the planet, as it will not recognize the parent body.

### (7) Configuring the simulation

Click on "Config" at the bottom left in Excel to open this sheet to make modifications.

### (8) Notes and Issues

① If there are errors in the data entered in the table, a popup prompt will appear when running the program to help resolve the error.
② Data entries in the table now supports both half-width and full-width punctuations.
③ The type "SpaceCraft" do not support the "shape" and "sun" attributes.
④ The value "true" should be written as "True" or "TRUE" in the table, and the value "false" must be written as "False" or "FALSE".
⑤ The names of the tables "Celestial Bodies" and "Config" cannot be changed, as this will cause the program to be unable to read the data.

## 4.Program 'Satellite Orbit Change'

Run the program and click the "Accelerate" and "Deceleratie" buttons to demonstrate the orbit change process of the satellite, similar to launching an artificial satellite. 
Click the 'Reset' button to restore the initial satellite orbit.

## 5. Program 'Sun Earth Moon'

The program can simulate the motion of the sun, earth, and moon. Click the "Sun Earth Distance+" "Sun Earth Distance -" "Moon Earth Distance+" "Moon Earth Distance -" button to change the orbit radius of the Earth and Moon. 
Note that if the distance between the moon and the earth is too large or the distance between the sun and the earth is too small, the orbit of the moon and the earth will be unstable due to the influence of the tidal force of the sun.


## 6. Program "Kepler 1st"

Kepler's first law of planetary motion refers to:

(1) Each planet orbits the sun in its own elliptical orbit.

(2) The sun is at a focal point of the ellipse.


If the output PF~1~+PF~2~ of the program is approximately equal to the output long axis 2a, it is verified that the orbit of the planet is approximately elliptical, and Johannes Kepler's first law is verified.

## 7. Program "Kepler 2nd"

Kepler's Second Law states that on the same orbit, the line connecting the Sun and a planet in the solar system sweeps out equal areas in equal times. 
If the planet is on the same orbit, the program's output of "Area swept by planet ÷ time" is approximately a constant value, then the verification of Kepler's Second Law is successful. 
However, note that according to Kepler's Second Law, "Area swept by planet ÷ time" is not the same value on different orbits.

## 8. Program "Kepler 3rd"

Kepler's third law refers to the ratio of the cube of the semi major axis a of an elliptical orbit to the square of the period T of a planet orbiting the same celestial body. 

If the output result k of the program is approximately a fixed value, the verification of Johannes Kepler's third law passes.

## 9. Program 'Cosmic Velocities'

Run program to observe that the objects with the first cosmic speed orbit around the stars in a circular orbit, while those with the escape velocity fly out along a parabola. Click the 'Restart' button to restart the simulation process.

## 10. Units in the program

In the program, the distance is measured in pixels, and the time is virtual and has no units. 
The speed of time can be adjusted by clicking the "Speed Up" or "Slow Down" buttons. 
Note that if the time speed is too fast, the accuracy of the gravitational simulation may decrease.