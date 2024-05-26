import pygame
import sys
import os

# Initialisation de Pygame
pygame.init()

# Taille de la fenêtre
width, height = 1000, 400
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Piano Virtuel بيانو إفتراضي")

# Définir l'icône de la fenêtre
icon_path = os.path.join(os.path.dirname(__file__), 'clef_de_sol.png')
if os.path.exists(icon_path):
    icon = pygame.image.load(icon_path)
    pygame.display.set_icon(icon)
else:
    print(f"File not found: {icon_path}")
    
# Couleurs
white = (255, 255, 255)
black = (0, 0, 0)
grey = (169, 169, 169)
dark_grey = (105, 105, 105)
blue = (0, 0, 255)
green = (0, 255, 0)

# Police pour le texte
font = pygame.font.Font(None, 20)

# Chemin absolu vers le dossier des sons
sound_dir = os.path.join(os.path.dirname(__file__), 'sounds')

# Initialisation des variables
current_instrument = 'piano'
recording = False
sequence = []
start_time = None
play_index = 0
is_playing = False

# Définir les boutons
side_panel_x = width - 150
record_button = pygame.Rect(side_panel_x + 10, 10, 130, 40)
play_button = pygame.Rect(side_panel_x + 10, 70, 130, 40)

instrument_buttons = {
    'Piano': pygame.Rect(side_panel_x + 10, 130, 130, 40),
    'Guitar': pygame.Rect(side_panel_x + 10, 190, 130, 40),
    'Flute': pygame.Rect(side_panel_x + 10, 250, 130, 40),
    'Oud': pygame.Rect(side_panel_x + 10, 310, 130, 40)
}

# Fonction pour charger les sons en fonction de l'instrument
def load_sounds(instrument):
    global notes
    notes = {}
    keys_and_files = {
        pygame.K_q: ("Do.wav", "Do"),
        pygame.K_z: ("Do#.wav", "Do#"),
        pygame.K_s: ("Re.wav", "Re"),
        pygame.K_e: ("Re#.wav", "Re#"),
        pygame.K_d: ("Mi.wav", "Mi"),
        pygame.K_f: ("Fa.wav", "Fa"),
        pygame.K_t: ("Fa#.wav", "Fa#"),
        pygame.K_g: ("Sol.wav", "Sol"),
        pygame.K_y: ("Sol#.wav", "Sol#"),
        pygame.K_h: ("La.wav", "La"),
        pygame.K_u: ("La#.wav", "La#"),
        pygame.K_j: ("Si.wav", "Si"),
        pygame.K_k: ("do-high.wav", "do")
    }

    for key, (filename, note) in keys_and_files.items():
        filepath = os.path.join(sound_dir, instrument, filename)
        if os.path.exists(filepath):
            notes[key] = (pygame.mixer.Sound(filepath), note)
        else:
            print(f"File not found: {filepath}")

load_sounds(current_instrument)

# Définir les touches blanches et noires
white_keys = [pygame.K_q, pygame.K_s, pygame.K_d, pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_j, pygame.K_k]
black_keys = [pygame.K_z, pygame.K_e, pygame.K_t, pygame.K_y, pygame.K_u]
black_key_positions = [1, 2, 4, 5, 6]  # Positions relatives des touches noires

# Fonction pour détecter les clics de souris et jouer les notes correspondantes
def check_mouse_click():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    # Vérifier si le clic de souris est dans le cadre noir
    border_thickness = (width - 200) // 16
    if not pygame.Rect(border_thickness, border_thickness, width - 200 - 2 * border_thickness, height - 2 * border_thickness).collidepoint(mouse_x, mouse_y):
        return  # Inhibition du son sur le cadre noir
    
    # Vérifier si le clic de souris est dans une zone de touche noire
    white_key_width = (width - 200) // len(white_keys)
    black_key_width = white_key_width // 2
    black_key_height = height // 1.5
    for i, key in enumerate(black_keys):
        key_rect = pygame.Rect(black_key_positions[i] * white_key_width - black_key_width // 2, 0, black_key_width, black_key_height)
        if key_rect.collidepoint(mouse_x, mouse_y):
            notes[key][0].play()
            pressed_keys.add(key)
            pressed_mouse_keys.add(key)
            return  # Sortir de la fonction après avoir détecté une touche noire

    # Vérifier si le clic de souris est dans une zone de touche blanche
    for i, key in enumerate(white_keys):
        key_rect = pygame.Rect(i * white_key_width, 0, white_key_width, height)
        if key_rect.collidepoint(mouse_x, mouse_y):
            notes[key][0].play()
            pressed_keys.add(key)
            pressed_mouse_keys.add(key)

# Boucle principale
running = True
pressed_keys = set()
pressed_mouse_keys = set()

while running:
    window.fill(black)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in notes:
                notes[event.key][0].play()
                pressed_keys.add(event.key)
                if recording:
                    timestamp = pygame.time.get_ticks() - start_time
                    sequence.append((event.key, timestamp))
        if event.type == pygame.MOUSEBUTTONDOWN:  # Ajouter la vérification des clics de souris
            if record_button.collidepoint(event.pos):
                recording = not recording
                if recording:
                    sequence = []
                    start_time = pygame.time.get_ticks()
            elif play_button.collidepoint(event.pos):
                if sequence:
                    is_playing = True
                    play_index = 0
                    play_start_time = pygame.time.get_ticks()
            else:
                check_mouse_click()
        if event.type == pygame.KEYUP:
            if event.key in pressed_keys:
                pressed_keys.remove(event.key)
        if event.type == pygame.MOUSEBUTTONUP:  # Libérer les touches cliquées avec la souris
            pressed_keys.difference_update(pressed_mouse_keys)
            pressed_mouse_keys.clear()
        if event.type == pygame.MOUSEBUTTONDOWN:
            for instrument, rect in instrument_buttons.items():
                if rect.collidepoint(event.pos):
                    current_instrument = instrument.lower()
                    load_sounds(current_instrument)

    # Gérer la lecture des notes enregistrées
    if is_playing and play_index < len(sequence):
        key, timestamp = sequence[play_index]
        current_time = pygame.time.get_ticks() - play_start_time
        if current_time >= timestamp:
            notes[key][0].play()
            play_index += 1
        if play_index >= len(sequence):
            is_playing = False

    # Dessiner les touches blanches du piano
    white_key_width = (width - 200) // len(white_keys)
    for i, key in enumerate(white_keys):
        rect = pygame.Rect(i * white_key_width, 0, white_key_width - 2, height)
        if key in pressed_keys:
            pygame.draw.rect(window, grey, rect)  # Couleur différente si la touche est jouée
        else:
            pygame.draw.rect(window, white, rect)
        pygame.draw.rect(window, black, rect, 1)

        # Ajouter le nom de la note sur la touche si elle est pressée
        if key in pressed_keys:
            note_text = font.render(notes[key][1], True, black)
            text_rect = note_text.get_rect(center=rect.center)
            window.blit(note_text, text_rect)
    
    # Dessiner les touches noires du piano
    black_key_width = white_key_width // 2
    black_key_height = height // 1.5
    for i, key in enumerate(black_keys):
        rect = pygame.Rect(black_key_positions[i] * white_key_width - black_key_width // 2, 0, black_key_width - 2, black_key_height)
        if key in pressed_keys:
            pygame.draw.rect(window, dark_grey, rect)  # Couleur différente si la touche est jouée
        else:
            pygame.draw.rect(window, black, rect)
        
        # Ajouter le nom de la note sur la touche noire si elle est pressée
        if key in pressed_keys:
            note_text = font.render(notes[key][1], True, white)
            text_rect = note_text.get_rect(center=(rect.centerx, rect.centery - 10))
            window.blit(note_text, text_rect)

    # Dessiner la bordure noire autour du piano
    border_thickness = black_key_width // 2
    pygame.draw.rect(window, black, (0, 0, width - 200, height), border_thickness)

    # Dessiner les boutons sur le côté
    pygame.draw.rect(window, blue if recording else grey, record_button)
    pygame.draw.rect(window, grey, play_button)
    window.blit(font.render("Record", True, white), (record_button.x + (record_button.width - font.size("Record")[0]) // 2, record_button.y + (record_button.height - font.size("Record")[1]) // 2))
    window.blit(font.render("Play", True, black), (play_button.x + (play_button.width - font.size("Play")[0]) // 2, play_button.y + (play_button.height - font.size("Play")[1]) // 2))

    for instrument, rect in instrument_buttons.items():
        pygame.draw.rect(window, grey if current_instrument == instrument.lower() else white, rect)
        window.blit(font.render(instrument, True, black), (rect.x + (rect.width - font.size(instrument)[0]) // 2, rect.y + (rect.height - font.size(instrument)[1]) // 2))

    pygame.display.flip()

pygame.quit()
sys.exit()
