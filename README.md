# WoWVideoSplitter

Options:  
  -i, --input PATH         Video file input  [required]  
  -r, --report TEXT        WarcraftLogs report id  [required]  
  -o, --output PATH        Video file output  [required]  
  -k, --api_key TEXT       WarcraftLogs API Key  [required]  
  --fights TEXT            Whitelist of fights to export  
  --creation_time INTEGER  Override file creation time  
  --modified_time INTEGER  Override file modified time  
  --padding INTEGER        Number of seconds to include before and after the fight  
  --start_padding INTEGER  Number of seconds to include before the fight  
  --end_padding INTEGER    Number of seconds to include after the fight  
  --ffmpeg_options TEXT    Custom ffmpeg options  
  --vcodec TEXT            ffmpeg video codec  [default: copy]  
  --acodec TEXT            ffmpeg audio codec  [default: copy]  
  --ffmpeg_map TEXT        ffmpeg map  [default: 0]  
  --print                  Print ffmpeg commands instead of running them  
  --help                   Show this message and exit.  
  
