# 🐍 Jungle Adventure – Platformer em Python (PgZero)

Este projeto foi desenvolvido como parte de um **desafio técnico para tutores de Python**, cujo objetivo era criar um jogo completo utilizando exclusivamente:

- **PgZero**
- **math**
- **random**
- (e opcionalmente) `Rect` do pygame

Além disso, o desafio exigia:

✔ Criar um jogo em um dos gêneros permitidos (Roguelike, Point & Click ou Platformer)  
✔ Criar um menu funcional com botões clicáveis  
✔ Movimentação e animações de sprites (parado e andando)  
✔ Inimigos com comportamento próprio  
✔ Música e efeitos sonoros  
✔ Código 100% autoral, legível e organizado  
✔ Mecânica consistente e sem bugs  
✔ Uso de classes para organizar animação, movimento e lógica  

Este repositório contém a minha solução: **um platformer completo**, com câmera dinâmica, animações, inimigos, objetivo final e até uma **abelha gigante passando no fundo** para dar vida ao cenário.

---

# 🎮 **Sobre o jogo**

Você controla um personagem em uma pequena aventura dentro da selva.  
O objetivo é:

➡ **Atravessar a fase**,  
➡ **Desviar das abelhas inimigas**,  
➡ **E alcançar o personagem final (Ramiles) no fim do mapa**.

O jogo contém:

- Movimento fluido com física (gravidade, salto, colisão)
- Câmera lateral que segue o jogador
- Mapa baseado em tiles lidos de um arquivo CSV
- Inimigos com patrulha e animação própria
- Menu inicial completo:
  - Start
  - Som ON/OFF
  - Exit
- Tela de introdução
- Tela de vitória
- Tela de morte
- Tela de despedida
- Música de fundo e efeitos sonoros
- **Abelha gigante animada passando ao fundo (efeito de profundidade/decoração)**

---

# 🧠 **Desafios enfrentados**

Durante o desenvolvimento deste projeto, precisei lidar com algumas dificuldades técnicas que me ajudaram a evoluir ainda mais:

### 🔹 1. Sistema de colisão e física
Implementar pulo, gravidade e colisão com plataformas usando apenas `Rect` e listas exigiu bastante cuidado, principalmente para evitar bugs clássicos como:

- Travar dentro da parede  
- Quicar no teto  
- Falhar para detectar chão  

Resolvi isso dividindo a física em duas fases (horizontal e vertical), o que deixou a movimentação sólida e intuitiva.

---

### 🔹 2. Leitura e renderização do mapa via CSV
Precisava que o jogo carregasse o mapa dinamicamente, então implementei:

- Leitura linha por linha  
- Conversão de cada número em um tile  
- Posicionamento automático  
- Cálculo da largura total da fase  

Isso permitiu criar fases facilmente apenas editando um arquivo.

---

### 🔹 3. Câmera lateral suave
O PgZero não possui um sistema de câmera integrado, então criei manualmente um `camera_x` que:

- Acompanha o jogador
- Limita o movimento para não mostrar “fora do mapa”
- Ajusta posição de tudo que é desenhado

É um dos sistemas mais importantes do jogo.

---

### 🔹 4. Animação real de sprites
O desafio exigia **animação verdadeira**, não apenas trocar imagens de esquerda/direita.

Implementei:

- Lista de frames
- Timer de animação
- Alternância cíclica automática

Tanto para o jogador quanto para os inimigos.

---

### 🔹 5. Arquitetura orientada a objetos
Criei classes separadas:

- `Character`  
- `Player`  
- `Enemy`  
- `BackgroundBee`  

Assim, cada entidade tem seu próprio comportamento, animação e atualização.

---

### 🔹 6. Criar a "Background Bee", uma abelha gigante no fundo
Esse foi um extra criativo para deixar o jogo mais vivo.  
Desafios aqui:

- Animação própria  
- Movimento independente da câmera  
- Reset automático ao sair da tela  
- Variação de altura e velocidade (efeito natural)  

Resultado: um detalhe visual que enriquece a experiência.

---

# 📂 **Estrutura do projeto**

