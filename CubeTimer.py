# David Lanza
# 12/19/25
# Rubiks Cube Timer Program Requirements:
#   -be a very clear graph that is very clear that it is a graph
#   -must look good!
#   -must be clear numerical denominations on Y axis
#   -show scatterplot [future: other plot types]
#   -keep constant Y range
#   -adjustable window size
#   wtf else?
#
# fix/add to existing version:
#   -backspace should delete characters while held down, rather than once per button press.
#   -mouse over a datapoint should show the time and the comment.
#   -show last time on the timer display rather than getting rid of it
#   -should be able to delete solves


###########################
## this was the old heading info on this file when it was made:
# David Lanza
# GPT 4o
# 8-23-24
# rubiks cube timer program
###########################



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
FONT = pygame.font.SysFont('Courier', 60)
LABEL_FONT = pygame.font.SysFont('Courier', 20)
BUTTON_FONT = pygame.font.SysFont('Courier', 20)
INPUT_FONT = pygame.font.SysFont('Courier', 20)

# Fixed heights for timer and comment boxes
TIMER_HEIGHT = 100
COMMENT_HEIGHT = 40
outer_margin = 10  # Define outer_margin here

# Initialize screen (with resizable window)
screen = pygame.display.set_mode((600, 700), pygame.RESIZABLE)
pygame.display.set_caption("Rubik's Cube Timer")

scatter_plot_surface = None
last_scatter_size = (0, 0)
last_session_list = []

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

############################################################################################
### original working version
# def draw_scatterplot_cached(screen, scatter_rect, session_list):
#     global scatter_plot_surface, last_scatter_size, last_session_list

#     # Check if we need to rebuild the scatterplot surface
#     if (scatter_plot_surface is None 
#         or (scatter_rect.width, scatter_rect.height) != last_scatter_size
#         or session_list != last_session_list):

#         print("Rebuilding scatterplot surface")
        
#         scatter_plot_surface = pygame.Surface((scatter_rect.width, scatter_rect.height))
#         scatter_plot_surface.fill(BLACK)  # Fill with black or another background

#         # Build the scatterplot on scatter_plot_surface
#         if len(session_list) > 1:
#             # Extract the solve times
#             solve_times = [time for _, time, _ in session_list]
#             num_solves = len(solve_times)

#             # Determine the scale of the plot
#             max_time = 30 # max(solve_times)
#             min_time = 5 #min(solve_times)
#             time_range = max_time - min_time
#             if time_range == 0:
#                 time_range = 1

#             plot_width = scatter_rect.width - 20
#             plot_height = scatter_rect.height - 20
#             point_radius = 10

#             # Draw lines every 5 seconds
#             for i in range(0, int(max_time), 5):
#                 y = 10 + int((1 - (i - min_time) / time_range) * plot_height)
#                 color = (255, 0, 0) if i == 15 else (100, 100, 100)
#                 pygame.draw.line(scatter_plot_surface, color, (10, y), (plot_width, y), 1)

#             # Draw points
#             for i, solve_time in enumerate(solve_times):
#                 x = 10 + int(i * (plot_width / (num_solves - 1)))
#                 y = 10 + int((1 - (solve_time - min_time) / time_range) * plot_height)
#                 pygame.draw.circle(scatter_plot_surface, (0, 0, 255), (x, y), point_radius)

#         # Update cached size and data
#         last_scatter_size = (scatter_rect.width, scatter_rect.height)
#         last_session_list = list(session_list)

#     # Blit the cached scatterplot onto the screen
#     screen.blit(scatter_plot_surface, (scatter_rect.x, scatter_rect.y))

######################################################################################################
### edited version that currenntly works

# def draw_scatterplot_cached(screen, scatter_rect, session_list):
#     global scatter_plot_surface, last_scatter_size, last_session_list

#     # Check if we need to rebuild the scatterplot surface
#     if (scatter_plot_surface is None or (scatter_rect.width, scatter_rect.height) != last_scatter_size or session_list != last_session_list):

#         print("Rebuilding scatterplot surface")
        
#         scatter_plot_surface = pygame.Surface((scatter_rect.width, scatter_rect.height))
#         scatter_plot_surface.fill(BLACK)  # Fill with black or another background

#         # Build the scatterplot on scatter_plot_surface
#         if len(session_list) > 1:
#             # Extract the solve times
#             solve_times = [time for _, time, _ in session_list]
#             num_solves = len(solve_times)

#             # Determine the scale of the plot
#             max_time = 30 # max(solve_times)
#             min_time = 5 #min(solve_times)
#             time_range = max_time - min_time
#             if time_range == 0:
#                 time_range = 1

#             plot_border = 10
#             plot_width = scatter_rect.width - 2*plot_border
#             plot_height = scatter_rect.height - 2*plot_border
#             point_radius = 8

#             # Draw lines every 5 seconds
#             for i in range(0, int(max_time), 5):
#                 y = plot_border + int((1 - (i - min_time) / time_range) * plot_height)
#                 color = (200, 200, 200) if i == 15 else (100, 100, 100)
#                 pygame.draw.line(scatter_plot_surface, color, (plot_border, y), (plot_width, y), 1)
#                 label_text = LABEL_FONT.render(f"Save ({i})", True, WHITE)
#                 screen.blit(label_text, (0, y-10))

#             # Draw points
#             for i, solve_time in enumerate(solve_times):
#                 x = plot_border + int(i * (plot_width / (num_solves - 1)))
#                 y = plot_border + int((1 - (solve_time - min_time) / time_range) * plot_height)
#                 pygame.draw.circle(scatter_plot_surface, (0, 0, 255), (x, y), point_radius)

#         # Update cached size and data
#         last_scatter_size = (scatter_rect.width, scatter_rect.height)
#         last_session_list = list(session_list)

#     # Blit the cached scatterplot onto the screen
#     screen.blit(scatter_plot_surface, (scatter_rect.x, scatter_rect.y))


###################################################################################################
### nnew edited version (blobs of a1-5)

# def centered_stats(lst, n):
#     averages = []
#     stddevs = []
#     length = len(lst)
#     for i in range(length):
#         # Window bounds
#         start = max(0, i - n)
#         end   = min(length, i + n + 1)
#         window = lst[start:end]
#         mean = sum(window) / len(window)
#         # Standard deviation
#         variance = sum((x - mean)**2 for x in window) / len(window)
#         std = math.sqrt(variance)
#         print("mean ")
#         print(mean)
#         print("std ")
#         print(std)
#         # Store results
#         averages.append(mean)
#         stddevs.append(std)
#     return averages, stddevs


# def draw_scatterplot_cached(screen, scatter_rect, session_list):
#     global scatter_plot_surface, last_scatter_size, last_session_list
#     # Check if we need to rebuild the scatterplot surface
#     if (scatter_plot_surface is None or (scatter_rect.width, scatter_rect.height) != last_scatter_size or session_list != last_session_list):
#         print("Rebuilding scatterplot surface")
#         scatter_plot_surface = pygame.Surface((scatter_rect.width, scatter_rect.height))
#         scatter_plot_surface.fill(BLACK)  # Fill with black or another background
#         # Build the scatterplot on scatter_plot_surface
#         if len(session_list) > 1:
#             # Extract the solve times
#             solve_times = [time for _, time, _ in session_list]
#             num_solves = len(solve_times)
#             # Determine the scale of the plot
#             max_time = 30 # max(solve_times)
#             min_time = 0 #min(solve_times)
#             time_range = max_time - min_time
#             if time_range == 0:
#                 time_range = 1
#             plot_border = 10
#             plot_width = scatter_rect.width - 2*plot_border
#             plot_height = scatter_rect.height - 2*plot_border
#             point_radius = 5



#             window = 5
#             a10, s10 = centered_stats(solve_times,window)
#             # Draw average of 5 points
#             for i, a10t in enumerate(a10):
#                 x10 = plot_border + int(i * (plot_width / (num_solves - 1)))
#                 y10 = plot_border + int((1 - (a10t - min_time) / time_range) * plot_height)
#                 pygame.draw.circle(scatter_plot_surface, (0, 0, 50), (x10, y10), math.sqrt(s10[i]*(2*window+1))*plot_height/(3*time_range))

#             # window = 4
#             # a4, s4 = centered_stats(solve_times,window)
#             # # Draw average of 5 points
#             # for i, a4t in enumerate(a4):
#             #     x4 = plot_border + int(i * (plot_width / (num_solves - 1)))
#             #     y4 = plot_border + int((1 - (a4t - min_time) / time_range) * plot_height)
#             #     pygame.draw.circle(scatter_plot_surface, (0, 0, 50), (x4, y4), math.sqrt(s4[i]*(2*window+1))*plot_height/(3*time_range))

#             # window = 3
#             # a3, s3 = centered_stats(solve_times,window)
#             # # Draw average of 5 points
#             # for i, a3t in enumerate(a3):
#             #     x3 = plot_border + int(i * (plot_width / (num_solves - 1)))
#             #     y3 = plot_border + int((1 - (a3t - min_time) / time_range) * plot_height)
#             #     pygame.draw.circle(scatter_plot_surface, (0, 0, 100), (x3, y3), math.sqrt(s3[i]*(2*window+1))*plot_height/(3*time_range))

#             # window = 2
#             # a5, s5 = centered_stats(solve_times,window)
#             # # Draw average of 5 points
#             # for i, a5t in enumerate(a5):
#             #     x5 = plot_border + int(i * (plot_width / (num_solves - 1)))
#             #     y5 = plot_border + int((1 - (a5t - min_time) / time_range) * plot_height)
#             #     pygame.draw.circle(scatter_plot_surface, (0, 0, 150), (x5, y5), math.sqrt(s5[i]*(2*window+1))*plot_height/(3*time_range))

#             window = 1
#             a1, s1 = centered_stats(solve_times,window)
#             # Draw average of 5 points
#             for i, a1t in enumerate(a1):
#                 x1 = plot_border + int(i * (plot_width / (num_solves - 1)))
#                 y1 = plot_border + int((1 - (a1t - min_time) / time_range) * plot_height)
#                 pygame.draw.circle(scatter_plot_surface, (0, 0, 200), (x1, y1), math.sqrt(s1[i]*(2*window+1))*plot_height/(3*time_range))
            

            
#             # Draw lines every 5 seconds
#             for i in range(0, int(max_time), 5):
#                 y = plot_border + int((1 - (i - min_time) / time_range) * plot_height)
#                 color = (100, 100, 100) if i == 15 else (100, 100, 100)
#                 pygame.draw.line(scatter_plot_surface, color, (plot_border, y), (plot_width, y), 1)
#                 label_text = LABEL_FONT.render(str(i), True, WHITE)
#                 scatter_plot_surface.blit(label_text, (0, y))

#             # Draw points
#             for i, solve_time in enumerate(solve_times):
#                 x = plot_border + int(i * (plot_width / (num_solves - 1)))
#                 y = plot_border + int((1 - (solve_time - min_time) / time_range) * plot_height)
#                 pygame.draw.circle(scatter_plot_surface, (255, 255, 255), (x, y), point_radius)




                

#         # Update cached size and data
#         last_scatter_size = (scatter_rect.width, scatter_rect.height)
#         last_session_list = list(session_list)

#     # Blit the cached scatterplot onto the screen
#     screen.blit(scatter_plot_surface, (scatter_rect.x, scatter_rect.y))


###################################################################################################
###################################################################################################
### new edited version (rectangles)

# def centered_stats(lst, n):
#     averages = []
#     stddevs = []
#     length = len(lst)
#     for i in range(length):
#         # Window bounds
#         start = max(0, i - n)
#         end   = min(length, i + n + 1)
#         window = lst[start:end]
#         mean = sum(window) / len(window)
#         # Standard deviation
#         variance = sum((x - mean)**2 for x in window) / len(window)
#         std = math.sqrt(variance)
#         print("mean ")
#         print(mean)
#         print("std ")
#         print(std)
#         # Store results
#         averages.append(mean)
#         stddevs.append(std)
#     return averages, stddevs


# def draw_scatterplot_cached(screen, scatter_rect, session_list):
#     global scatter_plot_surface, last_scatter_size, last_session_list
#     # Check if we need to rebuild the scatterplot surface
#     if (scatter_plot_surface is None or (scatter_rect.width, scatter_rect.height) != last_scatter_size or session_list != last_session_list):
#         print("Rebuilding scatterplot surface")
#         scatter_plot_surface = pygame.Surface((scatter_rect.width, scatter_rect.height))
#         scatter_plot_surface.fill(BLACK)  # Fill with black or another background
#         # Build the scatterplot on scatter_plot_surface
#         if len(session_list) > 1:
#             # Extract the solve times
#             solve_times = [time for _, time, _ in session_list]
#             num_solves = len(solve_times)
#             # Determine the scale of the plot
#             max_time = 30 # max(solve_times)
#             min_time = 0 #min(solve_times)
#             time_range = max_time - min_time
#             if time_range == 0:
#                 time_range = 1
#             plot_border = 10
#             plot_width = scatter_rect.width - 2*plot_border
#             plot_height = scatter_rect.height - 2*plot_border
#             point_radius = 5



#             # window = 5
#             # a10, s10 = centered_stats(solve_times,window)
#             # # Draw average of 5 points
#             # for i, a10t in enumerate(a10):
#             #     x10 = plot_border + int(i * (plot_width / (num_solves - 1)))
#             #     y10 = plot_border + int((1 - (a10t - min_time) / time_range) * plot_height)
#             #     pygame.draw.circle(scatter_plot_surface, (0, 0, 25), (x10, y10), math.sqrt(s10[i]*(2*window+1))*plot_height/time_range)


#             w = 5
#             #a10, s10 = centered_stats(solve_times,window)
#             # Draw boxes
#             for i in range(0, int(num_solves), w):
#                 start = max(0, i-w)
#                 end   = min(num_solves, i)
#                 window = solve_times[start:end]
#                 if len(window) > 0:
#                     mean = sum(window) / len(window)
#                     variance = sum((x - mean)**2 for x in window) / len(window)
#                 else:
#                     mean = 0
#                     variance = 0
#                 # Standard deviation
#                 std = math.sqrt(variance)
#                 print("i: ", i, " mean: ",mean," var: ",variance)
#                 x20left = plot_border + int((start) * (plot_width / (num_solves - 1)))
#                 x20right = plot_border + int((end) * (plot_width / (num_solves - 1)))
#                 y20top = plot_border + int((1 - (mean + std - min_time) / time_range) * plot_height)
#                 y20bot = plot_border + int((1 - (mean - std - min_time) / time_range) * plot_height)
#                 pygame.draw.rect(scatter_plot_surface, (100, 100, 100), (x20left,y20top,abs(x20right-x20left),abs(y20top-y20bot)),0)


            

            
#             # Draw lines every 5 seconds
#             for i in range(0, int(max_time), 5):
#                 y = plot_border + int((1 - (i - min_time) / time_range) * plot_height)
#                 color = (100, 100, 100) if i == 15 else (100, 100, 100)
#                 pygame.draw.line(scatter_plot_surface, color, (plot_border, y), (plot_width, y), 1)
#                 label_text = LABEL_FONT.render(str(i), True, WHITE)
#                 scatter_plot_surface.blit(label_text, (0, y))

#             # Draw points
#             for i, solve_time in enumerate(solve_times):
#                 x = plot_border + int(i * (plot_width / (num_solves - 1)))
#                 y = plot_border + int((1 - (solve_time - min_time) / time_range) * plot_height)
#                 pygame.draw.circle(scatter_plot_surface, (255, 255, 255), (x, y), point_radius)




                

#         # Update cached size and data
#         last_scatter_size = (scatter_rect.width, scatter_rect.height)
#         last_session_list = list(session_list)

#     # Blit the cached scatterplot onto the screen
#     screen.blit(scatter_plot_surface, (scatter_rect.x, scatter_rect.y))

##############################################################################################################
###################################################################################################
###################################################################################################
### new edited version (rectangles)

def centered_stats(lst, n):
    averages = []
    stddevs = []
    length = len(lst)
    for i in range(length):
        # Window bounds
        start = max(0, i - n)
        end   = min(length, i + n + 1)
        window = lst[start:end]
        mean = sum(window) / len(window)
        # Standard deviation
        variance = sum((x - mean)**2 for x in window) / len(window)
        std = math.sqrt(variance)
        print("mean ")
        print(mean)
        print("std ")
        print(std)
        # Store results
        averages.append(mean)
        stddevs.append(std)
    return averages, stddevs

def competition_average(lst):
    averages = []
    stddevs = []
    length = len(lst)
    for i in range(length):
        if i > 3 and i<length:
            # Window bounds
            start = max(0, i - 5)
            end   = i
            window = lst[start:end]
            mean = (sum(window)-max(window)-min(window)) / (len(window)-2)
            # Store results
            averages.append(mean)
    return averages


def draw_scatterplot_cached(screen, scatter_rect, session_list):
    global scatter_plot_surface, last_scatter_size, last_session_list
    # Check if we need to rebuild the scatterplot surface
    if (scatter_plot_surface is None or (scatter_rect.width, scatter_rect.height) != last_scatter_size or session_list != last_session_list):
        print("Rebuilding scatterplot surface")
        scatter_plot_surface = pygame.Surface((scatter_rect.width, scatter_rect.height))
        scatter_plot_surface.fill(BLACK)  # Fill with black or another background
        # Build the scatterplot on scatter_plot_surface
        if len(session_list) > 1:
            # Extract the solve times
            solve_times = [time for _, time, _ in session_list]
            num_solves = len(solve_times)
            # Determine the scale of the plot
            max_time = 30 # max(solve_times)
            min_time = 0 #min(solve_times)
            time_range = max_time - min_time
            if time_range == 0:
                time_range = 1
            plot_border = 10
            plot_width = scatter_rect.width - 2*plot_border
            plot_height = scatter_rect.height - 2*plot_border
            point_radius = 5



            # window = 5
            # a10, s10 = centered_stats(solve_times,window)
            # # Draw average of 5 points
            # for i, a10t in enumerate(a10):
            #     x10 = plot_border + int(i * (plot_width / (num_solves - 1)))
            #     y10 = plot_border + int((1 - (a10t - min_time) / time_range) * plot_height)
            #     pygame.draw.circle(scatter_plot_surface, (0, 0, 25), (x10, y10), math.sqrt(s10[i]*(2*window+1))*plot_height/time_range)



            w = 5
            #a10, s10 = centered_stats(solve_times,window)
            # Draw boxes
            for i in range(0, int(num_solves), w):
                start = max(0, i-w)
                end   = min(num_solves, i)
                window = solve_times[start:end]
                if len(window) > 0:
                    mean = sum(window) / len(window)
                    variance = sum((x - mean)**2 for x in window) / len(window)
                else:
                    mean = 0
                    variance = 0
                # Standard deviation
                std = math.sqrt(variance)
                print("i: ", i, " mean: ",mean," var: ",variance)
                x20left = plot_border + int((start) * (plot_width / (num_solves - 1)))
                x20right = plot_border + int((end) * (plot_width / (num_solves - 1)))
                y20top = plot_border + int((1 - (mean + std - min_time) / time_range) * plot_height)
                y20bot = plot_border + int((1 - (mean - std - min_time) / time_range) * plot_height)
                pygame.draw.rect(scatter_plot_surface, (100, 100, 100), (x20left,y20top,abs(x20right-x20left),abs(y20top-y20bot)),0)


            aC = competition_average(solve_times)
            # draw avg points
            for i, a in enumerate(aC):
                x = plot_border + int(i * (plot_width / (num_solves - 1)))
                y = plot_border + int((1 - (a - min_time) / time_range) * plot_height)
                pygame.draw.circle(scatter_plot_surface, (255, 0, 0), (x, y), point_radius)

            
            # Draw lines every 5 seconds
            for i in range(0, int(max_time), 5):
                y = plot_border + int((1 - (i - min_time) / time_range) * plot_height)
                color = (100, 100, 100) if i == 15 else (100, 100, 100)
                pygame.draw.line(scatter_plot_surface, color, (plot_border, y), (plot_width, y), 1)
                label_text = LABEL_FONT.render(str(i), True, WHITE)
                scatter_plot_surface.blit(label_text, (0, y))

            # Draw points
            for i, solve_time in enumerate(solve_times):
                x = plot_border + int(i * (plot_width / (num_solves - 1)))
                y = plot_border + int((1 - (solve_time - min_time) / time_range) * plot_height)
                pygame.draw.circle(scatter_plot_surface, (255, 255, 255), (x, y), point_radius)




                

        # Update cached size and data
        last_scatter_size = (scatter_rect.width, scatter_rect.height)
        last_session_list = list(session_list)

    # Blit the cached scatterplot onto the screen
    screen.blit(scatter_plot_surface, (scatter_rect.x, scatter_rect.y))

##############################################################################################################


# Timer instance
timer = CubeTimer()
countdown = 15
countdown_started = False
countdown_start_time = None
background_color = DARK
timer_running = False
countdown_time = countdown

# Session list to store times
session_list = []

# User comment
user_comment = ""

# Get screen size for dynamic layout
screen_width, screen_height = screen.get_size()

# Calculate scatter plot height to fill the remaining space
scatter_rect_height = screen_height - TIMER_HEIGHT - COMMENT_HEIGHT - 4 * outer_margin

# Define rectangles
timer_rect = pygame.Rect(outer_margin, outer_margin, screen_width - 2 * outer_margin, TIMER_HEIGHT)
scatter_rect = pygame.Rect(outer_margin, timer_rect.bottom + outer_margin, screen_width - 2 * outer_margin, scatter_rect_height)
comment_rect = pygame.Rect(outer_margin, scatter_rect.bottom + outer_margin, screen_width - 2 * outer_margin, COMMENT_HEIGHT)
save_button_rect = pygame.Rect(timer_rect.width - 140 + outer_margin, timer_rect.bottom - 40, 140, 40)

# Main loop
running = True
input_active = False
while running:
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
                    background_color = DARK
            elif input_active:
                if event.key == pygame.K_BACKSPACE:
                    user_comment = user_comment[:-1]
                else:
                    user_comment += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if save_button_rect.collidepoint(event.pos):
                with open(DATA_FILE, "a") as f:
                    for timestamp, duration, comment in session_list:
                        f.write(f"{timestamp}, {duration}, {comment}\n")
                session_list.clear()  # Clear the session list after saving
            elif comment_rect.collidepoint(event.pos):
                input_active = True
            else:
                input_active = False

    # Handle countdown
    if countdown_started and not timer_running:
        time_passed = time.time() - countdown_start_time
        countdown_time = countdown - time_passed
        if countdown_time <= 0:
            background_color = RED

    
    # Clear the screen by filling it with the background color
    screen.fill(DARK)

    # Draw the outer rectangle for the timer section
    pygame.draw.rect(screen, BLACK, timer_rect)

    # Initialize time_text with a default value
    time_text = FONT.render("", True, WHITE)  # Default empty text

    # Update time_text based on state
    if countdown_started and not timer_running:
        display_time = int(countdown_time) if countdown_time > 0 else -int(abs(countdown_time))
        time_text = FONT.render(f"{display_time}", True, WHITE)
    elif timer_running:
        time_text = FONT.render(f"{timer.get_time()}", True, WHITE)

    # Center the text within the timer rectangle
    text_rect = time_text.get_rect(center=timer_rect.center)
    screen.blit(time_text, text_rect)

    # Draw save button at the bottom right inside the timer rectangle
    pygame.draw.rect(screen, DARK, save_button_rect)
    button_text = BUTTON_FONT.render(f"Save ({len(session_list)})", True, WHITE)
    screen.blit(button_text, (save_button_rect.x + 15, save_button_rect.y + 10))

    # Draw the outer rectangle for the scatter plot section
    pygame.draw.rect(screen, BLACK, scatter_rect)

    # Draw scatter plot inside the scatter_rect
    draw_scatterplot_cached(screen, scatter_rect, session_list)

    # Draw the outer rectangle for the comment section
    pygame.draw.rect(screen, BLACK, comment_rect)

    # Render the comment text
    comment_text = INPUT_FONT.render(user_comment, True, WHITE)
    screen.blit(comment_text, (comment_rect.x + 10, comment_rect.y + 10))

    pygame.display.flip()

pygame.quit()
sys.exit()
