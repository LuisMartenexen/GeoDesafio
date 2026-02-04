# GeoArena — Visão geral do sistema

## Descrição
O **GeoArena** é uma plataforma web + mobile voltada para uso em sala de aula, combinando um banco de questões de Geografia com um modo de disputa ao vivo. O professor controla as rodadas, e os grupos respondem em tempo real.

## Como rodar (API inicial)
Este repositório contém uma **API inicial** em FastAPI + SQLite para servir como base do sistema.

### Requisitos
- Python 3.11+

### Instalação
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Executar
```bash
uvicorn app.main:app --reload
```

### Endpoints principais
- `POST /users` — cria usuário (professor, aluno, moderador).
- `POST /classrooms` — cria turma.
- `POST /questions` — cadastra questão com alternativas.
- `POST /questions/import` — importa questões via CSV.
- `POST /sessions` — cria sessão (aula).
- `POST /sessions/{session_id}/questions` — monta a lista de perguntas da sessão.
- `POST /groups` — cria grupo dentro da sessão.
- `POST /answers` — registra resposta.
- `GET /sessions/{session_id}/ranking` — ranking (pontos por acertos).
- `GET /sessions/{session_id}/themes` — resumo de acertos/erros por tema.

#### Formato CSV (exemplo)
```csv
theme,subtheme,difficulty,type,statement,explanation,tags,source,status
Cartografia,Escala,1,multiple_choice,\"O que é escala cartográfica?\",\"Relação entre distância no mapa e na realidade.\",\"6º ano\",BNCC,approved
```

## Objetivos principais
- Organizar um banco de questões por temas de Geografia.
- Classificar a dificuldade por estrelas/pontos (1 a 5).
- Facilitar a adição e revisão de novas questões.
- Oferecer modo de disputa em grupos com perguntas escolhidas pelo professor.
- Contabilizar tempo por pergunta.
- Aplicar gamificação (XP, níveis, conquistas, efeitos e feedback visual).
- Exibir ranking por aula, por turma e por semestre.

## Perfis de usuário (permissões)
### 1) Professor (admin da turma)
- Cria turmas e sessões de jogo (aulas).
- Seleciona temas, dificuldade, quantidade de perguntas e tempo.
- Cria/edita questões e aprova questões sugeridas.
- Visualiza relatórios: desempenho por tema, por grupo e por aluno.

### 2) Aluno (jogador)
- Entra numa turma por código.
- Participa de disputas em grupo.
- Pode sugerir novas perguntas (se o professor permitir).
- Vê seu progresso (XP, acertos, temas fortes/fracos).

### 3) Moderador/Coordenador (opcional)
- Audita conteúdo, ajuda professores e controla o banco geral da escola.

## Banco de questões (estrutura)
As questões ficam em um banco central (ex.: PostgreSQL), com suporte a milhares/milhões de registros. Cada questão possui:
- **Tema principal**: Cartografia, Clima, Geopolítica, Urbanização, Geografia do Brasil, População, Relevo, Hidrografia, Economia, Globalização, Meio Ambiente etc.
- **Subtema**: ex. “Clima → massas de ar”, “Cartografia → escala”.
- **Dificuldade (1 a 5)**: 1 bem fácil, 5 avançada.
- **Tipo**: múltipla escolha / verdadeiro-falso / resposta curta / associação (opcional).
- **Enunciado** (texto) + recursos (imagem, mapa, gráfico) (opcional).
- **Alternativas** (se for múltipla escolha).
- **Resposta correta + explicação** (foco no aprendizado).
- **Tags**: ENEM, vestibular, 6º ano, 9º ano etc.
- **Fonte/autor + data + status** (ativa/em revisão/desativada).

## Inserção de novas perguntas (sem bagunça)
- Formulário rápido para cadastro.
- Importação via planilha (CSV) para inserir centenas de uma vez.
- Sistema de revisão: **rascunho → pendente → aprovado → publicado**.
- Controle anti-duplicação (detecta questões muito parecidas).

## Taxonomia sugerida (temas de Geografia)
- Cartografia (escala, projeções, coordenadas, fusos)
- Climatologia (climas, massas de ar, El Niño/La Niña)
- Geomorfologia (relevo, tectonismo, erosão)
- Hidrografia (bacias, aquíferos, usos da água)
- Biomas e Meio Ambiente (Amazônia, Cerrado, impactos ambientais)
- Geografia do Brasil (regiões, economia, agricultura, urbanização)
- População e Demografia (migrações, pirâmides etárias)
- Urbanização (metrópoles, rede urbana, segregação)
- Geopolítica (blocos econômicos, guerras, globalização)
- Economia e Indústria (cadeias produtivas, energia, transportes)

## Dificuldade 1 a 5 (na prática)
- **Nível 1 (⭐)**: conceito direto, definição, reconhecimento.
- **Nível 2 (⭐⭐)**: interpretação simples, exemplos.
- **Nível 3 (⭐⭐⭐)**: relacionar dois conceitos, leitura de gráfico simples.
- **Nível 4 (⭐⭐⭐⭐)**: análise, causa/consequência, cenário.
- **Nível 5 (⭐⭐⭐⭐⭐)**: interpretação avançada, múltiplas variáveis, estilo ENEM.

## Pontuação base (exemplo)
- N1: 100 pts
- N2: 200 pts
- N3: 350 pts
- N4: 500 pts
- N5: 700 pts

> Ainda entra o bônus por tempo.

## Modo “Disputa de Grupos” (ao vivo em sala)
### Fluxo da aula
1. Professor cria uma sessão (ex.: “8ºA – Urbanização – 20min”).
2. Alunos entram com um PIN/QR code e escolhem seu grupo (ou o professor monta).
3. Professor seleciona:
   - temas/subtemas
   - dificuldade permitida
   - número de perguntas
   - tempo por pergunta (ex.: 20s, 30s, 45s)
   - modo de resposta: “um líder responde” ou “todos votam e vale maioria”
4. Começa a rodada. A tela do professor mostra:
   - pergunta atual
   - cronômetro
   - porcentagem de respostas por alternativa
5. No final: pódio e ranking.

### Tempo e regras
- Cada pergunta tem um timer visível (ex.: barra diminuindo + som leve).
- Se responder antes, ganha bônus.
- Empate: “pergunta de desempate” (dificuldade maior) ou “morte súbita”.

## Gamificação (para ficar atrativo)
### Elementos principais
- XP por participação (mesmo errando, ganha um pouco).
- Streak (sequência de acertos) dá multiplicador.
- Power-ups (configurável pelo professor):
  - **50/50** (remove duas alternativas)
  - **+5s** (mais tempo uma vez por rodada)
  - **Trocar pergunta** (apenas em treinos, não na disputa)

### Conquistas/Badges
- “Mestre da Cartografia” (80%+ no tema)
- “Velocista” (3 respostas corretas com bônus de tempo)

### Feedback visual
- Animação curta ao acertar.
- Explicação após a pergunta (“por que é isso?”).

## Visual (educacional e moderno)
- Interface estilo “quiz show” (limpa, colorida, com mapas/ícones).
- Cards grandes, tipografia legível, contraste alto.
- Temas com ícones: 🌎 clima, 🧭 cartografia, 🏙️ urbanização etc.

## Ranking (colocação)
O sistema mantém rankings em camadas:
- Ranking da sessão (aula de hoje)
- Ranking da turma (mês/bimestre)
- Ranking individual (opcional, se a escola permitir)
- Ranking por tema (quem manda em Clima? quem manda em Geopolítica?)

### Critérios possíveis
- Pontos totais
- Taxa de acerto
- Tempo médio
- Dificuldade média enfrentada

> O professor pode escolher: “ranking só por grupos” (mais seguro para sala).

## Relatórios para o professor
- Quais temas tiveram mais erro (ex.: cartografia e escala).
- Questões “campeãs de erro” (para revisar conteúdo).
- Evolução da turma ao longo do tempo.
- Comparação entre grupos (sem expor aluno, se quiser).

## Exemplos de perguntas (tema + nível + resposta)
1) **Cartografia – Nível 1**
   - **Pergunta**: O que é escala cartográfica?
   - **Resposta**: É a relação entre a distância no mapa e a distância real.

2) **Clima – Nível 2**
   - **Pergunta**: Qual fenômeno geralmente aumenta as chuvas no Sul do Brasil e pode reduzir no Nordeste?
   - **Resposta**: El Niño (em muitos casos altera padrões de chuva).

3) **Urbanização – Nível 3**
   - **Pergunta**: Cite uma consequência comum da urbanização acelerada sem planejamento.
   - **Resposta**: Aumento de favelização/ocupações irregulares, problemas de mobilidade, saneamento precário (qualquer uma válida conforme gabarito).

4) **Geopolítica – Nível 4**
   - **Pergunta**: Como a dependência energética pode influenciar decisões geopolíticas de um país?
   - **Resposta**: Pode gerar alianças, disputas por rotas e recursos, pressão diplomática e vulnerabilidade em crises.

5) **Meio Ambiente – Nível 5 (interpretação)**
   - **Pergunta**: Um gráfico mostra aumento de desmatamento e, ao mesmo tempo, redução de chuvas em uma região. Qual relação pode explicar isso?
   - **Resposta**: O desmatamento pode reduzir evapotranspiração e umidade disponível, alterando o regime de chuvas local/regional.

## Extras (diferencial)
- Modo offline (ideal para escolas com internet ruim), sincronizando quando voltar.
- Banco com questões por BNCC (organização por habilidade).
- Versões da mesma pergunta (variações) para evitar cola.
- Anti-chute: se responder muito rápido sempre, reduz bônus.
- Painel “telão” para projetor: placar + próxima pergunta + clima de game show.
