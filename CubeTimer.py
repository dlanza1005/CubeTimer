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
#   x-when typing a comment, clicking the plot area should give program attention back to the timer.
#   x-wrap text in a comment. Change the size of the plot area to accommodate, perhaps?
#   -mousing over the comp_ao5 and avg of 20 should show name of the stat and value, as well as highlight the points that it is averaging (?)
#   -need an x axis label!!
#   -maybe innstead of deleting data points, put a flag for "deleted" and if it is deleted, it could be undone..
#   x-the comment field should clear itself after each solve.
#   x-tailor the size of the save button to the size of the text object. 
#   x-make sure save button is drawn before the timer itself so the timer is on top.
#   -backspace should work while being held down not just when pressed…

# 1-3-26
#   -tried using this for 4x4 solve. cannot delete solves if the datapoint is off the y axis scale.

# 1-15-26:
# rubiks cube program changes:
#   -rectangle mouseover is broken
#   -make deleting solves safer
#   -changeable range for Y axis
#   -fix highlighting and mouseover data (maybe in the future)
#   -add +2 and DNF buttons?
#   -see comments on mouseover. edit comments on mouseover.



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
save_button_text = BUTTON_FONT.render(f"Save", True, WHITE)
INPUT_FONT = pygame.font.SysFont('Courier', 20, bold = True)
comment_text = INPUT_FONT.render(f".", True, WHITE)

# Fixed heights for timer and comment boxes
TIMER_HEIGHT = 100 # pixels
TIMER_WIDTH = 1 # %
SCATTER_WIDTH = 1 # %
SCATTER_HEIGHT = .65 # %
HISTOGRAM_WIDTH = 1 # %
HISTOGRAM_HEIGHT = .35 # %
COMMENT_HEIGHT = 40 # pixels
BORDER_RADIUS = 10 # pixels
outer_margin = 10  # pixels

# Initialize screen (with resizable window)
screen = pygame.display.set_mode((600, 700), pygame.RESIZABLE)
pygame.display.set_caption("Rubik's Cube Timer")

scatter_plot_surface = None
histogram_surface = None
last_scatter_size = (0, 0)
last_session_list = []
hovered_point_index = None
scatter_point_hitboxes = [] # (index, hitbox)
ao5_hitboxes = [] # (index, hitbox)
a10_hitboxes = [] # (index, hitbox)
hover_targets = []
highlighted_a10s = []
highlighted_ao5s = []
highlighted_points = []


# Timer class
class CubeTimer:
    def __init__(self):
        self.countdown_duration = 15  # seconds
        self.countdown_start_time = None
        self.start_time = None
        self.end_time = None
        self.state = "RESTING"  # RESTING, COUNTDOWN, SOLVING

    def space_pressed(self):
        if self.state == "RESTING":
            self.state = "COUNTDOWN"
            self.countdown_start_time = time.time()  # Start countdown timer
        elif self.state == "COUNTDOWN":
            self.state = "SOLVING"
            self.start_time = time.time()  # Start solve timer
        elif self.state == "SOLVING":
            self.state = "RESTING"
            self.end_time = time.time()
            return [time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_time)), round(self.end_time-self.start_time, 2)]
        return None

    def get_display_time(self):
        if self.state == "COUNTDOWN":
            return int(round(self.countdown_duration - (time.time() - self.countdown_start_time), 0))
        elif self.state == "SOLVING":
            return f"{time.time() - self.start_time:.2f}"
        elif self.state == "RESTING" and self.start_time and self.end_time:
            return f"{self.end_time - self.start_time:.2f}"
        else:
            return "0.00"

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


def draw_points(surface, ctx, values):
    global scatter_point_hitboxes
    scatter_point_hitboxes = []
    #global hover_targets
    global highlighted_points

    radius = 5
    hit_radius = radius*2  # easier to click

    for i, v in enumerate(values):
        x = ctx.x(i)
        y = ctx.y(v)

        # store clickable region
        hitbox = pygame.Rect( x - radius, y - radius, hit_radius * 2, hit_radius * 2)
        scatter_point_hitboxes.append((i, hitbox, v)) # remove?
        #hover_targets.append(("point", 0, i, hitbox,"tooltip", [i])) # type, priority, index, hitbox, tooltip, highlight
        if (i, hitbox, v) in highlighted_points:
            pygame.draw.circle(surface, BLACK, (x, y), radius+2)
        pygame.draw.circle(surface, WHITE, (x, y), radius)


def draw_highlighted_point(surface, ctx, index, value):
    x = ctx.x(index)
    y = ctx.y(value)
    radius = 5
    pygame.draw.circle(surface, BLACK, (x, y), radius+1)
    pygame.draw.circle(surface, WHITE, (x, y), radius)

def draw_std_boxes(surface, ctx, values, window):
    global a10_hitboxes
    a10_hitboxes = []
    #hover_boxes = []
    #global hover_targets
    global highlighted_a10s

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
        # store clickable region
        hitbox = pygame.Rect( x1, y1, x2-x1, x2-x1)
        a10_hitboxes.append((i, hitbox, mean, std))
        #hovered = False
        #hover_targets.append(("a10", 2, i, hitbox, "a10 tooltip", list(range(max(0, i-window), i)))) # type, priority, index, hitbox, tooltip, highlight


def draw_competition_ao5(surface, ctx, ao5_vals):
    global ao5_hitboxes
    ao5_hitboxes = []
    # hover_ao5s = []
    #global hover_targets
    global highlighted_ao5s
    
    points = []
    radius = 5
    hit_radius = radius*2  # easier to click
    for i, v in enumerate(ao5_vals):
        x = ctx.x(i+4)
        y = ctx.y(v)
        points.append((x, y))
        
        # store clickable region
        hitbox = pygame.Rect( x - radius, y - radius, hit_radius * 2, hit_radius * 2)
        ao5_hitboxes.append((i, hitbox, v)) 
        #hover_targets.append(("ao5", 1, i, hitbox, "ao5 tooltip", list(range(i, i + 5)))) # type, priority, index, hitbox, tooltip, highlight
        if (i, hitbox, v) in highlighted_ao5s:
            pygame.draw.circle(surface, BLACK,(x, y), radius+2)
        pygame.draw.circle(surface, ORANGE1,(x, y), radius)
    if len(points)>1:
        pygame.draw.lines(surface,ORANGE1,False,points,3)


def draw():
    pass


def render_wrapped_text(text, font, color, max_width):
    words = text.split(" ")
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        test_width, _ = font.size(test_line)

        if test_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    line_surfaces = [font.render(line, True, color) for line in lines]
    line_height = font.get_linesize()

    total_height = line_height * len(line_surfaces)
    surface = pygame.Surface((max_width, total_height), pygame.SRCALPHA)
    y = 0
    for line_surf in line_surfaces:
        surface.blit(line_surf, (0, y))
        y += line_height
    return surface


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
    global scatter_plot_surface, last_scatter_size, last_session_list, mouse_hover_change
    # Check if we need to rebuild the scatterplot surface
    if (scatter_plot_surface is None or scatter_rect.size != last_scatter_size or session_list != last_session_list or mouse_hover_change): # or mouse moved
        print("Rebuilding scatterplot surface")
        scatter_plot_surface = pygame.Surface(scatter_rect.size)
        scatter_plot_surface.fill(FG_COLOR)  # Fill with black or another background

        solve_times = [time for _, time, _ in session_list]
        if solve_times:
            ctx = PlotContext(scatter_rect, 0, max(max(solve_times), 30), len(solve_times))
        else:
            ctx = PlotContext(scatter_rect, 0, 30, len(solve_times))

        draw_grid(scatter_plot_surface, ctx)
        draw_std_boxes(scatter_plot_surface, ctx, solve_times, window=20)
        draw_points(scatter_plot_surface, ctx, solve_times)
        draw_competition_ao5(scatter_plot_surface, ctx, ao5(solve_times))

        last_scatter_size = scatter_rect.size
        last_session_list = list(session_list)

        mouse_hover_change = False

    # Blit the cached scatterplot onto the screen
    screen.blit(scatter_plot_surface, scatter_rect.topleft)

######################################################################################################################


timer = CubeTimer() # Timer instance
session_list = [] # Session list to store times
user_comment = "" # User comment


###############################################
###############################################

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

###############################################
###############################################

# Get screen size for dynamic layout
screen_width, screen_height = screen.get_size()

# Start everything as 0 or None.
COMMENT_WIDTH = 0
COMMENT_HEIGHT = 0
scatter_rect_height = 0
timer_rect = None
scatter_rect = None
comment_rect = None
save_button_rect = None

def update_sections():
    # Get screen size for dynamic layout
    screen_width, screen_height = screen.get_size()

    COMMENT_WIDTH = screen_width - 2*outer_margin
    COMMENT_HEIGHT = comment_text.get_height()+2*outer_margin
    # Calculate scatter plot height to fill the remaining space
    scatter_rect_height = screen_height - TIMER_HEIGHT - COMMENT_HEIGHT - 4 * outer_margin

    # Define rectangles
    timer_rect = pygame.Rect(outer_margin, outer_margin, screen_width - 2 * outer_margin, TIMER_HEIGHT)
    scatter_rect = pygame.Rect(outer_margin, timer_rect.bottom + outer_margin, screen_width - 2 * outer_margin, scatter_rect_height)
    comment_rect = pygame.Rect(outer_margin, screen_height-outer_margin-COMMENT_HEIGHT, COMMENT_WIDTH, COMMENT_HEIGHT)
    save_button_rect = pygame.Rect(timer_rect.width - save_button_text.get_width() - outer_margin, timer_rect.height - save_button_text.get_height()-2*outer_margin, save_button_text.get_width()+2*outer_margin, save_button_text.get_height()+2*outer_margin)
    return timer_rect, scatter_rect, comment_rect, save_button_rect

timer_rect, scatter_rect, comment_rect, save_button_rect = update_sections()

#####################################################
#new main loop start constants...
timer_return = None

# Main loop
running = True
input_active = False
backspacing = False
BACKSPACE_DELAY = 0.4     # seconds before repeat
BACKSPACE_REPEAT = 0.05  # seconds between repeats
backspace_start_time = 0
last_backspace_time = 0
mouse_hover_change = True
tooltip_point_info = None
tooltip_ao5_info = None
tooltip_a10_info = None

while running:
    timer_rect, scatter_rect, comment_rect, save_button_rect = update_sections()
    pressed = pygame.key.get_pressed()
    now = time.time()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not input_active:
                timer_return = timer.space_pressed()
                if timer_return is not None:
                    session_list.append((timer_return[0], timer_return[1], user_comment))
                    print(f"Duration: {timer_return[0]}, {timer_return[1]}, Comment: {user_comment}")
                    user_comment = ""
            elif input_active:
                if event.key == pygame.K_BACKSPACE:
                    backspacing = True #user_comment = user_comment[:-1]
                else:
                    backspacing = False
                    user_comment += event.unicode
        elif event.type == pygame.MOUSEMOTION:
            hovered_point_index = None
            if scatter_rect.collidepoint(event.pos):
                local_pos = (event.pos[0] - scatter_rect.x, event.pos[1] - scatter_rect.y)
                mouse_hover_change = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if save_button_rect.collidepoint(event.pos):
                with open(DATA_FILE, "a") as f:
                    for timestamp, duration, comment in session_list:
                        f.write(f"{timestamp}, {duration}, {comment}\n")
                session_list.clear()  # Clear the session list after saving
            elif comment_rect.collidepoint(event.pos):
                input_active = True
            elif scatter_rect.collidepoint(event.pos):
                input_active = False
                local_x = event.pos[0] - scatter_rect.x
                local_y = event.pos[1] - scatter_rect.y
                for i, hitbox, _ in scatter_point_hitboxes:
                    if hitbox.collidepoint((local_x, local_y)):
                        del session_list[i]
                        mouse_hover_change = False # dont highlight if a point is deleted because all point locations will change
                        hovered_point_index = None
                        break
            else:
                input_active = False
        
    if input_active and pressed[pygame.K_BACKSPACE]:
        #user_comment = user_comment[:-1]
        if not backspacing:
            # initial delete
            user_comment = user_comment[:-1]
            backspacing = True
            backspace_start_time = now
            last_backspace_time = now
        else:
            # repeating delete
            if now - backspace_start_time > BACKSPACE_DELAY:
                if now - last_backspace_time > BACKSPACE_REPEAT:
                    user_comment = user_comment[:-1]
                    last_backspace_time = now
    else:
        backspacing = False



    # Handle mouse hover highlighting
    highlighted_points = []
    highlighted_a10s = []
    highlighted_ao5s = []
    #tooltip_info = None
    if mouse_hover_change:
        for i, hitbox, mean, std in a10_hitboxes:
            if hitbox.collidepoint(local_pos):
                #hovered_point_index = i
                highlighted_a10s.append((i, hitbox, mean, std))
                tooltip_a10_info = [pygame.mouse.get_pos(), ["a10 "+f"{mean:.2f}±{std:.2f}"]]
                break
            else:
                tooltip_a10_info = None
        for i, hitbox, v in ao5_hitboxes:
            if hitbox.collidepoint(local_pos):
                # hovered_point_index = i
                highlighted_ao5s.append((i, hitbox, v))
                tooltip_ao5_info = [pygame.mouse.get_pos(), ["comp_ao5 "+f"{v:.2f}"]]

                break
            else:
                tooltip_ao5_info = None
        for i, hitbox, v in scatter_point_hitboxes:
            if hitbox.collidepoint(local_pos):
                highlighted_points.append((i, hitbox, v))
                tooltip_point_info = [pygame.mouse.get_pos(), [f"{v:.2f}"]]
                break
            else:
                tooltip_point_info = None

    # Clear the screen by filling it with the BG color
    screen.fill(BG_COLOR)

    # Draw Timer Section
    pygame.draw.rect(screen, BG_COLOR, timer_rect, border_radius = BORDER_RADIUS)
    time_text = TIMER_FONT.render(f"{timer.get_display_time()}", True, WHITE)
    time_text_rect = time_text.get_rect(center=timer_rect.center)
    screen.blit(time_text, time_text_rect)

    # Draw Save Button
    save_button_text = BUTTON_FONT.render(f"Save ({len(session_list)})", True, WHITE)
    pygame.draw.rect(screen, FG_COLOR, save_button_rect, border_radius = BORDER_RADIUS)
    screen.blit(save_button_text, (save_button_rect.x+outer_margin, save_button_rect.y+outer_margin))


    hovered = None
    hover_targets = []

    # Draw Scatterplot Section
    pygame.draw.rect(screen, FG_COLOR, scatter_rect, border_radius = BORDER_RADIUS)
    shrunken_rect = scatter_rect.inflate(-outer_margin, -outer_margin) # create a smaller rect for the actual plot area to allow for margins
    draw_scatterplot_cached(screen, shrunken_rect, session_list)

    # Draw Comment Section
    pygame.draw.rect(screen, FG_COLOR, comment_rect, border_radius = BORDER_RADIUS)
    comment_text = render_wrapped_text(user_comment, INPUT_FONT, WHITE, comment_rect.width-2*outer_margin)
    screen.blit(comment_text, (comment_rect.x + outer_margin, comment_rect.y + outer_margin))

    if tooltip_point_info is not None: # NEED TO ADD COMMENT TOOLTIP
        draw_tooltip(screen, pygame.mouse.get_pos(), tooltip_point_info[1])

    if tooltip_ao5_info is not None: # need to make this show ao5 value. also where do we designate to highlight the 5 averaged points?
        draw_tooltip(screen, pygame.mouse.get_pos(), tooltip_ao5_info[1])

    if tooltip_a10_info is not None: 
        draw_tooltip(screen, pygame.mouse.get_pos(), tooltip_a10_info[1])
    
    pygame.display.flip()

pygame.quit()
sys.exit()
