# Scrape google index
Semi-automatic script for collecting google index positions of specific site for specific google search.
Part of handling non human factor is not handled. That part needs to be manually done.

# Usage
py main.py 
- site [site url] 
-keywords [keyword1],[keyword2]...[keywordn] 
-latitude [latitude coordinate] 
-longitude [longitude coordinate]

Can also be converted into .exe file for easier usage.
1) run "python -m PyInstaller --onefile --name scraper main.py"
2) in scraper.spec add import "from kivy_deps import sdl2, glew"
3) in scraper.spec find "into "exe = EXE(pyz, Tree('scraper'),...."" and change "[]," into "*[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)]," 
4) run "python -m PyInstaller scraper.spec"
