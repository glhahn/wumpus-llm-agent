import logging
from datetime import datetime

from game_db import GameMetrics, WumpusDB
from game_handler import WumpusGameInterface
from game_planner import GamePlanner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

instructor_logger = logging.getLogger("instructor")
instructor_logger.setLevel(logging.INFO)

litellm_logger = logging.getLogger("litellm")
litellm_logger.setLevel(logging.INFO)


def run_game(db: WumpusDB):
    # initialize metrics tracking
    start_time = datetime.now()
    turns = 0
    response_times = []

    game_handler = WumpusGameInterface()
    planner = GamePlanner(game_handler)

    try:
        # start game
        game_handler.start_game()
        logger.info("* Game started successfully.")

        # main game loop
        while not game_handler.get_game_state().game_over:
            turns += 1

            try:
                # record response time
                response_start = datetime.now()
                action, game_state = planner.play_turn()
                response_time = (datetime.now() - response_start).total_seconds()
                response_times.append(response_time)

                logger.info(
                    "* Turn completed - Action: %s Room: %s - Reasoning: %s",
                    action.action,
                    action.room,
                    action.reasoning,
                )

            except Exception as e:
                logger.error("* Error during game play: %s", str(e))
                break

    except Exception as e:
        logger.error("* Error during game initialization: %s", str(e))

    finally:
        # record final state and metrics
        final_state = game_handler.get_game_state()

        if final_state.win_state:
            logger.info("* Game won!")
        else:
            logger.info("* Game over.")

        # calculate metrics
        total_time = sum(response_times)
        avg_time = total_time / len(response_times) if response_times else 0

        # save metrics to database
        metrics = GameMetrics(
            timestamp=start_time,
            num_turns=turns,
            rooms_explored=len(final_state.explored_rooms),
            death_by_pit=final_state.game_over 
                and "FELL IN PIT" in ",".join(final_state.last_output),
            death_by_wumpus=final_state.game_over
                and "WUMPUS GOT YOU" in ",".join(final_state.last_output),
            death_by_arrows=final_state.game_over
                and "RAN OUT OF ARROWS" in ",".join(final_state.last_output),
            game_won=final_state.win_state,
            arrows_remaining=final_state.arrows_left,
            action_generation_errors=planner.action_generation_errors,
            average_response_time=avg_time,
            total_response_time=total_time,
        )

        db.add_game_metrics(metrics)
        logger.info("* Game session ended and metrics recorded.")


def main():
    db = WumpusDB()

    run_game(db)


if __name__ == "__main__":
    main()
