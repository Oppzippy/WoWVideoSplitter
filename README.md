# WoWVideoSplitter

Splits video recordings of World of Warcraft raids into separate video files. Timing is determined by a WarcraftLogs report and the creation time of the video.

* Options:  
  * -i, --input PATH         Video file input  [required]
  * -r, --report TEXT        WarcraftLogs report id  [required]
  * -o, --output PATH        Video file output  [required]
  * -k, --api_key TEXT       WarcraftLogs API Key  [required]
  * --fights TEXT            Whitelist of fights to export
  * --creation_time INTEGER  Override file creation time
  * --modified_time INTEGER  Override file modified time
  * --padding INTEGER        Number of seconds to include before and after the fight
  * --start_padding INTEGER  Number of seconds to include before the fight
  * --end_padding INTEGER    Number of seconds to include after the fight
  * --ffmpeg_options TEXT    Custom ffmpeg options
  * --print                  Print ffmpeg commands instead of running them
  * --help                   Show this message and exit.
