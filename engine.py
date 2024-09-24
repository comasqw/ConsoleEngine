from abc import ABC, abstractmethod
import time

EMPTY_CELL_SYMBOL = " "
CELL_DEFAULT_SYMBOL = "#"


class Cell:
    def __init__(self, x: int, y: int, symbol: str = EMPTY_CELL_SYMBOL):
        """
        Initializes a Cell object.

        :param x: The x-coordinate of the cell.
        :param y: The y-coordinate of the cell.
        :param symbol: The symbol representing the cell. Default is an empty cell symbol.
        """
        self.x = x
        self.y = y
        self.symbol = symbol
        self.is_active: bool = False

    def activate(self, symbol: str | None = None):
        """
        Activates the cell, setting its symbol and marking it as active.

        :param symbol: The symbol to assign to the cell. If None, a default symbol is used.
        """
        if symbol is None:
            symbol = CELL_DEFAULT_SYMBOL

        self.symbol = symbol
        self.is_active = True

    def deactivate(self):
        """
        Deactivates the cell, clearing its symbol and marking it as inactive.
        """
        self.symbol = EMPTY_CELL_SYMBOL
        self.is_active = False


class EngineObject:
    def __init__(self, object_form: list[tuple[int, int, str | None]]):
        """
        Initializes an EngineObject.

        :param object_form: A list of tuples representing the object's form,
                            where each tuple contains (x_offset, y_offset, symbol).
        """
        self.object_form = object_form
        self.object_coordinates: None | list[Cell] = None

    def init_object_coordinates(self, object_coordinates: list[Cell]):
        """
        Initializes the coordinates of the object.

        :param object_coordinates: A list of Cell objects representing the coordinates of the EngineObject.
        """
        self.object_coordinates = object_coordinates

    def del_object_coordinates(self):
        """
        Deletes the coordinates of the object by setting them to None.
        """
        self.object_coordinates = None


class Display:
    def __init__(self, size_x: int = 120, size_y: int = 30):
        """
        Initializes a Display object with a specified size.

        :param size_x: The width of the display.
        :param size_y: The height of the display.
        """
        self.size_x = size_x
        self.size_y = size_y
        self.display = self._display_init()

    def _display_init(self) -> list[list[Cell]]:
        """
        Initializes the display grid with Cell objects.

        :return: A 2D list representing the display grid filled with Cell objects.
        """
        return [[Cell(col, row) for col in range(self.size_x)] for row in range(self.size_y)]

    def _check_coordinates(self, x: int, y: int) -> bool:
        """
        Checks if the given coordinates are within the display bounds.

        :param x: The x-coordinate to check.
        :param y: The y-coordinate to check.
        :return: True if the coordinates are valid, False otherwise.
        """
        return 0 <= x < self.size_x and 0 <= y < self.size_y

    def activate_cell(self, x: int, y: int, symbol: str | None = None):
        """
        Activates a cell at the specified coordinates with the given symbol.

        :param x: The x-coordinate of the cell to activate.
        :param y: The y-coordinate of the cell to activate.
        :param symbol: The symbol to assign to the cell. If None, a default symbol is used.
        """
        if symbol is None:
            symbol = CELL_DEFAULT_SYMBOL

        if self._check_coordinates(x, y):
            self.display[y][x].activate(symbol)

    def deactivate_cell(self, x: int, y: int):
        """
        Deactivates a cell at the specified coordinates.

        :param x: The x-coordinate of the cell to deactivate.
        :param y: The y-coordinate of the cell to deactivate.
        """
        if self._check_coordinates(x, y):
            self.display[y][x].deactivate()

    def check_cell_condition(self, x: int, y: int) -> bool:
        """
        Checks if a cell at the specified coordinates is active.

        :param x: The x-coordinate of the cell.
        :param y: The y-coordinate of the cell.
        :return: True if the cell is active, False otherwise.
        """
        if self._check_coordinates(x, y):
            return self.display[y][x].is_active
        return False

    def draw_object(self, engine_object: EngineObject, start_x: int, start_y: int):
        """
        Draws an EngineObject on the display at the specified coordinates.

        :param engine_object: The EngineObject to draw.
        :param start_x: The starting x-coordinate for drawing the object.
        :param start_y: The starting y-coordinate for drawing the object.
        """
        object_coordinates = []
        for coordinate in engine_object.object_form:
            new_x = start_x + coordinate[0]
            new_y = start_y + coordinate[1]
            if self._check_coordinates(new_x, new_y):
                self.activate_cell(new_x, new_y, coordinate[2])
                object_coordinates.append(self.display[new_y][new_x])

        engine_object.init_object_coordinates(object_coordinates)

    def del_object(self, engine_object: EngineObject):
        """
        Deletes an EngineObject from the display.

        :param engine_object: The EngineObject to delete.
        """
        for coordinate in engine_object.object_coordinates:
            self.deactivate_cell(coordinate.x, coordinate.y)
        engine_object.del_object_coordinates()

    def move_object(self, engine_object: EngineObject, move_to_x: int, move_to_y: int):
        """
        Moves an EngineObject to new coordinates on the display.

        :param engine_object: The EngineObject to move.
        :param move_to_x: The x-coordinate to move the object to.
        :param move_to_y: The y-coordinate to move the object to.
        """
        self.del_object(engine_object)
        self.draw_object(engine_object, move_to_x, move_to_y)

    def render(self):
        """
        Renders the current state of the display to the console.
        Clears the console and prints the grid of symbols representing active cells.
        """
        print("\033[H", end="")
        display = ""
        for row in self.display:
            display += "".join(cell.symbol for cell in row) + "\n"
        print(display)


class Engine(ABC):
    def __init__(self, display: Display):
        """
        Initializes the Engine.

        :param display: The Display object associated with the engine.
        """
        self.display = display

    @abstractmethod
    def update(self):
        """
        Abstract method to update the engine state.
        This method should be implemented in derived classes.
        """
        pass

    def _run_without_fps_limit(self):
        """
        Runs the engine loop without any FPS limit.
        Continuously calls the update method and renders the display.
        """
        while True:
            self.update()
            self.display.render()

    def _run_with_fps_limit(self, fps: float | None = None):
        """
        Runs the engine loop with an optional FPS limit.

        :param fps: The desired frames per second. If None, runs without FPS limit.
        """
        last_time = time.time()
        while True:
            if fps is not None:
                current_time = time.time()
                elapsed_time = current_time - last_time

                if elapsed_time < fps:
                    time.sleep(fps - elapsed_time)

                last_time = time.time()

            self.update()
            self.display.render()

    def run(self, fps: float | None = None):
        """
        Starts the engine, either with or without FPS limit.

        :param fps: The desired frames per second. If provided, runs with FPS limit.
        """
        if fps:
            self._run_with_fps_limit(fps)
        self._run_without_fps_limit()
