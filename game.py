import os
import tkinter
import customtkinter
from PIL import Image, ImageTk
import pygame
import cv2

# Get the directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the paths to the music and video files relative to the script's directory
music_path = os.path.join(BASE_DIR, "Assests", "Royalty free forest music for games.mp3")
video_path = os.path.join(BASE_DIR, "Assests", "Pixel Art Forest - Background.mp4")

# Initialize the Pygame mixer for audio
pygame.mixer.init()

# Load and play the background music if the file exists
if os.path.exists(music_path):
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(0.5)  # Set the initial volume (0.0 to 1.0)
    pygame.mixer.music.play(-1)  # Play the music in a loop (-1 means infinite loop)
else:
    print(f"Error: Music file not found -> {music_path}")

# Initialize video capture from the specified video file
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"Error: Video file not found -> {video_path}")

# Initialize the main Tkinter application window using CustomTkinter
app = customtkinter.CTk()
app.geometry("1920x1080")  # Set the initial size of the window
customtkinter.set_appearance_mode("dark")  # Set the overall theme to dark mode
app.title("ECHOES")  # Set the title of the application window

# Function to update the background video frame by frame
def update_video():
    # Read a frame from the video capture
    ret, frame = cap.read()
    if ret:  # If a frame was successfully read
        # Resize the frame to the window dimensions
        frame = cv2.resize(frame, (1920, 1080))
        # Convert the frame from BGR (OpenCV's default) to RGB (for PIL)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Convert the NumPy array (frame) to a PIL Image object
        img = Image.fromarray(frame)
        # Convert the PIL Image object to a Tkinter PhotoImage object
        img_tk = ImageTk.PhotoImage(image=img)

        # Update the background label's image
        bg_label.config(image=img_tk)
        # Keep a reference to the image object to prevent garbage collection
        bg_label.image = img_tk

    # Schedule this function to be called again after 30 milliseconds (approximately 30 frames per second)
    app.after(30, update_video)

# Function to display the main menu screen
def show_main_menu():
    # Clear all widgets from the screen (except the background label)
    clear_screen()
    # Place the title label in the center-top of the screen
    title_label.place(relx=0.5, rely=0.15, anchor="center")
    # Place the start button in the center of the screen
    btn_start.place(relx=0.5, rely=0.4, anchor="center")
    # Place the options button below the start button
    btn_options.place(relx=0.5, rely=0.5, anchor="center")
    # Place the credits button below the options button
    btn_credits.place(relx=0.5, rely=0.6, anchor="center")
    # Place the exit button below the credits button
    btn_exit.place(relx=0.5, rely=0.7, anchor="center")

# Function to display the options menu
def show_options():
    # Clear all widgets from the screen (except the background label)
    clear_screen()

    # Boolean variable to track the music state (initially ON)
    music_var = tkinter.BooleanVar(value=True)

    # Function to toggle the background music on/off
    def toggle_music():
        if music_var.get():
            pygame.mixer.music.play(-1)  # Start or resume playing the music loop
            music_status.configure(text="Music: ON")  # Update the music status label
        else:
            pygame.mixer.music.stop()  # Stop the background music
            music_status.configure(text="Music: OFF")  # Update the music status label

    # Checkbox to enable/disable music
    music_checkbox = customtkinter.CTkCheckBox(
        app, text="Enable Music", variable=music_var, command=toggle_music
    )
    music_checkbox.place(relx=0.5, rely=0.4, anchor="center")

    # Label to display the current music status
    music_status = customtkinter.CTkLabel(app, text="Music: ON", font=("Pixelify Sans", 20), text_color="white")
    music_status.place(relx=0.5, rely=0.45, anchor="center")

    # Label for the volume slider
    volume_label = customtkinter.CTkLabel(app, text="Volume", font=("Pixelify Sans", 20), text_color="white")
    volume_label.place(relx=0.5, rely=0.5, anchor="center")

    # Function to change the volume of the background music
    def change_volume(value):
        pygame.mixer.music.set_volume(float(value) / 100)  # Set volume based on slider value (0.0 to 1.0)

    # Slider to control the music volume
    volume_slider = customtkinter.CTkSlider(app, from_=0, to=100, command=change_volume)
    volume_slider.set(50)  # Set the initial slider value to 50
    volume_slider.place(relx=0.5, rely=0.55, anchor="center")

    # Place the back button to return to the main menu
    btn_back.place(relx=0.5, rely=0.7, anchor="center")

# Function to display the credits screen
def show_credits():
    # Clear all widgets from the screen (except the background label)
    clear_screen()

    # Label to display the game credits
    credits_label = customtkinter.CTkLabel(
        app, text="Game Created by:\nBaldonado Arnaldo\nChing Jose\nMamaril Lance\nSantiago Hermogenes",
        font=("Pixelify Sans", 24), text_color="white"
    )
    credits_label.place(relx=0.5, rely=0.5, anchor="center")

    # Place the back button to return to the main menu
    btn_back.place(relx=0.5, rely=0.7, anchor="center")

# Function to remove all widgets from the application window (except the background label)
def clear_screen():
    for widget in app.winfo_children():
        # Check if the widget is not the background label
        if not isinstance(widget, tkinter.Label):
            widget.place_forget()  # Remove the widget from the screen

# Create a label to display the background video
bg_label = tkinter.Label(app)
bg_label.place(relwidth=1, relheight=1)  # Make the label fill the entire window

# Create the title label for the main menu
title_label = customtkinter.CTkLabel(
    master=app,
    text="ECHOES OF HOME",
    font=("Pixelify Sans", 40, "bold"),
    text_color="white",
    fg_color="transparent",
    bg_color="transparent"
)

# Configuration dictionary for the menu buttons
button_config = {
    "width": 220, "height": 60, "font": ("Pixelify Sans", 20, "bold"),
    "corner_radius": 32, "fg_color": "transparent", "bg_color": "transparent",
    "border_width": 3, "text_color": "white"
}

# Create the "Start" button
btn_start = customtkinter.CTkButton(master=app, text="Start", border_color="#50C878", hover_color="#50C878", command=lambda: print("Start Game"), **button_config)
# Create the "Options" button
btn_options = customtkinter.CTkButton(master=app, text="Options", border_color="#FFD700", hover_color="#FFD700", command=show_options, **button_config)
# Create the "Credits" button
btn_credits = customtkinter.CTkButton(master=app, text="Credits", border_color="#1E90FF", hover_color="#1E90FF", command=show_credits, **button_config)
# Create the "Exit" button
btn_exit = customtkinter.CTkButton(master=app, text="Exit", border_color="#FF4500", hover_color="#FF4500", command=app.quit, **button_config)
# Create the "Back" button (used in options and credits menus)
btn_back = customtkinter.CTkButton(master=app, text="Back", border_color="white", hover_color="gray", command=show_main_menu, **button_config)

# Initially show the main menu
show_main_menu()
# Start updating the background video
update_video()

# Start the Tkinter event loop, which keeps the application running and responsive
app.mainloop()

# Release the video capture object when the application is closed
cap.release()