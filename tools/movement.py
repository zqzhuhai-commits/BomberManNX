from pathlib import Path
import sys
p=Path(sys.argv[1])
(p/"include/Utility/Movement.h").write_text(Path("tools/Movement.h").read_text(encoding="utf-8"),encoding="utf-8")
f=p/"include/Entity/Player.h";s=f.read_text(encoding="utf-8")
s=s.replace("        Timer          m_timer;","        Timer          m_timer;\n        Timer m_animation_timer;\n        double m_movement_carry=0.0;")
f.write_text(s,encoding="utf-8")
f=p/"src/Entity/Player.cpp";s=f.read_text(encoding="utf-8")
s=s.replace('#include "Entity/Player.h"','#include "Entity/Player.h"\n#include "Utility/Movement.h"')
a=s.index("    if(m_timer.GetTimeElapsed()>(m_speed / 2))");b=s.index("\n}\n",a)
s=s[:a]+'''    unsigned long elapsed=m_timer.GetTimeElapsed();
    m_timer.ResetTimer();
    int dx=0,dy=0;
    if(m_keyboard_input->IsKeyOn(m_up)) dy=-1;
    else if(m_keyboard_input->IsKeyOn(m_down)) dy=1;
    else if(m_keyboard_input->IsKeyOn(m_left)) dx=-1;
    else if(m_keyboard_input->IsKeyOn(m_right)) dx=1;
    if(dx || dy) {
        int pixels=Movement::Pixels(m_movement_carry,elapsed,m_move_speed*2000.0/m_speed);
        for(int i=0;i<pixels;++i) PlayerMove(dx,dy);
    } else {
        m_movement_carry=0; m_status=0; m_animation_timer.ResetTimer();
    }
'''+s[b:]
a=s.index("void Player::PlayerMove(int x, int y)");b=s.index("unsigned int Player::GetX()",a)
s=s[:a]+'''void Player::PlayerMove(int dx,int dy) {
    const int oldDx=m_direction==LEFT?-1:m_direction==RIGHT?1:0;
    const int oldDy=m_direction==UP?-1:m_direction==DOWN?1:0;
    int x=static_cast<int>(m_x),y=static_cast<int>(m_y);
    int beforeX=x,beforeY=y;
    bool moved=Movement::Step(x,y,dx,dy,oldDx,oldDy,m_tile_size,m_player_size_w,m_player_size_h,
        [this](int row,int col){return m_relay->GetMap()->Walkable(row,col);});
    if(moved) {
        m_x=x;m_y=y;
        // Face the actual forward movement, keeping correction pixels from
        // flipping the sprite when aligning to a corridor.
        if(dx && ((x-beforeX)*dx)>0) m_direction=dx<0?LEFT:RIGHT;
        else if(dy && ((y-beforeY)*dy)>0) m_direction=dy<0?UP:DOWN;
        m_status=(m_animation_timer.GetTimeElapsed()/110)%m_rotation_const;
    } else m_status=0;
}

'''+s[b:]
f.write_text(s,encoding="utf-8")
f=p/"src/main.cpp";s=f.read_text(encoding="utf-8")
s=s.replace('#include "game.h"','#include "game.h"\n#include "Utility/Movement.h"\n#include <algorithm>\n#include <cstdlib>')
a=s.index("        // Poll both sticks");b=s.index("        OnLoop();",a)
s=s[:a]+'''        int bestX=0,bestY=0,bestMagnitude=0;
        for (int i=0;i<SDL_NumJoysticks();++i) {
            SDL_Joystick* joy=SDL_JoystickFromInstanceID(SDL_JoystickGetDeviceInstanceID(i));
            if(!joy) joy=SDL_JoystickOpen(i);
            if(!joy) continue;
            for(int axis=0;axis+1<SDL_JoystickNumAxes(joy) && axis<4;axis+=2) {
                int x=SDL_JoystickGetAxis(joy,axis),y=SDL_JoystickGetAxis(joy,axis+1);
                int magnitude=std::max(std::abs(x),std::abs(y));
                if(magnitude>bestMagnitude) { bestX=x;bestY=y;bestMagnitude=magnitude; }
            }
        }
        static int stickDirection=-1;
        stickDirection=Movement::Stick(bestX,bestY,stickDirection);
        for(int i=0;i<4;++i) {
            if(i==stickDirection) keyboard_input->TurnKeyOn(1000+i);
            else keyboard_input->TurnKeyOff(1000+i);
        }
'''+s[b:]
f.write_text(s,encoding="utf-8")
f=p/"src/Display/GameDisplay.cpp";s=f.read_text(encoding="utf-8")
s=s.replace(">=200000",">=300000").replace("elapsed>=200?0:200-elapsed","elapsed>=300?0:300-elapsed")
f.write_text(s,encoding="utf-8")
f=p/"Makefile";s=f.read_text(encoding="utf-8").replace("VERSION_MINOR := 2","VERSION_MINOR := 3");f.write_text(s,encoding="utf-8")

# Keep the Chinese HUD font open; reopening a 17MB font every second causes stalls.
f=p/"include/Display/GameDisplay.h";s=f.read_text(encoding="utf-8").replace("#include <string>",'#include <string>\n#include "System/TextRenderer.h"').replace("        mutable std::string m_hud_text;","        mutable std::string m_hud_text;\n        mutable TextRenderer* m_hud_font=nullptr;");f.write_text(s,encoding="utf-8")
f=p/"src/Display/GameDisplay.cpp";s=f.read_text(encoding="utf-8")
s=s.replace("        TextRenderer font(RESOURCES_BASE_PATH+RESOURCES_FONT,24);\n        m_hud=font.RenderText","        if(!m_hud_font) m_hud_font=new TextRenderer(RESOURCES_BASE_PATH+RESOURCES_FONT,24);\n        m_hud=m_hud_font->RenderText")
s=s.replace("    if(m_hud) { SDL_DestroyTexture(m_hud); m_hud=nullptr; }","    if(m_hud) { SDL_DestroyTexture(m_hud); m_hud=nullptr; }\n    delete m_hud_font; m_hud_font=nullptr;")
s=s.replace("GameDisplay::~GameDisplay()\n{","GameDisplay::~GameDisplay()\n{\n    if(m_hud) SDL_DestroyTexture(m_hud);\n    delete m_hud_font;")
f.write_text(s,encoding="utf-8")
