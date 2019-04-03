#!/usr/bin/env python3

import click
import requests
import re
import platform
import os
import math
import subprocess

# Util
def clamp(num, min, max):
	if num < min:
		return min
	elif num > max:
		return max
	return num

# WCL
def get_report_time(report):
	url = f'https://www.warcraftlogs.com/reports/{report}'
	response = requests.get(url)
	text = response.text
	start_match = re.search('^var start_time = ([0-9]+);$', text, re.MULTILINE)
	end_match = re.search('^var end_time = ([0-9]+);$', text, re.MULTILINE)
	return int(start_match[1]), int(end_match[1])

def get_report_fight_times(api_key, report, bosses_only=True):
	url = f'https://www.warcraftlogs.com/v1/report/fights/{report}?api_key={api_key}'
	response = requests.get(url)
	json = response.json()
	fight_times = [
		{
			'start_time': f['start_time'],
			'end_time': f['end_time'],
			'id': f['id']
		} for f in json['fights'] if not bosses_only or f['boss'] != 0
	]
	return fight_times

# Video file
def get_creation_time(path):
	if platform.system() == 'Windows':
		return os.path.getctime(path), os.path.getmtime(path)
	else:
		raise Exception('Automatic file creation time is not available on operating systems other than Windows')

# FFmpeg
def ms_to_time(ms):
	seconds = math.floor(ms / 1000) % 60
	minutes = math.floor(ms / 1000 / 60) % 60
	hours = math.floor(ms / 1000 / 60 / 60)
	return '%d:%02d:%02d' % (hours, minutes, seconds)

def generate_ffmpeg_command(input, output, vcodec, start_time, duration, id, options, ffmpeg_map, acodec):
	options = options.split(' ')
	return [
		'ffmpeg',
		'-ss', start_time,
		'-i', input,
		'-map', ffmpeg_map,
		'-t', duration,
		'-c:v', vcodec,
		'-c:a', acodec,
		'-avoid_negative_ts', '1',
		*options,
		output % id
	]

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
	elif list_match:
		fights = [int(fight) for fight in list_match]
		return fights
	else:
		raise click.BadParameter('Fights must be formated as 1-5 or 1,2,3,4,5')

def validate_output(ctx, param, value):
	if not re.search('%[0-9]*d', value):
		raise click.BadParameter('Output file must contain %d, which will be the fight id')
	return value

def validate_padding(ctx, param, value):
	return (value or 5) * 1000 # Default value is 5000

def validate_start_padding(ctx, param, value):
	return (value or 0) * 1000

def validate_end_padding(ctx, param, value):
	return (value or 10) * 1000 # Default is 10

@click.command()
@click.option('-i', '--input', type=click.Path(), help='Video file input', required=True)
@click.option('-r', '--report', type=str, help='WarcraftLogs report id', required=True)
@click.option('-o', '--output', type=click.Path(), help='Video file output', required=True, callback=validate_output)
@click.option('-k', '--api_key', type=str, help='WarcraftLogs API Key', required=True)
@click.option('--fights', type=str, help='Whitelist of fights to export', callback=validate_fights)
@click.option('--creation_time', type=int, help='Override file creation time')
@click.option('--modified_time', type=int, help='Override file modified time')
@click.option('--padding', type=int, help='Number of seconds to include before and after the fight', callback=validate_padding)
@click.option('--start_padding', type=int, help='Number of seconds to include before the fight', callback=validate_start_padding)
@click.option('--end_padding', type=int, help='Number of seconds to include after the fight', callback=validate_end_padding)
@click.option('--ffmpeg_options', type=str, help='Custom ffmpeg options')
@click.option('--vcodec', type=str, help='ffmpeg video codec', default='copy', show_default=True)
@click.option('--acodec', type=str, help='ffmpeg audio codec', default='copy', show_default=True)
@click.option('--ffmpeg_map', type=str, help='ffmpeg map', default='0', show_default=True)
@click.option('--print', 'printCommands', flag_value=True, default=False, help="Print ffmpeg commands instead of running them")
def main(input, report, output, api_key, fights,
		creation_time, modified_time, padding, start_padding, end_padding,
		ffmpeg_options, vcodec, acodec, ffmpeg_map, printCommands):
	if not creation_time or not modified_time:
		creation_time, modified_time = tuple(i * 1000 for i in get_creation_time(input))
	report_start_time, report_end_time = get_report_time(report)

	fight_times = get_report_fight_times(api_key, report)
	# Filter fights if there is a whilteist
	if fights:
		fight_times = filter(lambda f: f['id'] in fights, fight_times)

	video_bounds = []
	for fight in fight_times:
		start_time = fight['start_time'] + report_start_time - padding - start_padding
		end_time = fight['end_time'] + report_start_time + padding + end_padding

		start_time = clamp(start_time, creation_time, modified_time)
		end_time = clamp(end_time, creation_time, modified_time)
		duration = end_time - start_time + padding * 2 + start_padding + end_padding

		if start_time < end_time and end_time <= modified_time:
			video_bounds.append({
				'start_time': ms_to_time(start_time - creation_time),
				'end_time': ms_to_time(end_time - creation_time),
				'duration': ms_to_time(duration),
				'id': fight['id']
			})

	commands = [
		generate_ffmpeg_command(input, output,
				vcodec, video['start_time'], video['duration'], video['id'],
				ffmpeg_options, ffmpeg_map, acodec
		)
		for video in video_bounds
	]
	print('Fetched data, starting video split')
	for command in commands:
		if printCommands:
			print(' '.join(command))
		else:
			subprocess.call(command)
	print('Finished')


if __name__ == '__main__':
	main()
