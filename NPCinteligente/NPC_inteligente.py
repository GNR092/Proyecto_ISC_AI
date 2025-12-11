# npc_smart_behavior_v3.py
# Versi\u00f3n 3: mejoras solicitadas sobre v2

import pygame
import random
import os
import json
from datetime import datetime

try:
    from gensim.models import Word2Vec
    GENSIM_AVAILABLE = True
except Exception:
    GENSIM_AVAILABLE = False

SCREEN_W, SCREEN_H = 640, 480
FPS = 60
BG = (30,30,40)
PLAYER_COLOR = (50,200,50)
NPC_COLOR = (200,50,50)
OBST_COLOR = (120,120,120)
# Las fuentes se inicializarán después de pygame.init()
FONT_XS = FONT_S = FONT_M = FONT_L = None

# Configuración de daños
PLAYER_CLICK_DAMAGE = 8            # daño base por clic izquierdo
PLAYER_MELEE_DAMAGE = 20           # daño base para ataque cuerpo a cuerpo (espacio)
NPC_ATTACK_DAMAGE = 15             # daño base de ataque NPC
PLAYER_TO_NPC_REDUCE = 0.10        # reducción de daño jugador->NPC (10%)
NPC_TO_PLAYER_REDUCE = 0.13        # reducción de daño NPC->jugador (13%)

PATROL = 'patrol'
PURSUE = 'pursue'
FLEE = 'flee'
STATE_NAMES = {PATROL:'PATRULLA',PURSUE:'PERSEGUIR',FLEE:'HUIR'}

# helpers
def _orient(a,b,c):
    return (b.x-a.x)*(c.y-a.y) - (b.y-a.y)*(c.x-a.x)

def _seg_intersect(a,b,c,d):
    return (_orient(a,c,d)*_orient(b,c,d) < 0) and (_orient(a,b,c)*_orient(a,b,d) < 0)

def line_intersects_rect(a,b,rect):
    pts = [pygame.Vector2(rect.topleft), pygame.Vector2(rect.topright), pygame.Vector2(rect.bottomright), pygame.Vector2(rect.bottomleft)]
    for i in range(4):
        if _seg_intersect(a,b,pts[i],pts[(i+1)%4]):
            return True
    return False

def circle_rect_collide(cx,cy,r,rect):
    rx,ry = rect.topleft
    rw,rh = rect.size
    nearest_x = max(rx, min(cx, rx+rw))
    nearest_y = max(ry, min(cy, ry+rh))
    dx = cx - nearest_x
    dy = cy - nearest_y
    return (dx*dx + dy*dy) <= (r*r)

def collides_any_obs(x,y,r,obs):
    return any(circle_rect_collide(x,y,r,ob) for ob in obs)

class NPC:
    def __init__(self,pos,patrol_pts):
        self.pos = pygame.Vector2(pos)
        self.speed = 1.2
        self.patrol = [pygame.Vector2(p) for p in patrol_pts]
        self.i = 0
        self.state = PATROL
        self.vision = 90
        self.health = 100
        self.aggr = 0.5
        self.attack_cd = 0
        self.radius = 12
        self.obstacles = []
        # aprendizaje online
        self.player_history = []
        self.history_max = 120
        self.learning_scale = 0.0
        # regeneración acumulador (para aplicar curación en enteros)
        self._regen_acc = 0.0

    def set_obstacles(self,obs):
        self.obstacles = obs

    def can_see(self, target):
        if self.pos.distance_to(target) > self.vision:
            return False
        for ob in self.obstacles:
            if line_intersects_rect(self.pos,target,ob):
                return False
        return True

    def learn_from_history(self):
        h = self.player_history
        if len(h) < 5:
            return
        total = 0.0
        for a,b in zip(h[:-1], h[1:]):
            total += a.distance_to(b)
        avg_speed = total / max(1, len(h)-1)
        visible = 0
        for p in h:
            if self.can_see(p):
                visible += 1
        frac = visible / len(h)
        # La tasa de aprendizaje se escala con learning_scale (comienza con algo pequeño)
        lr = 0.005 + 0.045 * max(0.0, min(1.0, self.learning_scale))
        target_aggr = max(0.0, min(1.0, 0.3 + 0.7*frac + (avg_speed/3.0)))
        self.aggr += (target_aggr - self.aggr) * lr
      # adaptación de visión pequeña
        self.vision += ( (frac-0.5) * 0.2 ) * lr * 10
        self.vision = max(60, min(200, self.vision))

    def _resolve_patrol_start(self):
        best = 0
        bestd = float('inf')
        for idx,pt in enumerate(self.patrol):
            d = self.pos.distance_to(pt)
            if d < bestd:
                best = idx; bestd = d
        def blocked_to(idx):
            return any(line_intersects_rect(self.pos, self.patrol[idx], ob) for ob in self.obstacles)
        if not blocked_to(best):
            self.i = best
            return
        n = len(self.patrol)
        for step in range(1, n):
            cand = (best + step) % n
            if not blocked_to(cand):
                self.i = cand
                return
            cand2 = (best - step) % n
            if not blocked_to(cand2):
                self.i = cand2
                return
        self.i = best

    def _collides_any(self,x,y,r=None):
        if r is None: r = self.radius
        return any(circle_rect_collide(x,y,r,ob) for ob in self.obstacles)

    def _resolve_stuck(self):
        for ob in self.obstacles:
            if circle_rect_collide(self.pos.x, self.pos.y, self.radius, ob):
                center = pygame.Vector2(ob.center)
                v = self.pos - center
                if v.length_squared() == 0:
                    v = pygame.Vector2(random.uniform(-1,1), random.uniform(-1,1))
                v = v.normalize()
                for _ in range(12):
                    self.pos += v * 2
                    if not circle_rect_collide(self.pos.x, self.pos.y, self.radius, ob):
                        break

    def update(self,player_pos, player_history=None):
        if player_history is not None:
            self.player_history = player_history[-self.history_max:]
            self.learn_from_history()

        prev_state = self.state
        if self.attack_cd>0:
            self.attack_cd-=1

        dist = self.pos.distance_to(player_pos)
        # forzar HUIR si la salud es 20% o menos (independiente de la distancia)
        if self.health <= 20:
            if self.state != FLEE:
                self.state = FLEE
        else:
            if self.state==PATROL:
                if self.can_see(player_pos) and dist < self.vision*(0.6+0.4*self.aggr):
                    self.state = PURSUE
            elif self.state==PURSUE:
                if not self.can_see(player_pos) or dist>self.vision*1.2:
                    self.state = PATROL
            elif self.state==FLEE:
                if self.health>30 and dist>self.vision:
                    self.state = PATROL

        if prev_state != self.state and self.state == PATROL:
            self._resolve_patrol_start()

        if self.state==PATROL:
            target = self.patrol[self.i]
            moved = self.move_towards(target)
            # si colisiona con obstaculo mientras patrulla, cambiar direccion de patrulla
            if self._collides_any(self.pos.x,self.pos.y,self.radius):
                # intentar resolver y cambiar al siguiente punto
                self._resolve_stuck()
                self.i = (self.i+1) % len(self.patrol)
            else:
                if moved and self.pos.distance_to(target)<6:
                    self.i = (self.i+1)%len(self.patrol)
        elif self.state==PURSUE:
            self.move_towards(player_pos)
        elif self.state==FLEE:
            dir_away = (self.pos - player_pos)
            if dir_away.length_squared()>0:
                dir_away = dir_away.normalize()
                # usar move_towards-style step para respetar colisiones y resolver atascos
                self.step(dir_away * self.speed * 1.6)
                # si tras el paso qued0b atascado, intentar resolver
                if self._collides_any(self.pos.x,self.pos.y,self.radius):
                    self._resolve_stuck()
            # regeneración de salud: 5% del máximo por segundo => 5 HP por segundo (max=100)
            # acumulador para aplicar solo enteros
            self._regen_acc += 5.0 / FPS
            add = int(self._regen_acc)
            if add > 0:
                self._regen_acc -= add
                self.health = int(min(100, int(self.health) + int(add)))

        self.pos.x = max(self.radius, min(SCREEN_W-self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(SCREEN_H-self.radius, self.pos.y))

    def step(self, delta):
        nx = self.pos.x + delta.x
        ny = self.pos.y + delta.y
      # intento X
        if not self._collides_any(nx,self.pos.y,self.radius):
            self.pos.x = nx
        else:
            self.pos.x += delta.x*0.15
        # intento Y
        if not self._collides_any(self.pos.x,ny,self.radius):
            self.pos.y = ny
        else:
            self.pos.y += delta.y*0.15
        # Si está atascada, paso perpendicular
        if self._collides_any(self.pos.x,self.pos.y,self.radius):
            perp = pygame.Vector2(-delta.y, delta.x)
            if perp.length_squared()>0:
                perp = perp.normalize()* (self.speed*0.5)
                altx = self.pos.x + perp.x
                alty = self.pos.y + perp.y
                if not self._collides_any(altx,self.pos.y,self.radius):
                    self.pos.x = altx
                elif not self._collides_any(self.pos.x,alty,self.radius):
                    self.pos.y = alty

    def move_towards(self,target,speed=None):
        if speed is None:
            speed = self.speed * (1.2 + 0.8*self.aggr) if self.state==PURSUE else self.speed
        to = (pygame.Vector2(target)-self.pos)
        if to.length_squared()==0:
            return False
        delta = to.normalize()*speed
        self.step(delta)
        return True

    def draw(self,surf):
        pygame.draw.circle(surf,NPC_COLOR,(int(self.pos.x),int(self.pos.y)),self.radius)
        pygame.draw.circle(surf,(90,90,120),(int(self.pos.x),int(self.pos.y)),int(self.vision),1)
        pygame.draw.rect(surf,(40,40,40),(self.pos.x-16,self.pos.y-26,32,6))
        pygame.draw.rect(surf,(0,200,0),(self.pos.x-16,self.pos.y-26,32*(self.health/100),6))
        txt = FONT_XS.render(STATE_NAMES.get(self.state,self.state),True,(220,220,220))
        surf.blit(txt,(self.pos.x-20,self.pos.y+16))

class Player:
    def __init__(self,pos):
        self.pos = pygame.Vector2(pos)
        self.base_speed = 2.6
        self.speed = self.base_speed
        self.boost_timer = 0
        self.boost_multiplier = 1.0
        self.health = 100
        self.radius = 10

    def update(self,obs):
        # administrar el temporizador de impulso
        if self.boost_timer>0:
            self.boost_timer -= 1
            if self.boost_timer==0:
                self.boost_multiplier = 1.0
        self.speed = self.base_speed * self.boost_multiplier

        keys = pygame.key.get_pressed()
        d = pygame.Vector2(0,0)
        if keys[pygame.K_w] or keys[pygame.K_UP]: d.y=-1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: d.y=1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: d.x=-1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: d.x=1
        if d.length_squared()>0:
            d = d.normalize()*self.speed
            nx = self.pos.x + d.x
            ny = self.pos.y + d.y
            if not collides_any_obs(nx,self.pos.y,self.radius,obs):
                self.pos.x = nx
            if not collides_any_obs(self.pos.x,ny,self.radius,obs):
                self.pos.y = ny
        self.pos.x = max(self.radius, min(SCREEN_W-self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(SCREEN_H-self.radius, self.pos.y))

    def draw(self,surf):
        pygame.draw.circle(surf,PLAYER_COLOR,(int(self.pos.x),int(self.pos.y)),self.radius)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W,SCREEN_H))
    clock = pygame.time.Clock()
   # administrar el temporizador de impulso
    global FONT_XS, FONT_S, FONT_M, FONT_L
    FONT_XS = pygame.font.Font(None,14)
    FONT_S = pygame.font.Font(None,18)
    FONT_M = pygame.font.Font(None,20)
    FONT_L = pygame.font.Font(None,48)

    player = Player((SCREEN_W/2,SCREEN_H/2))
    npc = NPC((100,100),[(80,80),(560,80),(560,400),(80,400)])

    obstacles = [pygame.Rect(220,150,80,180), pygame.Rect(400,60,40,120), pygame.Rect(120,320,200,30), pygame.Rect(40,40,60,60), pygame.Rect(500,200,50,140), pygame.Rect(300,10,80,40)]
    npc.set_obstacles(obstacles)

    if GENSIM_AVAILABLE:
        try:
            # anteriormente se usaban frases de ejemplo para entrenar Word2Vec; se omiten para evitar datos estáticos
            # si se desea, el usuario puede proporcionar un corpus real aquí
            modelo = Word2Vec([['ejemplo']], vector_size=50, window=3, min_count=1, workers=1)
            # Ajustes básicos aplicados siempre si el modelo se construye correctamente.
            try:
                # calcular una heuredstica simple basada en los vectores del vocabulario (si los hay)
                words = getattr(modelo.wv, 'index_to_key', [])
                all_vecs = [modelo.wv[w] for w in words]
                if len(all_vecs) > 0:
                    try:
                        import numpy as _np
                        avg_vec = _np.mean(all_vecs, axis=0)
                        factor = float(_np.linalg.norm(avg_vec))
                    except Exception:
                        # sin numpy, usar tamaño de vocabulario como heuredstica
                        factor = min(1.0, len(all_vecs)/10.0)
                    npc.vision = min(200, npc.vision + 10 + factor*10)
                    npc.speed = npc.speed + 0.05 + factor*0.02
                    npc.aggr = min(1.0, npc.aggr + 0.02 + factor*0.01)
                    print('Gensim: modelo entrenado. Ajustados vision, speed y agresividad del NPC')
            except Exception:
                # fallback sencillo
                npc.vision = min(200, npc.vision + 15)
                npc.speed += 0.15
                npc.aggr = min(1.0, npc.aggr + 0.03)
        except Exception as e:
            print('Gensim: entrenamiento fall\u00f3:', e)

    running = True
    game_over = False
    result = ''

    player_history = []

    gp_file = os.path.join(os.path.dirname(__file__), 'games_played.txt')
    meta_file = os.path.join(os.path.dirname(__file__), 'games_meta.json')
    model_file = os.path.join(os.path.dirname(__file__), 'gensim_model.model')
    # administrar el temporizador de impulso
    try:
        with open(gp_file, 'r') as f:
            games_played = int(f.read().strip() or '0')
    except Exception:
        games_played = 0
    # cargar metadatos si existen (preferible)
    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
            games_played = int(meta.get('games_played', games_played))
           # restaurar los parámetros del NPC almacenados si están presentes
            npc_meta = meta.get('npc', {})
            if 'aggr' in npc_meta: npc.aggr = float(npc_meta.get('aggr', npc.aggr))
            if 'vision' in npc_meta: npc.vision = float(npc_meta.get('vision', npc.vision))
            if 'speed' in npc_meta: npc.speed = float(npc_meta.get('speed', npc.speed))
    except Exception:
        meta = {}

    def save_meta():
        try:
            meta_out = {
                'games_played': games_played,
                'npc': {'aggr': float(npc.aggr), 'vision': float(npc.vision), 'speed': float(npc.speed)},
                'stats': meta.get('stats', {}),
                'ts': datetime.utcnow().isoformat() + 'Z'
            }
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(meta_out, f, ensure_ascii=False, indent=2)
            # También mantenga el contador simple para compatibilidad con versiones anteriores
            try:
                with open(gp_file, 'w') as f:
                    f.write(str(games_played))
            except Exception:
                pass
           # si el modelo gensim está en la memoria, guárdelo
            if GENSIM_AVAILABLE and 'modelo' in locals():
                try:
                    modelo.save(model_file)
                except Exception:
                    pass
        except Exception:
            pass

    while running:
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                running=False
            if e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE and game_over:
                running=False
            # boton para resetear aprendizaje: tecla R
            if e.type==pygame.KEYDOWN and e.key==pygame.K_r:
                games_played = 0
                try:
                    # reinicio completo: borrar estadísticas, restablecer parámetros de NPC a los valores predeterminados, eliminar modelo guardado
                    meta['stats'] = {}
                    # restablecer los parámetros principales del NPC
                    npc.aggr = 0.5
                    npc.vision = 90
                    npc.speed = 1.2
                    npc.player_history = []
                    npc.learning_scale = 0.0
                   # eliminar el archivo del modelo persistente si existe
                    try:
                        if os.path.exists(model_file):
                            os.remove(model_file)
                    except Exception:
                        pass
                    # eliminar el modelo en memoria si está presente
                    if 'modelo' in locals():
                        try:
                            del modelo
                        except Exception:
                            pass
                    save_meta()
                except Exception:
                    pass
                print('Aprendizaje del NPC reiniciado (reset completo).')
            if e.type==pygame.MOUSEBUTTONDOWN and e.button==1 and not game_over:
                m = pygame.Vector2(e.pos)
                if m.distance_to(npc.pos)<20:
                    # aplicar dañ reducido al NPC
                    dmg = int(PLAYER_CLICK_DAMAGE * (1.0 - PLAYER_TO_NPC_REDUCE))
                    npc.health = int(max(0, int(npc.health) - int(dmg)))
                    npc.aggr = max(0.0,npc.aggr-0.1)

        if not game_over:
            player.update(obstacles)
            player_history.append(pygame.Vector2(player.pos))
            if len(player_history)>240:
                player_history.pop(0)
            # aprendizaje lento primeras 3 partidas
            if games_played < 3:
                npc.learning_scale = min(0.3, (games_played/3.0)*0.3)
            else:
                npc.learning_scale = min(1.0, (games_played-3)/17.0)

            npc.update(player.pos, player_history)

            # manejo aumento temporal de velocidad del jugador
            # se activa cuando NPC persigue, est\u00e1 MUY cerca y tiene linea de vista
            very_close_dist = npc.radius + player.radius + 36
            if npc.state==PURSUE and npc.pos.distance_to(player.pos) < very_close_dist and npc.can_see(player.pos):
                player.boost_timer = 60  # ~1s a 60 FPS
                player.boost_multiplier = 1.5
            else:
                # si NPC ya no persigue, est\u00e1 lejos o hay obstaculo entre ambos, quitar boost
                blocked = any(line_intersects_rect(npc.pos, player.pos, ob) for ob in obstacles)
                if blocked or npc.state!=PURSUE or npc.pos.distance_to(player.pos) >= npc.vision*1.2:
                    player.boost_timer = 0
                    player.boost_multiplier = 1.0

            if npc.attack_cd>0: npc.attack_cd-=1
            if npc.state==PURSUE and npc.pos.distance_to(player.pos)<(npc.radius+player.radius+6) and npc.attack_cd==0:
                # aplicar dao del NPC reducido
                dmg = int(NPC_ATTACK_DAMAGE * (1.0 - NPC_TO_PLAYER_REDUCE))
                player.health = int(max(0, int(player.health) - int(dmg)))
                npc.attack_cd = 45
                npc.aggr = min(1.0,npc.aggr+0.05)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and player.pos.distance_to(npc.pos)<(npc.radius+player.radius+6):
                # jugador daño cuerpo a cuerpo reducido
                dmg = int(PLAYER_MELEE_DAMAGE * (1.0 - PLAYER_TO_NPC_REDUCE))
                npc.health = int(max(0, int(npc.health) - int(dmg)))
                npc.aggr = max(0.0,npc.aggr-0.1)

            if player.health<=0 or npc.health<=0:
                game_over=True
                if player.health<=0 and npc.health<=0: result='Juego terminado: Empate'
                elif player.health<=0: result='Juego terminado: Has sido derrotado'
                else: result='Juego terminado: Has derrotado al NPC'
                try:
                    games_played += 1
                   # jugador daño cuerpo a cuerpo reducido
                    stats = meta.get('stats', {})
                    if 'wins' not in stats: stats['wins'] = 0
                    if 'losses' not in stats: stats['losses'] = 0
                    if npc.health<=0 and player.health>0:
                        stats['player_wins'] = stats.get('player_wins',0) + 1
                    elif player.health<=0 and npc.health>0:
                        stats['npc_wins'] = stats.get('npc_wins',0) + 1
                    meta['stats'] = stats
                    save_meta()
                except Exception:
                    pass

        screen.fill(BG)
        for ob in obstacles: pygame.draw.rect(screen,OBST_COLOR,ob)
        player.draw(screen)
        npc.draw(screen)
        info = FONT_M.render(f"Salud jugador: {player.health}   Salud NPC: {npc.health}   Estado NPC: {STATE_NAMES.get(npc.state)}   Partidas jugadas: {games_played}",True,(220,220,220))
        screen.blit(info,(8,8))
        hint = FONT_S.render('Presiona R para reiniciar aprendizaje del NPC', True, (200,200,200))
        screen.blit(hint,(8,30))

        if game_over:
            overlay = pygame.Surface((SCREEN_W,SCREEN_H),pygame.SRCALPHA)
            overlay.fill((0,0,0,160))
            screen.blit(overlay,(0,0))
            txt = FONT_L.render(result,True,(255,255,255))
            screen.blit(txt,txt.get_rect(center=(SCREEN_W/2,SCREEN_H/2-20)))
            sub = pygame.font.Font(None,28).render('Presiona ESC o cierra la ventana para salir.',True,(200,200,200))
            screen.blit(sub,sub.get_rect(center=(SCREEN_W/2,SCREEN_H/2+30)))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__=='__main__':
    main()
