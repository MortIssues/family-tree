import pygame
import threading
from command_interface import CommandInterface


def run_pygame(cli, lock):
    """
    Initialises and runs the pygame main loop

    Args:
        cli (CommandInterface): Command interface object for retrieving up-to-date data.
        lock (threading.Lock): Lock object for ensuring consistency.
    """

    pygame.init()

    WIDTH = 800
    HEIGHT = 800
    BACKGROUND_COL = (18, 18, 18)

    display = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Family Tree')

    dragging_node = None

    # Start the main loop.
    running = True
    while running:

        # Cycle through events.
        for event in pygame.event.get():
            # Check for quit.
            if event.type == pygame.QUIT:
                running = False

            # Check for left click.
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                with lock:
                    if cli.graph:
                        # Cycle through nodes to see if one has been clicked and set dragging_node if it has.
                        for node in cli.graph.nodes:
                            node = cli.graph.nodes[node]
                            if node.is_clicked(event.pos):
                                dragging_node = node
                                mouse_offset = (node.x - event.pos[0], node.y - event.pos[1])

            # Check for a mouse motion.
            elif event.type == pygame.MOUSEMOTION:
                with lock:
                    # Move node along with mouse if there is a clicked node.
                    if dragging_node:
                        new_x = event.pos[0] + mouse_offset[0]
                        new_y = event.pos[1] + mouse_offset[1]
                        dragging_node.x = new_x
                        dragging_node.y = new_y

            # Check for left click being released.
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                # If there is a clicked node release it.
                if dragging_node:
                    dragging_node = None

        # Draw things to screen.
        display.fill(BACKGROUND_COL)

        with lock:
            if cli.graph:
                graph = cli.graph
                graph.draw_connections(display)
                graph.draw(display)

        pygame.display.update()

    # Quit on exit.
    cli.do_quit()
    pygame.quit()

def main():
    # Set up multithreading so that both the command loop and pygame loop can run similtaneously including a lock for information syncing.
    # Note: Cmd2 throws a hissy fit if its not the main thread.
    lock = threading.Lock()
    cli = CommandInterface(lock)

    pygame_thread = threading.Thread(target=run_pygame, args=(cli, lock), daemon=True)
    pygame_thread.start()

    cli.cmdloop()

if __name__ == '__main__':
    main()