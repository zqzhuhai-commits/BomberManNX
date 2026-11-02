#pragma once
#include <vector>
#include <algorithm>
namespace Classic {
struct Cell { int row, col; };
template<class TileAt> std::vector<Cell> Blast(int row,int col,int range,TileAt at) {
    std::vector<Cell> result{{row,col}};
    const int directions[4][2]={{-1,0},{1,0},{0,-1},{0,1}};
    for(auto& d:directions) for(int step=1;step<=range;++step) {
        int r=row+d[0]*step,c=col+d[1]*step,tile=at(r,c);
        if(tile==2) break;
        result.push_back({r,c});
        if(tile==1) break;
    }
    return result;
}
inline bool CanExit(bool atDoor,unsigned enemies,unsigned lives) { return atDoor && enemies==0 && lives>0; }
struct Campaign {
    inline static unsigned lives=3,bombs=1,range=1,speed=100;
    inline static bool remote=false;
    static void Reset() { lives=3; bombs=1; range=1; speed=100; remote=false; }
    static void Complete(unsigned remaining) { lives=remaining+1; }
};
}
