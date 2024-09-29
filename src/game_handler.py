import logging
from dataclasses import dataclass, field
from typing import List

import pexpect

logger = logging.getLogger(__name__)


@dataclass
class WumpusGameState:
    current_room: int = 0
    adjacent_rooms: List[int] = field(default_factory=list)
    explored_rooms: set[int] = field(default_factory=set)
    bat_nearby: bool = False
    draft_felt: bool = False
    wumpus_smell: bool = False
    arrows_left: int = 5
    game_over: bool = False
    win_state: bool = False
    last_output: str = ""


class WumpusGameInterface:
    def __init__(self, game_cmd="wumpus") -> None:
        self.game_cmd = game_cmd
        self.game_process = None
        self.game_state = WumpusGameState()

    def start_game(self) -> None:
        logger.info("* Starting Wumpus game ...")
        self.game_process = pexpect.spawn(self.game_cmd)
        self._process_game_output()
        self._send_command("N")
        self._process_game_output()
        logger.info("* Game started. Initial state: %s", self.game_state)

    def move(self, room) -> None:
        logger.info("* Attempting to move to: %s", room)
        self._send_command("M")
        self._process_game_output()
        self._send_command(f"{room}")
        self._process_game_output()
        logger.info("* Move completed. New state: %s", self.game_state)
        self.game_state.explored_rooms.add(room)

    def shoot(self, room, num_rooms=1) -> None:
        logger.info("* Attempting to shoot arrow into: %s", room)
        self._send_command("S")
        self._process_game_output()
        self._send_command(f"{num_rooms}")
        self._process_game_output()
        self._send_command(f"{room}")
        self._process_game_output()
        self.game_state.arrows_left -= 1
        logger.info("* Shot completed. New state: %s", self.game_state)

    def get_game_state(self) -> WumpusGameState:
        return self.game_state

    def exit_game(self) -> None:
        logger.info("* Exiting game ...")
        if self.game_process:
            try:
                # check if the process is still alive
                if not self.game_process.terminated:
                    self.game_process.sendintr()
                    try:
                        # wait for process to terminate with timeout
                        self.game_process.expect(pexpect.EOF, timeout=5)
                    except (pexpect.TIMEOUT, pexpect.EOF):
                        # if timeout or EOF, force kill
                        self.game_process.terminate(force=True)
            except OSError as e:
                logger.debug("* Process already terminated: %s", str(e))
            finally:
                self.game_process = None
                self.game_state.game_over = True

    def _send_command(self, command) -> None:
        if self.game_process:
            self.game_process.sendline(command)

    def _process_game_output(self, timeout=5) -> None:
        if not self.game_process:
            return

        try:
            self.game_process.expect(r"\?", timeout=timeout)
            output = self.game_process.before.decode("utf-8").strip()
        except pexpect.TIMEOUT:
            logger.warning("* Timeout reached while waiting for game output.")
            output = self.game_process.before.decode("utf-8").strip()
        except pexpect.EOF:
            logger.warning("* Game process ended unexpectedly.")
            output = self.game_process.before.decode("utf-8").strip()

        self.game_state.last_output = [s.rstrip() for s in output.split("\n")]

        # reset environment flags
        self.game_state.bat_nearby = False
        self.game_state.draft_felt = False
        self.game_state.wumpus_smell = False

        for line in self.game_state.last_output:
            self._update_game_state(line)
        logger.debug("* Processed game output: %s", output)

        if self.game_state.game_over:
            self.exit_game()

    def _update_game_state(self, output) -> None:
        # convert to uppercase to handle all-caps text
        output = output.upper()

        print(output)

        if "YOU ARE IN ROOM" in output:
            self.game_state.current_room = int(output.split()[-1])
        if "TUNNELS LEAD TO" in output:
            self.game_state.adjacent_rooms = [int(room) for room in output.split()[-3:]]
        if "BATS NEARBY" in output:
            self.game_state.bat_nearby = True
        if "FEEL A DRAFT" in output:
            self.game_state.draft_felt = True
        if "SMELL A WUMPUS" in output:
            self.game_state.wumpus_smell = True
        if (
            "WUMPUS GOT YOU" in output
            or "YOU RAN OUT OF ARROWS" in output
            or "FELL IN PIT" in output
        ):
            self.game_state.game_over = True
            self.game_state.win_state = False
        if "YOU GOT THE WUMPUS" in output:
            self.game_state.game_over = True
            self.game_state.win_state = True
