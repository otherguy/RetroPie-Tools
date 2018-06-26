#!/usr/bin/env python3
from os import path, listdir, makedirs
from locale import setlocale, LC_ALL
from dialog import Dialog as dialog
from sys import exit
from xml.etree import ElementTree as xml
from pathlib import Path
from shutil import move

#####

ROM_PATH       = "Downloads/Roms/roms" # RetroPie/roms
UNSCRAPED_PATH = "Downloads/Roms/roms/unscraped"

#####

home          = str(Path.home())
rompath       = path.join(home, ROM_PATH)
unscrapedpath = path.join(home, UNSCRAPED_PATH)

setlocale(LC_ALL, '')

# Set up 'dialog'
d = dialog(autowidgetsize=True)
d.set_background_title("Remove Unscraped Roms")

# Make sure the rompath exists
if not path.isdir(rompath):
  d.msgbox("Could not find rom path %s!" % rompath)
  exit(1)

# Show an infobox
d.infobox("Searching for unscraped roms in %s...\n" % rompath)

# List of systems to clean up
systems = []

# Loop over all files in the rompath
for system in listdir(rompath):
  
  # Make sure it's a directory
  if path.isdir(path.join(rompath, system)) and path.join(rompath, system) != unscrapedpath:
    
    # Make sure there is a 'gamelist.xml' file inside
    gamelist = path.join(rompath, system, 'gamelist.xml')
    if path.exists(gamelist):
        
      # Append the system
      systems.append( (system, "", 1 ) )

# Create checklist of all found systems
code, systems = d.checklist("Which folders should be cleaned of unscraped roms?", choices=systems)

# If cancel was pressed, quit the program
if code == d.CANCEL:
  print("\033[H\033[J")
  d.clear()
  exit(1)

# Create a list of roms to move and a text placeholder
move_roms = []
move_text = ""

# Show an infobox while searching
d.infobox("Searching for unscraped roms of selected systems...")

# Loop over all selected systems
for system in systems:
  
  # Create a subfolder in the move path, if it doesn't exist
  unscraped_system_path = path.join(unscrapedpath, system)
  if not path.exists(unscraped_system_path):
    makedirs(unscraped_system_path)
    
  # Count total games (only files, subtract one for gamelist.xml which we know exists)
  total_games   = len([rom for rom in listdir(path.join(rompath, system)) if path.isfile(path.join(rompath, system, rom))]) - 1
  scraped_games = []
  
  # Get paths of scraped roms from the systems 'gamelist.xml'
  for game in xml.parse(path.join(rompath, system, 'gamelist.xml')).getroot():
    scraped_games.append(game.find('path').text)
  
  # Append to the list text
  move_text += "Games in '%s' folder: %d total, %d scraped\n===================================================\n\n" % (system, total_games, len(scraped_games))
  
  # Loop over all roms in the system path
  for rom in listdir(path.join(rompath, system)):
    
    # Build full rompath
    romfile = path.join(rompath, system, rom)
             
    # Check if the rom is a file, not in scraped games and is not the 'gamelist.xml'
    if path.isfile(romfile) and romfile not in scraped_games and rom != 'gamelist.xml':
      
      # Excception for cue/bin pairs
      if romfile.endswith('.bin') and (romfile[:-4] + ".cue") in scraped_games :
        break
      
      # Append the rom and text
      move_text += "   - %s\n" % rom
      move_roms.append( ( path.join(rompath, system, rom), path.join(unscrapedpath, system, rom) ) )

  # Add some linebreaks
  move_text += "\n\n"

# If there are no unscraped roms, we're done
if len(move_roms) == 0 :
  d.msgbox("Did not find any unscraped roms across %d systems in %s!" % (len(systems), rompath), width=60, height=6)
  print("\033[H\033[J")
  d.clear()
  exit(0)
  
# Ask if the roms should be moved
if d.scrollbox(move_text, extra_button=True, ok_label="Move roms", extra_label="Exit") == d.OK :
  
  # Show an infobox while moving
  d.infobox("Moving unscraped roms...")
  
  # Move roms to unscrapedpath
  for source, destination in move_roms:
    move(source, destination)
  
  # Done with this system
  d.msgbox("Moved %d unscraped roms to %s!\n" % (len(move_roms), unscrapedpath), width=60, height=6)

# Done  
print("\033[H\033[J")
d.clear()
exit(0)