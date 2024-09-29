import logging
import os
from typing import Literal, Tuple

import instructor
from litellm import completion
from pydantic import BaseModel, Field

from game_handler import WumpusGameInterface, WumpusGameState

logger = logging.getLogger(__name__)


class GameAction(BaseModel):
    """
    Represents a single action in the Hunt the Wumpus game.
    The agent must either move to an adjacent room or shoot an arrow into a room.
    """

    action: Literal["move", "shoot"] = Field(
        description="The type of action to take. Must be either 'move' to enter an adjacent room, or "
        "'shoot' to fire an arrow.",
        examples=["move", "shoot"],
    )

    room: int = Field(
        description="The room number for the action. The number should be in the current list of adjacent rooms. "
        "When moving, specifies which adjacent room to enter. When shooting, specifies which room to fire "
        "the arrow into.",
        examples=[1, 13, 11],
    )

    # num_rooms: int = Field(
    #     description="The number of rooms to shoot through with an arrow. Must be a positive integer, 1-5.",
    #     ge=1,
    #     le=5,
    #     examples=[1, 2, 3, 4, 5]
    # )

    reasoning: str = Field(
        description="A brief explanation of why this action was chosen, considering strategy and available information "
        "about hazards.",
        min_length=10,
        max_length=200,
        examples=[
            "Moving to room 10 to explore a safe adjacent room with no detected hazards.",
            "Shooting into 2 because we detected Wumpus smell and the room layout suggests it's likely there.",
            "Moving to 18 to avoid the detected pit (draft) in room 20.",
        ],
    )


class GamePlanner:
    def __init__(self, game_handler: WumpusGameInterface) -> None:
        """
        Initialize the game planner with a game handler instance.

        Args:
            game_handler: Instance of the WumpusGameInterface
        """
        self.game_handler = game_handler
        self.action_generation_errors = 0

        self.model_name = os.environ.get("LITELLM_MODEL")
        self.client = instructor.from_litellm(completion, mode=instructor.Mode.JSON)

        logger.info("* Initialized GamePlanner")

    def get_next_action(self, game_state: WumpusGameState) -> GameAction:
        """
        Determine the next action based on current game state and strategy.

        Args:
            game_state: Current WumpusGameState

        Returns:
            GameAction object containing the next action to take
        """

        # add system message to enforce response format
        system_message = """
        You are a game-playing agent that must respond with ONLY a JSON object.
        DO NOT include any other text, explanations, or code blocks.
        The JSON must have exactly these fields:
        - "action": either "move" or "shoot"
        - "room": an integer room number
        - "num_rooms": (only for shoot actions) integer 1-5
        - "reasoning": brief explanation (maximum 200 characters)"""

        unexplored_adjacent = [
            room
            for room in game_state.adjacent_rooms
            if room not in game_state.explored_rooms
        ]

        action_prompt = f"""
        Current game state:
        - You are in room {game_state.current_room}
        - Adjacent rooms: {game_state.adjacent_rooms}
        - UNEXPLORED adjacent rooms: {', '.join(str(x) for x in sorted(unexplored_adjacent))}
        - Hazards detected:
          * Bats nearby: {game_state.bat_nearby}
          * Draft felt: {game_state.draft_felt}
          * Wumpus smell: {game_state.wumpus_smell} {'(IMMEDIATE DANGER - CONSIDER SHOOTING!)' if game_state.wumpus_smell else ''}
        - Arrows remaining: {game_state.arrows_left}
        
        Strategy to follow: To win the game of Hunt the Wumpus, I will adopt a strategic approach that prioritizes safe exploration, 
        efficient use of hazard indicators, and optimal arrow usage. Here's a high-level strategy:

        1. Safe exploration:
        I will start by exploring adjacent rooms and use the hazard indicators to identify dangerous areas. I will avoid rooms with 
        drafts, foul smells, or bat sounds, as they may contain the Wumpus or pits. I will also keep track of the room connectivity 
        and navigate through safe paths.

        2. Using hazard indicators:
        I will pay close attention to the hazard indicators (drafts, smells, bat sounds) and use them to make informed decisions about 
        which rooms to explore next. For instance, if I detect a draft or a foul smell in a room, I will avoid it and move on to the 
        next room. If I hear bat sounds, I will mark that room as a potential location of the Wumpus and avoid it for the time being.

        3. Risk assessment for movements:
        I will assess the risk of each movement carefully before making a decision. I will consider the information I have gathered 
        from the hazard indicators and the connectivity of the rooms. I will also prioritize exploring rooms that are less risky based 
        on the available information.

        4. Optimal arrow usage:
        I will use my arrows strategically to eliminate potential Wumpus locations. I will aim for rooms that have a high probability 
        of containing the Wumpus based on the hazard indicators and room connectivity. I will also consider the risk of each shot and 
        avoid taking unnecessary risks. I will try to save at least one arrow for the final shot, if possible.

        5. Room connectivity and navigation:
        I will keep track of the room connectivity and use it to navigate through the caves efficiently. I will try to explore rooms 
        that are connected to each other, as they are less risky than exploring rooms that are isolated. I will also try to create a 
        mental map of the cave system to help me navigate through it more effectively.

        By following this strategy, I aim to explore the cave system safely, identify the location of the Wumpus, and eliminate it using 
        my arrows efficiently.
        
        Based on the current game state and strategy, what should be the next action?

        Consider:
        1. Prioritize unexplored rooms unless there is a clear danger based on detected hazards
           - You have already explored these rooms: {', '.join(str(x) for x in sorted(game_state.explored_rooms))}
        2. If you smell a Wumpus and have arrows, consider shooting before moving
        3. NEVER enter a room where you've detected a Wumpus smell unless you've shot an arrow first
        4. Avoid moving back to the previous room unless absolutely necessary
        5. If all adjacent rooms have been explored:
           - If you smell a Wumpus, SHOOT in the most likely direction
           - Otherwise, move through an explored room to reach unexplored areas
        6. Previous game output: {game_state.last_output}

        RESPOND WITH ONLY A SINGLE JSON OBJECT:
        For move actions:
        {{"action": "move", "room": <adjacent_room>, "reasoning": "<brief_reason>"}}

        For shoot actions:
        {{"action": "shoot", "room": <target_room>, "reasoning": "<brief_reason>"}}

        REQUIREMENTS:
        1. reasoning must be less than 200 characters
        2. room must be an integer
        3. DO NOT include code blocks, explanations, or any other text
        4. DO NOT use placeholders like <adjacent_room> - use actual numbers
        """

        try:
            action = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": action_prompt},
                ],
                response_model=GameAction,
            )
            logger.info("* Generated action: %s %s", action.action, action.room)
            return action

        except Exception as e:
            logger.error("* Error generating action: %s", str(e))
            self.action_generation_errors += 1
            raise

    def execute_action(self, action: GameAction) -> WumpusGameState:
        """
        Execute the given action using the game handler.

        Args:
            action: GameAction object containing the action to execute

        Returns:
            Updated WumpusGameState after executing the action
        """
        logger.info("* Executing action: %s %s", action.action, action.room)

        if action.action == "move":
            self.game_handler.move(action.room)
        elif action.action == "shoot":
            self.game_handler.shoot(action.room)
        else:
            raise ValueError(f"Invalid action: {action.action}")

        return self.game_handler.get_game_state()

    def play_turn(self) -> Tuple[GameAction, WumpusGameState]:
        """
        Play a single turn of the game.

        Returns:
            Tuple of (action taken, resulting game state)
        """
        current_state = self.game_handler.get_game_state()
        action = self.get_next_action(current_state)
        new_state = self.execute_action(action)
        return action, new_state
