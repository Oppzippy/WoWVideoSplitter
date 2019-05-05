#!/usr/bin/env python3

import re
import platform
import os
import math
import subprocess
import click
import requests

# Util
def clamp(num, min_val, max_val):
    if num < min_val:
        return min_val
    if num > max_val:
        return max_val
    return num

# WCL
class WCLReport:
    def __init__(self, api_key, report, fights=None):
        self.api_key = api_key
        self.report = report
        self.fights = fights

    def get_time_bounds(self):
        url = f'https://www.warcraftlogs.com/reports/{self.report}'
        response = requests.get(url)
        text = response.text
        start_match = re.search('^var start_time = ([0-9]+);$', text, re.MULTILINE)
        end_match = re.search('^var end_time = ([0-9]+);$', text, re.MULTILINE)
        return int(start_match[1]), int(end_match[1])

    def get_fight_times(self, bosses_only=True):
        url = f'https://www.warcraftlogs.com/v1/report/fights/{self.report}?api_key={self.api_key}'
        response = requests.get(url)
        json = response.json()
        fight_times = [
            {
                'start_time': f['start_time'],
                'end_time': f['end_time'],
                'id': f['id']
            } for f in json['fights']
            if (not self.fights or f['id'] in self.fights) and (not bosses_only or f.get('boss', 0) != 0)
        ]
        return fight_times

# Video file
def get_creation_time(path):
    if platform.system() == 'Windows':
        return os.path.getctime(path) * 1000, os.path.getmtime(path) * 1000
    raise Exception('Automatic file creation time is not available on operating systems other than Windows')

# FFmpeg
class VideoSplitter:
    def __init__(self, report, input_file, output_file):
        self.report = report
        self.input_file = input_file
        self.output_file = output_file

    @classmethod
    def ms_to_time(cls, ms):
        # pylint: disable=C0103
        seconds = math.floor(ms / 1000) % 60
        minutes = math.floor(ms / 1000 / 60) % 60
        hours = math.floor(ms / 1000 / 60 / 60)
        return '%d:%02d:%02d' % (hours, minutes, seconds)

    def generate_ffmpeg_command(self, video_id, start_time, duration, options):
        return [
            'ffmpeg',
            '-ss', start_time,
            '-i', self.input_file,
            *options,
            '-t', duration,
            '-avoid_negative_ts', '1',
            self.output_file % video_id
        ]

    def generate_ffmpeg_commands(self, clips, options):
        commands = [
            self.generate_ffmpeg_command(
                video['id'], video['start_time'], video['duration'], options
            )
            for video in clips
        ]
        return commands

    def split(self, creation_time, modified_time, start_padding, end_padding):
        fight_times = self.report.get_fight_times()
        report_start_time, _ = self.report.get_time_bounds()
        clips = []
        for fight in fight_times:
            start_time = fight['start_time'] + report_start_time - start_padding
            end_time = fight['end_time'] + report_start_time + end_padding

            start_time = clamp(start_time, creation_time, modified_time)
            end_time = clamp(end_time, creation_time, modified_time)
            duration = end_time - start_time

            if start_time < end_time <= modified_time:
                clips.append({
                    'start_time': self.ms_to_time(start_time - creation_time),
                    'end_time': self.ms_to_time(end_time - creation_time),
                    'duration': self.ms_to_time(duration),
                    'id': fight['id']
                })
        return clips

# Argument validators

def validate_fights(ctx, param, value):
    if not value:
        return
    range_match = re.search('^([0-9]+)-([0-9]+)$', value)
    list_match = re.findall('([0-9]+),?', value)
    if range_match:
        start = int(range_match[1])
        end = int(range_match[2])
        if start > end:
            start, end = end, start
        return range(start, end + 1)
    if list_match:
        fights = [int(fight) for fight in list_match]
        return fights
    raise click.BadParameter('Fights must be formated as 1-5 or 1,2,3,4,5')

def validate_output(ctx, param, value):
    if not re.search('%[0-9]*d', value):
        raise click.BadParameter('Output file must contain %d, which will be the fight id')
    return value

def validate_start_padding(ctx, param, value):
    return value * 1000

def validate_end_padding(ctx, param, value):
    return value * 1000 # Default is 10

def validate_options(ctx, param, value):
    options = value.split(' ') if value else []
    if '-map' not in options:
        options.insert(0, '-map')
        options.insert(1, '0')
    if '-vcodec' not in options and '-c:v' not in options:
        options.append('-c:v')
        options.append('copy')
    if '-acodec' not in options and '-c:a' not in options:
        options.append('-c:a')
        options.append('copy')
    return options

@click.command()
@click.option('-i', '--input', type=click.Path(), help='Video file input', required=True)
@click.option('-r', '--report', type=str, help='WarcraftLogs report id', required=True)
@click.option('-o', '--output', type=click.Path(), help='Video file output', required=True, callback=validate_output)
@click.option('-k', '--api_key', type=str, help='WarcraftLogs API Key', required=True)
@click.option('--fights', type=str, help='Whitelist of fights to export', callback=validate_fights)
@click.option('--creation_time', type=int, help='Override file creation time')
@click.option('--modified_time', type=int, help='Override file modified time')
@click.option('--start_padding', type=int, default=5, help='Number of seconds to include before the fight', callback=validate_start_padding)
@click.option('--end_padding', type=int, default=10, help='Number of seconds to include after the fight', callback=validate_end_padding)
@click.option('--ffmpeg_options', type=str, help='Custom ffmpeg options', callback=validate_options)
@click.option('--print', 'printCommands', flag_value=True, default=False, help='Print ffmpeg commands instead of running them')
def main(**args):
    # Get creation time from OS if not specified
    if args.get('creation_time') is None or args.get('modified_time') is None:
        args['creation_time'], args['modified_time'] = get_creation_time(args['input'])

    report = WCLReport(args['api_key'], args['report'], args['fights'])
    vsplitter = VideoSplitter(report, args['input'], args['output'])
    clips = vsplitter.split(args['creation_time'], args['modified_time'], args['start_padding'], args['end_padding'])
    commands = vsplitter.generate_ffmpeg_commands(clips, args['ffmpeg_options'])

    if args.get('printCommands'):
        for command in commands:
            print(' '.join(command))
    else:
        subprocess.call(command)


if __name__ == '__main__':
    main()
