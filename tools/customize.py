from pathlib import Path
import sys
p=Path(sys.argv[1])
translations={
"NEW GAME":"开始游戏","OPTIONS":"游戏设置","EXIT":"退出游戏",
"RESUME":"继续游戏","QUIT":"返回主菜单",
"CHOOSE NUMBER OF PLAYERS":"选择玩家人数","One Player":"单人游戏",
"Two Players (Not working yet)":"双人游戏（暂不可用）",
"WELCOME TO BOMBERMAN NX":"欢迎来到炸弹人","Press ( + ) to start":"按 ＋ 键开始",
"GAME OVER":"游戏结束","GAME COMPLETED":"恭喜通关","STAGE ":"关卡 "
}
for f in (p/"src/Display").glob("*.cpp"):
    s=f.read_text()
    for a,b in translations.items(): s=s.replace('"'+a+'"','"'+b+'"')
    f.write_text(s)
f=p/"src/System/TextRenderer.cpp"
f.write_text(f.read_text().replace("TTF_RenderText_Blended(","TTF_RenderUTF8_Blended("))
f=p/"include/Constants/ResourcesConstants.h"
f.write_text(f.read_text().replace('"Zabdilus.ttf"','"NotoSansSC.ttf"'))
f=p/"src/Entity/Player.cpp"
s=f.read_text().replace("GetTimeElapsed()>m_speed","GetTimeElapsed()>(m_speed / 2)").replace("DecreaseTimer(m_speed)","DecreaseTimer(m_speed / 2)")
s=s.replace("m_relay->GetBombManager()->MakeBomb(5000,","if (m_relay->GetBombManager()->MakeBomb(5000,")
s=s.replace("m_player_id,m_bomb_intensity, m_bomb_damage);","m_player_id,m_bomb_intensity, m_bomb_damage))")
f.write_text(s)
f=p/"src/Entity/DestructibleWall.cpp"
f.write_text(f.read_text().replace("m_integrity -= value;","if (value > 0) m_integrity = 0;"))
f=p/"include/Manager/BombManager.h"
f.write_text(f.read_text().replace("void MakeBomb(","bool MakeBomb("))
f=p/"src/Manager/BombManager.cpp"
s=f.read_text().replace("void BombManager::MakeBomb(","bool BombManager::MakeBomb(")
s=s.replace("    Bomb* b = new Bomb(","    for (const Bomb* existing : m_bombs) {\n        if (existing->GetX() / m_tile_size == x / m_tile_size &&\n            existing->GetY() / m_tile_size == y / m_tile_size) return false;\n    }\n    Bomb* b = new Bomb(")
s=s.replace("    AddBomb(b);","    AddBomb(b);\n    return true;")
f.write_text(s)
f=p/"src/main.cpp"
s=f.read_text()
poll=r"""
        // Poll both sticks each frame; use separate virtual keys so D-pad releases
        // cannot cancel a held stick. SDL updates joystick state during event polling.
        bool left = false, right = false, up = false, down = false;
        for (int i = 0; i < SDL_NumJoysticks(); ++i) {
            SDL_Joystick* joy = SDL_JoystickFromInstanceID(SDL_JoystickGetDeviceInstanceID(i));
            if (!joy) joy = SDL_JoystickOpen(i);
            if (!joy) continue;
            for (int axis = 0; axis + 1 < SDL_JoystickNumAxes(joy) && axis < 4; axis += 2) {
                int x = SDL_JoystickGetAxis(joy, axis);
                int y = SDL_JoystickGetAxis(joy, axis + 1);
                left |= x < -12000; right |= x > 12000;
                up |= y < -12000; down |= y > 12000;
            }
        }
        const bool directions[] = {left, right, up, down};
        for (int i = 0; i < 4; ++i) {
            if (directions[i]) keyboard_input->TurnKeyOn(1000 + i);
            else keyboard_input->TurnKeyOff(1000 + i);
        }
"""
s=s.replace("        OnLoop();",poll+"\n        OnLoop();")
f.write_text(s)
f=p/"src/System/KeyboardInput.cpp"
s=f.read_text()
s=s.replace("    if (m_keys_pressed.count(key) > 0)","    const int stick = key == 12 ? 1000 : key == 14 ? 1001 : key == 13 ? 1002 : key == 15 ? 1003 : -1;\n    if (stick >= 0 && m_keys_pressed[stick]) return true;\n    if (m_keys_pressed.count(key) > 0)")
f.write_text(s)
f=p/"Makefile"
s=f.read_text().replace("VERSION_MINOR := 0","VERSION_MINOR := 1").replace("APP_TITLE\t:=  BomberManNX","APP_TITLE\t:=  炸弹人").replace("TARGET\t\t:=\t$(APP_TITLE)","TARGET\t\t:=\tBomberManNX").replace("KranK/Kuranku","Xiao Fan")
f.write_text(s)
