import cv2
import random

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class TileTransformation:
    def __init__(self, name="Transformation"):
        self._name = name
        
    def get_name(self):
        return self._name
        
    def apply(self, tiles, tile_ids):
        raise NotImplementedError
    
class SwapTransformation(TileTransformation):
    def __init__(self):
        super().__init__("Swap")
        
    def apply(self, tiles, tile_ids):
        index1, index2 = random.sample(range(len(tiles)), 2)

        tiles[index1], tiles[index2] = tiles[index2], tiles[index1]
        tile_ids[index1], tile_ids[index2] = tile_ids[index2], tile_ids[index1]

        print("Swapped tiles:", index1, "and", index2)
        
class RotateTransformation(TileTransformation):
    def __init__(self):
        super().__init__("Rotate")
        
    def apply(self, tiles, tile_ids):
        rotate_index = random.randrange(len(tiles))
        angle = random.choice([90, 180, 270])

        if angle == 90:
            tiles[rotate_index] = cv2.rotate(
                tiles[rotate_index],
                cv2.ROTATE_90_CLOCKWISE
            )
        elif angle == 180:
            tiles[rotate_index] = cv2.rotate(
                tiles[rotate_index],
                cv2.ROTATE_180
            )
        else:
            tiles[rotate_index] = cv2.rotate(
                tiles[rotate_index],
                cv2.ROTATE_90_COUNTERCLOCKWISE
            )

        print("Rotated tile:", rotate_index, "by", angle, "degrees")
    
class FlipTransformation(TileTransformation):
    def __init__(self):
        super().__init__("Flip")
        
    def apply(self, tiles, tile_ids):
        flip_index = random.randrange(len(tiles))
        flip_direction = random.choice(["horizontal", "vertical"])

        if flip_direction == "horizontal":
            tiles[flip_index] = cv2.flip(
                tiles[flip_index],
                1
            )
        else:
            tiles[flip_index] = cv2.flip(
                tiles[flip_index],
                0
            )

        print("Flipped tile:", flip_index, flip_direction)
        
class TransformationManager:
    def __init__(self):
        self._transformations = [
            SwapTransformation(),
            RotateTransformation(),
            FlipTransformation()
        ]

    def get_random_transformation(self):
        return random.choice(self._transformations)

transformation_manager = TransformationManager()

selected_tile = None
current_transformed_image = None
current_tiles = None
move_count = 0
original_tiles = None
hint_count = 0
hint_tile = None
puzzle_completed = False
current_tile_ids = None

def load_image():
    global move_count
    global original_tiles
    global hint_count
    global hint_tile
    global puzzle_completed
    global current_tile_ids
    
    file_path = filedialog.askopenfilename(
        filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.bmp"),
            ("All files", "*.*")
        ]
    )

    if file_path:
        image = cv2.imread(file_path)

        if image is not None:
            move_count = 0
            puzzle_completed = False
            move_label.config(text="Moves: 0")
            
            hint_count = 0
            hint_tile = None
            hint_button.config(state="normal")
            
            print("Image loaded successfully")
            print("Original size:", image.shape)

            height, width = image.shape[:2]

            max_size = 400
            scale = min(max_size / width, max_size / height)

            new_width = int(width * scale)
            new_height = int(height * scale)

            resized_image = cv2.resize(image, (new_width, new_height))

            top = (400 - new_height) // 2
            bottom = 400 - new_height - top
            left = (400 - new_width) // 2
            right = 400 - new_width - left

            resized_image = cv2.copyMakeBorder(
                resized_image,
                top,
                bottom,
                left,
                right,
                cv2.BORDER_CONSTANT,
                value=[255, 255, 255]
            )

            print("Resized size:", resized_image.shape)
            
            rgb_original = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
            pil_original = Image.fromarray(rgb_original)
            tk_original = ImageTk.PhotoImage(pil_original)

            original_label.config(image=tk_original, text="")
            original_label.image = tk_original

            grid = int(grid_size.get()[0])

            height, width = resized_image.shape[:2]

            new_height = height - (height % grid)
            new_width = width - (width % grid)

            cropped_image = resized_image[:new_height, :new_width]

            print("Grid:", grid)
            print("Cropped size:", cropped_image.shape)
           
            tile_height = new_height // grid
            tile_width = new_width // grid

            tiles = []

            for row in range(grid):
                for col in range(grid):
                    y1 = row * tile_height
                    y2 = y1 + tile_height
                    x1 = col * tile_width
                    x2 = x1 + tile_width

                    tile = cropped_image[y1:y2, x1:x2]
                    tiles.append(tile)

            print("Number of tiles:", len(tiles))
            print("Each tile size:", tiles[0].shape)
            
            original_tiles = [tile.copy() for tile in tiles]
            current_tile_ids = list(range(len(tiles)))
            
            if grid == 3:
                transformation_count = 6
            elif grid == 4:
                transformation_count = 12
            else:
                transformation_count = 20

            for _ in range(transformation_count):
                transformation = transformation_manager.get_random_transformation()
                print("Applying transformation:", transformation.get_name())
                transformation.apply(tiles, current_tile_ids)
            
            global current_tiles
            current_tiles = tiles
            
            rows = []

            for row in range(grid):
                start = row * grid
                end = start + grid

                row_tiles = tiles[start:end]
                row_image = cv2.hconcat(row_tiles)
                rows.append(row_image)

            transformed_image = cv2.vconcat(rows)
            global current_transformed_image
            current_transformed_image = transformed_image.copy()
            
            for i in range(len(current_tiles)):
                if is_tile_correct(i):
                    row = i // grid
                    col = i % grid

                    x1 = col * tile_width
                    y1 = row * tile_height
                    x2 = x1 + tile_width

                    tick_size = max(8, min(tile_width, tile_height) // 8)

                    tick_x = x2 - tick_size - 8
                    tick_y = y1 + tick_size + 8

                    cv2.line(
                        transformed_image,
                        (tick_x - tick_size // 2, tick_y),
                        (tick_x, tick_y + tick_size // 2),
                        (0, 255, 0),
                        3
                    )

                    cv2.line(
                        transformed_image,
                        (tick_x, tick_y + tick_size // 2),
                        (tick_x + tick_size, tick_y - tick_size // 2),
                        (0, 255, 0),
                        3
                    )
            
            for i in range(1, grid):
                x = i * tile_width
                y = i * tile_height

                cv2.line(transformed_image, (x, 0), (x, transformed_image.shape[0]), (180, 180, 180), 1)
                cv2.line(transformed_image, (0, y), (transformed_image.shape[1], y), (180, 180, 180), 1)

            print("Transformed image size:", transformed_image.shape)
            
            rgb_transformed = cv2.cvtColor(transformed_image, cv2.COLOR_BGR2RGB)
            pil_transformed = Image.fromarray(rgb_transformed)
            tk_transformed = ImageTk.PhotoImage(pil_transformed)

            transformed_label.config(image=tk_transformed, text="")
            transformed_label.image = tk_transformed
            
            update_incorrect_tiles()
            
def update_incorrect_tiles():
    global puzzle_completed
    
    if current_tiles is None or original_tiles is None:
        return

    incorrect = 0

    for i in range(len(current_tiles)):
        if not (current_tiles[i] == original_tiles[i]).all():
            incorrect += 1

    incorrect_label.config(text="Incorrect tiles: " + str(incorrect))
    
    if incorrect == 0 and move_count > 0 and not puzzle_completed:
        puzzle_completed = True
        
        messagebox.showinfo(
            "Puzzle Complete",
            "Congratulations! You completed the puzzle in "
            + str(move_count)
            + " moves!"
        )

def on_tile_click(event):
    global selected_tile
    global current_transformed_image
    global current_tiles
    global move_count
    global current_tile_ids
    
    if puzzle_completed:
        return

    grid = int(grid_size.get()[0])

    tile_width = 400 // grid
    tile_height = 400 // grid

    col = event.x // tile_width
    row = event.y // tile_height

    tile_index = row * grid + col

    if selected_tile is None:
        selected_tile = tile_index
        print("Selected tile:", tile_index)

    elif selected_tile == tile_index:
        selected_tile = None
        print("Deselected tile:", tile_index)

    else:
        first_tile = selected_tile
        second_tile = tile_index

        current_tiles[first_tile], current_tiles[second_tile] = \
            current_tiles[second_tile], current_tiles[first_tile]
            
        current_tile_ids[first_tile], current_tile_ids[second_tile] = \
            current_tile_ids[second_tile], current_tile_ids[first_tile]

        print("Swapped tiles:", first_tile, "and", second_tile)
        
        move_count += 1
        print("Moves:", move_count)
        move_label.config(text="Moves: " + str(move_count))
        
        clear_hint()

        selected_tile = None
        
        rows = []

        for row_num in range(grid):
            start = row_num * grid
            end = start + grid

            row_tiles = current_tiles[start:end]
            row_image = cv2.hconcat(row_tiles)
            rows.append(row_image)

        current_transformed_image = cv2.vconcat(rows)
        
        for i in range(1, grid):
            x = i * tile_width
            y = i * tile_height

            cv2.line(
                current_transformed_image,
                (x, 0),
                (x, current_transformed_image.shape[0]),
                (180, 180, 180),
                1
            )

            cv2.line(
                current_transformed_image,
                (0, y),
                (current_transformed_image.shape[1], y),
                (180, 180, 180),
                1
            )

    display_image = current_transformed_image.copy()
    
    for i in range(len(current_tiles)):
        if is_tile_correct(i):
            row = i // grid
            col = i % grid

            x1 = col * tile_width
            y1 = row * tile_height
            x2 = x1 + tile_width
            y2 = y1 + tile_height

            tick_size = max(8, min(tile_width, tile_height) // 8)

            tick_x = x2 - tick_size - 8
            tick_y = y1 + tick_size + 8

            cv2.line(
                display_image,
                (tick_x - tick_size // 2, tick_y),
                (tick_x, tick_y + tick_size // 2),
                (0, 255, 0),
                3
            )

            cv2.line(
                display_image,
                (tick_x, tick_y + tick_size // 2),
                (tick_x + tick_size, tick_y - tick_size // 2),
                (0, 255, 0),
                3
            )

    if selected_tile is not None:
        row = selected_tile // grid
        col = selected_tile % grid

        x1 = col * tile_width
        y1 = row * tile_height
        x2 = x1 + tile_width
        y2 = y1 + tile_height

        cv2.rectangle(
            display_image,
            (x1, y1),
            (x2 - 1, y2 - 1),
            (0, 0, 255),
            3
        )

    rgb_image = cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_image)
    tk_image = ImageTk.PhotoImage(pil_image)

    transformed_label.config(image=tk_image)
    transformed_label.image = tk_image
    
    update_incorrect_tiles()
    
def on_tile_right_click(event):
    global selected_tile
    global current_tiles
    global current_transformed_image
    global move_count
    
    if puzzle_completed:
        return

    grid = int(grid_size.get()[0])
    
    tile_width = current_transformed_image.shape[1] // grid
    tile_height = current_transformed_image.shape[0] // grid

    col = event.x // tile_width
    row = event.y // tile_height
    tile_index = row * grid + col

    # Rotate clicked tile 90 degrees clockwise
    current_tiles[tile_index] = cv2.rotate(
        current_tiles[tile_index],
        cv2.ROTATE_90_CLOCKWISE
    )

    print("Rotated tile:", tile_index)
    
    move_count += 1
    print("Moves:", move_count)
    move_label.config(text="Moves: " + str(move_count))
    
    clear_hint()

    # Rebuild transformed image
    rows = []

    for row_num in range(grid):
        start = row_num * grid
        end = start + grid

        row_tiles = current_tiles[start:end]
        row_image = cv2.hconcat(row_tiles)
        rows.append(row_image)

    current_transformed_image = cv2.vconcat(rows)
    
    for i in range(1, grid):
        x = i * tile_width
        y = i * tile_height

        cv2.line(
            current_transformed_image,
            (x, 0),
            (x, current_transformed_image.shape[0]),
            (180, 180, 180),
            1
        )

        cv2.line(
            current_transformed_image,
            (0, y),
            (current_transformed_image.shape[1], y),
            (180, 180, 180),
            1
        )

    selected_tile = None

    display_image = current_transformed_image.copy()

    tile_width = current_transformed_image.shape[1] // grid
    tile_height = current_transformed_image.shape[0] // grid

    for i in range(len(current_tiles)):
        if is_tile_correct(i):
            row = i // grid
            col = i % grid

            x1 = col * tile_width
            y1 = row * tile_height
            x2 = x1 + tile_width
            y2 = y1 + tile_height

            tick_size = max(8, min(tile_width, tile_height) // 8)

            tick_x = x2 - tick_size - 8
            tick_y = y1 + tick_size + 8

            cv2.line(
                display_image,
                (tick_x - tick_size // 2, tick_y),
                (tick_x, tick_y + tick_size // 2),
                (0, 255, 0),
                3
            )

            cv2.line(
                display_image,
                (tick_x, tick_y + tick_size // 2),
                (tick_x + tick_size, tick_y - tick_size // 2),
                (0, 255, 0),
                3
            )

    rgb_image = cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_image)
    tk_image = ImageTk.PhotoImage(pil_image)

    transformed_label.config(image=tk_image)
    transformed_label.image = tk_image
    
    update_incorrect_tiles()
    
def flip_clicked_tile(event):
    global selected_tile
    global current_tiles
    global current_transformed_image
    global move_count
    
    if puzzle_completed:
        return

    grid = int(grid_size.get()[0])
    
    tile_width = current_transformed_image.shape[1] // grid
    tile_height = current_transformed_image.shape[0] // grid

    col = event.x // tile_width
    row = event.y // tile_height
    tile_index = row * grid + col

    # Flip clicked tile horizontally
    current_tiles[tile_index] = cv2.flip(
        current_tiles[tile_index],
        1
    )

    print("Flipped tile:", tile_index)
    
    move_count += 1
    print("Moves:", move_count)
    move_label.config(text="Moves: " + str(move_count))
    
    clear_hint()

    # Rebuild transformed image
    rows = []

    for row_num in range(grid):
        start = row_num * grid
        end = start + grid

        row_tiles = current_tiles[start:end]
        row_image = cv2.hconcat(row_tiles)
        rows.append(row_image)

    current_transformed_image = cv2.vconcat(rows)
    
    for i in range(1, grid):
        x = i * tile_width
        y = i * tile_height

        cv2.line(
            current_transformed_image,
            (x, 0),
            (x, current_transformed_image.shape[0]),
            (180, 180, 180),
            1
        )

        cv2.line(
            current_transformed_image,
            (0, y),
            (current_transformed_image.shape[1], y),
            (180, 180, 180),
            1
        )

    selected_tile = None

    display_image = current_transformed_image.copy()

    tile_width = current_transformed_image.shape[1] // grid
    tile_height = current_transformed_image.shape[0] // grid

    for i in range(len(current_tiles)):
        if is_tile_correct(i):
            row = i // grid
            col = i % grid

            x1 = col * tile_width
            y1 = row * tile_height
            x2 = x1 + tile_width
            y2 = y1 + tile_height

            tick_size = max(8, min(tile_width, tile_height) // 8)

            tick_x = x2 - tick_size - 8
            tick_y = y1 + tick_size + 8

            cv2.line(
                display_image,
                (tick_x - tick_size // 2, tick_y),
                (tick_x, tick_y + tick_size // 2),
                (0, 255, 0),
                3
            )

            cv2.line(
                display_image,
                (tick_x, tick_y + tick_size // 2),
                (tick_x + tick_size, tick_y - tick_size // 2),
                (0, 255, 0),
                3
            )

    rgb_image = cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_image)
    tk_image = ImageTk.PhotoImage(pil_image)

    transformed_label.config(image=tk_image)
    transformed_label.image = tk_image
    
    update_incorrect_tiles()
    
def is_tile_correct(index):
    if current_tiles is None or original_tiles is None:
        return False

    return (current_tiles[index] == original_tiles[index]).all()

def clear_hint():
    global hint_tile

    hint_tile = None

    if original_tiles is None:
        return

    grid = int(grid_size.get()[0])

    original_image = cv2.vconcat([
        cv2.hconcat(original_tiles[i * grid:(i + 1) * grid])
        for i in range(grid)
    ])

    rgb_original = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
    pil_original = Image.fromarray(rgb_original)
    tk_original = ImageTk.PhotoImage(pil_original)

    original_label.config(image=tk_original)
    original_label.image = tk_original
    
def show_hint():
    global hint_count
    global hint_tile
    global current_tile_ids
    
    if puzzle_completed:
        return

    if current_tiles is None or original_tiles is None:
        return

    if hint_count >= 3:
        hint_button.config(state="disabled")
        return

    incorrect_indices = []

    for i in range(len(current_tiles)):
        if not is_tile_correct(i):
            incorrect_indices.append(i)

    if len(incorrect_indices) == 0:
        return

    hint_tile = random.choice(incorrect_indices)
    correct_home = current_tile_ids[hint_tile]
    hint_count += 1

    print("Hint tile:", hint_tile)
    print("Hints used:", hint_count)

    if hint_count >= 3:
        hint_button.config(state="disabled")
    
    grid = int(grid_size.get()[0])
    tile_width = current_transformed_image.shape[1] // grid
    tile_height = current_transformed_image.shape[0] // grid

    row = hint_tile // grid
    col = hint_tile % grid

    x1 = col * tile_width
    y1 = row * tile_height
    x2 = x1 + tile_width
    y2 = y1 + tile_height

    display_image = current_transformed_image.copy()

    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    radius = min(tile_width, tile_height) // 4

    cv2.circle(
        display_image,
        (center_x, center_y),
        radius,
        (255, 0, 0),
        3
    )

    rgb_image = cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_image)
    tk_image = ImageTk.PhotoImage(pil_image)

    transformed_label.config(image=tk_image)
    transformed_label.image = tk_image

        # Draw blue circle on the correct home position in the original image
    original_image = cv2.vconcat([
        cv2.hconcat(original_tiles[i * grid:(i + 1) * grid])
        for i in range(grid)
    ])

    original_display = original_image.copy()
    
    home_row = correct_home // grid
    home_col = correct_home % grid

    home_center_x = home_col * tile_width + tile_width // 2
    home_center_y = home_row * tile_height + tile_height // 2

    cv2.circle(
    original_display,
    (home_center_x, home_center_y),
    radius,
    (255, 0, 0),
    3
)

    rgb_original = cv2.cvtColor(original_display, cv2.COLOR_BGR2RGB)
    pil_original = Image.fromarray(rgb_original)
    tk_original = ImageTk.PhotoImage(pil_original)

    original_label.config(image=tk_original)
    original_label.image = tk_original
       
def solve_puzzle():
    global current_tiles
    global current_transformed_image
    global move_count
    global selected_tile
    global hint_tile
    global puzzle_completed
    global current_tile_ids

    if original_tiles is None:
        return

    grid = int(grid_size.get()[0])

    current_tiles = [tile.copy() for tile in original_tiles]
    current_tile_ids = list(range(len(original_tiles)))

    rows = []

    for row_num in range(grid):
        start = row_num * grid
        end = start + grid

        row_tiles = current_tiles[start:end]
        row_image = cv2.hconcat(row_tiles)
        rows.append(row_image)

    current_transformed_image = cv2.vconcat(rows)
    
    tile_width = current_transformed_image.shape[1] // grid
    tile_height = current_transformed_image.shape[0] // grid

    for i in range(1, grid):
        x = i * tile_width
        y = i * tile_height

        cv2.line(
            current_transformed_image,
            (x, 0),
            (x, current_transformed_image.shape[0]),
            (180, 180, 180),
            1
        )

        cv2.line(
            current_transformed_image,
            (0, y),
            (current_transformed_image.shape[1], y),
            (180, 180, 180),
            1
        )

    for i in range(len(current_tiles)):
        row = i // grid
        col = i % grid

        x1 = col * tile_width
        y1 = row * tile_height
        x2 = x1 + tile_width

        tick_size = max(8, min(tile_width, tile_height) // 8)

        tick_x = x2 - tick_size - 8
        tick_y = y1 + tick_size + 8

        cv2.line(
            current_transformed_image,
            (tick_x - tick_size // 2, tick_y),
            (tick_x, tick_y + tick_size // 2),
            (0, 255, 0),
            3
        )

        cv2.line(
            current_transformed_image,
            (tick_x, tick_y + tick_size // 2),
            (tick_x + tick_size, tick_y - tick_size // 2),
            (0, 255, 0),
            3
        )
    
    move_count = 0
    selected_tile = None
    hint_tile = None
    clear_hint()
    puzzle_completed = True

    move_label.config(text="Moves: 0")
    incorrect_label.config(text="Incorrect tiles: 0")

    rgb_image = cv2.cvtColor(
        current_transformed_image,
        cv2.COLOR_BGR2RGB
    )

    pil_image = Image.fromarray(rgb_image)
    tk_image = ImageTk.PhotoImage(pil_image)

    transformed_label.config(image=tk_image)
    transformed_label.image = tk_image

root = tk.Tk()
root.title("HIT137 Image Puzzle")
root.geometry("1000x700")

grid_label = tk.Label(root, text="Grid Size:")
grid_label.pack(pady=10)

grid_size = tk.StringVar(value="3x3")

grid_menu = tk.OptionMenu(root, grid_size, "3x3", "4x4", "5x5")
grid_menu.pack()

load_button = tk.Button(root, text="Load Image", command=load_image)
load_button.pack(pady=20)

move_label = tk.Label(root, text="Moves: 0")
move_label.pack(pady=5)

incorrect_label = tk.Label(root, text="Incorrect tiles: 0")
incorrect_label.pack(pady=5)

hint_button = tk.Button(root, text="Hint", command=show_hint)
hint_button.pack(pady=5)

solve_button = tk.Button(root, text="Solve", command=solve_puzzle)
solve_button.pack(pady=5)

image_frame = tk.Frame(root)
image_frame.pack(pady=20)

original_label = tk.Label(image_frame, text="Original Image")
original_label.grid(row=0, column=0, padx=20)

transformed_label = tk.Label(image_frame, text="Transformed Image")
transformed_label.grid(row=0, column=1, padx=20)

transformed_label.bind("<Button-1>", on_tile_click)
transformed_label.bind("<Button-3>", on_tile_right_click)
transformed_label.bind("<Shift-Button-1>", flip_clicked_tile)

root.mainloop()