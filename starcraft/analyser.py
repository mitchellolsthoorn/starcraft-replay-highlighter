#!/usr/local/bin/python
import argparse
import csv
import logging
import os
import time
# import statistics
import sys

root = logging.getLogger()
root.setLevel(logging.DEBUG)


def data_from_csv(folder_location):
    with open(os.path.join(folder_location, 'replay.csv'), 'rb') as replay_stream:
        replay_data = list(csv.reader(replay_stream))
    with open(os.path.join(folder_location, 'playerreplay.csv'), 'rb') as player_stream:
        player_data = list(csv.reader(player_stream))
    with open(os.path.join(folder_location, 'unit.csv'), 'rb') as unit_stream:
        unit_data = list(csv.reader(unit_stream))
    with open(os.path.join(folder_location, 'action.csv'), 'rb') as action_stream:
        action_data = list(csv.reader(action_stream))

    return replay_data, player_data, unit_data, action_data


WINDOW_SIZE = 100
FRAME_DURATION = 0.042
BOT_THRESHOLD = 400


def process_actions(action_data):
    game_data = {0: dict(), 1: dict()}

    for action in action_data:
        player_number = int(action[0])
        frame_number = int(action[1])

        window_number = int(frame_number / WINDOW_SIZE)

        window_list = game_data[player_number - 1].get(window_number, [])
        window_list.append(action)

        if len(window_list) == 1:  # first item added
            game_data[player_number - 1][window_number] = window_list

    return game_data


def analyse_processed_action_data(processed_action_data):
    player1_data = []
    player1_min_apm = sys.maxsize
    player1_max_apm = 0

    for window_number, actions in processed_action_data[0].iteritems():
        num_of_actions = len(actions)
        apm = num_of_actions * (60 / (WINDOW_SIZE * FRAME_DURATION))

        player1_data.append(apm)

        player1_min_apm = apm if apm < player1_min_apm else player1_min_apm
        player1_max_apm = apm if apm > player1_max_apm else player1_max_apm

    player1_avg_apm = sum(player1_data) / len(player1_data)
    player1_bot = True if player1_avg_apm > BOT_THRESHOLD else False

    player1 = argparse.Namespace(
        max=player1_max_apm,
        min=player1_min_apm,
        avg=player1_avg_apm,
        bot=player1_bot
    )

    player2_data = []
    player2_min_apm = 0
    player2_max_apm = 0

    for window_number, actions in processed_action_data[1].iteritems():
        num_of_actions = len(actions)
        apm = num_of_actions * (60 / (WINDOW_SIZE * FRAME_DURATION))

        player2_data.append(apm)

        player2_min_apm = apm if apm < player2_min_apm else player2_min_apm
        player2_max_apm = apm if apm > player2_max_apm else player2_max_apm

    player2_avg_apm = sum(player2_data)/len(player2_data)
    player2_bot = True if player2_avg_apm > BOT_THRESHOLD else False

    player2 = argparse.Namespace(
        max=player2_max_apm,
        min=player2_min_apm,
        avg=player2_avg_apm,
        bot=player2_bot
    )

    return player1, player2, None


def main():
    logging.info('Started')
    start = time.time()

    parser = argparse.ArgumentParser(description='Starcraft replay analyser.')
    parser.add_argument('folder', type=str, help='location to the replay folder')
    args = parser.parse_args()

    dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    os.chdir(dir_path)

    data = data_from_csv(args.folder)
    (replay_data, player_data, unit_data, action_data) = data

    # Replay
    logging.info('Analysing {replay} replay file'.format(replay=replay_data[0][0]))

    # Players
    logging.info('Players: {player_data[0][0]} vs {player_data[1][0]}'.format(player_data=player_data))

    processed_action_data = process_actions(action_data)
    player1, player2, game_data = analyse_processed_action_data(processed_action_data)

    logging.info(
        'Player 1: min {player.min}, avg {player.avg}, max {player.max}, bot {player.bot}'.format(player=player1))
    logging.info(
        'Player 2: min {player.min}, avg {player.avg}, max {player.max}, bot {player.bot}'.format(player=player2))

    end = time.time()
    logging.info('Finished in {time} seconds'.format(time=end - start))


if __name__ == '__main__':
    main()
