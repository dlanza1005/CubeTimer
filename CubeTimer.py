# David Lanza
# 12/9/25
# Rubiks Cube Timer Program Requirements:
#   -be a very clear graph that is very clear that it is a graph
#   -must look good!
#   x-must be clear numerical denominations on Y axis
#   x-show scatterplot [future: other plot types]
#   x-keep constant Y range
#   x-adjustable window size
#   wtf else?
#
# fix/add to existing version:
#   -backspace should delete characters while held down, rather than once per button press.
#   -mouse over a datapoint should show the time and the comment.
#   x-show last time on the timer display rather than getting rid of it
#   -should be able to delete solves
#   -move countdown functionality into the timer class?

# 12-15-25
#   -when typing a comment, clicking the plot area should give program attention back to the timer.
#   -wrap text in a comment. Change the size of the plot area to accommodate, perhaps?
#   -mousing over the comp_ao5 and avg of 20 should show name of the stat and value, as well as highlight the points that it is averaging (?)
#   -need an x axis label!!
#   -maybe innstead of deleting data points, put a flag for "deleted" and if it is deleted, it could be undone..
#   -the comment field should clear itself after each solve.
#   -tailor the size of the save button to the size of the text object. Also make sure it is drawn before the timer itself so the timer is on top.
#   -backspace should work while being held down not just when pressed…


import pygame
import sys
import time
import math
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.txt")

# Pygame setup
pygame.init()

# Constants
WHITE = (255, 255, 255)
DARK = (50, 50, 50)
RED = (200, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0,255,0)
ORANGE1 = (230,80,0)
ORANGE2 = (230,128,0)
ORANGE3 = (230,158,0)
BG_COLOR = ORANGE3
FG_COLOR = ORANGE2
POINT_COLOR = WHITE
AVG_COLOR = ORANGE3
TIMER_FONT = pygame.font.SysFont('Courier', 60, bold = True)
LABEL_FONT = pygame.font.SysFont('Courier', 20, bold = True)
BUTTON_FONT = pygame.font.SysFont('Courier', 20, bold = True)
INPUT_FONT = pygame.font.SysFont('Courier', 20, bold = True)

# Fixed heights for timer and comment boxes
TIMER_HEIGHT = 100 # pixels
SCATTER_HEIGHT = .65 # %
HISTOGRAM_HEIGHT = .35 # %
COMMENT_HEIGHT = 40 # pixels
BORDER_RADIUS = 10
outer_margin = 10  # pixels

# Initialize screen (with resizable window)
screen = pygame.display.set_mode((600, 700), pygame.RESIZABLE)
pygame.display.set_caption("Rubik's Cube Timer")

scatter_plot_surface = None
histogram_surface = None
last_scatter_size = (0, 0)
last_session_list = []
hovered_point_index = None
scatter_point_hits = []

# Timer class
class CubeTimer:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.running = False

    def start(self):
        if not self.running:
            self.start_time = time.time()
            self.running = True

    def stop(self):
        if self.running:
            self.end_time = time.time()
            self.running = False
            return self.get_time()

    def reset(self):
        self.start_time = None
        self.end_time = None
        self.running = False

    def get_time(self):
        if self.running:
            return round(time.time() - self.start_time, 2)
        elif self.start_time and self.end_time:
            return round(self.end_time - self.start_time, 2)
        else:
            return 0.0


###################################################################################################
class PlotContext:
    def __init__(self, rect, min_time, max_time, count):
        self.rect = rect
        self.min_time = min_time
        self.max_time = max_time
        self.range = max_time - min_time or 1
        self.border = outer_margin
        self.width = rect.width - 2*self.border
        self.height = rect.height - 2*self.border
        self.count = max(count, 2)

    def x(self, i):
        return self.border + int(i * self.width / (self.count - 1))

    def y(self, value):
        return self.border + int((1 - (value - self.min_time) / self.range) * self.height)


##################################################################################################
# Statistical functions

def rolling_mean_std(values, window):
    means, stds = [], []
    for i in range(len(values)):
        start = max(0, i - window)
        end = min(len(values), i + window + 1)
        w = values[start:end]
        mean = sum(w) / len(w)
        var = sum((x - mean)**2 for x in w) / len(w)
        means.append(mean)
        stds.append(math.sqrt(var))
    return means, stds

def ao5(values):
    out = []
    for i in range(4, len(values)):
        w = values[i-4:i+1]
        out.append(((sum(w) - min(w) - max(w)) / 3))
    return out

##################################################################################################
# Drawing functions

def draw_grid(surface, ctx, step=5):
    grid_color = ORANGE3 #WHITE # (50, 50, 50)
    label_color = ORANGE3 #WHITE # (120, 120, 120)

    for t in range(int(ctx.min_time), int(ctx.max_time) + 1, step):
        y = ctx.y(t)

        # Horizontal grid line
        pygame.draw.line(surface, grid_color, (ctx.border*3, y), (ctx.border + ctx.width, y), 2)

        # Y-axis label (left side)
        label = LABEL_FONT.render(str(t), True, label_color)
        label_rect = label.get_rect( right=ctx.border+15, centery=y)
        surface.blit(label, label_rect)


# def draw_points(surface, ctx, values):
#     for i, v in enumerate(values):
#         pygame.draw.circle(surface, WHITE,(ctx.x(i), ctx.y(v)), 4)
def draw_points(surface, ctx, values):
    global scatter_point_hits
    scatter_point_hits = []

    radius = 5
    hit_radius = radius*2  # easier to click

    for i, v in enumerate(values):
        x = ctx.x(i)
        y = ctx.y(v)

        pygame.draw.circle(surface, WHITE, (x, y), radius)

        # store clickable region
        hitbox = pygame.Rect( x - hit_radius, y - hit_radius, hit_radius * 2, hit_radius * 2)
        scatter_point_hits.append((i, hitbox))


def draw_std_boxes(surface, ctx, values, window):
    for i in range(0, len(values), window):
        w = values[max(0,i-window):i]
        if not w: continue
        mean = sum(w)/len(w)
        std = math.sqrt(sum((x-mean)**2 for x in w)/len(w))

        x1 = ctx.x(max(0,i-window))+1
        x2 = ctx.x(i)-1
        y1 = ctx.y(mean + std)
        y2 = ctx.y(mean - std)

        pygame.draw.rect(surface, AVG_COLOR,(x1, y1, x2-x1, y2-y1), 0, border_radius=min(math.ceil((y2-y1)/2),10))


def draw_competition_ao5(surface, ctx, ao5_vals):
    points = []
    for i, v in enumerate(ao5_vals):
        points.append((ctx.x(i+4), ctx.y(v)))
        pygame.draw.circle(surface, ORANGE1,(ctx.x(i+4), ctx.y(v)), 5)
    if len(points)>1:
        pygame.draw.lines(surface,ORANGE1,False,points,3)


def draw():
    pass


def draw():
    pass

def draw_tooltip(screen, pos, text_lines):
    padding = 6
    line_height = 18

    rendered = [LABEL_FONT.render(t, True, WHITE) for t in text_lines]

    width = max(r.get_width() for r in rendered) + padding * 2
    height = len(rendered) * line_height + padding * 2

    x, y = pos
    x += 12  # offset from cursor
    y += 12

    # Keep tooltip on screen
    screen_rect = screen.get_rect()
    if x + width > screen_rect.right:
        x -= width
    if y + height > screen_rect.bottom:
        y -= height

    bg_rect = pygame.Rect(x, y, width, height)

    pygame.draw.rect(screen, ORANGE1, bg_rect)
    pygame.draw.rect(screen, ORANGE3, bg_rect, 2)

    for i, surf in enumerate(rendered):
        screen.blit( surf, (x + padding, y + padding + i * line_height))

######################################################################################################################

def draw_scatterplot_cached(screen, scatter_rect, session_list):
    global scatter_plot_surface, last_scatter_size, last_session_list
    # Check if we need to rebuild the scatterplot surface
    if (scatter_plot_surface is None or scatter_rect.size != last_scatter_size or session_list != last_session_list):
        print("Rebuilding scatterplot surface")
        scatter_plot_surface = pygame.Surface(scatter_rect.size)
        scatter_plot_surface.fill(FG_COLOR)  # Fill with black or another background

        solve_times = [time for _, time, _ in session_list]
        ctx = PlotContext(scatter_rect, 0, 30, len(solve_times))

        draw_grid(scatter_plot_surface, ctx)
        draw_std_boxes(scatter_plot_surface, ctx, solve_times, window=10)
        draw_points(scatter_plot_surface, ctx, solve_times)
        draw_competition_ao5(scatter_plot_surface, ctx, ao5(solve_times))

        last_scatter_size = scatter_rect.size
        last_session_list = list(session_list)

    # Blit the cached scatterplot onto the screen
    screen.blit(scatter_plot_surface, scatter_rect.topleft)

######################################################################################################################

# Timer instance
timer = CubeTimer()
countdown = 15
countdown_started = False
countdown_start_time = None
timer_bg_color = FG_COLOR
timer_running = False
countdown_time = countdown

# Session list to store times
session_list = []
#####################################################
#####################################################

def load_session_data(filepath):
    session_list = []
    if not os.path.exists(filepath):
        print("doesnt exist")
        return session_list
    with open(filepath, "r") as f:
        print("did exist")
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                stuff = line.split(",", 2)
                timestamp = stuff[0]
                duration = stuff[1]
                comment = stuff[2]
                session_list.append((timestamp, float(duration), comment))
            except ValueError:
                print("line skipped!")
                continue
    return session_list

# last_session_list = load_session_data(DATA_FILE)
# session_list = last_session_list
#print(session_list)
#####################################################
#####################################################

# User comment
user_comment = ""

# Get screen size for dynamic layout
screen_width, screen_height = screen.get_size()

#####################################################
# Calculate scatter plot height to fill the remaining space
scatter_rect_height = screen_height - TIMER_HEIGHT - COMMENT_HEIGHT - 4 * outer_margin

# Define rectangles
timer_rect = pygame.Rect(outer_margin, outer_margin, screen_width - 2 * outer_margin, TIMER_HEIGHT)
scatter_rect = pygame.Rect(outer_margin, timer_rect.bottom + outer_margin, screen_width - 2 * outer_margin, scatter_rect_height)
comment_rect = pygame.Rect(outer_margin, scatter_rect.bottom + outer_margin, screen_width - 2 * outer_margin, COMMENT_HEIGHT)
save_button_rect = pygame.Rect(timer_rect.width - 140 + outer_margin, timer_rect.bottom - 40, 140, 40)

def update_sections():
    # Get screen size for dynamic layout
    screen_width, screen_height = screen.get_size()

    # Calculate scatter plot height to fill the remaining space
    scatter_rect_height = screen_height - TIMER_HEIGHT - COMMENT_HEIGHT - 4 * outer_margin

    # Define rectangles
    timer_rect = pygame.Rect(outer_margin, outer_margin, screen_width - 2 * outer_margin, TIMER_HEIGHT)
    scatter_rect = pygame.Rect(outer_margin, timer_rect.bottom + outer_margin, screen_width - 2 * outer_margin, scatter_rect_height)
    comment_rect = pygame.Rect(outer_margin, scatter_rect.bottom + outer_margin, screen_width - 2 * outer_margin, COMMENT_HEIGHT)
    save_button_rect = pygame.Rect(timer_rect.width - 140 + outer_margin, timer_rect.bottom - 40, 140, 40)
    return timer_rect, scatter_rect, comment_rect, save_button_rect

timer_rect, scatter_rect, comment_rect, save_button_rect = update_sections()
#####################################################
# tryinng to remove outer_margin from this.
# # Calculate scatter plot height to fill the remaining space
# scatter_rect_height = screen_height - TIMER_HEIGHT - COMMENT_HEIGHT

# # Define rectangles
# timer_rect = pygame.Rect(0, 0, screen_width, TIMER_HEIGHT)
# scatter_rect = pygame.Rect(0, timer_rect.bottom, screen_width, scatter_rect_height)
# comment_rect = pygame.Rect(0, scatter_rect.bottom, screen_width, COMMENT_HEIGHT)
# save_button_rect = pygame.Rect(timer_rect.width - 140, timer_rect.bottom - 40, 140, 40)

# def update_sections():
#     # Get screen size for dynamic layout
#     screen_width, screen_height = screen.get_size()

#     # Calculate scatter plot height to fill the remaining space
#     scatter_rect_height = screen_height - TIMER_HEIGHT - COMMENT_HEIGHT

#     # Define rectangles
#     timer_rect = pygame.Rect(0, 0, screen_width, TIMER_HEIGHT)
#     timer_rect = timer_rect.inflate(-outer_margin,-outer_margin)
#     scatter_rect = pygame.Rect(0, timer_rect.bottom, screen_width, scatter_rect_height)
#     scatter_rect = scatter_rect.inflate(-outer_margin,-outer_margin)
#     comment_rect = pygame.Rect(0, scatter_rect.bottom, screen_width, COMMENT_HEIGHT)
#     comment_rect = comment_rect.inflate(-outer_margin,-outer_margin)
#     save_button_rect = pygame.Rect(timer_rect.width - 140, timer_rect.bottom - 40, 140, 40)
#     save_button_rect = save_button_rect.inflate(-outer_margin,-outer_margin)
#     return timer_rect, scatter_rect, comment_rect, save_button_rect

# timer_rect, scatter_rect, comment_rect, save_button_rect = update_sections()
#####################################################

# Main loop
running = True
input_active = False
while running:
    timer_rect, scatter_rect, comment_rect, save_button_rect = update_sections()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not input_active:
                if not countdown_started and not timer_running:
                    countdown_started = True
                    countdown_start_time = time.time()
                elif countdown_started and not timer_running:
                    timer.reset()
                    timer.start()
                    timer_running = True
                elif timer_running:
                    elapsed_time = timer.stop()
                    start_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timer.start_time))
                    session_list.append((start_timestamp, elapsed_time, user_comment))
                    print(f"Duration: {elapsed_time}, Comment: {user_comment}")
                    countdown_started = False
                    timer_running = False
                    countdown_time = countdown
                    timer_bg_color = FG_COLOR
            elif input_active:
                if event.key == pygame.K_BACKSPACE:
                    user_comment = user_comment[:-1]
                else:
                    user_comment += event.unicode
        elif event.type == pygame.MOUSEMOTION:
            hovered_point_index = None
            if scatter_rect.collidepoint(event.pos):
                local_pos = (event.pos[0] - scatter_rect.x, event.pos[1] - scatter_rect.y)
                for i, hitbox in scatter_point_hits:
                    if hitbox.collidepoint(local_pos):
                        hovered_point_index = i
                        break
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if save_button_rect.collidepoint(event.pos):
                with open(DATA_FILE, "a") as f:
                    for timestamp, duration, comment in session_list:
                        f.write(f"{timestamp}, {duration}, {comment}\n")
                session_list.clear()  # Clear the session list after saving
            elif comment_rect.collidepoint(event.pos):
                input_active = True
            elif scatter_rect.collidepoint(event.pos):
                local_x = event.pos[0] - scatter_rect.x
                local_y = event.pos[1] - scatter_rect.y
                for i, hitbox in scatter_point_hits:
                    if hitbox.collidepoint((local_x, local_y)):
                        del session_list[i]
                        hovered_point_index = None
                        break
            else:
                input_active = False
        

    # Handle countdown
    if countdown_started and not timer_running:
        time_passed = time.time() - countdown_start_time
        countdown_time = countdown - time_passed
        if countdown_time <= 0:
            timer_bg_color = RED

    
    # Clear the screen by filling it with the background color
    screen.fill(BG_COLOR)

    # Draw the outer rectangle for the timer section
    pygame.draw.rect(screen, BG_COLOR, timer_rect, border_radius = BORDER_RADIUS)

    # Initialize time_text with a default value
    if len(session_list)>0:
        time_text = TIMER_FONT.render(f"{session_list[-1][1]}", True, WHITE)  # when idle, show last time
    else:
        time_text = TIMER_FONT.render("0.00", True, WHITE)  # Default empty text

    # Update time_text based on state
    if countdown_started and not timer_running:
        display_time = int(countdown_time) if countdown_time > 0 else -int(abs(countdown_time))
        time_text = TIMER_FONT.render(f"{display_time}", True, WHITE)
    elif timer_running:
        time_text = TIMER_FONT.render(f"{timer.get_time()}", True, WHITE)

    # Center the text within the timer rectangle
    text_rect = time_text.get_rect(center=timer_rect.center)
    screen.blit(time_text, text_rect)

    # Draw save button at the bottom right inside the timer rectangle
    pygame.draw.rect(screen, FG_COLOR, save_button_rect,border_radius = BORDER_RADIUS)
    button_text = BUTTON_FONT.render(f"Save ({len(session_list)})", True, WHITE)
    screen.blit(button_text, (save_button_rect.x + 15, save_button_rect.y + 10))

    # Draw the outer rectangle for the scatter plot section
    pygame.draw.rect(screen, FG_COLOR, scatter_rect, border_radius = BORDER_RADIUS)

    # Draw scatter plot inside the scatter_rect
    shrunken_rect = scatter_rect.inflate(-outer_margin, -outer_margin)
    draw_scatterplot_cached(screen, shrunken_rect, session_list)

    # Draw the outer rectangle for the comment section
    pygame.draw.rect(screen, BG_COLOR, comment_rect, border_radius = BORDER_RADIUS)

    # Render the comment text
    comment_text = INPUT_FONT.render(user_comment, True, WHITE)
    screen.blit(comment_text, (comment_rect.x + 10, comment_rect.y + 10))

    if hovered_point_index is not None and 0 <= hovered_point_index < len(session_list):
        timestamp, duration, comment = session_list[hovered_point_index]
        lines = [f"{duration:.2f}"]
        if comment.strip():
            lines.append(comment)
        draw_tooltip(screen, pygame.mouse.get_pos(), lines)


    pygame.display.flip()

pygame.quit()
sys.exit()
