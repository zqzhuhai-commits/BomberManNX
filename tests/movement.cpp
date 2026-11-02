#include "../tools/Movement.h"
#include <cassert>
#include <iostream>
bool open(int row,int col) { return row>0 && col>0 && row<8 && col<8; }
int distance(int hz) {
    double carry=0;int pixels=0;
    for(int i=0;i<hz;++i) {
        unsigned a=(i+1)*1000/hz,b=i*1000/hz;
        pixels+=Movement::Pixels(carry,a-b,100);
    }
    return pixels;
}
int main() {
    assert(distance(30)==100 && distance(60)==100 && distance(120)==100);
    double carry=0; assert(Movement::Pixels(carry,5000,100)==5); // no jump after stall
    assert(Movement::Stick(1000,1000,-1)==-1);
    assert(Movement::Stick(20000,15000,-1)==1); // strongest axis wins
    assert(Movement::Stick(19000,20000,1)==1); // diagonal noise cannot flip direction
    assert(Movement::Stick(10000,25000,1)==3);
    assert(Movement::Stick(9500,0,1)==1 && Movement::Stick(8500,0,1)==-1);
    int x=44+10+8,y=44+6;
    for(int i=0;i<30;++i) Movement::Step(x,y,0,1,1,0,44,23,31,open);
    assert(x==54 && y>50); // off-center vertical turn aligns smoothly
    auto corridor=[](int row,int col){return row==2 && col>0 && col<8;};
    x=2*44+10;y=2*44+6;
    for(int i=0;i<20;++i) Movement::Step(x,y,0,-1,1,0,44,23,31,corridor);
    assert(x>98 && y==94); // blocked early turn keeps moving along corridor
    x=44;y=44;
    auto wall=[](int row,int col){return row==1 && col==1;};
    for(int i=0;i<1000;++i) Movement::Step(x,y,1,0,1,0,44,23,31,wall);
    assert(x+23<=88 && y>=44); // no wall penetration at any speed
    std::cout<<"Frame-rate independence, turn assistance, wall blocking and stick stability passed\n";
}
