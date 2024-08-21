rm -rf dist/*
rm -rf temp/*

pyinstaller --onefile --name 主播统计.exe --distpath dist --workpath temp --specpath temp app/run_streamer.py
pyinstaller --onefile --name 创作者中心.exe --distpath dist --workpath temp --specpath temp app/run_creator.py
pyinstaller --onefile --name 服务平台.exe --distpath dist --workpath temp --specpath temp app/run_platform.py