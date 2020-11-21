
union() difference() { 
    cube(size = [500,300,5], center = false);
    translate([5,5,0])
    cylinder( d = 4.00, h = 20);
    translate([155,5,0])
    cylinder( d = 4.00, h = 20);
    translate([5,95,0])
    cylinder( d = 4.00, h = 20);
    translate([155,95,0])
    cylinder( d = 4.00, h = 20);
} 