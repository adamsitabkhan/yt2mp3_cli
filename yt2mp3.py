import os
import sys
import yt_dlp
# import pyinputplus as pyip
from prompt_toolkit import prompt
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from dotenv import load_dotenv, set_key

def get_valid_input(prompt):
    """Helper to ensure non-empty input."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Input cannot be empty. Please try again.")

def set_metadata(file_path, title, artist):
    """Sets the Title and Artist ID3 tags for an MP3 file."""
    try:
        audio = MP3(file_path, ID3=EasyID3)
        try:
            audio.add_tags()
        except Exception:
            pass  # Tags might already exist
        
        audio['title'] = title
        audio['artist'] = artist
        audio.save()
        print(f"✅ Downloaded '{title}' by '{artist}'\n")
    except Exception as e:
        print(f"⚠️ Could not tag file: {e}")

def process_video(entry, output_folder):
    """
    Process a single video entry: verify metadata, download, and tag.
    """
    video_url = entry.get('webpage_url') or entry.get('url')
    original_title = entry.get('title', 'Unknown Title')
    original_artist = entry.get('uploader', 'Unknown Artist')

    # print(f"\n--- Processing: {original_title} ---")
    
    # Step 3a: Verify Metadata
    print(f"Detected Title:  {original_title}")
    print(f"Detected Artist: {original_artist}")
    
    confirm = input("Are these properties correct? [Y/n]: ").strip().lower()
    
    final_title = original_title
    final_artist = original_artist

    if confirm == 'n':
        # This puts the text inside the input buffer so it's already typed out
        final_title = prompt("Edit Title: ", default=original_title)
        final_artist = prompt("Edit Artist: ", default=original_artist)
        
    final_name = f"{final_title} - {final_artist}"

    # Configure download options
    # We use a temporary filename template to ensure we can locate the file easily
    temp_filename = f"{entry['id']}_temp"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_folder, f"{final_name}.%(ext)s"), # Output filename based on final title
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': f"C:\\Users\\{os.environ.get('USERNAME')}\\AppData\\Local\\Microsoft\\WinGet\\Packages\\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\\ffmpeg-8.0.1-full_build\\bin",
        'quiet': True,
        'no_warnings': True,
    }

    try:
        print(f"⬇️  Downloading '{final_name}'...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        # Calculate expected file path
        # Note: yt-dlp sanitizes filenames, so we must be careful. 
        # A simpler approach for tagging is to find the file we just created.
        # However, since we named it based on final_title, let's look for that.
        
        # To handle filesystem sanitization (e.g., removing characters like "?"), 
        # we check the directory for the most recently created mp3 if exact match fails, 
        # or rely on standard sanitization.
        
        expected_filename = f"{final_name}.mp3"
        # Sanitize filename simply to match common OS restrictions if needed, 
        # but usually yt-dlp handles this. 
        # For this script, we assume the user inputs valid filename characters or we scan.
        
        file_path = os.path.join(output_folder, expected_filename)
        
        # If strict match fails, try finding the file by creation time (fallback)
        if not os.path.exists(file_path):
             # Try to find the file via yt-dlp's prepare_filename if needed, 
             # but simpler is to list dir and find the match.
             # For robust CLI, we'll assume standard naming succeeded.
             pass

        # Apply Metadata
        if os.path.exists(file_path):
            set_metadata(file_path, final_title, final_artist)
        else:
            print(f"⚠️  File downloaded but path not found for tagging: {file_path}")
            # Fallback: Scan folder for the file that closely matches
            
    except Exception as e:
        print(f"❌ Error downloading {original_title}: {e}")

def main():
    print("===== YouTube to MP3 Downloader CLI =====\n")
    
    load_dotenv()
    output_folder = os.getenv("OUTPUT_FOLDER")

    # check if output folder is stored in .env
    replace = None
    if output_folder:
        replace = input(f"Output folder path set to \"{output_folder}\". Continue? [Y/n] ")
    
    # set new output folder
    if not output_folder or replace == 'n':    
        while True:
            output_folder = input("Enter output folder path: ").strip()
            # Remove quotes if user copied path as "path/to/folder"
            output_folder = output_folder.strip('"').strip("'")
            
            if not os.path.exists(output_folder):
                create = input("Folder does not exist. Create it? [Y/n]: ").strip().lower()
                if create != 'n':
                    try:
                        os.makedirs(output_folder)
                        break
                    except OSError as e:
                        print(f"Error creating folder: {e}")
                else:
                    continue
            else:
                break
            
    # write output folder to .env
    set_key(".env", "OUTPUT_FOLDER", output_folder)
    
    while True:

        # input link
        url = get_valid_input("Enter YouTube video or playlist link: ")

        print("\n🔍 Fetching information... please wait.")
        
        try:
            # Extract info without downloading first to determine if playlist or video
            ydl_opts_info = {
                'extract_flat': 'in_playlist', # Just get video metadata, don't download
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                info = ydl.extract_info(url, download=False)

            # 3. Process Logic
            if 'entries' in info:
                # It's a playlist
                print(f"\n📋 Playlist detected: {info.get('title')}")
                print(f"Found {len(info['entries'])} videos.\n")
                
                for entry in info['entries']:
                    process_video(entry, output_folder)
            else:
                # It's a single video
                process_video(info, output_folder)

        except Exception as e:
            print(f"\n❌ Critical Error: {e}")
            print("Ensure the link is valid and yt-dlp is up to date.")


if __name__ == "__main__":
    main()