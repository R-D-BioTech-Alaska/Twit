# This program is a rough draft, but it works well for current x.com settings. I created this to spread more information about Qelm.
# Currently this program calls your keys from the keys.py file and sends random texts from a text file you include in the same folder.
# I will update this more as time allows, but don't expect much.

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import datetime, os, random, re
import tweepy
import openai
import ssl
import urllib.parse
import threading
import keys

#  New helper functions from references

def initialize_tweepy():
    client_v2 = tweepy.Client(
        consumer_key=keys.api_key,
        consumer_secret=keys.api_secret,
        access_token=keys.access_token,
        access_token_secret=keys.access_token_secret
    )
    auth = tweepy.OAuthHandler(keys.api_key, keys.api_secret)
    auth.set_access_token(keys.access_token, keys.access_token_secret)
    api_v1 = tweepy.API(auth)
    return client_v2, api_v1

def generate_response(prompt):
    openai.api_key = keys.openai_key
    model = "gpt-4-1106-preview"
    # Check if ChatCompletion is available (new API)
    if hasattr(openai, 'ChatCompletion'):
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    else:
        # Fallback using text completion for older API versions
        fallback_model = "text-davinci-003"
        response = openai.Completion.create(
            model=fallback_model,
            prompt=prompt,
            temperature=0,
            max_tokens=150
        )
        return response.choices[0].text.strip()

def get_formatted_date():
    return datetime.date.today().strftime("%B %d, %Y")

# Main Application (GUI + Scheduling)

class AutoTweetApp:
    def __init__(self, master):
        self.master = master
        master.title("Twit - Auto Tweet Program")
        master.configure(bg='#ADD8E6')

        self.scheduled_tweets = []
        self.client_v2 = None

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill='both', expand=True)

        # Tab 1: Scheduling
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text='Scheduling')
        self.create_scheduling_tab(self.tab1)

        # Tab 2: AI Tweets
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text='AI Tweets')
        self.create_ai_tweets_tab(self.tab2)

        # Tab 3: Progress & Daily
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text='Progress & Daily')
        self.create_progress_daily_tab(self.tab3)

    def create_scheduling_tab(self, parent):
        frame = ttk.Frame(parent, padding="5")
        frame.pack(fill=tk.BOTH, expand=True)

        self.btn_test_tweet = ttk.Button(frame, text="Send Test Tweet", command=self.send_test_tweet)
        self.btn_test_tweet.grid(row=0, column=0, pady=3, sticky='ew')

        self.btn_upload = ttk.Button(frame, text="Upload File", command=self.upload_file)
        self.btn_upload.grid(row=0, column=1, pady=3, sticky='ew')

        ttk.Label(frame, text="Tweet Content:").grid(row=1, column=0, sticky=tk.W)
        self.text_tweet = tk.Text(frame, height=3, width=40)
        self.text_tweet.grid(row=2, column=0, columnspan=2, pady=3, sticky='ew')

        self.use_file_var = tk.BooleanVar()
        self.check_use_file = ttk.Checkbutton(frame, text="Use random tweet from file", variable=self.use_file_var)
        self.check_use_file.grid(row=3, column=0, columnspan=2, pady=3, sticky='w')

        ttk.Label(frame, text="Select Days:").grid(row=4, column=0, sticky=tk.W)
        days_frame = ttk.Frame(frame)
        days_frame.grid(row=5, column=0, columnspan=2, sticky='w')
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.days_vars = {}
        for d in days:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(days_frame, text=d, variable=var)
            cb.pack(side=tk.LEFT, padx=2)
            self.days_vars[d] = var

        ttk.Label(frame, text="Select Hours:").grid(row=6, column=0, sticky=tk.W, pady=(5,0))
        self.listbox_hours = tk.Listbox(frame, selectmode='multiple', height=4)
        self.listbox_hours.grid(row=7, column=0, columnspan=2, sticky='ew')
        hours = [f"{h:02d}:00" for h in range(24)]
        for hour in hours:
            self.listbox_hours.insert(tk.END, hour)

        self.btn_schedule = ttk.Button(frame, text="Schedule Tweet", command=self.schedule_tweet)
        self.btn_schedule.grid(row=8, column=0, columnspan=2, pady=5, sticky='ew')

        ttk.Label(frame, text="Scheduled Tweets:").grid(row=9, column=0, sticky=tk.W)
        self.listbox_scheduled = tk.Listbox(frame, selectmode='extended', height=6)
        self.listbox_scheduled.grid(row=10, column=0, columnspan=2, sticky='ew', pady=3)

        self.btn_activate = ttk.Button(frame, text="Activate/Deactivate Selected", command=self.toggle_tweet)
        self.btn_activate.grid(row=11, column=0, columnspan=2, pady=3, sticky='ew')

        self.btn_remove = ttk.Button(frame, text="Remove Selected", command=self.remove_selected_tweets)
        self.btn_remove.grid(row=12, column=0, columnspan=2, pady=3, sticky='ew')

    def create_ai_tweets_tab(self, parent):
        frame = ttk.Frame(parent, padding="5")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="AI Tweet Template:").grid(row=0, column=0, sticky=tk.W)
        self.ai_template = tk.Text(frame, height=3, width=40)
        self.ai_template.grid(row=1, column=0, columnspan=2, pady=3, sticky='ew')

        self.btn_preview_ai = ttk.Button(frame, text="Generate Preview", command=self.preview_ai_tweet)
        self.btn_preview_ai.grid(row=2, column=0, pady=3, sticky='ew')

        self.btn_send_ai = ttk.Button(frame, text="Send AI Tweet", command=self.send_ai_custom_tweet)
        self.btn_send_ai.grid(row=2, column=1, pady=3, sticky='ew')

        ttk.Label(frame, text="Preview:").grid(row=3, column=0, sticky=tk.W)
        self.ai_preview = tk.Text(frame, height=4, width=40, state='disabled')
        self.ai_preview.grid(row=4, column=0, columnspan=2, pady=3, sticky='ew')

    def create_progress_daily_tab(self, parent):
        frame = ttk.Frame(parent, padding="5")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Progress:").pack(anchor=tk.W)
        self.progress = ttk.Progressbar(frame, length=200, mode='determinate')
        self.progress.pack(anchor=tk.W)

        ttk.Label(frame, text="Today's Schedule:").pack(anchor=tk.W, pady=(5,0))
        self.listbox_daily = tk.Listbox(frame, height=10, width=50)
        self.listbox_daily.pack(fill=tk.BOTH, expand=True)

    def send_test_tweet(self):
        client_v2, _ = initialize_tweepy()
        try:
            with open('tweets.txt', 'r', encoding='utf-8') as f:
                content = f.read()
            tweets = re.findall(r"\{(.*?)\}", content, re.DOTALL)
            if not tweets:
                raise ValueError("No tweets found enclosed in curly braces.")
            tweet_text = random.choice(tweets).strip()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read tweets from file: {e}")
            return

        try:
            response = client_v2.create_tweet(text=tweet_text)
            messagebox.showinfo("Success", "Test tweet sent successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send test tweet: {e}")

    def preview_ai_tweet(self):
        prompt = self.ai_template.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showerror("Error", "Please provide an AI tweet template.")
            return
        try:
            tweet_text = generate_response(prompt)
            self.ai_preview.config(state='normal')
            self.ai_preview.delete("1.0", tk.END)
            self.ai_preview.insert(tk.END, tweet_text)
            self.ai_preview.config(state='disabled')
        except Exception as e:
            messagebox.showerror("Error", f"AI generation failed: {e}")

    def send_ai_custom_tweet(self):
        prompt = self.ai_template.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showerror("Error", "Please provide an AI tweet template.")
            return
        client_v2, _ = initialize_tweepy()
        try:
            tweet_text = generate_response(prompt)
        except Exception as e:
            messagebox.showerror("Error", f"AI generation failed: {e}")
            return

        try:
            response = client_v2.create_tweet(text=tweet_text)
            messagebox.showinfo("Success", "AI tweet posted successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send AI tweet: {e}")

    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    _ = f.read()
                messagebox.showinfo("File Loaded", f"Successfully loaded {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file: {e}")

    def schedule_tweet(self):
        if self.use_file_var.get():
            try:
                with open('tweets.txt', 'r', encoding='utf-8') as f:
                    content = f.read()
                tweets = re.findall(r"\{(.*?)\}", content, re.DOTALL)
                if not tweets:
                    raise ValueError("No tweets found enclosed in curly braces.")
                tweet_content = random.choice(tweets).strip()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to get tweet from file: {e}")
                return
        else:
            tweet_content = self.text_tweet.get("1.0", tk.END).strip()
            if not tweet_content:
                messagebox.showerror("Error", "Tweet content cannot be empty.")
                return

        selected_days = [day for day, var in self.days_vars.items() if var.get()]
        selected_hours = [self.listbox_hours.get(i) for i in self.listbox_hours.curselection()]

        if not selected_days:
            messagebox.showerror("Error", "Please select at least one day.")
            return
        if not selected_hours:
            messagebox.showerror("Error", "Please select at least one hour.")
            return

        start_date = datetime.date.today()
        end_date = start_date + datetime.timedelta(days=30)
        current_date = start_date

        while current_date <= end_date:
            if current_date.strftime('%A') in selected_days:
                for hour_str in selected_hours:
                    hour_int = int(hour_str.split(':')[0])
                    scheduled_datetime = datetime.datetime.combine(current_date, datetime.time(hour_int, 0))
                    tweet_data = {
                        "content": tweet_content,
                        "datetime": scheduled_datetime,
                        "active": True
                    }
                    self.scheduled_tweets.append(tweet_data)
                    display_text = f"{tweet_content[:30]}... at {scheduled_datetime.strftime('%Y-%m-%d %H:%M')} (Active)"
                    self.listbox_scheduled.insert(tk.END, display_text)
            current_date += datetime.timedelta(days=1)

        messagebox.showinfo("Scheduled", "Tweet(s) scheduled successfully!")

    def toggle_tweet(self):
        selection = self.listbox_scheduled.curselection()
        if selection:
            index = selection[0]
            tweet = self.scheduled_tweets[index]
            tweet["active"] = not tweet["active"]
            status = "Active" if tweet["active"] else "Inactive"
            self.listbox_scheduled.delete(index)
            content = tweet["content"]
            scheduled_datetime = tweet["datetime"]
            display_text = f"{content[:30]}... at {scheduled_datetime.strftime('%Y-%m-%d %H:%M')} ({status})"
            self.listbox_scheduled.insert(index, display_text)
        else:
            messagebox.showerror("Error", "No tweet selected")

    def remove_selected_tweets(self):
        selected_indices = self.listbox_scheduled.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "No tweets selected for removal.")
            return
        for index in reversed(selected_indices):
            self.listbox_scheduled.delete(index)
            del self.scheduled_tweets[index]
        messagebox.showinfo("Removed", "Selected tweets removed from schedule.")

    def update_progress(self, value):
        self.progress['value'] = value
        self.master.update_idletasks()

    def run_scheduler(self):
        now = datetime.datetime.now()

        self.listbox_daily.delete(0, tk.END)
        for tweet_dict in self.scheduled_tweets:
            if tweet_dict["active"] and tweet_dict["datetime"].date() == now.date():
                time_str = tweet_dict["datetime"].strftime("%H:%M")
                self.listbox_daily.insert(tk.END, f"{time_str} - {tweet_dict['content'][:30]}...")

        for tweet_dict in self.scheduled_tweets:
            if tweet_dict["active"] and tweet_dict["datetime"] <= now:
                try:
                    client_v2, _ = initialize_tweepy()
                    posted_tweet = client_v2.create_tweet(text=tweet_dict["content"])
                    print(f"Tweet Posted: ID {posted_tweet.data['id']}")
                    tweet_dict["active"] = False
                    self.update_progress(100)
                except tweepy.TweepyException as e:
                    messagebox.showerror("Error", f"Error posting tweet: {e}")

        self.master.after(60000, self.run_scheduler)

    def start(self):
        self.run_scheduler()
        self.master.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoTweetApp(root)
    app.start()
