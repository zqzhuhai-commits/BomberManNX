#include "../tools/ClassicRules.h"
#include <cassert>
#include <iostream>
bool has(const std::vector<Classic::Cell>& cells,int r,int c) {
    for(auto cell:cells) if(cell.row==r && cell.col==c) return true;
    return false;
}
int main() {
    int map[7][7]={};
    for(int i=0;i<7;++i) { map[0][i]=map[6][i]=map[i][0]=map[i][6]=2; }
    auto at=[&](int r,int c) { return r<0||r>=7||c<0||c>=7?2:map[r][c]; };
    auto open=Classic::Blast(3,3,2,at);
    assert(open.size()==9 && has(open,3,1) && has(open,1,3));
    assert(!has(open,2,2) && !has(open,4,4)); // no diagonal damage
    map[3][4]=1; map[2][3]=2;
    auto blocked=Classic::Blast(3,3,3,at);
    assert(has(blocked,3,4)); // first brick takes damage
    assert(!has(blocked,3,5)); // brick blocks further fire
    assert(!has(blocked,2,3) && !has(blocked,1,3)); // solid wall is untouched
    for(auto cell:blocked) assert(cell.row>0 && cell.col>0 && cell.row<6 && cell.col<6);
    assert(!Classic::CanExit(true,1,3)); // door locked while any enemy lives
    assert(!Classic::CanExit(false,0,3)); // clearing enemies is insufficient
    assert(!Classic::CanExit(true,0,0)); // dead player cannot finish
    assert(Classic::CanExit(true,0,1));
    Classic::Campaign::Reset(); assert(Classic::Campaign::lives==3);
    Classic::Campaign::bombs=4; Classic::Campaign::Complete(2);
    assert(Classic::Campaign::lives==3 && Classic::Campaign::bombs==4);
    Classic::Campaign::Reset(); assert(Classic::Campaign::lives==3 && Classic::Campaign::bombs==1);
    std::cout<<"Classic blast, blocked rays, exit gates and life progression tests passed\n";
}
