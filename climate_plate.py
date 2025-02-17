"""
# Author  : Jason Connie
# Created : Feb 2025

This code generates the climate plate of an astrolabe. It is also known as the plate, the climate or the tympan (Latin: tabula, Arabic: safiha). 
The outputted file is saved as 'plate.py'.

When running the code from terminal, place the latitude (in degrees) a space after the file-name. 
If using Python 3, 
     'python3 climate_plate.py 45.2'
would generate a plate for a latitude 45.2 degrees either North or South of the equator. 
A preferred latitude can also be placed directly into the code at line 44. 
If no latitude is given, the program defaults to South Africa.

The latitude should always be positive, from 0 to 90. This is regardless of the hemisphere. 
Since South Africa is 30.56°S, it's plate is generated by
     'python3 climate_plate.py 30.56'
And since Tunisia has a latitude of 33.89°N, we'd use
     'python3 climate_plate.py 33.89'
where there are no minus signs to distinguish North from South.

"""



import cairo
import os
from math import pi, tan, sin, cos
import math
import numpy as np
import sys


if __name__=="__main__":

    """#######"""
    """ Input """
    """#######"""
    
    # The latitude degree can be inputted immediately after the script name when running from the terminal, eg 'python3 astrolabe.py 39.3299'. 
    # If no degree is given, we default to the value 30.56 below
    if len(sys.argv)>1:
        latitude_degree = float(sys.argv[1])
    else: 
        latitude_degree = 30.56 # Defaults to South Africa
    
    # Division by 0 can be an issue when handling trig functions. This arises when our latitude is 0 or 90 exactly. More mathematically rigorous code will be implemented later, but a simple solution is to use incredibly close values that avoid any division by zero. Doing such produces climate plates visually indistinguishable from those for 0 and 90 degrees.
    if latitude_degree == 0:
        latitude_degree = 0.00001
    if latitude_degree == 90:
        latitude_degree = 89.9999
    
    
    
    """####################################################################"""
    """ Basic set-up: line width to be drawn, plot size, and Cairo details """
    """####################################################################"""
    
    almucantar_increment = 2.5
    outer_radius  = 125
    thick_line    = 0.8
    medium_line   = 0.575#0.55
    thin_line     = 0.15

    width         = int(2.3*outer_radius) # The width and height of the plot
    height        = int(2.3*outer_radius) 
    origin_x      = width//2              # The x and y points of the origin for the plot
    origin_y      = height//2
    axial_tilt    = (23.4/180)*pi         # Axial tilt of the Earth. Also called obliquity (of the ecliptic). Expressed in radians

    middle_radius = outer_radius*tan( (pi/2 - axial_tilt)/2) # Corresponds to equator
    inner_radius  = middle_radius*tan((pi/2 - axial_tilt)/2) # Corresponds to Tropic of Cancer (if latitude is North)

    phi = (latitude_degree/180)*pi     # We express the altitude for the constructed astrolabe in radians
    
    sfc = cairo.ImageSurface(cairo.Format.ARGB32, width, height)  # Pycairo stuff we need to do. Setting the surface and context to draw on.
    sfc = cairo.PDFSurface('plate.pdf', width, height)
    ctx = cairo.Context(sfc)

    ctx.set_line_width(thick_line)     # Setting the width of the brush stroke
    ctx.set_source_rgb(0,0,0)          # Colour is set to black for the brush
    
    
    
    """##########################################"""
    """ Constructing the horizon and almucantars """
    """##########################################"""
    
    if latitude_degree==0: # If latitude is the equator, the horizon is the y-axis and is already drawn
        start = almucantar_increment
    else:
        start = 0
    
    almucantar_range = list(np.arange(start,61,almucantar_increment)) + list(range(65,81,5))
    
    # We draw an individual almucantar for each degree of the range
    for altitude_degree in almucantar_range:
        altitude_angle  = (altitude_degree/180)*pi # We convert to the altitude angle in radians

        # If the latitude is divisible by 10, it is made slightly bolder
        if (altitude_degree%10==0):
            ctx.set_line_width(medium_line)
        else:
            ctx.set_line_width(thin_line)
        
        # We get the points of projection for the lower and upper ends of the circle: (phi +/- altitude_angle)/2 is only pi/2 when (latitude_degree + altitude_degree)==180, which is only true when the latitude is 90
        r_L = -middle_radius*tan((phi-altitude_angle)/2)     # r_L in Morrison
        r_U =  middle_radius*(1/tan((phi+altitude_angle)/2)) # r_U in Morrison
        
        # We use the above values to solve for the radius and center
        almucantar_radius = (r_U-r_L)/2
        almucantar_center = (r_U+r_L)/2
        
        # The 'tmp' value tells us whether the current almucantar circle intersects the outer circle
        if (latitude_degree == 90):
            tmp = 2                   # Can be any value above 1 or below -1. Special case to avoid division by 0.
        else:
            tmp = (almucantar_radius**2 + almucantar_center**2 - outer_radius**2)/(2*almucantar_radius*almucantar_center)
        
        
        # If 'tmp' is above 1 or below -1, the current almucantar does not intersect the outer circle and can be drawn fully.
        # If 'tmp' is between 1 and -1, the complete circle is not drawn and the arc bounds must be adjusted.
        if (tmp>1 or tmp<-1):
            ctx.arc(origin_x, origin_y - almucantar_center, almucantar_radius, 0, 2*pi)
        else:
            ang = math.acos(tmp)
            ctx.arc(origin_x, origin_y - almucantar_center, almucantar_radius, pi/2-ang, pi/2+ang)

        ctx.stroke()
        
        # If the degree is divisible by 10, we add a label. 2.73 is the approximate height of the font.
        # Recall that the top left corner of the pdf plot has (x,y)=(0,0). So the top edge of the climate plate is (width-2*outer_radius)/2=width/2-outer_radius.
        label_y = origin_y - almucantar_center - almucantar_radius - 0.5
        if (altitude_degree%10==0 and label_y>width/2-outer_radius+2.73):
            ctx.set_font_size(5)
            ctx.select_font_face("Times New Roman", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.move_to(origin_x+0.4, label_y)
            ctx.show_text(str(int(altitude_degree)))
            ctx.stroke()
            
            
            
    """################################"""
    """ Constructing the azimuth lines """
    """################################"""
    
    # All azimuth circles go through the nadir and zenith
    zenith_y            =  middle_radius*tan((pi/2-phi)/2)
    nadir_y             = -middle_radius*tan((pi/2+phi)/2)
    azimuth_centre_y    = (-1)*(zenith_y + nadir_y)/2   # we multiply by -1 due to coordinate system for pycairo starting at 0,0 in top left corner
    azimuth_y_to_zenith = azimuth_centre_y + zenith_y   # distance from the azimuth's centre's y co-ordinate, to the zenith


    horizon_L = -middle_radius*tan((phi)/2)
    horizon_U =  middle_radius*(1/tan((phi)/2))
    radius_horizon    = (horizon_U - horizon_L)/2
    horizon_centre_y  = (horizon_U + horizon_L)/2  # y_H

    ctx.set_line_width(thin_line)


    for ang in range(10,90,10):
        A = (90-ang)/180*pi   # A is the angle of the current azimuth, in radians
        
        x_A = azimuth_y_to_zenith * tan(A)  # x co-ordinate of the current azimuth's circle's centre
        R_A = azimuth_y_to_zenith / cos(A)  # radius of the current azimuth's circle's centre
        
        HC = ( (horizon_centre_y + azimuth_centre_y)**2 + x_A**2 )**0.5    # HC = ((y_H + y_C)**2 + x_A**2)**0.5
        
        if x_A == 0:      # If the azimuth centre's x co-ordinate is 0, the angle from the centre of the azimuth to the zenith is pi/2
            ang_CA = pi/2
            ctx.set_line_width(thick_line)
        else:             # The above condition is performed to avoid a division by zero
            ang_CA = math.atan( (horizon_centre_y + azimuth_centre_y)/x_A )
        
        ang_D = math.acos( (radius_horizon**2 - HC**2 - R_A**2)/(-2*HC*R_A)  )
        start_ang = pi+ang_CA-ang_D
        end_ang   = pi+ang_CA+ang_D
        
        diff = (azimuth_centre_y**2 + x_A**2)**0.5

        # We determine the end angle of the azimuth, so the arc isn't drawn beyond the edge of the climate plate
        tmp = (diff**2 + R_A**2 - outer_radius**2)/(2*diff*R_A)
        if abs(tmp)<=1 and x_A!=0:
            end_ang_2 = math.atan(azimuth_centre_y/x_A) + math.acos(tmp)
            end_ang_2 = pi + end_ang_2
            end_ang = min(end_ang, end_ang_2)

        # We draw two azimuths for every angle, given the symmetry of the situation
        ctx.arc(origin_x + x_A, origin_y + azimuth_centre_y, R_A, start_ang, end_ang)
        ctx.stroke()
        ctx.arc(origin_x - x_A, origin_y + azimuth_centre_y, R_A, 3*pi - end_ang, 3*pi - start_ang)
        ctx.stroke()

    # We draw a white-filled circle from the 80 to 90 degree latitudes. Done to avoid an overly busy congregation of lines around the zenith. [Note: this is not an azimuth circle]
    ctx.arc(origin_x, origin_y - almucantar_center, almucantar_radius, 0, 2*pi)
    ctx.set_source_rgb(1,1,1)
    ctx.fill_preserve()
    ctx.set_source_rgb(0,0,0)
    ctx.stroke()


    # We draw/redraw the prime vertical, the azimuth that goes from the eastern to western horizon, to stand out on top of the above white-filled circle  
    ctx.set_line_width(thick_line)
    x_A = 0
    R_A = azimuth_y_to_zenith
    HC = (horizon_centre_y + azimuth_centre_y)
    ang_CA = pi/2
    ang_D = math.acos( (radius_horizon**2 - HC**2 - R_A**2)/(-2*HC*R_A)  )
    start_ang = pi+ang_CA-ang_D
    end_ang   = pi+ang_CA+ang_D
    ctx.arc(origin_x + x_A, origin_y + azimuth_centre_y, R_A, start_ang, end_ang)
    ctx.stroke()
    
    
    
    
    """############################################"""
    """ Constructing the axis, equator and tropics """
    """############################################"""
    
    # Drawing the outer circle. For the Northern hemisphere, this is the Tropic of Capricorn. For the Southern hemisphere, this is the Tropic of Cancer.
    ctx.arc(origin_x, origin_y, outer_radius, 0, 2*pi) # defining the arc to draw
    ctx.stroke()                                       # drawing the stroke onto the canvas
    
    # Drawing the equator
    ctx.arc(origin_x, origin_y, middle_radius, 0, 2*pi)
    ctx.stroke()
    
    # Drawing the inner circle. For Northern altitudes, this corresponds to the Tropic of Cancer. For Southern altitudes, this corresponds to the Tropic of Capricorn
    ctx.arc(origin_x, origin_y, inner_radius, 0, 2*pi)
    ctx.stroke()
    
    # Drawing the y-axis
    ctx.move_to(origin_x, origin_y)
    ctx.line_to(origin_x, origin_y-outer_radius)
    ctx.stroke()
    ctx.move_to(origin_x, origin_y)
    ctx.line_to(origin_x, origin_y+outer_radius)
    ctx.stroke()
    
    # Drawing the x-axis 
    ctx.move_to(origin_x, origin_y)
    ctx.line_to(origin_x-outer_radius, origin_y)
    ctx.stroke()
    ctx.move_to(origin_x, origin_y)
    ctx.line_to(origin_x+outer_radius, origin_y)
    ctx.stroke()










