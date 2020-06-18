import pygame
import os
import time
import random
from pygame import mixer
pygame.font.init()

altura, largura = 750, 750
JANELA =  pygame.display.set_mode((altura,largura))
pygame.display.set_caption("Ataque espacial")

#imagens 

nave_1 = pygame.image.load(os.path.join("imagens","nave_1.png")) 
nave_2 = pygame.image.load(os.path.join("imagens","nave_2.1.png")) 
nave_3 = pygame.image.load(os.path.join("imagens","nave_3.png")) 

nave_jogador = pygame.image.load(os.path.join("imagens","nave_jo.png")) 

# laser tiros
tiro_1 = pygame.image.load(os.path.join("imagens","tiro_v1.png")) #trocar imgagem
tiro_2 = pygame.image.load(os.path.join("imagens","tiro_2V2.png")) #trocar imgagem
tiro_3 = pygame.image.load(os.path.join("imagens","tiro_3v2.png")) #trocar imgagem
tiro_4 = pygame.image.load(os.path.join("imagens","tiro4_v2.png")) #trocar imgagem

#fundo

fundo = pygame.transform.scale(pygame.image.load(os.path.join("imagens","espaco_fundo.jpg")),(altura,largura)) 


class Tiro:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def desenhar(self, janela):
        janela.blit(self.img, (self.x, self.y))

    def movimento(self, vel):
        self.y += vel
    
    def fora_da_tela(self, height):
        return not(self.y <= height and self.y >= 0)

    def colisao(self, obj):
        return collide (self, obj)


class Nave:
    TEMPO_DE = 30
    def __init__(self,x,y,hp=100):
        self.x = x
        self.y = y
        self.hp = hp
        self.nave_img  = None
        self.tiro_img = None
        self.tiros = []
        self.tempo_de_espera = 0
    
    def desenhar(self,janela):
        #pygame.draw.rect(janela,(255,0,0),(self.x, self.y, 50, 50))
        janela.blit(self.nave_img, (self.x, self.y))
        for tiro in self.tiros:
            tiro.desenhar(JANELA)
    
    def movimento_tiro(self, vel, obj):
        self.tempo_de()
        for tiro in self.tiros:
            tiro.movimento(vel)
            if tiro.fora_da_tela(largura):
                self.tiros.remove(tiro)
            elif tiro.colisao(obj):
                obj.hp -= 10
                self.tiros.remove(tiro)
    
    def tempo_de(self):
        if self.tempo_de_espera >= self.TEMPO_DE:
            self.tempo_de_espera = 0
        elif self.tempo_de_espera > 0:
            self.tempo_de_espera += 1

    def atirar(self):
        if self.tempo_de_espera == 0:
            tiro = Tiro(self.x, self.y, self.tiro_img)
            self.tiros.append(tiro)
            self.tempo_de_espera = 1
            efeito = pygame.mixer.Sound('tiro.wav')
            efeito.play()
    
    def get_altura(self):
        return self.nave_img.get_width()

    def get_largura(self):
        return self.nave_img.get_height()

class Inimigo(Nave):
    CORES = {
        "cor1": (nave_1,tiro_1),
        "cor2": (nave_2,tiro_2),
        "cor3": (nave_3,tiro_3)
    } 
    def __init__(self, x, y, cor, hp = 100):
        super().__init__(x, y, hp)
        self.nave_img, self.tiro_img = self.CORES[cor]
        self.mask = pygame.mask.from_surface(self.nave_img)

    def movimento(self, vel):
            self.y += vel

    def atirar(self):
        if self.tempo_de_espera == 0:
            tiro = Tiro(self.x -20, self.y, self.tiro_img)
            self.tiros.append(tiro)
            self.tempo_de_espera = 1

class Jogador(Nave):
    def __init__(self, x, y,hp =100):
        super().__init__(x, y, hp)
        self.nave_img = nave_jogador
        self.tiro_img = tiro_4
        self.mask = pygame.mask.from_surface(self.nave_img)
        self.vida_maxima = hp

    def movimento_tiro(self, vel, objs):
        self.tempo_de()
        for tiro in self.tiros:
            tiro.movimento(vel)
            if tiro.fora_da_tela(largura):
                self.tiros.remove(tiro)
            else:
                for obj in objs:
                    if tiro.colisao(obj):
                        objs.remove(obj)
                        if tiro in self.tiros:
                            self.tiros.remove(tiro)

    def desenhar(self, janela):
        super().desenhar(janela)
        self.barra_de_vida(janela)
    
    def barra_de_vida(self, janela):
        pygame.draw.rect(janela, (255,0,0), (self.x, self.y + self.nave_img.get_height() + 10, self.nave_img.get_width(), 10))
        pygame.draw.rect(janela, (0,255,0), (self.x, self.y + self.nave_img.get_height() + 10, self.nave_img.get_width() * (self.hp/self.vida_maxima), 10))


def collide(obj1, obj2):
    temp_x = obj2.x - obj1.x
    temp_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (temp_x, temp_y)) != None

def main():
    run = True
    FPS = 60
    nivel = 1
    vida = 4
    fonte_principal = pygame.font.SysFont("OpenDyslexic",50) #fonte utilizada
    fonte_perdeu = pygame.font.SysFont("OpenDyslexic",60)
    inimigos = []
    enxame = 5
    inimigo_vel = 1

    jogador_vel = 5

    velocidade_tiro = 6
    jogador = Jogador(300,650)

    perdeu = False
    contador_derrotas = 0

    clock = pygame.time.Clock()
    
    def recarga_janela():
        JANELA.blit(fundo,(0,0))
        #texto
        mostrador_vida = fonte_principal.render(f"Vidas: {vida}", 1, (255,255,255))
        mostrador_nivel = fonte_principal.render(f"Nivel: {nivel}", 1, (255,255,255))

        JANELA.blit(mostrador_vida,(10,10))
        JANELA.blit(mostrador_nivel,(altura - mostrador_vida.get_width() - 10, 10))
        
        for inimigo in inimigos:
            inimigo.desenhar(JANELA)
        
        if perdeu:
            perdeuuu = fonte_perdeu.render(f"Faleceu, perdeu", 1, (255,6,255))
            JANELA.blit(perdeuuu, (altura/2 - perdeuuu.get_width(), 350))
        jogador.desenhar(JANELA)
        pygame.display.update()

    while run:
        clock.tick(FPS)

        recarga_janela()

        if vida <= 0 or jogador.hp <= 0:
            perdeu = True
            contador_derrotas +=1

        if perdeu:
            if contador_derrotas > 50:
                run = False
            else:
                continue


        if len(inimigos) == 0:
            nivel += 1
            enxame += 5
            for i in range(enxame):                                                  #nivel/5
                inimigo = Inimigo(random.randrange(50, altura -100),random.randrange(-1500,-100), random.choice(["cor1","cor2","cor3"]))
                inimigos.append(inimigo)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_a] and jogador.x - jogador_vel > 0:
            jogador.x -= jogador_vel
        if teclas[pygame.K_d] and jogador.x + jogador_vel + jogador.get_altura() < altura:
            jogador.x += jogador_vel    
        if teclas[pygame.K_w] and jogador.y - jogador_vel > 0:
            jogador.y -= jogador_vel
        if teclas[pygame.K_s] and jogador.y + jogador_vel + jogador.get_largura() + 15 < largura:
            jogador.y += jogador_vel     
        if teclas[pygame.K_SPACE]:
            jogador.atirar()


        for inimigo in inimigos[:]:
            inimigo.movimento(inimigo_vel)
            inimigo.movimento_tiro(velocidade_tiro, jogador)

            if random.randrange(0, 2*FPS) == 1:
                inimigo.atirar()

            if collide(inimigo, jogador):
                jogador.hp -=10 
                inimigos.remove(inimigo)

            elif inimigo.y + inimigo.get_largura() > largura:
                vida -= 1
                inimigos.remove(inimigo)

            
            
        jogador.movimento_tiro(-velocidade_tiro, inimigos)


def menu():
    fonte_titulo = pygame.font.SysFont("comicsans", 80)
    jogando = True
    mixer.init()
    mixer.music.load('musica_top.mp3')
    mixer.music.play()

    while jogando:
        JANELA.blit(fundo,(0,0))
        titulo= fonte_titulo.render("Pressione para Jogar", 1,(255,255,255))
        JANELA.blit(titulo,(altura/2 - titulo.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                jogando = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


menu()