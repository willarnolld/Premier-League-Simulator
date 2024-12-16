import itertools
import numpy as np
import pandas as pd
import pygame


class Button:
    def __init__(self, text, pos, font, color= (255,255,255), bg=pygame.SRCALPHA, size = 20):
        self.x, self.y = pos
        self.font = pygame.font.Font(font, size)
        self.color = color
        self.change_text(text, bg)

    def change_text(self, text, bg=None):
        self.text = self.font.render(text, True, pygame.Color(self.color))
        self.size = self.text.get_size()
        self.surface = pygame.Surface(self.size, pygame.SRCALPHA)  # Use SRCALPHA for transparency
        if bg:
            self.surface.fill(pygame.Color(bg))
        else:
            self.surface.fill((0, 0, 0, 0))  # Fill with a fully transparent color
        self.surface.blit(self.text, (0, 0))
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])
        if bg:
            self.surface.set_colorkey(pygame.Color(bg))

    def show(self, screen):
        screen.blit(self.surface, (self.x, self.y))

    def click(self, event):
        x, y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(x, y):
                    return True
        return False



def generate_fixtures(teams):
    fixtures = []
    for i in range(2):
        for match in itertools.combinations(teams, 2):
            fixtures.append(match)
    return fixtures


def simulate_match(team1, team2, team_data):
    team1_stats = team_data[team_data['Squad'] == team1].iloc[0]
    team2_stats = team_data[team_data['Squad'] == team2].iloc[0]

    team1_goals_for = team1_stats['GF'] / team1_stats['MP']
    team2_goals_against = team2_stats['GA'] / team2_stats['MP']
    team2_goals_for = team2_stats['GF'] / team2_stats['MP']
    team1_goals_against = team1_stats['GA'] / team1_stats['MP']

    team1_expected_goals = (team1_goals_for + team2_goals_against) / 2
    team2_expected_goals = (team2_goals_for + team1_goals_against) / 2

    team1_score = np.random.poisson(team1_expected_goals)
    team2_score = np.random.poisson(team2_expected_goals)

    if team1_score > team2_score:
        return team1, team1_score, team2_score, 3, 0
    elif team2_score > team1_score:
        return team2, team1_score, team2_score, 0, 3
    else:
        return None, team1_score, team2_score, 1, 1


def simulate_season(team_data):
    teams = team_data['Squad'].tolist()
    fixtures = generate_fixtures(teams)

    standings = {}
    match_records = {team: [] for team in teams}
    for team in teams:
        standings[team] = {
            'P': 0, 'W': 0, 'D': 0, 'L': 0,
            'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0
        }

    for match in fixtures:
        team1, team2 = match
        winner, team1_score, team2_score, team1_points, team2_points = simulate_match(team1, team2, team_data)

        if winner == team1:
            result_team1 = 'Win'
        else:
            if winner == team2:
                result_team1 = 'Loss'
            else:
                result_team1 = 'Draw'

        team1_record = {
            'Opponent': team2,
            'Score': f'{team1_score}-{team2_score}',
            'Result': result_team1
        }

        if winner == team2:
            result_team2 = 'Win'
        else:
            if winner == team1:
                result_team2 = 'Loss'
            else:
                result_team2 = 'Draw'

        team2_record = {
            'Opponent': team1,
            'Score': f'{team2_score}-{team1_score}',
            'Result': result_team2
        }

        match_records[team1].append(team1_record)
        match_records[team2].append(team2_record)

        standings[team1]['P'] += 1
        standings[team1]['GF'] += team1_score
        standings[team1]['GA'] += team2_score
        standings[team1]['GD'] += team1_score - team2_score
        standings[team1]['Pts'] += team1_points
        standings[team1]['W'] += 1 if winner == team1 else 0
        standings[team1]['D'] += 1 if winner is None else 0
        standings[team1]['L'] += 1 if winner == team2 else 0

        standings[team2]['P'] += 1
        standings[team2]['GF'] += team2_score
        standings[team2]['GA'] += team1_score
        standings[team2]['GD'] += team2_score - team1_score
        standings[team2]['Pts'] += team2_points
        standings[team2]['W'] += 1 if winner == team2 else 0
        standings[team2]['D'] += 1 if winner is None else 0
        standings[team2]['L'] += 1 if winner == team1 else 0

    standings_df = pd.DataFrame.from_dict(standings, orient='index')
    standings_df = standings_df.sort_values(by=['Pts', 'GD', 'GF'], ascending=False)
    return standings_df, match_records


def render_table(screen, table, team_buttons, back_button, start_y=110, scroll_offset=0):
    screen.fill(PURPLE)  # Set background to purple
    plbg = pygame.image.load("plbg.png")
    plbg = pygame.transform.scale(plbg, (960, 540))
    screen.blit(plbg, (0, 0))

    y_offset = start_y + scroll_offset

    screen.blit(pl_logo, (10, y_offset - 110))  # Top-right corner, with 10px padding
    screen.blit(pl_logo, (SCREEN_WIDTH - 100, y_offset - 110))  # Top-right corner, with 10px padding

    # Render the title
    title_text = titFONT.render("Premier League Season Standings", True, GOLD)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 10 + scroll_offset))

    # Render the headers
    headers = ["Team", "P", "W", "D", "L", "GF", "GA", "GD", "Pts"]
    header_x = [60, 340, 400, 460, 510, 560, 620, 680, 740, 800]
    for i, header in enumerate(headers):
        header_surface = FONT.render(header, True, WHITE)
        screen.blit(header_surface, (header_x[i], y_offset))

    y_offset = start_y + 30 + scroll_offset  # Adjust for scroll offset

    for index, (team, stats) in enumerate(table.iterrows()):
        if index < 4:
            row_color = GREEN  # Champions League spots
        elif index >= len(table) - 3:
            row_color = RED  # Relegation zone
        else:
            row_color = GRAY if index % 2 == 0 else WHITE

        # Draw a rounded rectangle for each row
        pygame.draw.rect(screen, row_color, (50, y_offset, SCREEN_WIDTH - 100, 30), 0, 5)

        # Create button for each team
        button = Button(team, (60, y_offset + 5), "PLFONT.otf", BLACK)
        team_buttons[team] = button
        button.show(screen)

        # Render statistics
        row_text = [
            str(stats['P']), str(stats['W']), str(stats['D']),
            str(stats['L']), str(stats['GF']), str(stats['GA']),
            str(stats['GD']), str(stats['Pts'])
        ]
        for i, text in enumerate(row_text):
            row_surface = FONT.render(text, True, BLACK)
            screen.blit(row_surface, (header_x[i + 1], y_offset + 5))

        y_offset += 35
    back_button.show(screen)


def render_team_stats(screen, team, records, back_button, start_y=200, scroll_offset=0):
    screen.fill(PURPLE)
    plbg = pygame.image.load("plbg.png")
    plbg = pygame.transform.scale(plbg, (960, 540))
    screen.blit(plbg, (0, 0))

    title_text = titFONT.render(f"{team} Season Stats", True, GOLD)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 10+scroll_offset))

    team_logo = pygame.image.load(f"{team}.png")

    if team in ["Manchester Utd","Liverpool",'Arsenal',"Chelsea",'Everton','Ipswich Town']:
        team_logo = pygame.transform.scale(team_logo, ((team_logo.get_width())/2, team_logo.get_height()/2))
    else:
        team_logo = pygame.transform.scale(team_logo, (team_logo.get_width(), team_logo.get_height()))
    screen.blit(team_logo, (SCREEN_WIDTH -150 - team_logo.get_width() // 2, 60))

    back_button.show(screen)

    y_offset = start_y + scroll_offset
    headers = ["Opponent", "Score", "Result"]
    header_x = [60, 400, 600]


    for i, header in enumerate(headers):
        header_surface = FONT.render(header, True, BLUE)
        screen.blit(header_surface, (header_x[i], y_offset))

    y_offset += 40

    for record in records:
        row_text = [record["Opponent"], record["Score"], record["Result"]]
        for i, text in enumerate(row_text):
            if text == "Win":
                color = GREEN
            elif text == "Loss":
                color = RED
            else:
                color = WHITE
            row_surface = FONT.render(text, True, color)
            screen.blit(row_surface, (header_x[i], y_offset))
        y_offset += 30

def render_sim_state(screen, sim_button, simbox, quit_box, view_button, simulation_complete):
    screen.fill(PURPLE)
    plbg = pygame.image.load("plbg.png")
    plbg= pygame.transform.scale(plbg,(960,540))
    screen.blit(plbg, (0, 0))

    title = titFONT.render("barclays presents:", True, GOLD)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 10))
    league = bigFONT.render("the premier league", True, GOLD)
    screen.blit(league, (SCREEN_WIDTH // 2 - league.get_width() // 2, 50))
    pygame.draw.rect(screen, DPURPLE, simbox, 0, 100)
    pygame.draw.rect(screen, DPURPLE, quit_box, 0, 200)

    screen.blit(lion, (SCREEN_WIDTH //2 - lion.get_width()//2, 130))

    quit_button.show(screen)
    sim_button.show(screen)

    if simulation_complete:
        view_button.show(screen)


pygame.init()

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Premier League Simulation")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (4, 245, 255)
RED = (233, 0, 82)
GREEN = (0, 255, 133)
PURPLE = (56, 0, 60)
DPURPLE = (36, 0, 40)
GOLD = (255, 215, 0)

FONT = pygame.font.Font("PLFONT.otf", 20)
titFONT = pygame.font.Font("PLFONT.otf", 40)
bigFONT = pygame.font.Font("PLFONT.otf", 80)

pl_logo = pygame.image.load("PLLOGO.png")
pl_logo = pygame.transform.scale(pl_logo, (100, 100))
lion = pygame.image.load("lion.png")
lion = pygame.transform.scale(lion, (lion.get_width()-20, lion.get_height()-20))

team_buttons = {}
back_button = Button("Back", (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50), "PLFONT.otf", WHITE)
sim_button = Button("Run New Simulation", (SCREEN_WIDTH//2-175, 385), "PLFONT.otf", RED, size = 35)
view_button = Button("View current", (SCREEN_WIDTH - 175, SCREEN_HEIGHT - 50), "PLFONT.otf", BLUE)
quit_button = Button("Quit", (25,SCREEN_HEIGHT-30),"PLFONT.otf",RED)

simbox = pygame.rect.Rect(SCREEN_WIDTH // 2 - 200, 375, 400, 50)
quitbox = pygame.rect.Rect(10, SCREEN_HEIGHT-35, 75, 25)

scroll_offset = 0
max_scroll = -(max(0, (20) * 35 - (SCREEN_HEIGHT - 150)))
team_scroll_offset = 0
team_max_scroll = 0

simulation_complete = False

gamestage = 0
current_team = None

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                if gamestage == 2:
                    team_scroll_offset = min(team_scroll_offset + 30, 0)
                else: scroll_offset = min(scroll_offset + 30, 0)
            elif event.button == 5:
                if gamestage == 2:
                    team_scroll_offset = max(team_scroll_offset - 30, team_max_scroll)
                elif gamestage == 1:
                    scroll_offset = max(scroll_offset - 30, max_scroll)
                else:
                    scroll_offset = max(scroll_offset - 30, max_scroll)

        if gamestage == 0:
            if sim_button.click(event):
                data = pd.read_csv('PLdata.csv')
                final_table, match_records = simulate_season(data)
                simulation_complete = True
            if view_button.click(event) and simulation_complete:
                gamestage = 1
            if quit_button.click(event):
                running = False
            if sim_button.click(event) and simulation_complete:
                data = pd.read_csv('PLdata.csv')
                final_table, match_records = simulate_season(data)
                gamestage = 1

        elif gamestage == 2:
            if back_button.click(event):
                gamestage = 1
        else:
            for team, button in team_buttons.items():
                if button.click(event):
                    gamestage = 2
                    current_team = team
                    team_scroll_offset = 0
                    team_max_scroll = -(max(0, len(match_records[team]) * 30 - (SCREEN_HEIGHT - 240)))
                    break
            if back_button2.click(event):
                gamestage = 0


    if gamestage == 0:
        render_sim_state(screen, sim_button, quitbox, simbox, view_button, simulation_complete)
        pygame.display.flip()

    elif gamestage == 1:
        back_button2 = Button("Back", (150, 75 + scroll_offset), "PLFONT.otf", RED)
        render_table(screen, final_table, team_buttons, back_button2, scroll_offset=scroll_offset)

    elif gamestage == 2:
        render_team_stats(screen, current_team, match_records[current_team], back_button, scroll_offset=team_scroll_offset)
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
