from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from plyer import tts
import platform


class RunningApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        # Initial UI components
        self.status_label = Label(text='Ready to start your workout!', size_hint=(1, 0.2), font_size=24)
        self.add_widget(self.status_label)

        # Dropdown for Run Cycle Duration with 15s increments up to 10 minutes
        run_values = [str(i) for i in range(15, 601, 15)]  # 15s, 30s, 45s, ..., 600s (10 minutes)
        self.run_duration_spinner = Spinner(
            text='Run Cycle (s)', values=run_values,
            size_hint=(0.5, None), height=44
        )
        self.run_duration_spinner.bind(text=self.update_run_duration)
        self.add_widget(self.run_duration_spinner)

        # Dropdown for Walk Cycle Duration with 15s increments up to 10 minutes
        walk_values = [str(i) for i in range(15, 601, 15)]  # 15s, 30s, 45s, ..., 600s (10 minutes)
        self.walk_duration_spinner = Spinner(
            text='Walk Cycle (s)', values=walk_values,
            size_hint=(0.5, None), height=44
        )
        self.walk_duration_spinner.bind(text=self.update_walk_duration)
        self.add_widget(self.walk_duration_spinner)

        # Dropdown for Total Cycles
        self.cycles_spinner = Spinner(
            text='Total Cycles', values=('3', '5', '7', '10'),
            size_hint=(0.5, None), height=44
        )
        self.cycles_spinner.bind(text=self.update_cycles)
        self.add_widget(self.cycles_spinner)

        # Progress Bar for visual feedback
        self.progress_bar = ProgressBar(max=100, value=0, size_hint=(1, None), height=30)
        self.add_widget(self.progress_bar)

        # Control buttons
        self.start_button = Button(text='Start Workout', on_press=self.start_workout, size_hint=(1, 0.2))
        self.add_widget(self.start_button)

        self.stop_button = Button(text='Stop Workout', on_press=self.stop_workout, size_hint=(1, 0.2))
        self.stop_button.disabled = True
        self.add_widget(self.stop_button)

        # Initialize state variables
        self.running_duration = 60  # Default running time
        self.walking_duration = 30  # Default walking time
        self.total_cycles = 3  # Default number of cycles
        self.is_running = False
        self.current_cycle = 0

    def start_workout(self, instance):
        self.status_label.text = f'Starting Warm-Up...'
        self.speak('Starting warm-up')
        self.is_running = True
        self.current_cycle = 1
        self.start_button.disabled = True
        self.stop_button.disabled = False
        Clock.schedule_once(self.start_running_phase, 1)

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
            self.stop_workout(None)
        else:
            self.start_running_phase(None)

    def stop_workout(self, instance):
        self.is_running = False
        self.status_label.text = 'Workout Stopped'
        self.speak('Workout has been stopped')
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.progress_bar.value = 0

    def update_run_duration(self, spinner, text):
        self.running_duration = int(text)
        if self.is_running:
            self.status_label.text = f"Run cycle set to {self.running_duration} seconds."

    def update_walk_duration(self, spinner, text):
        self.walking_duration = int(text)
        if self.is_running:
            self.status_label.text = f"Walk cycle set to {self.walking_duration} seconds."

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


class RunTrackerApp(App):
    def build(self):
        return RunningApp()


if __name__ == '__main__':
    RunTrackerApp().run()
