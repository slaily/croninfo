"""
Instruction for running the script:

    Example with using pipe:
        python3 application.py 16:10 < config_file

    Example without using pipe:
        python3 application.py 16:10 <config_file≥
"""
import fileinput

from datetime import datetime
from argparse import ArgumentParser


def _is_time_slot_available(current_time, target_time):
    """
        Evaluates the time slot availability according to
        the current time and the target time.
    """
    if current_time == '*':
        return True

    if int(current_time) >= int(target_time):
        return True

    return False


def is_input_time_format_valid(input_time_str):
    """
        Validates the format of the input time argument `HH:MM`.
    """
    try:
        input_time = datetime.strptime(input_time_str, '%H:%M')

        return True, input_time
    except ValueError as exc:
        print(f'*** Invalid Time Format ***')
        print(f'*** {str(exc)} ***')
        print(f'***************************')

        return False, None


def is_today(conf_minute, input_minute, conf_hour, input_hour):
    """
        Checks are the time slot for today is available.
    """
    return (
        _is_time_slot_available(conf_minute, input_minute) and
        _is_time_slot_available(conf_hour, input_hour)
    )


def format_soonest_time(conf_minute, input_minute, conf_hour, input_hour):
    """
        Formats the output line time according to the patterns.
    """
    if conf_minute == '*' and conf_hour == '*':
        return ':'.join([str(input_hour), str(input_minute)])

    hour = input_hour if conf_hour == '*' else conf_hour
    minute = '00' if conf_minute == '*' else conf_minute

    return ':'.join([str(hour), str(minute)])


def content_processor(*args):
    """
        Processes the content from the cron config line by line.
    """
    content, input_time = args

    for line in content:
        day = 'tomorrow'
        minute, hour, command_to_run = line.split(' ')

        if is_today(minute, input_time.minute, hour, input_time.hour):
            day = 'today'

        time = format_soonest_time(minute, input_time.minute, hour, input_time.hour)

        yield f'{time} {day} - {command_to_run}'


def process():
    # The command line parser
    parser = ArgumentParser()
    parser.add_argument('time', help='Enter the time in format HH:MM')
    parser.add_argument(
        'files',
        metavar='FILE',
        nargs='*',
        help='Pipe of file/files to read'
    )
    # Parse the command line arguments
    args = parser.parse_args()
    # Validate the input argument
    is_input_valid, input_time = is_input_time_format_valid(args.time)

    if not is_input_valid:
        return None

    files_args = args.files if len(args.files) > 0 else ('-', )
    content = (line.strip() for line in fileinput.input(files=files_args))

    # Processing the content and outputing the results
    for output_line in content_processor(content, input_time):
        print(output_line)


process()