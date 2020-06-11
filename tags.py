import sys
import os
import logging
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from datetime import datetime
import stat
import json
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

EXT_MP3 = ".mp3"
EXT_FLAC = ".flac"
MUSIC_FILES = [EXT_MP3, EXT_FLAC]
FS_ENC = sys.getfilesystemencoding()

def get_mp3_metadata(f):
	return dict(EasyID3(f).items())

def get_flac_metadata(f):
	return dict(FLAC(f).items())


FILE_PROCESSORS = {
	EXT_MP3: get_mp3_metadata,
	EXT_FLAC: get_flac_metadata
}

def get_file_metadata(f):
	try:
		log.info("getting metadata for file " + f)
		tag_data = FILE_PROCESSORS[os.path.splitext(f)[1].lower()](f)
		stats = os.stat(f)
		return dict(file=f, 
				tag_data=tag_data, 
				create_date=datetime.fromtimestamp(stats[stat.ST_CTIME]).isoformat(),
				modify_date=datetime.fromtimestamp(stats[stat.ST_MTIME]).isoformat()
)
	except Exception as ex:
		log.exception(ex)
		return dict(file=f, exception=str(ex))

def iter_music_files(directory):
	for r, dirs, files in os.walk(directory):
		for file_item in (os.path.join(r, f) for f in files):
			if os.path.splitext(file_item)[1].lower() in MUSIC_FILES:
				yield get_file_metadata(file_item)



if __name__ == '__main__':
	root_dir = sys.argv[1]
	if not os.path.exists(root_dir):
		raise ValueError(root_dir + " does not exist")
	with open("output.json", "w+") as f:
		f.write(json.dumps(list(iter_music_files(root_dir)))	)
