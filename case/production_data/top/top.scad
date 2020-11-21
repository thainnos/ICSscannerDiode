difference() {
    union() {
        // Base plate
        translate([-1,-1,0])
            cube(size = [162,102,1], center = false);
        // Place in
        translate([0.2,0,-3])
            cube(size = [159.6,100,3], center = false);
    }
    // PCB mount
    translate([5,5,-4])
        cylinder( d = 4.00, h = 40);
    translate([155,5,-4])
        cylinder( d = 4.00, h = 40);
    translate([5,95,-4])
        cylinder( d = 4.00, h = 40);
    translate([155,95,-4])
        cylinder( d = 4.00, h = 40);
    // For case
    translate([80,50,-4])
        cylinder( d = 4.00, h = 20);
    
    //display
    translate([2,8,-3])
        cube(size = [74,83,4], center = false);
    translate([84,8,-3])
        cube(size = [74,83,4], center = false);
    translate([80,0,-3])
        cylinder( d = 13.00, h = 3);
    // many holes
    //for (i = [1 : 15]){
    //    for (j = [1 : 9]){
    //        translate([10*i,10*j,-2])
    //            cylinder( d = 8.00, h = 3);
    //    }
    //}
    

}
//close back
    translate([125.4,100,-7])
        cube(size = [29.2,3.5,7], center = false);
//close left rp
    translate([5.4,-3.5,-20])
        cube(size = [64.2,3.5,20], center = false);
//close right rp
    translate([90.4,-3.5,-20])
        cube(size = [64.2,3.5,20], center = false);

// Rounded corners
// front left
    translate([-1,-1,0])
        cylinder( d = 5.00, h = 1);

// front right
    translate([161,-1,0])
        cylinder( d = 5.00, h = 1);

// back right
    translate([161,101,0])
        cylinder( d = 5.00, h = 1);

// back left
     translate([-1,101,0])
        cylinder( d = 5.00, h = 1);


// Left
translate([-3.5,-1,0])
    cube(size = [2.5,102,1], center = false);
// Right
translate([161,-1,0])
    cube(size = [2.5,102,1], center = false);
// Front
translate([-1,-3.5,0])
    cube(size = [162,2.5,1], center = false);
// Back
translate([-1,101,0])
    cube(size = [162,2.5,1], center = false);
