import pygame 
import time
import heapq
import pandas as pd

# Load Item Locations from DataFrame with Empty Rows
original_rows = {
    "C": 2, "D": 3, "E": 5, "F": 6, "G": 8  # Shift E, F, G due to empty rows
}

data = {
    "Product_ID": list(range(1, 31)),
    "Product_Name": [
        "Sugar", "Groundnut", "Jeera", "Almonds", "Kaju", "Jaggery", "Kismis", "Elachi", "Pepper", "Chilli powder",
        "Anjeer", "Dry coconut", "Pista", "Sabja", "Seeded Dates", "Kalvanji", "Eating soda", "Dry ginger",
        "Desseded Dates", "Mix Masala", "Dried dates", "Moong dal", "Mix dal", "Rajma", "kinderjoy", "Dairymilk",
        "ferrorochers", "Kitkat", "Fivestar", "Barone"
    ],
    "Row": [
        "C", "C", "C", "C", "C", "C", "D", "D", "D", "D", "D", "D",
        "E", "E", "E", "E", "E", "E", "F", "F", "F", "F", "F", "F",
        "G", "G", "G", "G", "G", "G"
    ],
    "Column": [2, 3, 4, 5, 6, 8, 2, 3, 4, 5, 6, 8, 2, 3, 4, 5, 6, 8, 2, 3, 4, 5, 6, 8, 2, 3, 4, 5, 6, 8]
}

data["Row"] = [original_rows[row] for row in data["Row"]]
df = pd.DataFrame(data)

# Grid Configuration
GRID_SIZE = 12  # Increase size due to added empty rows
CELL_SIZE = 60
warehouse_grid = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]

# Mark Item Locations as Obstacles
for _, row in df.iterrows():
    warehouse_grid[row["Row"]][row["Column"] - 1] = 1  # Mark items as obstacles

# Pygame Initialization
pygame.init()
screen = pygame.display.set_mode((GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE))
font = pygame.font.Font(None, 36)

# Load robot images
robot_img = pygame.image.load("download.png")
robot_img = pygame.transform.scale(robot_img, (CELL_SIZE, CELL_SIZE))
robot_with_item_img = pygame.image.load("imag.png")
robot_with_item_img = pygame.transform.scale(robot_with_item_img, (CELL_SIZE, CELL_SIZE))

def draw_grid():
    screen.fill((255, 255, 255))
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            color = (255, 255, 255)
            if (x, y) == (10, 9):
                color = (0, 255, 0)  # Counter position
            if (x==11 or y==11):
                color = (2, 48, 32)    
            pygame.draw.rect(screen, color, (y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE), 0 if color != (200, 200, 200) else 1)


    for _, row in df.iterrows():
        item_x, item_y = row["Row"], row["Column"] - 1
        pygame.draw.rect(screen, (0, 84, 119), (item_y * CELL_SIZE, item_x * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)

start_pos = (10, 9)
counter_pos = start_pos

# A* Pathfinding with Strict Item Avoidance
def astar(grid, start, goal, picking=False):
    rows, cols = len(grid), len(grid[0])
    open_list = []
    heapq.heappush(open_list, (0, start))
    came_from = {start: None}
    g_score = {start: 0}
    
    while open_list:
        _, current = heapq.heappop(open_list)
        if current == goal:
            path = []
            while current:
                path.append(current)
                current = came_from[current]
            return path[::-1]
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols:
                if grid[neighbor[0]][neighbor[1]] == 1 and not (picking and neighbor == goal):
                    continue  # Avoid items unless picking up that specific item
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    g_score[neighbor] = tentative_g_score
                    came_from[neighbor] = current
                    heapq.heappush(open_list, (tentative_g_score, neighbor))
    return []

def return_robot_to_start():

    pygame.quit()
    quit()

def deliver_items(customer_items):
    global start_pos
    customer_items = [item.strip().lower() for item in customer_items]
    
    # Check if "z" is in the input
    if "z" in customer_items:
        return_robot_to_start()
        return  # Exit the function after returning to start

    # Parse input to handle quantities
    item_quantities = {}
    for item in customer_items:
        if '*' in item:
            item_name, quantity = item.split('*')
            item_name = item_name.strip().lower()
            quantity = int(quantity)
            item_quantities[item_name] = item_quantities.get(item_name, 0) + quantity
        else:
            item_name = item.strip().lower()
            item_quantities[item_name] = item_quantities.get(item_name, 0) + 1

    # Filter items that exist in the DataFrame
    selected_items = []
    for item_name, quantity in item_quantities.items():
        if item_name in df["Product_Name"].str.lower().values:
            selected_items.extend([(item_name, quantity)])

    current_pos = start_pos
    
    for item_name, quantity in selected_items:
        item_row = df[df["Product_Name"].str.lower() == item_name].iloc[0]
        item_pos = (item_row["Row"], item_row["Column"] - 1)
        
        # Move to the item
        path_to_item = astar(warehouse_grid, current_pos, item_pos, picking=True)
        for r, c in path_to_item:
            draw_grid()
            screen.blit(robot_img, (c * CELL_SIZE, r * CELL_SIZE))  # Use default robot image
            pygame.display.update()
            time.sleep(0.1)
        
        # Update current position
        current_pos = item_pos
        
        # Display picking up the item
        text = font.render(f"Picking up {item_name} (x{quantity})", True, (255, 0, 0))
        screen.blit(text, (150, 50))
        screen.blit(robot_with_item_img, (current_pos[1] * CELL_SIZE, current_pos[0] * CELL_SIZE))  # Change to robot_with_item_img
        pygame.display.update()
        time.sleep(quantity)  # Wait for 'n' seconds, where n is the quantity

    # Move to the counter
    path_to_counter = astar(warehouse_grid, current_pos, (10, 9))
    for r, c in path_to_counter:
        draw_grid()
        screen.blit(robot_with_item_img, (c * CELL_SIZE, r * CELL_SIZE))  # Use robot_with_item_img while delivering
        pygame.display.update()
        time.sleep(0.1)
    
    # Display delivery message
    text = font.render("Delivered All Items to Counter", True, (0, 0, 255))
    screen.blit(text, (150, 50))
    screen.blit(robot_img, (counter_pos[1] * CELL_SIZE, counter_pos[0] * CELL_SIZE))  # Revert to default robot image
    pygame.display.update()
    time.sleep(2)
    start_pos = counter_pos

while True:
    customer_items = input("Enter your items: ").split(',')
    deliver_items(customer_items)