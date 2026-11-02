#pragma once
#include <algorithm>
#include <cmath>
namespace Movement {
inline int Pixels(double& carry,unsigned long milliseconds,double pixelsPerSecond) {
    carry+=std::min(milliseconds,50ul)*pixelsPerSecond/1000.0;
    int result=static_cast<int>(carry+1e-9); carry-=result;
    return result;
}
inline int Stick(int x,int y,int previous) {
    int ax=std::abs(x),ay=std::abs(y),largest=std::max(ax,ay);
    if(largest < (previous<0?12000:9000)) return -1;
    if(previous==0 && x<0 && ax*5>=ay*4) return 0;
    if(previous==1 && x>0 && ax*5>=ay*4) return 1;
    if(previous==2 && y<0 && ay*5>=ax*4) return 2;
    if(previous==3 && y>0 && ay*5>=ax*4) return 3;
    return ax>=ay ? (x<0?0:1) : (y<0?2:3);
}
template<class Walkable>
bool Step(int& x,int& y,int dx,int dy,int oldDx,int oldDy,int tile,int width,int height,Walkable walkable) {
    auto fits=[&](int nx,int ny) {
        if(nx<0 || ny<0) return false;
        return walkable(ny/tile,nx/tile) && walkable(ny/tile,(nx+width-1)/tile) &&
               walkable((ny+height-1)/tile,nx/tile) && walkable((ny+height-1)/tile,(nx+width-1)/tile);
    };
    int beforeX=x,beforeY=y;
    int row=(y+height/2)/tile,col=(x+width/2)/tile;
    int laneX=col*tile+(tile-width)/2,laneY=row*tile+(tile-height)/2;
    bool turn=(dx*oldDy-dy*oldDx)!=0;
    int offset=dx?laneY-y:laneX-x;
    bool opening=walkable(row+dy,col+dx) && std::abs(offset)<=tile/3;
    if(turn && !opening) { dx=oldDx;dy=oldDy;offset=dx?laneY-y:laneX-x; }
    if(std::abs(offset)<=tile/3) {
        int correction=(offset>0)-(offset<0);
        int nx=x+(dy?correction:0),ny=y+(dx?correction:0);
        if(fits(nx,ny)) { x=nx;y=ny; }
    }
    if(fits(x+dx,y+dy)) { x+=dx;y+=dy; }
    return x!=beforeX || y!=beforeY;
}
}
