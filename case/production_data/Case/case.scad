content = "Industrial Scanner";
font = "Liberation Sans";

union() difference() { 
    translate([-1,-1,0])
    cube(size = [162,102,5], center = false);
    // PCB mount
    translate([5,5,0])
    cylinder( d = 4.00, h = 20);
    translate([155,5,0])
    cylinder( d = 4.00, h = 20);
    translate([5,95,0])
    cylinder( d = 4.00, h = 20);
    translate([155,95,0])
    cylinder( d = 4.00, h = 20);
    
    // Case mount
    translate([30,25,0])
        cylinder( d = 4.00, h = 20);
    translate([80,25,0])
        cylinder( d = 4.00, h = 20);
    translate([130,25,0])
        cylinder( d = 4.00, h = 20);
    translate([30,50,0])
        cylinder( d = 4.00, h = 20);
    translate([80,50,0])
        cylinder( d = 4.00, h = 20);
    translate([130,50,0])
        cylinder( d = 4.00, h = 20);
    translate([30,75,0])
        cylinder( d = 4.00, h = 20);
    translate([80,75,0])
        cylinder( d = 4.00, h = 20);
    translate([130,75,0])
        cylinder( d = 4.00, h = 20);
       
} 



// Rounded corners
union() difference() { // front left
    translate([-1,-1,0])
        cylinder( d = 5.00, h = 50);
    translate([-1,-1,0])
        cube(size = [5,5,50], center = false);
} 
union() difference() { // front right
    translate([161,-1,0])
        cylinder( d = 5.00, h = 50);
    translate([156,-1,0])
        cube(size = [5,5,50], center = false);
} 
union() difference() { // back right
    translate([161,101,0])
        cylinder( d = 5.00, h = 50);
    translate([156,96,0])
        cube(size = [5,5,50], center = false);
} 
union() difference() { // back left
     translate([-1,101,0])
        cylinder( d = 5.00, h = 50);
    translate([-1,96,0])
        cube(size = [5,5,50], center = false);
} 

// Left
translate([-3.5,-1,0])
    cube(size = [2.5,102,50], center = false);
// Right
translate([161,-1,0])
    cube(size = [2.5,102,50], center = false);
// Front
translate([-1,-3.5,0])
    cube(size = [162,2.5,10], center = false);
translate([-1,-3.5,0])
    cube(size = [6,2.5,50], center = false);
translate([155,-3.5,0])
    cube(size = [6,2.5,50], center = false);
translate([70,-3.5,0])
    cube(size = [20,2.5,50], center = false);
union() difference() { // back left
    translate([81,-1,0])
        cylinder(d = 10.00, h = 50);
    translate([70,-13.5,0])
        cube(size = [20,10,50], center = false);
}
// Back
translate([-1,101,0])
    cube(size = [162,2.5,30], center = false);

translate([155,101,0])
        cube(size = [6,2.5,50], center = false);
union() difference() { 
    translate([-1,101,0])
        cube(size = [126,2.5,50], center = false);
    translate ([122,102,30]) {
        rotate([90,0,180])
        linear_extrude(height = 20) {
           text(content, font = font, size = 11);
       }
    }
}
