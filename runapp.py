import os
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from plyer import tts

# File paths
USER_DATA_FILE = 'users.json'
WORKOUT_HISTORY_FILE = 'workout_history.json'
LOGIN_FILE = 'login.json'

# Simple in-memory user storage
users_db = {}
workout_history = []


def load_data():
    global users_db
    # Load user data from the file
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            users_db = json.load(f)

    # Load the logged-in user from the login file
    if os.path.exists(LOGIN_FILE):
        with open(LOGIN_FILE, 'r') as f:
            login_data = json.load(f)
            username = login_data.get("username")
            if username and username in users_db:
                return username, users_db[username].get('workout_history', [])

    return None, []  # Return None if no logged-in user is found


def save_data(users_db):
    # Save user data (with workout history) to the file
    username = users_db.get("current_username")  # Make sure to define the current logged-in user
    if username:
        # Update the user's workout history (if any changes)
        users_db[username]['workout_history'] = workout_history
        save_data(users_db)

    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users_db, f, indent=4)


class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.username_input = TextInput(hint_text="Username", size_hint=(1, None), height=44)
        self.password_input = TextInput(hint_text="Password", password=True, size_hint=(1, None), height=44)
        self.confirm_password_input = TextInput(hint_text="Confirm Password", password=True, size_hint=(1, None),
                                                height=44)

        self.signup_button = Button(text="Sign Up", size_hint=(1, None), height=44)
        self.signup_button.bind(on_press=self.signup)

        self.error_label = Label(text="", color=(1, 0, 0, 1))

        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(self.confirm_password_input)
        layout.add_widget(self.signup_button)
        layout.add_widget(self.error_label)

        self.add_widget(layout)

    def signup(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        confirm_password = self.confirm_password_input.text

        if not username or not password or not confirm_password:
            self.error_label.text = "All fields are required!"
        elif password != confirm_password:
            self.error_label.text = "Passwords do not match!"
        elif username in users_db:
            self.error_label.text = "Username already exists!"
        else:
            # Only save the password to the users_db, not the confirm_password
            users_db[username] = {'password': password, 'workout_history': []}
            self.error_label.text = "Signup successful!"
            save_data(users_db)  # Save user data, including workout history (empty initially)
            # Switch to login screen after signup
            self.manager.current = 'login'


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.username_input = TextInput(hint_text="Username", size_hint=(1, None), height=44)
        self.password_input = TextInput(hint_text="Password", password=True, size_hint=(1, None), height=44)

        self.login_button = Button(text="Login", size_hint=(1, None), height=44)
        self.login_button.bind(on_press=self.login)

        self.signup_button = Button(text="Sign Up", size_hint=(1, None), height=44)
        self.signup_button.bind(on_press=self.go_to_signup)

        self.error_label = Label(text="", color=(1, 0, 0, 1))

        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(self.login_button)
        layout.add_widget(self.signup_button)
        layout.add_widget(self.error_label)

        self.add_widget(layout)

    def login(self, instance):
        username = self.username_input.text
        password = self.password_input.text

        if not username or not password:
            self.error_label.text = "Both fields are required!"
        elif username not in users_db:
            self.error_label.text = "Account does not exist!"  # Adjusted error message
        elif users_db[username]['password'] != password:
            self.error_label.text = "Invalid username or password!"
        else:
            self.error_label.text = "Login successful!"
            # Save the logged-in user in login.json
            with open(LOGIN_FILE, 'w') as f:
                json.dump({"username": username}, f)
            self.manager.current = 'home'

    def go_to_signup(self, instance):
        self.manager.current = 'signup'


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.greeting_label = Label(text="Welcome to the Workout App!", font_size=24, size_hint=(1, 0.2))
        layout.add_widget(self.greeting_label)

        # Button to start the workout
        self.start_button = Button(text="Start Workout", size_hint=(1, 0.2))
        self.start_button.bind(on_press=self.go_to_workout)
        layout.add_widget(self.start_button)

        # Button to see workout history
        self.history_button = Button(text="Workout History", size_hint=(1, 0.2))
        self.history_button.bind(on_press=self.go_to_history)
        layout.add_widget(self.history_button)

        # Button to go to the account screen
        self.account_button = Button(text="Account", size_hint=(1, 0.2))
        self.account_button.bind(on_press=self.go_to_account)
        layout.add_widget(self.account_button)

        self.add_widget(layout)

    def go_to_workout(self, instance):
        self.manager.current = 'workout'

    def go_to_history(self, instance):
        self.manager.current = 'history'

    def go_to_account(self, instance):
        self.manager.current = 'account'


class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.history_label = Label(text="Workout History", font_size=24, size_hint=(1, 0.2))
        layout.add_widget(self.history_label)

        self.history_list = BoxLayout(orientation='vertical', size_hint=(1, None), height=300)
        layout.add_widget(self.history_list)

        self.back_button = Button(text="Back", size_hint=(1, 0.2))
        self.back_button.bind(on_press=self.go_back)
        layout.add_widget(self.back_button)

        self.add_widget(layout)

        # Make sure to update history when the screen is created
        self.update_history_list()

    def update_history_list(self):
        # Clear the history list and add new data for the current logged-in user
        self.history_list.clear_widgets()

        # Get the logged-in user's data
        username, _ = load_data()
        if username and username in users_db:
            workout_history = users_db[username].get('workout_history', [])
            for entry in workout_history:
                workout_entry = Label(text=f"Cycle: {entry['cycle']} | Duration: {entry['duration']}s")
                self.history_list.add_widget(workout_entry)

    def go_back(self, instance):
        self.manager.current = 'home'

    def on_enter(self):
        # Update history every time the screen is entered
        self.update_history_list()


class RunningApp(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Status label
        self.status_label = Label(text='Ready to start your workout!', size_hint=(1, 0.2), font_size=24)
        layout.add_widget(self.status_label)

        # Dropdown for Run Cycle Duration with formatted time intervals (mm:ss)
        run_values = [self.format_time(i) for i in range(15, 601, 15)]  # 15s, 30s, ..., 10 minutes
        self.run_duration_spinner = Spinner(
            text='Run Cycle (s)', values=run_values,
            size_hint=(0.5, None), height=44
        )
        self.run_duration_spinner.bind(text=self.update_run_duration)
        layout.add_widget(self.run_duration_spinner)

        # Dropdown for Walk Cycle Duration
        walk_values = [self.format_time(i) for i in range(15, 601, 5)]  # 15s, 20s, ..., 10 minutes
        self.walk_duration_spinner = Spinner(
            text='Walk Cycle (s)', values=walk_values,
            size_hint=(0.5, None), height=44
        )
        self.walk_duration_spinner.bind(text=self.update_walk_duration)
        layout.add_widget(self.walk_duration_spinner)

        # Dropdown for Total Cycles
        cycle_values = [str(i) for i in range(1, 11)]  # 1 through 10 cycles
        self.cycles_spinner = Spinner(
            text='Total Cycles', values=cycle_values,
            size_hint=(0.5, None), height=44
        )
        self.cycles_spinner.bind(text=self.update_cycles)
        layout.add_widget(self.cycles_spinner)

        # Progress Bar for visual feedback
        self.progress_bar = ProgressBar(max=100, value=0, size_hint=(1, None), height=30)
        layout.add_widget(self.progress_bar)

        # Control buttons
        self.start_button = Button(text='Start Workout', on_press=self.start_workout, size_hint=(1, 0.2))
        layout.add_widget(self.start_button)

        self.stop_button = Button(text='Stop Workout', on_press=self.stop_workout, size_hint=(1, 0.2))
        self.stop_button.disabled = True
        layout.add_widget(self.stop_button)

        # Back button
        self.back_button = Button(text='Back', size_hint=(1, 0.2))
        self.back_button.bind(on_press=self.go_back)
        layout.add_widget(self.back_button)

        self.add_widget(layout)

        # Initialize state variables
        self.running_duration = 60  # Default running time
        self.walking_duration = 30  # Default walking time
        self.total_cycles = 3  # Default number of cycles
        self.is_running = False
        self.current_cycle = 0
        self.countdown_time = 10

    def format_time(self, seconds):
        """Format time in mm:ss format"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def start_workout(self, instance):
        self.status_label.text = f'Starting Warm-Up...'
        self.speak('Starting warm-up')
        self.is_running = True
        self.current_cycle = 1
        self.start_button.disabled = True
        self.stop_button.disabled = False
        self.countdown(phase="warm-up", next_phase=self.start_running_phase)

    def start_running_phase(self, dt):
        if not self.is_running:
            return
        self.status_label.text = f'Running! Cycle {self.current_cycle}/{self.total_cycles}'
        self.progress_bar.max = self.running_duration
        self.progress_bar.value = 0
        self.speak('Start running')
        Clock.schedule_once(self.update_progress_bar_running, 1)

    def update_progress_bar_running(self, dt):
        if self.progress_bar.value < self.running_duration:
            self.progress_bar.value += 1
            Clock.schedule_once(self.update_progress_bar_running, 1)
        else:
            self.start_walking_phase(None)

    def start_walking_phase(self, dt):
        if not self.is_running:
            return
        self.status_label.text = f'Walking! Cycle {self.current_cycle}/{self.total_cycles}'
        self.progress_bar.max = self.walking_duration
        self.progress_bar.value = 0
        self.speak('Start walking')
        Clock.schedule_once(self.update_progress_bar_walking, 1)

    def update_progress_bar_walking(self, dt):
        if self.progress_bar.value < self.walking_duration:
            self.progress_bar.value += 1
            Clock.schedule_once(self.update_progress_bar_walking, 1)
        else:
            self.complete_cycle()

    def complete_cycle(self):
        self.current_cycle += 1
        if self.current_cycle > self.total_cycles:
            self.status_label.text = "Starting Cool Down..."
            self.speak("Starting cool-down")
            self.countdown(phase="cool-down", next_phase=self.stop_workout)
        else:
            self.start_running_phase(None)

    def stop_workout(self, instance):
        self.is_running = False
        self.status_label.text = 'Workout Stopped'
        self.speak('Workout has been stopped')
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.progress_bar.value = 0

        # Save workout history under the logged-in user
        username, _ = load_data()
        if username:
            workout_entry = {
                'cycle': self.total_cycles,
                'duration': (self.running_duration + self.walking_duration) * self.total_cycles,
                # Total workout duration
            }
            users_db[username].setdefault('workout_history', []).append(workout_entry)
            save_data(users_db)  # Save to file

    def countdown(self, phase, next_phase):
        """Handle a 10-second countdown."""
        if self.countdown_time > 0:
            self.status_label.text = f"{phase.capitalize()} countdown: {self.countdown_time} seconds remaining"
            self.speak(str(self.countdown_time))
            self.countdown_time -= 1
            Clock.schedule_once(lambda dt: self.countdown(phase, next_phase), 1)
        else:
            self.countdown_time = 10  # Reset countdown time for the next use
            if phase == "warm-up":
                next_phase(None)
            elif phase == "cool-down":
                next_phase(None)

    def update_run_duration(self, spinner, text):
        # Convert formatted time back to seconds
        minutes, seconds = map(int, text.split(":"))
        self.running_duration = minutes * 60 + seconds
        if self.is_running:
            self.status_label.text = f"Run cycle set to {text}."

    def update_walk_duration(self, spinner, text):
        # Convert formatted time back to seconds
        minutes, seconds = map(int, text.split(":"))
        self.walking_duration = minutes * 60 + seconds
        if self.is_running:
            self.status_label.text = f"Walk cycle set to {text}."

    def update_cycles(self, spinner, text):
        self.total_cycles = int(text)
        if self.is_running:
            self.status_label.text = f"Total cycles set to {self.total_cycles}."

    def speak(self, message):
        try:
            tts.speak(message)
        except NotImplementedError:
            print("TTS not available on this platform.")
            self.status_label.text = f"{message}"

    def go_back(self, instance):
        self.manager.current = 'home'

    def on_enter(self):
        self.manager.current = 'workout'


class AccountScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.account_label = Label(text="Account Information", font_size=24, size_hint=(1, 0.2))
        layout.add_widget(self.account_label)

        # Display username
        username, _ = load_data()
        if username:
            self.username_label = Label(text=f"Username: {username}", size_hint=(1, 0.2))
            layout.add_widget(self.username_label)

        # Logout Button
        self.logout_button = Button(text="Logout", size_hint=(1, 0.2))
        self.logout_button.bind(on_press=self.logout)
        layout.add_widget(self.logout_button)

        # Back Button
        self.back_button = Button(text="Back", size_hint=(1, 0.2))
        self.back_button.bind(on_press=self.go_back)
        layout.add_widget(self.back_button)

        self.add_widget(layout)

    def logout(self, instance):
        # Remove the login data to log the user out by deleting the LOGIN_FILE
        if os.path.exists(LOGIN_FILE):
            os.remove(LOGIN_FILE)

        # Switch to the login screen after logout
        self.manager.current = 'login'

    def go_back(self, instance):
        # Go back to the previous screen (HomeScreen or wherever the user came from)
        self.manager.current = 'home'


# Screen manager to handle all screens
class WorkoutApp(App):
    def build(self):
        # Setup screen manager
        sm = ScreenManager()

        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignupScreen(name="signup"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(HistoryScreen(name="history"))
        sm.add_widget(RunningApp(name="workout"))
        sm.add_widget(AccountScreen(name="account"))

        return sm


if __name__ == '__main__':
    load_data()
    WorkoutApp().run()
