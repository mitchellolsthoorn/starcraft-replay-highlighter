#!/usr/local/bin/python
import argparse
import csv
import logging
import os
import time
import sys
import numpy as np

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
DISTANCE_THRESHOLD = 100
COMPRESSION_LENGTH = 2 #in windows, highlights that are within COMPRESSION_LENGTH windows of eachother will be merged.
ATTACK_COMPRESSION = 2 #in windows

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
    player1_apm_data = []
    player1_attack_data = []
    player1_x_data = []
    player1_y_data = []
    player1_attack_x_data = []
    player1_attack_y_data = []
    player1_min_apm = (sys.maxsize, 0)
    player1_max_apm = (0, 0)

    for window_number, actions in processed_action_data[0].iteritems():
        num_of_actions = len(actions)
        apm = num_of_actions * (60 / (WINDOW_SIZE * FRAME_DURATION))

        player1_apm_data.append(apm)
        player1_min_apm = (apm, window_number) if apm < player1_min_apm[0] else player1_min_apm
        player1_max_apm = (apm, window_number) if apm > player1_max_apm[0] else player1_max_apm

        num_of_attacks = 0
        attack_x_data = []
        attack_y_data = []
        x_list = []
        y_list = []
        for action in actions:
            if int(action[3]) == 8 or int(action[3]) == 14:
                num_of_attacks = num_of_attacks + 1
                attack_x_data.append(int(action[6]))
                attack_y_data.append(int(action[7]))

            x_coord = int(action[6])
            y_coord = int(action[7])
            #print '({x},{y}) '.format(x=x_coord, y=y_coord)
            x_list.append(x_coord)
            y_list.append(y_coord)

        player1_attack_data.append(num_of_attacks)
        x_mean = np.average(x_list)
        y_mean = np.average(y_list)
        player1_x_data.append(int(x_mean))
        player1_y_data.append(int(y_mean))
        #print 'Avg: ({x},{y}) '.format(x=x_mean, y=y_mean)
        #print '======'

        player1_attack_x_data = player1_attack_x_data + attack_x_data
        player1_attack_y_data = player1_attack_y_data + attack_y_data

    player1_avg_apm = sum(player1_apm_data) / len(player1_apm_data)
    player1_bot = True if player1_avg_apm > BOT_THRESHOLD else False

    player1 = argparse.Namespace(
        max=player1_max_apm,
        min=player1_min_apm,
        avg=player1_avg_apm,
        bot=player1_bot
    )

    player2_apm_data = []
    player2_attack_data = []
    player2_x_data = []
    player2_y_data = []
    player2_attack_x_data = []
    player2_attack_y_data = []
    player2_min_apm = (sys.maxsize, 0)
    player2_max_apm = (0, 0)

    for window_number, actions in processed_action_data[1].iteritems():
        num_of_actions = len(actions)
        apm = num_of_actions * (60 / (WINDOW_SIZE * FRAME_DURATION))

        player2_apm_data.append(apm)
        player2_min_apm = (apm, window_number) if apm < player2_min_apm[0] else player2_min_apm
        player2_max_apm = (apm, window_number) if apm > player2_max_apm[0] else player2_max_apm

        num_of_attacks = 0
        attack_x_data = []
        attack_y_data = []
        x_list = []
        y_list = []
        for action in actions:
            if int(action[3]) == 8 or int(action[3]) == 14:
                num_of_attacks = num_of_attacks + 1
                attack_x_data.append(int(action[6]))
                attack_y_data.append(int(action[7]))

            x_coord = int(action[6])
            y_coord = int(action[7])
            x_list.append(x_coord)
            y_list.append(y_coord)

        player2_attack_data.append(num_of_attacks)
        x_mean = np.average(x_list)
        y_mean = np.average(y_list)
        player2_x_data.append(int(x_mean))
        player2_y_data.append(int(y_mean))
        player2_attack_x_data = player2_attack_x_data + attack_x_data
        player2_attack_y_data = player2_attack_y_data + attack_y_data

    player2_avg_apm = sum(player2_apm_data) / len(player2_apm_data)
    player2_bot = True if player2_avg_apm > BOT_THRESHOLD else False

    player2 = argparse.Namespace(
        max=player2_max_apm,
        min=player2_min_apm,
        avg=player2_avg_apm,
        bot=player2_bot
    )

    return player1, player1_apm_data, player1_attack_data, player1_x_data, player1_y_data, player1_attack_x_data, player1_attack_y_data, \
           player2, player2_apm_data, player2_attack_data, player2_x_data, player2_y_data, player2_attack_x_data, player2_attack_y_data


def make_apm_graph(player1_data, player2_data, location):
    import matplotlib.pyplot as plt

    fig_apm = plt.figure()
    ax1 = fig_apm.add_subplot(111)
    x1 = [x * FRAME_DURATION * WINDOW_SIZE for x in range(0, len(player1_data))]
    x2 = [x * FRAME_DURATION * WINDOW_SIZE for x in range(0, len(player2_data))]
    bot_line, = ax1.plot([0, max(max(x1, x2))], [BOT_THRESHOLD, BOT_THRESHOLD])
    bot_line.set_label('Bot Threshold')
    player1_line, = ax1.plot(x1, player1_data)
    player1_line.set_label('Player 1 APM')
    player2_line, = ax1.plot(x2, player2_data)
    player2_line.set_label('Player 2 APM')
    ax1.set_title('APM')
    ax1.set_xlabel('Time in seconds')
    ax1.set_ylabel('Actions per minute')
    ax1.legend()
    fig_apm.savefig(location + '/apm.png')
    logging.info('APM graph saved in: {location}/apm.png'.format(location=location))


def make_attack_graph(player1_data, player2_data, location):
    import matplotlib.pyplot as plt

    fig_attack = plt.figure()
    ax1 = fig_attack.add_subplot(111)
    x1 = [x * FRAME_DURATION * WINDOW_SIZE for x in range(0, len(player1_data))]
    x2 = [x * FRAME_DURATION * WINDOW_SIZE for x in range(0, len(player2_data))]
    player1_line, = ax1.plot(x1, player1_data)
    player1_line.set_label('Player 1 Attacks')
    player2_line, = ax1.plot(x2, player2_data)
    player2_line.set_label('Player 2 Attacks')
    ax1.set_title('Attacks')
    ax1.set_xlabel('Time in seconds')
    ax1.set_ylabel('Attacks per frame')
    ax1.legend()
    fig_attack.savefig(location + '/attack.png')
    logging.info('APM graph saved in: {location}/attack.png'.format(location=location))


def make_location_graph(player1_x_data, player1_y_data, player2_x_data, player2_y_data, player1_attack_x_data, player1_attack_y_data, player2_attack_x_data, player2_attack_y_data, common_coords, location):
    import matplotlib.pyplot as plt

    fig_location = plt.figure()
    ax1 = fig_location.add_subplot(111)
    player1_line = ax1.scatter(player1_x_data, player1_y_data)
    player1_line.set_label('Player 1 Location')
    player2_line = ax1.scatter(player2_x_data, player2_y_data)
    player2_line.set_label('Player 2 Location')
    player2_line = ax1.scatter(player1_attack_x_data, player1_attack_y_data)
    player2_line.set_label('Player 1 Attack Location')
    player2_line = ax1.scatter(player2_attack_x_data, player2_attack_y_data)
    player2_line.set_label('Player 2 Attack Location')
    if len(common_coords) > 0:
        x, y, ax, ay, bx, by = zip(*common_coords)
        common_line = ax1.scatter(list(x), list(y))
        common_line.set_label('Common Location')
    ax1.set_title('Location')
    ax1.set_xlabel('X Coord')
    ax1.set_ylabel('Y Coord')
    ax1.legend()
    fig_location.gca().invert_yaxis()
    fig_location.savefig(location + '/location.png')
    logging.info('APM graph saved in: {location}/location.png'.format(location=location))


def formatTime(seconds):
    minutes = int(seconds / 60)
    sec = int(seconds % 60) 
    if sec < 10:
        sec = '0' + str(sec)
    return '{minutes}:{seconds}'.format(minutes=minutes, seconds=sec)

def attack_highlights(attacks):
    average_attack_amount = 0

    for amount, frame in attacks:
        average_attack_amount += amount

    average_attack_amount = average_attack_amount / len(attacks)

    return filter(lambda x: x[0] > average_attack_amount, attacks)

def extract_duplicates(windows):
    seen = set()
    duplicates = dict()
    for x in windows:
        if x in seen:
            if x in duplicates:
                duplicates[x] += 1
            else:
                duplicates[x] = 1
        else:
            seen.add(x)

    return sorted(duplicates.items())

def compress_highlights(highlights):
    delete = []

    for i, val in enumerate(highlights[:-1]):
        if highlights[i+1] - highlights[i] <= COMPRESSION_LENGTH:
            highlights[i+1] = int( (highlights[i+1] + highlights[i]) / 2)
            delete.append(i)

    for i in reversed(delete):
        del highlights[i]

    return highlights

def compress_attacks(attacks):
    delete = []

    for i, val in enumerate(attacks[:-1]):
        if attacks[i+1][1] - attacks[i][1] <= ATTACK_COMPRESSION:
            attacks[i+1] = ( attacks[i+1][0] + attacks[i][0], int( (attacks[i+1][1] + attacks[i][1]) / 2) )
            delete.append(i)

    for i in reversed(delete):
        del attacks[i]

    return attacks


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

    # Action processing and analysing
    processed_action_data = process_actions(action_data)

    player1, player1_apm_data, player1_attack_data, player1_x_data, player1_y_data, player1_attack_x_data, player1_attack_y_data, \
    player2, player2_apm_data, player2_attack_data, player2_x_data, player2_y_data, player2_attack_x_data, player2_attack_y_data \
        = analyse_processed_action_data(processed_action_data)

    # APM info
    logging.info(
        'Player 1: min {player.min}, avg {player.avg}, max {player.max}, bot {player.bot}'.format(player=player1))
    logging.info(
        'Player 2: min {player.min}, avg {player.avg}, max {player.max}, bot {player.bot}'.format(player=player2))
    make_apm_graph(player1_apm_data, player2_apm_data, args.folder)

    # Attack info
    make_attack_graph(player1_attack_data, player2_attack_data, args.folder)
    player1_attack_windows = [index for index, e in enumerate(player1_attack_data) if e != 0]
    player1_attack_counts = map(lambda x: player1_attack_data[x], player1_attack_windows)
    player1_attack = zip(player1_attack_counts, player1_attack_windows)
    logging.info('Player 1 attacks: {attack}'.format(attack=player1_attack))
    player2_attack_windows = [index for index, e in enumerate(player2_attack_data) if e != 0]
    player2_attack_counts = map(lambda x: player2_attack_data[x], player2_attack_windows)
    player2_attack = zip(player2_attack_counts, player2_attack_windows)
    logging.info('Player 2 attacks: {attack}'.format(attack=player2_attack))
    attacks = player1_attack + player2_attack
    logging.info('Attacks: {attack}'.format(attack=attacks))

    # Location info
    common_coords = [
        (np.average([ax, bx]), np.average([ay, by]), ax, ay, bx, by)
        for (ax, ay), (bx, by)
        in zip(zip(player1_x_data, player1_y_data), zip(player2_x_data, player2_y_data))
        if abs(ax - bx) < DISTANCE_THRESHOLD and abs(ay - by) < DISTANCE_THRESHOLD
    ]
    common_windows = map(lambda coord: zip(player1_x_data, player1_y_data).index((coord[2], coord[3])), common_coords)
    logging.info('Common Coords: {coords}'.format(coords=zip(common_coords, common_windows)))
    make_location_graph(player1_x_data, player1_y_data, player2_x_data, player2_y_data, player1_attack_x_data, player1_attack_y_data, player2_attack_x_data, player2_attack_y_data, common_coords, args.folder)

    # Highlighting
    p1_apm_windows = player1.max[1]
    p2_apm_windows = player2.max[1]

    p1_compressed_attacks = compress_attacks(player1_attack)
    p2_compressed_attacks = compress_attacks(player2_attack)

    _, p1_attack_windows = zip(*p1_compressed_attacks)
    _, p2_attack_windows = zip(*p2_compressed_attacks)

    #print 'attacks, ' , p2_attack_windows

    #print 'p1 attack:' , player1_attack, ' --- ', len(player1_attack)
    #print 'p1 attack compressed', compress_highlights(player1_attack_windows), '----', len(compress_highlights(player1_attack_windows))

    #_, p1_attack_windows = zip(*attack_highlights(player1_attack))
    #_, p2_attack_windows = zip(*attack_highlights(player2_attack))
    #p1_attack_windows = player1_attack_windows
    #p2_attack_windows = player2_attack_windows

    common_windows = common_windows

    potential_interest_windows = [p1_apm_windows] + [p2_apm_windows] + list(p1_attack_windows) + list(player2_attack_windows) + common_windows
    potential_interest_windows = sorted(potential_interest_windows)
    #interest = extract_duplicates(potential_interest)

    #if(len(interest) <= 3):
    #   logging.info('Too few actual highlights. Added the potential highlights.')
    #   windows = sorted(potential_interest)
    #else:
    #   windows, _ = zip(*interest)

    #windows, x = zip(*interest)
    #print windows
    #print x
    #windows, _ = zip(*interest)

    windows = compress_highlights(potential_interest_windows)


    print 'Highlighting windows: ' + str(windows)
    print 'Highlighting times: ' + str(map(formatTime, map(lambda x: x * FRAME_DURATION * WINDOW_SIZE, windows)))
   
    # End
    end = time.time()
    logging.info('Finished in {time} seconds'.format(time=end - start))


if __name__ == '__main__':
    main()
