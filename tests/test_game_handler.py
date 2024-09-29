import pytest

from game_handler import WumpusGameInterface, WumpusGameState


def test_update_game_state_with_bat_teleport():
    game = WumpusGameInterface()

    # test input
    game_outputs = [
        "5",
        "ZAP--SUPER BAT SNATCH! ELSEWHEREVILLE FOR YOU!",
        "",
        "I SMELL A WUMPUS!",
        "BATS NEARBY!",
        "YOU ARE IN ROOM 6",
        "TUNNELS LEAD TO 5 7 15",
        "",
        "SHOOT OR MOVE (S-M)",
    ]

    # get the game state
    for output in game_outputs:
        game._update_game_state(output)

    # verify the game state
    assert isinstance(game.game_state, WumpusGameState)
    assert game.game_state.current_room == 6
    assert game.game_state.adjacent_rooms == [5, 7, 15]
    assert game.game_state.bat_nearby == True
    assert game.game_state.draft_felt == False
    assert game.game_state.wumpus_smell == True
    assert game.game_state.arrows_left == 5
    assert game.game_state.game_over == False
    assert game.game_state.win_state == False

    # print the final state for debugging
    print(f"\nFinal game state: {game.game_state}")


def test_update_game_state_with_draft_felt():
    game = WumpusGameInterface()

    # test input
    game_outputs = [
        "12",
        "",
        "I FEEL A DRAFT",
        "YOU ARE IN ROOM 12",
        "TUNNELS LEAD TO 3 11 13",
        "",
        "SHOOT OR MOVE (S-M)",
    ]

    # get the game state
    for output in game_outputs:
        game._update_game_state(output)

    # verify the game state
    assert isinstance(game.game_state, WumpusGameState)
    assert game.game_state.current_room == 12
    assert game.game_state.adjacent_rooms == [3, 11, 13]
    assert game.game_state.bat_nearby == False
    assert game.game_state.draft_felt == True
    assert game.game_state.wumpus_smell == False
    assert game.game_state.arrows_left == 5
    assert game.game_state.game_over == False
    assert game.game_state.win_state == False

    # print the final state for debugging
    print(f"\nFinal game state: {game.game_state}")


# def test_update_game_state_with_pit_fall():
#     game = WumpusGameInterface()

#     # test input
#     game_outputs = [
#         '5',
#         'YYYIIIIEEEE...FELL IN PIT',
#         '',
#         'I SMELL A WUMPUS!',
#         'BATS NEARBY!',
#         'YOU ARE IN ROOM 6',
#         'TUNNELS LEAD TO 5 7 15',
#         '',
#         'SHOOT OR MOVE (S-M)'
#     ]

#     # get the game state
#     for output in game_outputs:
#         game._update_game_state(output)

#     # verify the game state
#     assert isinstance(game.game_state, WumpusGameState)
#     assert game.game_state.current_room == 6
#     assert game.game_state.adjacent_rooms == [5, 7, 15]
#     assert game.game_state.bat_nearby == True
#     assert game.game_state.draft_felt == False
#     assert game.game_state.wumpus_smell == True
#     assert game.game_state.arrows_left == 5
#     assert game.game_state.game_over == True
#     assert game.game_state.win_state == False

#     # print the final state for debugging
#     print(f"\nFinal game state: {game.game_state}")
