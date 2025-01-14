# Twit
Twit is an open source auto-tweet program with scheduler and AI addon.

Twit is a Python-based GUI application built with Tkinter that allows you to schedule tweets, generate tweets using OpenAI's GPT-4, and manage scheduled tweets. It integrates with Twitter via Tweepy and supports multi-line tweets from a file, AI-generated tweets, and scheduling options with an intuitive interface.

## Features

- **Scheduling Tweets:**
  - Schedule tweets by selecting specific days and hours.
  - Option to use random tweets from a file (`tweets.txt`) for scheduling.
  - Manage scheduled tweets: activate/deactivate and remove selected tweets.

- **AI Tweet Generation:**
  - Input a custom prompt/template for AI to generate tweets.
  - Preview AI-generated tweets before sending.
  - Send AI-generated tweets directly from the interface.

- **Progress & Daily Monitoring:**
  - View today's scheduled tweets.
  - Progress bar for scheduled tweet execution.

## Requirements

- Python 3.7+
- Packages:
  - `tweepy`
  - `openai`
  - Standard libraries: `tkinter`, `datetime`, `os`, `random`, `re`, etc.

Install required packages with:
```bash
pip install tweepy openai
```

## Setup

1. **Credentials:**
   - Create a `keys.py` file in the same directory as the main script.
   - Add your Twitter API and OpenAI credentials:
     ```python
     api_key = "YOUR_API_KEY"
     api_secret = "YOUR_API_SECRET"
     access_token = "YOUR_ACCESS_TOKEN"
     access_token_secret = "YOUR_ACCESS_TOKEN_SECRET"
     openai_key = "YOUR_OPENAI_KEY"
     ```

2. **Tweets File:**
   - Create a `tweets.txt` file in the same directory.
   - Enclose each tweet in curly braces `{...}`. For example:
     ```
     {
     This is the first tweet.
     It spans multiple lines.
     }
     {
     This is the second tweet.
     It also spans multiple lines.
     }
     ```

## Running the Application

Run the application with:
```bash
python Twit.py
```
Replace `Twit.py` with the actual name of the Python file containing the code.

## How to Use

### Scheduling Tab
- **Send Test Tweet:** Sends a random tweet from `tweets.txt`.
- **Upload File:** Opens a file dialog to upload a file (functionality placeholder).
- **Tweet Content:** Manually enter tweet content.
- **Use random tweet from file:** When checked, scheduling uses a random tweet from `tweets.txt` instead of manual content.
- **Select Days/Hours:** Choose days of the week and hours for scheduling tweets.
- **Schedule Tweet:** Schedules the tweet based on the selected options.
- **Scheduled Tweets List:** Displays scheduled tweets. Supports multiple selection.
- **Activate/Deactivate Selected:** Toggle activation status of selected tweets.
- **Remove Selected:** Remove selected tweets from the schedule.

### AI Tweets Tab
- **AI Tweet Template:** Enter a prompt/template for generating tweets with GPT-4.
- **Generate Preview:** Generates and displays a preview of the tweet based on the template.
- **Send AI Tweet:** Generates and posts a tweet using the provided template.

### Progress & Daily Tab
- **Progress Bar:** Visual indicator for scheduled tweet execution.
- **Today's Schedule:** Lists tweets scheduled for the current day.

## Scheduling Logic

The application periodically (every minute) checks for scheduled tweets and posts them at the specified times using the Twitter API.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
