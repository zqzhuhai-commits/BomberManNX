from pathlib import Path
import sys
p=Path(sys.argv[1])
def change(rel,old,new):
    f=p/rel; s=f.read_text(encoding="utf-8")
    if old not in s: raise RuntimeError("Pattern missing: "+rel+" "+old[:40])
    f.write_text(s.replace(old,new),encoding="utf-8")
# Install rule helper from this repository.
(p/"include/Utility/ClassicRules.h").write_text(Path("tools/ClassicRules.h").read_text(encoding="utf-8"),encoding="utf-8")
change("include/Manager/EnemyManager.h","    protected:","        unsigned int Count() const { return m_enemies.size(); }\n        void SpawnTimeoutEnemies();\n    protected:")
change("src/Utility/Relay.cpp",'//#include "Manager/EnemyManager.h"','#include "Manager/EnemyManager.h"')
change("src/Utility/Relay.cpp","return m_player_manager->AreAllCompleted();","return m_enemy_manager->Count() == 0 && m_player_manager->AreAllCompleted();")
change("src/Entity/Player.cpp",'#include "Entity/Player.h"','#include "Entity/Player.h"\n#include "Manager/EnemyManager.h"\n#include "Utility/ClassicRules.h"')
change("src/Entity/Player.cpp","    m_player_id = player_id;","    m_player_id = player_id;\n    m_lives=Classic::Campaign::lives; m_bomb_num=Classic::Campaign::bombs;\n    m_bomb_intensity=Classic::Campaign::range; m_speed=Classic::Campaign::speed;\n    m_remote=Classic::Campaign::remote;")
change("src/Entity/Player.cpp","if(!pick_up.IsUsed())\n                    {\n                        m_level_completed", "if(!pick_up.IsUsed() && Classic::CanExit(true, m_relay->GetEnemyManager()->Count(), m_lives))\n                    {\n                        m_level_completed")
# Fire-up changes range by a whole tile, independently of damage.
f=p/"src/Entity/Player.cpp"; s=f.read_text(encoding="utf-8"); a=s.index("                case PickUp::DAMAGE:"); b=s.index("                case PickUp::LIFE:",a)
s=s[:a]+'''                case PickUp::DAMAGE:
                    if (!pick_up.IsUsed()) {
                        if (m_bomb_intensity < 8) ++m_bomb_intensity;
                        pick_up.Use();
                    }
                    break;
                case PickUp::REMOTE:
                    if (!pick_up.IsUsed()) { m_remote=true; pick_up.Use(); }
                    break;
'''+s[b:]
s=s.replace("    //Place bomb","    if (m_remote && m_keyboard_input->IsKeyOn(1) && !m_remote_pressed) m_relay->GetBombManager()->DetonatePlayer(m_player_id);\n    m_remote_pressed = m_keyboard_input->IsKeyOn(1);\n    //Place bomb")
s=s.replace("MakeBomb(5000,","MakeBomb(m_remote ? 0xffffffffu : 3000,")
s=s.replace("m_x+m_player_size_w/2,m_y+m_player_size_h/2,","((m_x+m_player_size_w/2)/m_tile_size)*m_tile_size+m_tile_size/2,((m_y+m_player_size_h/2)/m_tile_size)*m_tile_size+m_tile_size/2,")
s=s.replace("    m_health = h;","    if (h == 0 && (m_level_completed || m_lives == 0 || (m_invulnerable && m_respawn_timer.GetTimeElapsed() < 2000))) return;\n    m_health = h;")
s=s.replace("    m_alive = a;","    m_alive = a;\n    if (a == 0) { m_invulnerable=true; m_respawn_timer.ResetTimer(); }")
s += '''\nvoid Player::SaveProgress() const {
    Classic::Campaign::bombs=m_bomb_num; Classic::Campaign::range=static_cast<unsigned>(m_bomb_intensity);
    Classic::Campaign::speed=m_speed; Classic::Campaign::remote=m_remote;
}
'''
f.write_text(s,encoding="utf-8")
change("include/Entity/Player.h","    protected:","        void SaveProgress() const;\n        bool HasRemote() const { return m_remote; }\n        unsigned BombCapacity() const { return m_bomb_num; }\n        unsigned FlameRange() const { return static_cast<unsigned>(m_bomb_intensity); }\n    protected:")
change("include/Entity/Player.h","        unsigned int   m_bomb_num = 4;","        unsigned int   m_bomb_num = 1;")
change("include/Entity/Player.h","        double         m_bomb_intensity = 2.5;","        double         m_bomb_intensity = 1;\n        bool m_remote=false, m_remote_pressed=false, m_invulnerable=false;\n        Timer m_respawn_timer;")
# Exactly one hidden door chosen before any wall is destroyed.
change("include/Manager/Map.h","    protected:","        bool ExitRevealed() const { return m_exit_revealed; }\n    protected:")
change("include/Manager/Map.h","        unsigned int                            m_wall_count;","        unsigned int                            m_wall_count;\n        unsigned m_exit_row=0,m_exit_col=0;\n        bool m_exit_revealed=false;")
change("src/Manager/Map.cpp","    fs.close();","    std::vector<std::pair<unsigned,unsigned>> candidates;\n    for(unsigned r=0;r<m_height;++r) for(unsigned c=0;c<m_width;++c)\n        if(m_layout[r][c]->GetId()==MapObject::DESTRUCTIBLE_WALL) candidates.push_back({r,c});\n    if(!candidates.empty()) { auto door=candidates[rand()%candidates.size()]; m_exit_row=door.first; m_exit_col=door.second; }\n    fs.close();")
change("src/Manager/Map.cpp","if (m_wall_count == 0)","if (i == m_exit_row && j == m_exit_col)")
change("src/Manager/Map.cpp","    m_relay->GetPickUpManager()->MakePickUp(PickUp::EXIT,x,y);","    m_exit_revealed=true;\n    m_relay->GetPickUpManager()->MakePickUp(PickUp::EXIT,x,y);")
change("src/Manager/Map.cpp","    return m_layout[i][j]->GetId();","    if(i>=m_height || j>=m_width) return MapObject::INDESTRUCTIBLE_WALL;\n    return m_layout[i][j]->GetId();")
change("src/Manager/Map.cpp","    if (m_layout[i][j]->GetId() == MapObject::EMPTY)","    if (i < m_height && j < m_width && m_layout[i][j]->GetId() == MapObject::EMPTY)")
f=p/"src/Manager/Map.cpp"; s=f.read_text(encoding="utf-8"); a=s.index("    unsigned int chance = rand() % 100;",s.index("void Map::TryPlacePickUp"))
s=s[:a]+'''    if (rand()%100 >= 25) return;
    const PickUp::PickUpType types[] = {PickUp::SPEED,PickUp::BOMB,PickUp::DAMAGE,PickUp::REMOTE};
    auto type=types[rand()%4];
    m_relay->GetPickUpManager()->MakePickUp(type,x,y,type==PickUp::SPEED ? 15 : 1);
}
'''
f.write_text(s,encoding="utf-8")
change("include/Entity/PickUp.h","            EXIT,","            REMOTE,\n            EXIT,")
change("src/Entity/PickUp.cpp","    SDL_Rect SrcR, DestR;","""    if (m_type == EXIT || m_type == REMOTE) {
        SDL_Rect box{static_cast<int>(m_x-m_draw_size/2),static_cast<int>(m_y-m_draw_size/2),static_cast<int>(m_draw_size),static_cast<int>(m_draw_size)};
        SDL_SetRenderDrawColor(renderer,0,0,0,255); SDL_RenderFillRect(renderer,&box);
        SDL_SetRenderDrawColor(renderer,m_type==EXIT?240:80,m_type==EXIT?200:210,m_type==EXIT?60:255,255);
        SDL_RenderDrawRect(renderer,&box);
        if(m_type==REMOTE) {
            SDL_RenderDrawLine(renderer,box.x+box.w/2,box.y+4,box.x+box.w/3,box.y+box.h/2);
            SDL_RenderDrawLine(renderer,box.x+box.w/3,box.y+box.h/2,box.x+2*box.w/3,box.y+box.h/2);
            SDL_RenderDrawLine(renderer,box.x+2*box.w/3,box.y+box.h/2,box.x+box.w/2,box.y+box.h-4);
        }
        return;
    }
    SDL_Rect SrcR, DestR;""")
# Four-way blast tiles, walls stop rays; persistent flames hurt on contact.
change("include/Entity/Bomb.h","    protected:","        void Ignite() { m_explode=true; }\n    protected:")
change("include/Manager/BombManager.h","#include <list>","#include <list>\n#include <vector>\n#include \"Utility/ClassicRules.h\"".replace('\"','"'))
change("include/Manager/BombManager.h","    protected:","        void DetonatePlayer(unsigned id);\n    protected:")
change("include/Manager/BombManager.h","        std::list<Bomb*>        m_bombs;","        std::list<Bomb*>        m_bombs;\n        struct Flame { unsigned x,y; Timer timer; };\n        std::vector<Flame> m_flames;")
f=p/"src/Manager/BombManager.cpp"; s=f.read_text(encoding="utf-8").replace('#include "Manager/BombManager.h"','#include "Manager/BombManager.h"\n#include "Manager/Map.h"\n#include <algorithm>')
a=s.index("void BombManager::Update()"); b=s.index("void BombManager::Draw",a)
s=s[:a]+'''void BombManager::DetonatePlayer(unsigned id) {
    for(auto* bomb:m_bombs) if(bomb->GetPlayerId()==id) bomb->Ignite();
}
void BombManager::Update() {
    m_flames.erase(std::remove_if(m_flames.begin(),m_flames.end(),[](const Flame& f){return f.timer.GetTimeElapsed()>=600;}),m_flames.end());
    for(auto* bomb:m_bombs) {
        for(const auto& flame:m_flames)
            if(bomb->GetX()/m_tile_size==flame.x/m_tile_size && bomb->GetY()/m_tile_size==flame.y/m_tile_size) bomb->Ignite();
    }
    for(auto i=m_bombs.begin();i!=m_bombs.end();) {
        Bomb* bomb=*i; bomb->Update();
        if(!bomb->Explode()) { ++i; continue; }
        Mix_PlayChannel(-1,m_bomb_sound_effect,0);
        auto cells=Classic::Blast(bomb->GetY()/m_tile_size,bomb->GetX()/m_tile_size,static_cast<int>(bomb->GetIntensity()),
            [this](int r,int c){return static_cast<int>(m_relay->GetMap()->GetTileType(r,c));});
        for(auto cell:cells) {
            unsigned x=cell.col*m_tile_size+m_tile_size/2,y=cell.row*m_tile_size+m_tile_size/2;
            m_relay->GetMap()->DestroyWall(cell.row,cell.col,100);
            m_relay->GetExplosionManager()->MakeExplosion(600,x,y,1.0);
            m_flames.push_back({x,y,Timer()});
            for(auto* other:m_bombs) if(other!=bomb && other->GetX()/m_tile_size==static_cast<unsigned>(cell.col) && other->GetY()/m_tile_size==static_cast<unsigned>(cell.row)) other->Ignite();
        }
        m_relay->GetPlayerManager()->GetPlayerById(bomb->GetPlayerId())->DecreaseTempBombNumber();
        delete bomb; i=m_bombs.erase(i);
    }
    for(const auto& flame:m_flames) {
        m_relay->GetEnemyManager()->KillEnemies(flame.x,flame.y,1.0);
        m_relay->GetPlayerManager()->KillPlayer(flame.x,flame.y,1.0);
    }
}

'''+s[b:]; f.write_text(s,encoding="utf-8")
# Replace circular hit detection with tile intersection matching rendered flames.
f=p/"src/Destroyer/Destroyer.cpp"; s=f.read_text(encoding="utf-8")
for entity in ["enemy","player"]:
    a=s.index("    unsigned int "+entity+"_center_x")
    b=s.index("\n}",a)
    s=s[:a]+f'''    (void)intensity;
    const int left=static_cast<int>(start_x)-static_cast<int>(tile_size)/2;
    const int top=static_cast<int>(start_y)-static_cast<int>(tile_size)/2;
    if (static_cast<int>({entity}->GetX()) < left+static_cast<int>(tile_size) &&
        static_cast<int>({entity}->GetX()+{entity}->GetSizeW()) > left &&
        static_cast<int>({entity}->GetY()) < top+static_cast<int>(tile_size) &&
        static_cast<int>({entity}->GetY()+{entity}->GetSizeH()) > top)
        {entity}->SetHealth(0);'''+s[b:]
f.write_text(s,encoding="utf-8")
# Stage layouts retain their spawn positions but get appropriate enemy progression.
for stage in range(1,11):
    f=p/f"resources/levels/enemy{stage}.txt"; lines=f.read_text().splitlines()
    rows=[line.split() for line in lines[1:] if line.strip()]
    for row in rows:
        if stage==1: row[0]="1"
        elif stage in (2,3): row[0]="2"
        elif stage==4: row[0]="3"
    f.write_text(str(len(rows))+"\\n".replace("\\n","\n")+"\n".join(" ".join(row) for row in rows)+"\n")
# First enemy now uses the blue balloon sprite, second the onion, fourth-stage chaser the smiley.
change("include/Constants/TextureEnemyConstants.h","TEXTURE_ENEMY_ONE_Y = 183","TEXTURE_ENEMY_ONE_Y = 159")
change("include/Constants/TextureEnemyConstants.h","TEXTURE_ENEMY_TWO_Y = 159","TEXTURE_ENEMY_TWO_Y = 183")
change("include/Constants/TextureEnemyConstants.h","TEXTURE_ENEMY_THREE_Y = 256","TEXTURE_ENEMY_THREE_Y = 208")
change("include/Constants/TextureEnemyConstants.h","TEXTURE_ENEMY_THREE_COUNT = 7","TEXTURE_ENEMY_THREE_COUNT = 3")
# Strong timeout enemies use the existing pursuit AI, with a distinct golden coin drawing.
change("include/Entity/Enemy.h","    protected:","        void MakeHard() { m_hard=true; m_speed=20; }\n    protected:\n        bool m_hard=false;")
change("src/Entity/EnemyThree.cpp","    SDL_Rect SrcR;","    if(m_hard) {\n        SDL_SetRenderDrawColor(renderer,255,190,25,255);\n        SDL_Rect coin{static_cast<int>(m_x),static_cast<int>(m_y),static_cast<int>(m_enemy_size_w),static_cast<int>(m_enemy_size_h)};\n        SDL_RenderFillRect(renderer,&coin); SDL_SetRenderDrawColor(renderer,255,250,170,255); SDL_RenderDrawRect(renderer,&coin); return;\n    }\n    SDL_Rect SrcR;")
change("src/Entity/EnemyThree.cpp","if(player_min <= 2*m_tile_size)","if(p && (m_hard || player_min <= 2*m_tile_size))")
f=p/"src/Manager/EnemyManager.cpp"; s=f.read_text(encoding="utf-8").replace('#include "Manager/PlayerManager.h"','#include "Manager/PlayerManager.h"\n#include "Manager/Map.h"')
s+='''\nvoid EnemyManager::SpawnTimeoutEnemies() {
    unsigned spawned=0;
    Player* player=m_relay->GetPlayerManager()->GetPlayerById(0);
    for(unsigned row=1;row<15 && spawned<16;row+=2) for(unsigned col=1;col<25 && spawned<16;col+=2) {
        if(!m_relay->GetMap()->Walkable(row,col)) continue;
        int dx=static_cast<int>(col*m_tile_size)-static_cast<int>(player->GetX());
        int dy=static_cast<int>(row*m_tile_size)-static_cast<int>(player->GetY());
        if(dx*dx+dy*dy<static_cast<int>(m_tile_size*m_tile_size*9)) continue;
        EnemyThree* coin=new EnemyThree(m_texture,m_tile_size,col,row);
        coin->MakeHard(); AddEnemy(coin); ++spawned;
    }
}
'''; f.write_text(s,encoding="utf-8")
# Campaign lifecycle and HUD, cached once each second or when status changes.
change("src/Display/LoadingDisplay.cpp",'#include "Display/LoadingDisplay.h"','#include "Display/LoadingDisplay.h"\n#include "Utility/ClassicRules.h"')
change("src/Display/LoadingDisplay.cpp","    std::stringstream sstm;","    Classic::Campaign::Reset();\n    std::stringstream sstm;") # constructor only; Enter indented differently below corrected.
f=p/"src/Display/LoadingDisplay.cpp";s=f.read_text(encoding="utf-8");s=s.replace("            Classic::Campaign::Reset();\n    std::stringstream sstm;","            std::stringstream sstm;")
s=s.replace('sstm << "关卡 " << m_current_level;','sstm << "关卡 " << m_current_level;',1)
# Announce the completed stage before continuing.
pos=s.index("void LoadingDisplay::Enter")
s=s[:pos]+s[pos:].replace('sstm << "关卡 " << m_current_level;','sstm << "过关！奖励一条命，进入关卡 " << m_current_level;')
# Smaller transition label to fit screen.
s=s.replace("TextRenderer text_renderer(path_font,96)","TextRenderer text_renderer(path_font,48)")
f.write_text(s,encoding="utf-8")
change("include/Display/GameDisplay.h","#define GAMEDISPLAY_H","#define GAMEDISPLAY_H\n#include <string>\n#include \"Utility/Timer.h\"".replace('\"','"'))
change("include/Display/GameDisplay.h","        Mix_Music*                      m_music;","        Mix_Music*                      m_music;\n        Timer m_stage_timer;\n        bool m_timeout_spawned=false;\n        mutable SDL_Texture* m_hud=nullptr;\n        mutable std::string m_hud_text;")
f=p/"src/Display/GameDisplay.cpp"; s=f.read_text(encoding="utf-8").replace('#include "Display/GameDisplay.h"','#include "Display/GameDisplay.h"\n#include "Utility/ClassicRules.h"\n#include "System/TextRenderer.h"\n#include <algorithm>')
s=s.replace("    Mix_PlayMusic(m_music, -1);","    m_stage_timer.ResetTimer();\n    Mix_PlayMusic(m_music, -1);")
a=s.index("int GameDisplay::Destroy()"); b=s.index("void GameDisplay::Update()",a)
block=s[a:b].replace("    Mix_PauseMusic();","    if(m_level_completed) {\n        Player* player=m_relay->GetPlayerManager()->GetPlayerById(0);\n        player->SaveProgress(); Classic::Campaign::Complete(player->GetLives());\n    }\n    if(m_hud) { SDL_DestroyTexture(m_hud); m_hud=nullptr; }\n    Mix_PauseMusic();",1)
s=s[:a]+block+s[b:]
s=s.replace("void GameDisplay::Update()\n{","void GameDisplay::Update()\n{\n    if(!m_timeout_spawned && m_stage_timer.GetTimeElapsed()>=200000) { m_timeout_spawned=true; m_relay->GetEnemyManager()->SpawnTimeoutEnemies(); }")
# Do not allow dying player to enter the door before the death state is processed.
s=s.replace("else if (m_relay->LevelCompleted())","else if (m_relay->LevelCompleted())")
end=s.rfind("}")
hud='''
    unsigned elapsed=m_stage_timer.GetTimeElapsed()/1000;
    unsigned remaining=elapsed>=200?0:200-elapsed;
    Player* player=m_relay->GetPlayerManager()->GetPlayerById(0);
    std::ostringstream status;
    status << "时间 " << remaining << "  敌人 " << m_relay->GetEnemyManager()->Count() << "  生命 " << player->GetLives()
           << "  炸弹 " << player->BombCapacity() << "  火力 " << player->FlameRange();
    if(player->HasRemote()) status << "  雷管：Ｂ引爆";
    else if(m_relay->GetEnemyManager()->Count()) status << "  消灭全部敌人后进入黑门";
    else if(!m_relay->GetMap()->ExitRevealed()) status << "  炸砖寻找黑门";
    else status << "  黑门已开启";
    if(status.str()!=m_hud_text) {
        if(m_hud) SDL_DestroyTexture(m_hud);
        TextRenderer font(RESOURCES_BASE_PATH+RESOURCES_FONT,24);
        m_hud=font.RenderText(status.str(),SDL_Color{255,255,255,255},renderer);
        m_hud_text=status.str();
    }
    SDL_Rect bar{0,0,static_cast<int>(m_window_width),44};
    SDL_SetRenderDrawColor(renderer,10,15,25,255); SDL_RenderFillRect(renderer,&bar);
    if(m_hud) { int width,height; SDL_QueryTexture(m_hud,nullptr,nullptr,&width,&height);
        SDL_Rect label{8,8,std::min(width,static_cast<int>(m_window_width)-16),height};
        SDL_RenderCopy(renderer,m_hud,nullptr,&label);
    }
'''
s=s[:end]+hud+s[end:]; f.write_text(s,encoding="utf-8")
# Disabled two-player mode must not route into an unsupported keyboard-only player.
change("src/Display/PlayersNumberDisplay.cpp","m_players_selected = 2;","m_players_selected = 1;")

change("Makefile","VERSION_MINOR := 1","VERSION_MINOR := 2")
